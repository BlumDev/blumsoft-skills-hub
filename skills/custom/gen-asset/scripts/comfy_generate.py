#!/usr/bin/env python3
"""Generate an image via the local ComfyUI HTTP API.

Loads a ComfyUI API-format workflow template, injects parameters (identified by
each node's _meta.title), submits it, polls /history until done, and downloads
the result. Stdlib only (urllib) so it runs with any Python, no pip install.

The verify step is the caller's job: read the output PNG and judge it, then
re-run with an adjusted prompt/seed if needed.

Usage (PowerShell):
  python comfy_generate.py --workflow sdxl_t2i.api.json --prompt "a red apple" \
    --out out\apple.png --width 1024 --height 1024
On success the final image path is printed to stdout.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


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


def inject(workflow, args):
    """Set parameters on nodes, matched by their _meta.title marker."""
    for node in workflow.values():
        title = node.get("_meta", {}).get("title", "")
        inp = node.get("inputs", {})
        if title == "POSITIVE_PROMPT":
            inp["text"] = args.prompt
        elif title == "NEGATIVE_PROMPT":
            inp["text"] = args.negative
        elif title == "LATENT":
            inp["width"] = args.width
            inp["height"] = args.height
        elif title == "SAMPLER":
            inp["seed"] = args.seed
            if args.steps is not None and "steps" in inp:
                inp["steps"] = args.steps
        elif title == "SAMPLER_HIRES":
            # Second pass of the hires workflows. Without this it kept the seed baked into
            # the template, so --seed only moved the first pass and neither seed iteration
            # nor reproduction reached the finished image. Same seed as the base pass, like
            # a hires fix. --steps stays out: the second pass runs deliberately fewer steps.
            inp["seed"] = args.seed
        elif title == "CHECKPOINT" and args.checkpoint:
            if "ckpt_name" in inp:
                inp["ckpt_name"] = args.checkpoint
            if "unet_name" in inp:
                inp["unet_name"] = args.checkpoint
        elif title == "LORA" and args.lora:
            inp["lora_name"] = args.lora
            inp["strength_model"] = args.lora_strength
            inp["strength_clip"] = args.lora_strength
    return workflow


def main():
    parser = argparse.ArgumentParser(description="ComfyUI image generation")
    parser.add_argument("--workflow", default=None, help="API workflow json template")
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--negative", default="")
    parser.add_argument("--out", required=True, help="output .png path")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--lora", default=None)
    parser.add_argument("--lora-strength", type=float, default=0.8, dest="lora_strength")
    parser.add_argument(
        "--url", default=os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188")
    )
    parser.add_argument("--timeout", type=int, default=900, help="max wait seconds")
    parser.add_argument(
        "--reproduce",
        default=None,
        help="path to a PNG; re-runs the exact workflow embedded in its metadata "
        "(native, no sidecar). --out still required.",
    )
    args = parser.parse_args()

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
        with open(args.workflow, "r", encoding="utf-8") as fh:
            workflow = json.load(fh)
        workflow = inject(workflow, args)

    client_id = str(uuid.uuid4())
    resp = api(args.url, "/prompt", {"prompt": workflow, "client_id": client_id})
    prompt_id = resp.get("prompt_id")
    if not prompt_id:
        sys.exit(f"Keine prompt_id erhalten: {resp}")
    print(f"queued prompt_id={prompt_id} seed={args.seed}", file=sys.stderr)

    image = None
    deadline = args.timeout / 1.5
    polls = 0
    while polls < deadline:
        time.sleep(1.5)
        polls += 1
        history = api(args.url, f"/history/{prompt_id}")
        entry = history.get(prompt_id)
        if not entry:
            continue
        for node_output in entry.get("outputs", {}).values():
            if node_output.get("images"):
                image = node_output["images"][0]
                break
        if image:
            break
    if not image:
        sys.exit(f"Timeout nach {args.timeout}s: kein Bild im History-Output.")

    download(args.url, image, args.out)
    if args.seed is not None:
        print(f"seed={args.seed}", file=sys.stderr)
    print(args.out)  # stdout = final path for the caller


if __name__ == "__main__":
    main()
