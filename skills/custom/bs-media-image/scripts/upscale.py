#!/usr/bin/env python3
"""Upscale an existing image via ComfyUI UltimateSDUpscale (tile re-diffusion).

Copies the input image into ComfyUI's input folder, runs workflows/upscale.api.json
(Z-Image-Turbo as tile refiner + 4x-UltraSharp at low denoise = sharper and more
detail while keeping the original look), polls and prints where
the result landed (ComfyUI's output folder is the image library, Text2Img/upscale/). --out is optional:
hardlink inside the library, plain copy elsewhere. Stdlib only, except for the optional
provenance stamp at the end, which needs Pillow and is skipped when it is missing.

Usage (PowerShell):
  python upscale.py --image in.png --upscale-by 2.0
Lower --denoise (e.g. 0.15) keeps the original more faithfully; higher (0.35) invents
more detail. Default 0.2 is a safe sharpen.
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

COMFY_INPUT = r"D:\Apps\Stability Matrix\Data\Packages\ComfyUI\input"
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


# Hosts whose input folder the local filesystem can be: everything else needs --input-dir.
LOCAL_HOSTS = frozenset(("localhost", "127.0.0.1", "::1", ""))
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WF = os.path.join(HERE, "..", "workflows", "upscale.api.json")


def expand_dates(workflow):
    """Bringt jeden SaveImage-Prefix in die Ablage nach Workflow (ablage.py): agent/%date:yyyy-MM-dd%/foto wird
    foto/foto, Testreihen landen unter _tests/<reihe>/. Ein Datum im Ordner gibt es seit dem Umzug der Bildablage
    nicht mehr, %date% käme über die HTTP-API sonst wörtlich an (WinError 267)."""
    return ablage.normalisiere(workflow)


def api(base, path, payload=None, timeout=900):
    url = base.rstrip("/") + path
    if payload is not None:
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def download(base, image, out_path):
    q = urllib.parse.urlencode({
        "filename": image["filename"],
        "subfolder": image.get("subfolder", ""),
        "type": image.get("type", "output"),
    })
    with urllib.request.urlopen(base.rstrip("/") + "/view?" + q, timeout=900) as r:
        blob = r.read()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(blob)


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


def stamp_source(ergebnis, quelle):
    """Schreibt die Herkunfts-Chunks der Galerie, damit ein Detailpass neben seinem Original steht.

    Ohne sie hängt das nachgeschärfte Bild unverknüpft in der Galerie und trägt den Refiner
    als Modell-Badge, obwohl das Motiv aus einem anderen Modell stammt.

    Geschrieben werden nur `gallery_src_key` und `gallery_src_method`. Modell und Prompt holt
    sich die Galerie in `link_sources()` über den Schlüssel beim Original ab (Ketten laufen bis
    zur Wurzel), ihre Label-Zuordnung hier nachzubauen ergäbe nur eine zweite Quelle, die
    auseinanderläuft. Vorhandene Chunks (prompt, workflow) werden unverändert übernommen.

    Braucht Pillow. Fehlt es, gelingt der Upscale trotzdem und nur die Verknüpfung fehlt.
    """
    if not (os.path.exists(ergebnis) and os.path.exists(quelle)):
        return
    quelle = os.path.abspath(quelle)
    if not os.path.normcase(quelle).startswith(os.path.normcase(IMAGES_ROOT + os.sep)):
        return  # außerhalb der Bibliothek kennt die Galerie keinen Schlüssel
    try:
        from PIL import Image
        from PIL.PngImagePlugin import PngInfo
    except ImportError:
        print("Pillow fehlt, Herkunft nicht gestempelt.", file=sys.stderr)
        return

    key = "images/" + os.path.relpath(quelle, IMAGES_ROOT).replace(os.sep, "/")
    with Image.open(ergebnis) as im:
        im.load()  # erst vollständig lesen, gleich wird dieselbe Datei überschrieben
        vorhanden, bild = dict(im.text), im.copy()
    info = PngInfo()
    for name, wert in vorhanden.items():
        info.add_text(name, wert)
    info.add_text("gallery_src_key", key)
    info.add_text("gallery_src_method", "detailpass")
    # In dieselbe Datei speichern, damit ein Hardlink aus deliver() weiter auf diesen Inhalt zeigt.
    bild.save(ergebnis, pnginfo=info)
    print(f"Herkunft gestempelt: {key}", file=sys.stderr)


def input_filename(image_path):
    """Name for the copy of the input image in ComfyUI's shared input folder.

    The random part keeps runs apart. With the plain basename, upscaling out\\hero.png and
    projekt\\hero.png (or two jobs in parallel) wrote the same file, so the second run
    overwrote the first one's input and a job still running read foreign pixels and saved
    them as its upscale result.
    """
    return "upscale_src_%s_%s" % (uuid.uuid4().hex[:8], os.path.basename(image_path))


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


def main():
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "WARTUNG")):
        raise SystemExit("bs-media-image ist in Wartung: die Bildablage zieht um. Erst weiterarbeiten, wenn die "
                         "Datei WARTUNG in bs-media-image fehlt.")
    p = argparse.ArgumentParser(description="ComfyUI UltimateSDUpscale")
    p.add_argument("--image", required=True, help="input image to upscale")
    p.add_argument(
        "--out",
        default=None,
        help="optional: hardlink (inside the image library) or copy of the result; "
        "without it the path in the library is printed",
    )
    p.add_argument("--workflow", default=DEFAULT_WF)
    p.add_argument("--upscale-by", type=float, default=2.0, dest="upscale_by")
    p.add_argument("--denoise", type=float, default=0.2)
    p.add_argument("--prompt", default=None, help="optional tile guidance prompt")
    p.add_argument("--checkpoint", default=None, help="override tile re-diffusion model (e.g. an anime checkpoint)")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--url", default=os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188"))
    p.add_argument("--input-dir", dest="input_dir", default=os.environ.get("COMFYUI_INPUT"),
                   help="input folder of the ComfyUI behind --url (default: local installation)")
    p.add_argument("--timeout", type=int, default=1200, help="max wait seconds")
    a = p.parse_args()
    reject_out_dir(a.out)

    if a.seed is None:
        a.seed = int.from_bytes(os.urandom(4), "big")

    try:
        api(a.url, "/system_stats", timeout=10)
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"ComfyUI nicht erreichbar unter {a.url} ({exc})")

    if not os.path.exists(a.image):
        sys.exit(f"Eingabebild nicht gefunden: {a.image}")

    # The workflow hands ComfyUI a bare filename, so the copy has to land in the input folder
    # of exactly the instance --url points at. COMFY_INPUT is the local installation; for a
    # remote instance or a tunnel it is certainly the wrong folder, and the old code copied
    # there anyway: the server never found the file and the run only ever hit its timeout.
    input_dir = a.input_dir or COMFY_INPUT
    host = (urllib.parse.urlparse(a.url).hostname or "").lower()
    if not a.input_dir and host not in LOCAL_HOSTS:
        sys.exit(
            f"--url zeigt auf '{host}', der Eingabeordner ist aber der lokale ({COMFY_INPUT}). "
            "Dort läge die Kopie, während der Server sie woanders sucht. "
            "--input-dir (oder COMFYUI_INPUT) auf den Input-Ordner dieser Instanz setzen."
        )

    os.makedirs(input_dir, exist_ok=True)
    fname = input_filename(a.image)
    staged_input = os.path.join(input_dir, fname)
    shutil.copy(a.image, staged_input)
    keep_staged = False
    try:
        with open(a.workflow, "r", encoding="utf-8") as f:
            wf = json.load(f)
        for node in wf.values():
            title = node.get("_meta", {}).get("title", "")
            inp = node.get("inputs", {})
            if title == "INPUT_IMAGE":
                inp["image"] = fname
            elif title == "UPSCALE":
                inp["upscale_by"] = a.upscale_by
                inp["denoise"] = a.denoise
                inp["seed"] = a.seed
            elif title == "POSITIVE_PROMPT" and a.prompt:
                # Seit dem 22.09.2026 ist Krea 2 der Refiner, score-Tags braucht es nicht mehr.
                inp["text"] = a.prompt
            elif title == "CHECKPOINT" and a.checkpoint:
                # Krea 2 kommt über UNETLoader, SDXL-Checkpoints über CheckpointLoaderSimple.
                if "unet_name" in inp:
                    inp["unet_name"] = a.checkpoint
                if "ckpt_name" in inp:
                    inp["ckpt_name"] = a.checkpoint

        cid = str(uuid.uuid4())
        wf = expand_dates(wf)
        # The copy belongs to the job from the moment the request leaves, not from the moment
        # the answer arrives: ComfyUI queues the prompt while the POST is still open. From here
        # the copy is the job's, not this process's, because ComfyUI opens the input only when
        # the job starts running, so deleting it while the job waits in the queue breaks it in
        # LoadImage and throws the GPU work away. The timeout is not the only exit that gets
        # there: Strg+C and any unexpected exception run through the finally as well. Only an
        # outcome that proves the job never made it into the queue, or is over, releases the
        # copy again. A connection that dies mid POST is not such a proof and keeps it: one
        # file too many in the shared input folder is cheaper than a queued job without input.
        keep_staged = True
        try:
            resp = api(a.url, "/prompt", {"prompt": wf, "client_id": cid, "extra_data": ablage.EXTRA})
        except urllib.error.HTTPError:
            keep_staged = False  # the server answered and refused, so it queued nothing
            raise
        pid = resp.get("prompt_id")
        if not pid:
            keep_staged = False  # an answer without an id is a refusal, not a queued job
            sys.exit(f"Keine prompt_id erhalten: {resp}")
        print(f"queued {pid} seed={a.seed} upscale_by={a.upscale_by} denoise={a.denoise}", file=sys.stderr)

        img = None
        # Wall clock, not a poll count. The old loop counted 1.5s sleeps and left the HTTP call
        # itself unbounded (api() defaults to 900s), so a single hanging /history poll stretched
        # the run far past --timeout. Each poll now gets the remaining budget as its socket timeout.
        deadline = time.monotonic() + a.timeout
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
                hist = api(a.url, f"/history/{pid}", timeout=min(30.0, remaining))
            except (OSError, ValueError, http.client.HTTPException) as exc:
                # A single failed poll must not kill a healthy run; the wall clock above still
                # ends the loop on time. All three classes describe the same restart, none of
                # them covers the other two: OSError is the connection, ValueError the body
                # json.loads in api() chokes on (an empty answer or an HTML page from a proxy),
                # and HTTPException the wire format itself, which http.client raises while
                # api() reads the response (IncompleteRead on a body cut off mid transfer,
                # BadStatusLine on a broken status line).
                # The error is remembered because it survives its poll: if the run ends in the
                # timeout below, the last one is the only trace of why nothing came back.
                last_poll_error = exc
                print(f"Poll fehlgeschlagen, weiter: {exc}", file=sys.stderr)
                continue
            # This poll came through, so the remembered error is over: it says nothing about a
            # run that polls fine afterwards and only ends on its own budget, and a timeout
            # blaming a healthy server costs the queued job if the reader restarts ComfyUI.
            last_poll_error = None
            entry = hist.get(pid)
            if not entry:
                continue
            for no in entry.get("outputs", {}).values():
                if no.get("images"):
                    img = no["images"][0]
                    break
            if img:
                break
            # A failed prompt lands in the history right away and never grows images. Without
            # this check the loop sat out the full timeout and reported a timeout instead of
            # the error ComfyUI already knew about.
            failure = execution_error(entry)
            if failure:
                keep_staged = False  # ComfyUI is done with this job and will not read the input
                sys.exit(f"ComfyUI-Fehler bei prompt_id={pid}: {failure}")
        if not img:
            # The timeout says nothing about the job: it may still be queued, and ComfyUI has
            # not opened the input yet. So the copy stays (keep_staged is still set from the
            # queueing above), named in the message, and the caller removes it once the job is
            # really over.
            reason = f" Letzter Poll-Fehler: {last_poll_error}." if last_poll_error else ""
            sys.exit(
                f"Timeout nach {a.timeout}s: kein Bild.{reason} Job {pid} kann noch in der Queue "
                f"stehen, die Eingabekopie bleibt deshalb liegen: {staged_input}"
            )
        # The result exists, so ComfyUI has read the input; the copy is free even if stamping or
        # delivery below fails.
        keep_staged = False
        # Erst stempeln, dann ausliefern: so trägt auch eine Kopie unter --out die Herkunft.
        stamp_source(os.path.normpath(os.path.join(COMFY_OUTPUT, img.get("subfolder", ""), img["filename"])), a.image)
        print(deliver(a.url, img, a.out))
    finally:
        # COMFY_INPUT is shared with every other run and with ComfyUI itself, so the copy has to
        # go once this run is really over: success and reported error alike. The unique name of
        # each run turns a leftover into a pile, one file per upscale.
        # Best effort on purpose: ComfyUI may still hold the file open, which blocks the delete
        # on Windows, and a failed cleanup must not turn a finished upscale into an error.
        if not keep_staged:
            try:
                os.remove(staged_input)
            except OSError:
                pass


if __name__ == "__main__":
    main()
