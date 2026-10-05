#!/usr/bin/env python3
"""Generate an image via the local ComfyUI HTTP API.

Loads a ComfyUI API-format workflow template, injects parameters (identified by
each node's _meta.title), submits it, polls /history until done and prints where
ComfyUI saved the result (its output folder is the Stability Matrix image library,
Text2Img/<workflow>/, test series under Text2Img/_tests/). --out is optional: a hardlink inside the library, a plain
copy elsewhere, never a second copy of the same bytes in the library. Stdlib only
(urllib) so it runs with any Python, no pip install.

The verify step is the caller's job: read the output PNG and judge it, then
re-run with an adjusted prompt/seed if needed.

Usage (PowerShell):
  python comfy_generate.py --workflow sdxl_t2i.api.json --prompt "a red apple" \
    --width 1024 --height 1024
On success the final image path is printed to stdout.
"""
import argparse
import http.client
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

import ablage  # Ablage nach Workflow und Quelle, liegt neben diesem Skript

# ComfyUI's output folder is a junction onto the Stability Matrix image library.
COMFY_OUTPUT = r"D:\Apps\Stability Matrix\Data\Images\Text2Img"
IMAGES_ROOT = r"D:\Apps\Stability Matrix\Data\Images"

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))


def reject_out_dir(out):
    """bs-media-image/out lies on another drive, so a --out there can only be a copy: exactly
    the duplicate this skill no longer makes. Derived files (comparison sheets) may go there."""
    if out and os.path.normcase(os.path.abspath(out)).startswith(os.path.normcase(OUT_DIR + os.sep)):
        sys.exit("--out unter bs-media-image/out legt eine Zweitkopie an. Weglassen und den ausgegebenen "
                 "Bibliothekspfad verwenden, nach out/ gehören nur abgeleitete Dateien wie Vergleichsblätter.")


def expand_dates(workflow):
    """Bringt jeden SaveImage-Prefix in die Ablage nach Workflow (ablage.py): agent/%date:yyyy-MM-dd%/foto wird
    foto/foto, Testreihen landen unter _tests/<reihe>/. Ein Datum im Ordner gibt es seit dem Umzug der Bildablage
    nicht mehr, %date% käme über die HTTP-API sonst wörtlich an (WinError 267)."""
    return ablage.normalisiere(workflow)


def api(base, path, payload=None, timeout=600):
    url = base.rstrip("/") + path
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download(base, image, out_path):
    query = urllib.parse.urlencode(
        {
            "filename": image["filename"],
            "subfolder": image.get("subfolder", ""),
            "type": image.get("type", "output"),
        }
    )
    url = base.rstrip("/") + "/view?" + query
    with urllib.request.urlopen(url, timeout=600) as resp:
        blob = resp.read()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "wb") as fh:
        fh.write(blob)


def deliver(base, image, out):
    """Path of the result. ComfyUI already saved it into the image library, so
    without --out that path is returned and nothing is copied. With --out the
    file is hardlinked when the target lies inside the library (one copy on
    disk) and copied elsewhere (project folders, other drives). Falls back to
    an HTTP download when the file is not on this machine (remote --url)."""
    src = os.path.normpath(os.path.join(COMFY_OUTPUT, image.get("subfolder", ""), image["filename"]))
    if image.get("type", "output") != "output" or not os.path.exists(src):
        if not out:
            sys.exit(f"Ergebnis liegt nicht unter {COMFY_OUTPUT}, --out angeben.")
        download(base, image, out)
        return out
    if not out:
        return src
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out):
        if os.path.samefile(out, src):
            return out
        os.remove(out)
    if os.path.normcase(out).startswith(os.path.normcase(IMAGES_ROOT + os.sep)):
        os.link(src, out)
    else:
        shutil.copyfile(src, out)
    return out


