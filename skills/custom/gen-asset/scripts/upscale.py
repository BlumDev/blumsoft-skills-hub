#!/usr/bin/env python3
"""Upscale an existing image via ComfyUI UltimateSDUpscale (tile re-diffusion).

Copies the input image into ComfyUI's input folder, runs workflows/upscale.api.json
(SDXL Juggernaut tiles + 4x-UltraSharp at low denoise = sharper and more detail while
keeping the original look), polls and downloads the result. Stdlib only.

Usage (PowerShell):
  python upscale.py --image in.png --out in_2x.png --upscale-by 2.0
Lower --denoise (e.g. 0.15) keeps the original more faithfully; higher (0.35) invents
more detail. Default 0.2 is a safe sharpen.
"""
import argparse
import json
import os
import shutil
import sys
import time
import urllib.parse
import urllib.request
import uuid

COMFY_INPUT = r"D:\Apps\Stability Matrix\Data\Packages\ComfyUI\input"
# Hosts whose input folder the local filesystem can be: everything else needs --input-dir.
LOCAL_HOSTS = frozenset(("localhost", "127.0.0.1", "::1", ""))
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WF = os.path.join(HERE, "..", "workflows", "upscale.api.json")


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
    p = argparse.ArgumentParser(description="ComfyUI UltimateSDUpscale")
    p.add_argument("--image", required=True, help="input image to upscale")
    p.add_argument("--out", required=True, help="output .png path")
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
                inp["text"] = a.prompt
            elif title == "CHECKPOINT" and a.checkpoint:
                inp["ckpt_name"] = a.checkpoint

        cid = str(uuid.uuid4())
        resp = api(a.url, "/prompt", {"prompt": wf, "client_id": cid})
        pid = resp.get("prompt_id")
        if not pid:
            sys.exit(f"Keine prompt_id erhalten: {resp}")
        print(f"queued {pid} seed={a.seed} upscale_by={a.upscale_by} denoise={a.denoise}", file=sys.stderr)
        # From here the copy belongs to the job, not to this process: ComfyUI opens the input
        # only when the job starts running, so deleting it while the job waits in the queue
        # breaks it in LoadImage and throws the GPU work away. The timeout was not the only
        # exit that got there: Strg+C and any unexpected exception run through the finally as
        # well. Every one of them keeps the file now, and only an outcome that proves the job
        # is over releases it again.
        keep_staged = True

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
            except (OSError, ValueError) as exc:  # connection, or a body that is not JSON
                # A single failed poll must not kill a healthy run; the wall clock above still
                # ends the loop on time. ValueError belongs in here as much as OSError does:
                # a restarting ComfyUI (or a proxy in front of it) answers with an empty body
                # or an HTML page, and json.loads in api() raises on that, not urllib.
                # The error is remembered because it survives its poll: if the run ends in the
                # timeout below, the last one is the only trace of why nothing came back.
                last_poll_error = exc
                print(f"Poll fehlgeschlagen, weiter: {exc}", file=sys.stderr)
                continue
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
        # The result exists, so ComfyUI has read the input; the copy is free even if the
        # download below fails.
        keep_staged = False
        download(a.url, img, a.out)
        print(a.out)
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
