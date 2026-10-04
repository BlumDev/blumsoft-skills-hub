#!/usr/bin/env python3
"""Free an EXISTING image via BiRefNet matting in the local ComfyUI.

Counterpart to comfy_generate.py: no generation, only cutout. Uploads the given
PNG/JPG to ComfyUI, runs workflows/birefnet_matte.api.json and prints where the
RGBA result landed (ComfyUI's output folder is the image library, Text2Img/<workflow>/).
--out is optional: hardlink inside the library, plain copy elsewhere. Stdlib only
(urllib), so any Python runs it.

Usage (PowerShell):
  python comfy_matte.py --image raw.png
On success the final image path is printed to stdout.
"""
import argparse
import hashlib
import json
import mimetypes
import os
import re
import shutil
import struct
import sys
import time
import urllib.parse
import urllib.request
import uuid
import zlib

import ablage  # Ablage nach Workflow und Quelle, liegt neben diesem Skript

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WORKFLOW = os.path.join(HERE, "..", "workflows", "birefnet_matte.api.json")

# ComfyUI's output folder is a junction onto the Stability Matrix image library.
COMFY_OUTPUT = r"D:\Apps\Stability Matrix\Data\Images\Text2Img"
IMAGES_ROOT = r"D:\Apps\Stability Matrix\Data\Images"

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))


def reject_out_dir(out):
    """gen-asset/out lies on another drive, so a --out there can only be a copy: exactly
    the duplicate this skill no longer makes. Derived files (comparison sheets) may go there."""
    if out and os.path.normcase(os.path.abspath(out)).startswith(os.path.normcase(OUT_DIR + os.sep)):
        sys.exit("--out unter gen-asset/out legt eine Zweitkopie an. Weglassen und den ausgegebenen "
                 "Bibliothekspfad verwenden, nach out/ gehören nur abgeleitete Dateien wie Vergleichsblätter.")


def png_text(path):
    """tEXt- und iTXt-Chunks eines PNG als {Schlüssel: Text}, ohne die Bilddaten zu
    dekodieren. Gleiches Verfahren wie in der Bildgalerie, damit beide dasselbe lesen."""
    out = {}
    try:
        with open(path, "rb") as fh:
            if fh.read(8) != b"\x89PNG\r\n\x1a\n":
                return out
            while True:
                head = fh.read(8)
                if len(head) < 8:
                    break
                length, ctype = struct.unpack(">I4s", head)
                data = fh.read(length)
                fh.read(4)  # CRC
                if ctype == b"tEXt":
                    key, _, value = data.partition(b"\x00")
                elif ctype == b"iTXt":
                    key, _, rest = data.partition(b"\x00")
                    flag, method, rest = rest[0:1], rest[1:2], rest[2:]
                    _lang, _, rest = rest.partition(b"\x00")
                    _translated, _, value = rest.partition(b"\x00")
                    if flag == b"\x01" and method == b"\x00":
                        try:
                            value = zlib.decompress(value)
                        except zlib.error:
                            value = b""
                elif ctype == b"IEND":
                    break
                else:
                    continue
                try:
                    out[key.decode("latin-1")] = value.decode("utf-8")
                except UnicodeDecodeError:
                    out[key.decode("latin-1")] = value.decode("latin-1")
    except OSError:
        pass
    return out


def add_png_text(path, pairs):
    """Setzt iTXt-Chunks vor IEND. Arbeitet auf dem Chunk-Strom statt über eine
    Bildbibliothek: die Pixel werden nicht neu komprimiert und die Chunks, die ComfyUI
    selbst geschrieben hat (prompt, workflow), bleiben unverändert stehen. Chunks mit
    denselben Schlüsseln werden vorher entfernt, egal in welcher Art sie dort stehen,
    ein zweiter Lauf verdoppelt also nichts.

    iTXt und nicht tEXt, weil ein Wert UTF-8 sein darf: ein tEXt-Chunk ist laut
    PNG-Spezifikation Latin-1, UTF-8-Bytes darin lesen fremde Werkzeuge als Buchstabensalat.
    Die Bildgalerie versucht zwar UTF-8 zuerst, das ist aber ihre Kulanz und keine Zusage.
    Gleiche Art wie in comfy_generate.py, damit beide Skripte dasselbe schreiben."""
    pairs = [(k, v) for k, v in pairs if v]
    if not pairs:
        return False
    with open(path, "rb") as fh:
        blob = fh.read()
    if not blob.startswith(b"\x89PNG\r\n\x1a\n"):
        return False
    ersetzt = {k.encode("ascii") for k, _ in pairs}
    behalten, pos = [blob[:8]], 8
    while pos + 8 <= len(blob):
        length, ctype = struct.unpack(">I4s", blob[pos:pos + 8])
        ende = pos + 12 + length
        if ctype == b"IEND":
            break
        data = blob[pos + 8:pos + 8 + length]
        if not (ctype in (b"tEXt", b"iTXt", b"zTXt") and data.partition(b"\x00")[0] in ersetzt):
            behalten.append(blob[pos:ende])
        pos = ende
    for key, value in pairs:
        # Schlüssel, Trenner, Kompression aus, Methode 0, leere Sprache, leerer Zweitname
        data = key.encode("ascii") + b"\x00\x00\x00\x00\x00" + str(value).encode("utf-8")
        behalten.append(struct.pack(">I", len(data)) + b"iTXt" + data
                        + struct.pack(">I", zlib.crc32(b"iTXt" + data) & 0xFFFFFFFF))
    behalten.append(blob[pos:])
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(b"".join(behalten))
    os.replace(tmp, path)
    return True