def embedded_workflow(png_path):
    """Read the API graph ComfyUI embeds in a PNG's 'prompt' tEXt chunk."""
    import struct

    with open(png_path, "rb") as fh:
        if fh.read(8) != b"\x89PNG\r\n\x1a\n":
            sys.exit(f"Keine PNG-Datei: {png_path}")
        while True:
            head = fh.read(8)
            if len(head) < 8:
                break
            length, ctype = struct.unpack(">I4s", head)
            data = fh.read(length)
            fh.read(4)  # CRC
            if ctype == b"tEXt" and data.startswith(b"prompt\x00"):
                return json.loads(data.split(b"\x00", 1)[1].decode("latin-1"))
            if ctype == b"IEND":
                break
    sys.exit(f"Kein eingebetteter Workflow im PNG: {png_path}")


def upload_image(base, path):
    """Push a local image into ComfyUI's input folder; returns the name LoadImage wants."""
    if not os.path.exists(path):
        sys.exit(f"Eingangsbild fehlt: {path}")
    boundary = "----genasset" + uuid.uuid4().hex
    name = os.path.basename(path)
    with open(path, "rb") as fh:
        blob = fh.read()
    body = b"".join([
        ("--%s\r\n" % boundary).encode(),
        ('Content-Disposition: form-data; name="image"; filename="%s"\r\n' % name).encode(),
        b"Content-Type: application/octet-stream\r\n\r\n",
        blob,
        b"\r\n",
        ("--%s\r\n" % boundary).encode(),
        b'Content-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n',
        ("--%s--\r\n" % boundary).encode(),
    ])
    req = urllib.request.Request(
        base.rstrip("/") + "/upload/image",
        data=body,
        headers={"Content-Type": "multipart/form-data; boundary=" + boundary},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        info = json.loads(resp.read().decode("utf-8"))
    sub = info.get("subfolder") or ""
    return f"{sub}/{info['name']}" if sub else info["name"]


def graph_model(graph):
    """Modelldatei aus einem API-Graphen, egal ob Checkpoint, UNET oder GGUF."""
    for node in (graph or {}).values():
        inp = node.get("inputs", {})
        for feld in ("ckpt_name", "unet_name"):
            if isinstance(inp.get(feld), str):
                return inp[feld]
    return None


def graph_prompt(graph):
    """Positiver Prompt aus einem API-Graphen, bevorzugt der Knoten mit dem Titel."""
    frei = None
    for node in (graph or {}).values():
        inp = node.get("inputs", {})
        text = inp.get("text") if isinstance(inp.get("text"), str) else inp.get("prompt")
        if not isinstance(text, str) or not text.strip():
            continue
        if node.get("_meta", {}).get("title", "").startswith("POSITIVE"):
            return text
        frei = frei or text
    return frei


def index_key(pfad):
    """Pfad als Schlüssel der Bildgalerie: images/<Pfad unterhalb der Bildwurzel>."""
    p, wurzel = os.path.normpath(os.path.abspath(pfad)), os.path.normpath(IMAGES_ROOT)
    if not os.path.normcase(p).startswith(os.path.normcase(wurzel + os.sep)):
        return None
    return "images/" + os.path.relpath(p, wurzel).replace(os.sep, "/")


def add_text_chunks(png_path, werte):
    """iTXt-Chunks vor IEND einfügen, ohne die vorhandenen anzurühren (prompt, workflow).

    Die Bildgalerie liest daraus die Herkunft. iTXt statt tEXt, weil der Wert UTF-8 sein darf,
    und mit Pillow geht es nicht: dieses Skript kommt bewusst mit der Standardbibliothek aus.
    """
    import struct
    import zlib

    with open(png_path, "rb") as fh:
        roh = fh.read()
    if roh[:8] != b"\x89PNG\r\n\x1a\n":
        return False
    ende = roh.rfind(b"\x00\x00\x00\x00IEND")
    if ende < 0:
        return False
    neu = b""
    for schluessel, wert in werte.items():
        if wert is None:
            continue
        körper = schluessel.encode("ascii") + b"\x00\x00\x00\x00\x00" + str(wert).encode("utf-8")
        neu += struct.pack(">I", len(körper)) + b"iTXt" + körper + struct.pack(">I", zlib.crc32(b"iTXt" + körper))
    if not neu:
        return False
    # Das Dateidatum ist in der Bildgalerie das Bilddatum. Neuschreiben setzt es auf jetzt,
    # deshalb den alten Stand sichern und zurückgeben, sonst rutscht ein altes Bild nach vorn.
    stat = os.stat(png_path)
    with open(png_path, "wb") as fh:
        fh.write(roh[:ende] + neu + roh[ende:])
    os.utime(png_path, (stat.st_atime, stat.st_mtime))
    return True


def stamp_source(ergebnis, quelle, workflow_name):
    """Herkunft eines Laufs mit Eingangsbild festhalten (Upscale, Edit, Freistellen).

    Ohne das steht ein Detailpass in der Galerie als eigenständiges Bild des REFINER-Modells,
    also etwa Z-Image, obwohl die Basis von WAI oder CyberRealistic stammt. Mit den Chunks erbt
    das Ergebnis die Vorlage und bleibt bei ihr in der Vergleichsgruppe.
    """
    key = index_key(quelle)
    if not key or not os.path.exists(ergebnis):
        return
    try:
        graph = embedded_workflow(quelle)
    except SystemExit:
        graph = None
    art = ("detailpass" if "upscale" in workflow_name else
           "freigestellt" if "matte" in workflow_name or "cutout" in workflow_name else
           "bearbeitet")
    add_text_chunks(ergebnis, {"gallery_src_key": key,
                               "gallery_src_model": graph_model(graph),
                               "gallery_src_prompt": graph_prompt(graph),
                               "gallery_src_method": art})


GROUPS_FILE = r"D:\Repos\comfy-gallery\data\groups.json"
GALLERY_URL = os.environ.get("GALLERY_URL", "http://127.0.0.1:8189")


def join_group(ergebnis, gruppe, vorlage=None, stamp=True):
    """Ergebnis in eine Gruppe der Bildgalerie eintragen, damit alle Läufe eines Motivs eine Kachel bilden.

    Die Galerie fasst von allein nur Läufe desselben Graphen, Vergleiche desselben Prompts über
    mindestens zwei Modelle und Varianten derselben Vorlage zusammen. Mehrere Anläufe auf einem
    Modell, geänderte Prompts oder ein Nachbau neben seiner Vorlage brauchen diese Klammer.

    Läuft die Galerie, geht der Eintrag über ihre Route /api/groups: sonst schrieben der Server und
    dieses Skript ohne gemeinsame Sperre in dieselbe Datei, und wer zuletzt schreibt, gewinnt. Nur
    ohne Galerie wird die Datei direkt geschrieben, mit derselben Regel: vereinigen, nie ersetzen.
    """
    key = index_key(ergebnis)
    ref = index_key(vorlage) if vorlage else None
    if not key:
        return
    if ref and stamp:  # Vorlage in der Lightbox, bei Läufen mit --image hat stamp_source das schon gesetzt
        add_text_chunks(ergebnis, {"gallery_src_key": ref, "gallery_src_method": "Nachbau"})
    # Ohne note: eine in der Galerie geänderte Notiz bleibt stehen, die Galerie zeigt sonst den Gruppennamen
    body = {"id": gruppe, "members": [k for k in (ref, key) if k], "rep": ref}
    try:
        req = urllib.request.Request(f"{GALLERY_URL}/api/groups", data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10):
            pass
    except urllib.error.HTTPError as exc:  # Galerie läuft, lehnt aber ab: nicht an ihr vorbei schreiben
        print(f"Galerie hat die Gruppe {gruppe} abgelehnt: {exc.code} {exc.read().decode('utf-8', 'replace')[:200]}",
              file=sys.stderr)
    except (urllib.error.URLError, OSError):
        try:
            with open(GROUPS_FILE, encoding="utf-8") as fh:
                daten = json.load(fh)
        except OSError:  # noch keine Datei
            daten = {}
        except ValueError:  # beschädigt: nicht mit dem leeren Stand überschreiben, sonst wären alle Gruppen weg
            print(f"{GROUPS_FILE} ist beschädigt, Gruppe {gruppe} wurde nicht eingetragen ({', '.join(body['members'])}). "
                  "Datei reparieren oder aus einer Sicherung zurückholen, dann mit laufender Galerie erneut eintragen.",
                  file=sys.stderr)
            return
        # Dieselbe Vereinigungsregel wie groups() in comfy-gallery/gallery_groups.py, sonst stünde ein Bild in zwei Gruppen: die Gruppe unter
        # diesem Namen oder Alias, dazu jede, die eines der Bilder schon enthält, wird eine
        neu = set(body["members"])
        beruehrt = [k for k, g in daten.items()
                    if k == gruppe or gruppe in (g.get("aliases") or []) or neu & set(g.get("members") or [])]
        ziel = next((k for k in beruehrt if k == gruppe or gruppe in (daten[k].get("aliases") or [])), gruppe)
        erste = next((daten[k] for k in beruehrt if k != ziel), {})  # Vertreter und Notiz bleiben erhalten
        eintrag = daten.setdefault(ziel, {"members": [], "rep": erste.get("rep") or ref or key,
                                          "note": erste.get("note") or "", "at": 0})
        for k in beruehrt:
            if k != ziel:
                alt = daten.pop(k)
                eintrag["members"] += [m for m in alt.get("members") or [] if m not in eintrag["members"]]
                eintrag["aliases"] = list(dict.fromkeys([*(eintrag.get("aliases") or []), k, *(alt.get("aliases") or [])]))
        for k in body["members"]:
            if k not in eintrag["members"]:
                eintrag["members"].append(k)
        if ref and eintrag.get("rep") not in eintrag["members"]:
            eintrag["rep"] = ref
        eintrag["at"] = int(time.time())
        tmp = GROUPS_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(daten, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, GROUPS_FILE)


# Stimmung der Krea-Kinobanner: Afterlight und Warm geben Tiefe und Kontrast, aber auch Unschärfe am
# Rand. Seit dem Blindtest K4 (Nutzerentscheid 03.10.2026) stehen die Knoten im Workflow auf diesen
# Werten, --no-mood setzt sie für neutrale Motive auf 0, --mood erzwingt sie.
STIMMUNG = {"STIMMUNG_AFTERLIGHT": 0.35, "STIMMUNG_WARM": 0.5}


def execution_error(entry):
    """A readable message if ComfyUI reported a failed run, else None.

    Anything unexpected in the history entry counts as 'keep waiting': a wrong abort would
    kill a healthy run, a missed one only falls back to the timeout that was there before.
    Older ComfyUI builds ship no 'status' at all, which lands in the same branch.
    """
    status = entry.get("status")
    if not isinstance(status, dict) or status.get("status_str") != "error":
        return None
    for message in status.get("messages") or []:
        if not (isinstance(message, (list, tuple)) and len(message) >= 2):
            continue
        name, payload = message[0], message[1]
        if name == "execution_error" and isinstance(payload, dict):
            node = payload.get("node_type") or payload.get("node_id") or "?"
            detail = payload.get("exception_message") or payload.get("exception_type") or ""
            return ("Node %s: %s" % (node, detail)).strip()
    return "status=error ohne Detailmeldung"


def with_trigger(prompt, trigger):
    """Put the template's trigger word (_meta.trigger at POSITIVE_PROMPT, e.g. purelens in
    krea2_produkt) in front of the prompt, never twice: compared without case and whitespace.
    The gallery cuts it off again before prompt and prompt_hash, so a motif still compares
    across models."""
    if not trigger or not prompt:
        return prompt
    plain = lambda s: "".join(s.split()).lower()
    return prompt if plain(prompt).startswith(plain(trigger)) else f"{trigger}, {prompt}"


def inject(workflow, args):
    """Set parameters on nodes, matched by their _meta.title marker."""
    if (getattr(args, "mood", False) or getattr(args, "no_mood", False)) and not any(
            n.get("_meta", {}).get("title") in STIMMUNG for n in workflow.values()):
        sys.exit("--mood/--no-mood: der Workflow hat keine Knoten STIMMUNG_AFTERLIGHT und STIMMUNG_WARM")
    for node in workflow.values():
        title = node.get("_meta", {}).get("title", "")
        inp = node.get("inputs", {})
        if title == "POSITIVE_PROMPT":
            # Qwen-Edit-Nodes heissen das Feld "prompt", CLIPTextEncode "text".
            inp["prompt" if "prompt" in inp else "text"] = with_trigger(args.prompt, node.get("_meta", {}).get("trigger"))
        elif title == "NEGATIVE_PROMPT":
            inp["prompt" if "prompt" in inp else "text"] = args.negative
        elif title == "INPUT_IMAGE" and args.uploaded_image:
            inp["image"] = args.uploaded_image
        elif title == "LATENT":
            inp["width"] = args.width
            inp["height"] = args.height
        elif title == "SAMPLER":
            # KSamplerAdvanced (Wan-MoE) nennt das Feld noise_seed.
            inp["noise_seed" if "noise_seed" in inp else "seed"] = args.seed
            if args.steps is not None and "steps" in inp:
                inp["steps"] = args.steps
        elif title == "CHECKPOINT" and args.checkpoint:
            if "ckpt_name" in inp:
                inp["ckpt_name"] = args.checkpoint
            if "unet_name" in inp:
                inp["unet_name"] = args.checkpoint
        elif title == "DETAIL_LORA":
            # Detail-Slider: 0.0 = aus, positiv = mehr Detail, negativ = weniger.
            # Ohne Schalter gewinnt die Voreinstellung des Workflows: in 09 steht sie
            # bewusst auf 1.0, ein festes Überschreiben haette den Look still gekippt.
            if args.detail_strength is not None:
                inp["strength_model"] = args.detail_strength
            if args.detail_lora:
                inp["lora_name"] = args.detail_lora
        elif title == "MATTE" and getattr(args, "matte_detail", False):
            # Kantenverfeinerung der BiRefNet-Node. Sie gehoert an den Rand des Motivs,
            # nicht an den Weg: viele kleine Strukturen (Haar, Fell, Flaum) gewinnen mit
            # GuidedFilter, klare Linien verlieren, weil er die Kante zu einem Glimmen
            # aufweicht (Abnahme 22.09.2026, acht Urteile, siehe learnings.md).
            inp["process_detail"] = True
            inp["detail_method"] = "GuidedFilter"
            inp["detail_erode"] = 4
            inp["detail_dilate"] = 2
        elif title in STIMMUNG and getattr(args, "no_mood", False):
            inp["strength_model"] = 0.0
        elif title in STIMMUNG and getattr(args, "mood", False):
            inp["strength_model"] = STIMMUNG[title]
        elif title == "LORA" and args.lora:
            inp["lora_name"] = args.lora
            inp["strength_model"] = args.lora_strength
            # LoraLoaderModelOnly (Z-Image, Qwen) kennt keinen CLIP-Strang.
            if "strength_clip" in inp:
                inp["strength_clip"] = args.lora_strength
    return workflow


def main():
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "WARTUNG")):
        raise SystemExit("bs-media-image ist in Wartung: die Bildablage zieht um. Erst weiterarbeiten, wenn die "
                         "Datei WARTUNG in bs-media-image fehlt.")
    parser = argparse.ArgumentParser(description="ComfyUI image generation")
    parser.add_argument("--workflow", default=None, help="API workflow json template")
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--negative", default="")
    parser.add_argument(
        "--out",
        default=None,
        help="optional: hardlink (inside the image library) or copy of the result; "
        "without it the path in the library is printed",
    )
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument(
        "--image",
        default=None,
        help="Eingangsbild für Edit-Workflows (wird nach ComfyUI/input hochgeladen "
        "und in den Knoten mit dem Titel INPUT_IMAGE gesetzt).",
    )
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--lora", default=None)
    parser.add_argument("--lora-strength", type=float, default=0.8, dest="lora_strength")
    parser.add_argument(
        "--detail-strength",
        type=float,
        default=None,
        dest="detail_strength",
        help="Stärke des DETAIL_LORA-Knotens. Ohne Angabe bleibt die Voreinstellung des "
        "Workflows stehen, sinnvoll -2.0 bis 2.0.",
    )
    parser.add_argument(
        "--detail-lora",
        default=None,
        dest="detail_lora",
        help="Andere Datei für den DETAIL_LORA-Knoten.",
    )
    parser.add_argument(
        "--matte-detail",
        action="store_true",
        dest="matte_detail",
        help="Kantenverfeinerung beim Freistellen einschalten (GuidedFilter 4/2). Für Motive "
        "mit vielen kleinen Strukturen: Haar, Fell, Flaum. Bei klaren Linien und harten "
        "Kanten weglassen, dort weicht sie die Kante auf.",
    )
    parser.add_argument(
        "--mood",
        action="store_true",
        help="Stimmung erzwingen: STIMMUNG_AFTERLIGHT auf 0.35 und STIMMUNG_WARM auf 0.5. In "
        "krea2_kinobanner seit 03.10.2026 ohnehin Standard.",
    )
    parser.add_argument(
        "--no-mood",
        action="store_true",
        dest="no_mood",
        help="Stimmung ausschalten (STIMMUNG_AFTERLIGHT und STIMMUNG_WARM auf 0) bei Produkt, Architektur, "
        "klarem Tageslicht und überall, wo Ränder scharf bleiben sollen.",
    )
    parser.add_argument(
        "--url", default=os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188")
    )
    parser.add_argument("--timeout", type=int, default=900, help="max wait seconds")
    parser.add_argument(
        "--group",
        default=None,
        help="Ergebnis in diese Gruppe der Bildgalerie eintragen (data/groups.json). Alle Läufe "
        "eines Motivs bekommen denselben Namen, dann stehen sie in der Galerie als eine Kachel.",
    )
    parser.add_argument(
        "--group-ref",
        default=None,
        dest="group_ref",
        help="Vorlage der Gruppe (Pfad unter der Bildwurzel, etwa das Civitai-Original). Wird "
        "Vertreter der Gruppe und steht im Ergebnis als Vorlage (gallery_src_key).",
    )
    parser.add_argument(
        "--reproduce",
        default=None,
        help="path to a PNG; re-runs the exact workflow embedded in its metadata "
        "(native, no sidecar).",
    )
    args = parser.parse_args()
    reject_out_dir(args.out)

    try:
        api(args.url, "/system_stats", timeout=10)
    except Exception as exc:  # noqa: BLE001 - want a friendly message for any failure
        sys.exit(
            f"ComfyUI nicht erreichbar unter {args.url}. "
            f"In Stability Matrix das ComfyUI-Package starten und Port pruefen. ({exc})"
        )

    if args.reproduce:
        # The source of truth is the image itself: every ComfyUI PNG embeds its
        # full API graph (seed and all) in the 'prompt' tEXt chunk. Re-submit it.
        workflow = embedded_workflow(args.reproduce)
    else:
        if not args.workflow or not args.prompt:
            sys.exit("Fehlt: --workflow und --prompt (oder --reproduce <png>).")
        if args.seed is None:
            args.seed = int.from_bytes(os.urandom(4), "big")
        args.uploaded_image = upload_image(args.url, args.image) if args.image else None
        with open(args.workflow, "r", encoding="utf-8") as fh:
            workflow = json.load(fh)
        workflow = inject(workflow, args)

    client_id = str(uuid.uuid4())
    workflow = expand_dates(workflow)
    resp = api(args.url, "/prompt", {"prompt": workflow, "client_id": client_id, "extra_data": ablage.EXTRA})
    prompt_id = resp.get("prompt_id")
    if not prompt_id:
        sys.exit(f"Keine prompt_id erhalten: {resp}")
    print(f"queued prompt_id={prompt_id} seed={args.seed}", file=sys.stderr)

    image = None
    # Wall clock, not a poll count. The old loop counted 1.5s sleeps and left the HTTP call
    # itself unbounded (api() defaults to 600s), so a single hanging /history poll stretched the
    # run far past --timeout. Each poll now gets the remaining budget as its own socket timeout.
    deadline = time.monotonic() + args.timeout
    last_poll_error = None
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(1.5, remaining))
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            history = api(args.url, f"/history/{prompt_id}", timeout=min(30.0, remaining))
        except (OSError, ValueError, http.client.HTTPException) as exc:
            # A single failed poll must not kill a healthy run; the wall clock above still
            # ends the loop on time. All three classes describe the same restart, none of them
            # covers the other two: OSError is the connection, ValueError the body json.loads
            # in api() chokes on (an empty answer or an HTML page from a proxy), and
            # HTTPException the wire format itself, which http.client raises while api() reads
            # the response (IncompleteRead on a body cut off mid transfer, BadStatusLine on a
            # broken status line).
            # The error is remembered because it survives its poll: if the run ends in the
            # timeout below, the last one is the only trace of why nothing came back.
            last_poll_error = exc
            print(f"Poll fehlgeschlagen, weiter: {exc}", file=sys.stderr)
            continue
        # This poll came through, so the remembered error is over: it says nothing about a run
        # that polls fine afterwards and only ends on its own budget, and a timeout blaming a
        # server that has been healthy since sends the reader after the wrong thing.
        last_poll_error = None
        entry = history.get(prompt_id)
        if not entry:
            continue
        # Mehrstufige Workflows (erst Basis, dann verfeinert) haben mehrere
        # SaveImage-Knoten. Gewollt ist die letzte Stufe, erkennbar am Titel
        # SAVE_DETAIL. Fehlt der, gilt wie bisher die erste Ausgabe.
        outputs = entry.get("outputs", {})
        vorn = [n for n in outputs
                if workflow.get(n, {}).get("_meta", {}).get("title", "").startswith("SAVE_DETAIL")]
        for nid in vorn + [n for n in outputs if n not in vorn]:
            node_output = outputs[nid]
            if node_output.get("images"):
                image = node_output["images"][0]
                break
            if node_output.get("videos"):
                image = node_output["videos"][0]
                break
        if image:
            break
        # A failed prompt (missing checkpoint, OOM, node error) lands in the history right
        # away and never grows images. Without this check the loop sat out the full timeout
        # and then reported a timeout instead of the error ComfyUI already knew about.
        failure = execution_error(entry)
        if failure:
            sys.exit(f"ComfyUI-Fehler bei prompt_id={prompt_id}: {failure}")
    if not image:
        reason = f" Letzter Poll-Fehler: {last_poll_error}." if last_poll_error else ""
        sys.exit(f"Timeout nach {args.timeout}s: kein Bild im History-Output.{reason}")

    final = deliver(args.url, image, args.out)
    # Läufe mit Eingangsbild erben dessen Herkunft, sonst zählt die Galerie den Refiner als Erzeuger
    if args.image:
        stamp_source(final, args.image, os.path.basename(args.workflow or ""))
    if args.group:
        join_group(final, args.group, args.group_ref, stamp=not args.image)
    if args.seed is not None:
        print(f"seed={args.seed}", file=sys.stderr)
    print(final)  # stdout = final path for the caller


if __name__ == "__main__":
    main()
