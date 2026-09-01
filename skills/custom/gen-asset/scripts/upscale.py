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
    os.makedirs(COMFY_INPUT, exist_ok=True)
    fname = "upscale_src_" + os.path.basename(a.image)
    shutil.copy(a.image, os.path.join(COMFY_INPUT, fname))

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

    img = None
    deadline = a.timeout / 1.5
    polls = 0
    while polls < deadline:
        time.sleep(1.5)
        polls += 1
        hist = api(a.url, f"/history/{pid}")
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
            sys.exit(f"ComfyUI-Fehler bei prompt_id={pid}: {failure}")
    if not img:
        sys.exit(f"Timeout nach {a.timeout}s: kein Bild.")
    download(a.url, img, a.out)
    print(a.out)


if __name__ == "__main__":
    main()