def prompt_hash(text):
    """Gleiche Normalisierung wie die Bildgalerie, sonst fällt das Bild aus dem
    Vergleichssatz seiner Vorlage."""
    normalized = re.sub(r"\W+", " ", text.lower()).strip()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:12]


def herkunft(src_path, verfahren):
    """Was aus dem Quellbild in das Ergebnis gehört. BiRefNet lädt kein
    Generierungsmodell, ein mattiertes Bild hätte sonst weder Modell noch Prompt:
    genau das ist der Grund, warum die Galerie Freisteller bisher leer anzeigt."""
    info = {"gallery_src_method": verfahren}
    src = os.path.abspath(src_path)
    if os.path.normcase(src).startswith(os.path.normcase(IMAGES_ROOT + os.sep)):
        rel = os.path.relpath(src, IMAGES_ROOT).replace(os.sep, "/")
        info["gallery_src_key"] = f"images/{rel}"
    graph = png_text(src).get("prompt")
    try:
        graph = json.loads(graph) if graph else None
    except ValueError:
        graph = None
    if not isinstance(graph, dict):
        return info
    nodes = [n for n in graph.values() if isinstance(n, dict)]
    for node in nodes:
        for field in ("unet_name", "ckpt_name"):
            name = node.get("inputs", {}).get(field)
            if isinstance(name, str) and name:
                info["gallery_src_model"] = os.path.splitext(os.path.basename(name))[0]
                break
        if "gallery_src_model" in info:
            break
    texts = [n.get("inputs", {}).get(f) for n in nodes
             for f in ("text", "prompt")
             if n.get("_meta", {}).get("title") == "POSITIVE_PROMPT"]
    if not texts:  # fremder Graph ohne die Titel des Skills: längster Textknoten
        texts = [n.get("inputs", {}).get(f) for n in nodes
                 if n.get("class_type", "").startswith("CLIPTextEncode")
                 for f in ("text", "prompt")]
    texts = sorted((t for t in texts if isinstance(t, str) and t.strip()), key=len, reverse=True)
    if texts:
        info["gallery_src_prompt"] = texts[0]
        info["gallery_src_prompt_hash"] = prompt_hash(texts[0])
    return info


def matte_verfahren(workflow):
    """Kurzform der Einstellung, mit der freigestellt wurde. Sie trennt in der Galerie
    zwei Ergebnisse derselben Vorlage voneinander, steht also in der Vergleichsleiste:
    deshalb nur das Unterscheidende, den Modellnamen liest die Galerie selbst aus dem
    Graphen. Wortlaut wie dort, damit beide Stellen dasselbe sagen."""
    for node in workflow.values():
        if node.get("_meta", {}).get("title") != "MATTE":
            continue
        inp = node.get("inputs", {})
        if not inp.get("process_detail"):
            return "Verfeinerung aus"
        erode, dilate = inp.get("detail_erode"), inp.get("detail_dilate")
        method = inp.get("detail_method") or "Verfeinerung"
        return f"{method} {erode}/{dilate}" if erode and dilate else method
    return None


def inject(workflow, server_name, args):
    """Parameter auf die Knoten setzen, erkannt am _meta.title. Eigene Funktion wie in
    comfy_generate.py, damit sich das Ergebnis ohne laufendes ComfyUI prüfen lässt."""
    for node in workflow.values():
        title = node.get("_meta", {}).get("title", "")
        if title == "INPUT_IMAGE":
            node["inputs"]["image"] = server_name
        elif title == "BIREFNET_MODEL" and args.model:
            node["inputs"]["version"] = args.model
        elif title == "MATTE" and args.matte_detail:
            # Kantenverfeinerung gehört an den Rand des Motivs, nicht an den Quellweg:
            # viele kleine Strukturen gewinnen mit GuidedFilter, klare Linien verlieren
            # (Abnahme 22.09.2026, acht Urteile, siehe reference/learnings.md).
            node["inputs"].update({"process_detail": True, "detail_method": "GuidedFilter",
                                   "detail_erode": 4, "detail_dilate": 2})
    return workflow


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


def upload(base, path, timeout=300):
    """POST /upload/image (multipart) and return the server-side filename."""
    name = os.path.basename(path)
    ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
    with open(path, "rb") as fh:
        blob = fh.read()
    boundary = "----comfymatte" + uuid.uuid4().hex
    parts = []
    for key, value in (("overwrite", "true"), ("type", "input")):
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n'
            f"{value}\r\n".encode("utf-8")
        )
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="image"; '
        f'filename="{name}"\r\nContent-Type: {ctype}\r\n\r\n'.encode("utf-8")
    )
    parts.append(blob)
    parts.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)
    req = urllib.request.Request(
        base.rstrip("/") + "/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        info = json.loads(resp.read().decode("utf-8"))
    sub = info.get("subfolder") or ""
    return f"{sub}/{info['name']}" if sub else info["name"]


def download(base, image, out_path):
    query = urllib.parse.urlencode(
        {
            "filename": image["filename"],
            "subfolder": image.get("subfolder", ""),
            "type": image.get("type", "output"),
        }
    )
    with urllib.request.urlopen(
        base.rstrip("/") + "/view?" + query, timeout=600
    ) as resp:
        blob = resp.read()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
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


def main():
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "WARTUNG")):
        raise SystemExit("gen-asset ist in Wartung: die Bildablage zieht um. Erst weiterarbeiten, wenn die "
                         "Datei WARTUNG in gen-asset fehlt.")
    parser = argparse.ArgumentParser(description="BiRefNet cutout of an existing image")
    parser.add_argument("--image", required=True, help="source image on disk")
    parser.add_argument(
        "--out",
        default=None,
        help="optional: hardlink (inside the image library) or copy of the result; "
        "without it the path in the library is printed",
    )
    parser.add_argument("--workflow", default=DEFAULT_WORKFLOW)
    parser.add_argument("--model", default=None, help="BiRefNet version override")
    parser.add_argument(
        "--matte-detail",
        action="store_true",
        dest="matte_detail",
        help="Kantenverfeinerung einschalten (GuidedFilter 4/2). Für Motive mit vielen "
        "kleinen Strukturen: Haar, Fell, Flaum. Bei klaren Linien und harten Kanten "
        "weglassen, dort weicht sie die Kante auf.",
    )
    parser.add_argument(
        "--url", default=os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188")
    )
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    reject_out_dir(args.out)

    try:
        api(args.url, "/system_stats", timeout=10)
    except Exception as exc:  # noqa: BLE001 - friendly message for any failure
        sys.exit(f"ComfyUI nicht erreichbar unter {args.url}: {exc}")

    server_name = upload(args.url, args.image)
    with open(args.workflow, "r", encoding="utf-8") as fh:
        workflow = json.load(fh)
    workflow = expand_dates(inject(workflow, server_name, args))

    resp = api(args.url, "/prompt", {"prompt": workflow, "client_id": str(uuid.uuid4()), "extra_data": ablage.EXTRA})
    prompt_id = resp.get("prompt_id")
    if not prompt_id:
        sys.exit(f"Keine prompt_id erhalten: {resp}")

    image = None
    started = time.time()
    while time.time() - started < args.timeout:
        time.sleep(1.0)
        entry = api(args.url, f"/history/{prompt_id}").get(prompt_id)
        if not entry:
            continue
        for node_output in entry.get("outputs", {}).values():
            if node_output.get("images"):
                image = node_output["images"][0]
                break
        if image:
            break
        if entry.get("status", {}).get("status_str") == "error":
            sys.exit(f"ComfyUI-Fehler: {json.dumps(entry.get('status'))[:800]}")
    if not image:
        sys.exit(f"Timeout nach {args.timeout}s: kein Bild im History-Output.")

    # Herkunft ins Ergebnis schreiben, BEVOR deliver hardlinkt oder kopiert: der Graph
    # dieses Bildes kennt nur LoadImage und BiRefNet, Modell und Prompt stehen allein
    # im Quellbild. Ohne diesen Schritt zeigt die Bildgalerie jeden Freisteller ohne
    # Modell und ohne Prompt an.
    lib = os.path.normpath(os.path.join(COMFY_OUTPUT, image.get("subfolder", ""), image["filename"]))
    if lib.lower().endswith(".png") and os.path.exists(lib):
        add_png_text(lib, herkunft(args.image, matte_verfahren(workflow)).items())

    print(deliver(args.url, image, args.out))


if __name__ == "__main__":
    main()
