#!/usr/bin/env python3
"""Curated recall index for proven gen-asset images.

This is intentionally NOT a reproduction store: every ComfyUI PNG already embeds
its full workflow/prompt natively (drag it back into ComfyUI to reload the graph,
or read it programmatically). The ledger adds only the one thing ComfyUI/Stability
Matrix lack: a curated, rated, vertical-tagged index so a future (head-less) run can
ask "what's my proven winzer hero recipe?" without browsing the whole gallery.

Each entry points at the PNG (the source of truth) plus rating/tags/vertical/note
and a couple of denormalized display fields (prompt, seed) pulled from the PNG.

Usage (PowerShell):
  # Remember a passed image (after Vision-verify PASS):
  python ledger.py add --image out\hero.png --rating 5 --vertical winzer --tags "hero,landscape"
  # Recall proven images before a new task:
  python ledger.py find --vertical winzer --min-rating 4
Reproduce: drag the listed PNG into ComfyUI, or load the matching workflow template.
Stdlib only.
"""
import argparse
import json
import os
import struct

LEDGER = os.path.join(os.path.dirname(__file__), "..", "reference", "ledger.jsonl")


def read_png_text(path):
    """Return ComfyUI's embedded tEXt chunks ({keyword: text}); {} if none/unreadable."""
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
                if ctype == b"tEXt" and b"\x00" in data:
                    key, _, val = data.partition(b"\x00")
                    out[key.decode("latin-1")] = val.decode("latin-1")
                elif ctype == b"IEND":
                    break
    except OSError:
        pass
    return out


def png_meta(path):
    """Best-effort {prompt, seed, model, lora} from the embedded ComfyUI 'prompt' chunk."""
    meta = {"prompt": None, "seed": None, "model": None, "lora": None}
    chunks = read_png_text(path)
    if "prompt" not in chunks:
        return meta
    try:
        graph = json.loads(chunks["prompt"])
    except ValueError:
        return meta
    for node in graph.values():
        ctype = node.get("class_type", "")
        title = node.get("_meta", {}).get("title", "")
        inp = node.get("inputs", {})
        if title == "POSITIVE_PROMPT" and isinstance(inp.get("text"), str):
            meta["prompt"] = inp["text"]
        if title == "SAMPLER" and "seed" in inp:
            meta["seed"] = inp["seed"]
        if ctype in ("CheckpointLoaderSimple", "ImageOnlyCheckpointLoader") and inp.get("ckpt_name"):
            meta["model"] = inp["ckpt_name"]
        elif ctype in ("UNETLoader", "UnetLoaderGGUF") and inp.get("unet_name"):
            meta["model"] = inp["unet_name"]
        if "LoraLoader" in ctype and inp.get("lora_name"):
            meta["lora"] = inp["lora_name"]
    return meta


def cmd_add(args):
    if not os.path.exists(args.image):
        raise SystemExit(f"Bild nicht gefunden: {args.image}")
    meta = png_meta(args.image)
    entry = {
        "image": os.path.abspath(args.image),
        "vertical": args.vertical,
        "tags": sorted({t.strip() for t in (args.tags or "").split(",") if t.strip()}),
        "rating": args.rating,
        "note": args.note,
        "model": args.model or meta["model"],
        "prompt": args.prompt or meta["prompt"],
        "seed": meta["seed"],
        "lora": args.lora or meta["lora"],
    }
    os.makedirs(os.path.dirname(os.path.abspath(LEDGER)), exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"ledger += {entry['image']} (rating {entry['rating']}, vertical {entry['vertical']})")


def cmd_find(args):
    if not os.path.exists(LEDGER):
        print("(Ledger leer - noch keine bewaehrten Bilder.)")
        return
    rows = []
    with open(LEDGER, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if args.vertical:
        rows = [r for r in rows if (r.get("vertical") or "").lower() == args.vertical.lower()]
    if args.tag:
        rows = [r for r in rows if args.tag.lower() in [t.lower() for t in r.get("tags", [])]]
    if args.min_rating is not None:
        rows = [r for r in rows if (r.get("rating") or 0) >= args.min_rating]
    rows.sort(key=lambda r: r.get("rating") or 0, reverse=True)
    if not rows:
        print("(Keine passenden Bilder.)")
        return
    for r in rows[: args.limit]:
        print(
            f"[{r.get('rating', '-')}] {r.get('vertical', '?')} | "
            f"model={r.get('model') or '?'} | lora={r.get('lora') or '-'} | "
            f"tags={','.join(r.get('tags', []))} | seed={r.get('seed')} | {r.get('image')}"
        )
        if r.get("prompt"):
            print(f"      prompt: {r['prompt'][:200]}")
    print("\nRepro: PNG in ComfyUI ziehen (Graph laedt) oder Workflow-Template laden.")


def main():
    parser = argparse.ArgumentParser(description="gen-asset recall index")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="index a passed image")
    p_add.add_argument("--image", required=True, help="path to the generated .png")
    p_add.add_argument("--vertical", default=None, help="e.g. winzer, food, bau, produkt, menschen")
    p_add.add_argument("--tags", default=None, help="comma-separated")
    p_add.add_argument("--rating", type=int, default=None, help="1-5")
    p_add.add_argument("--note", default=None)
    p_add.add_argument("--prompt", default=None, help="override; else read from PNG")
    p_add.add_argument("--model", default=None, help="override; else read from PNG")
    p_add.add_argument("--lora", default=None, help="override; else read from PNG")
    p_add.set_defaults(func=cmd_add)

    p_find = sub.add_parser("find", help="recall proven images")
    p_find.add_argument("--vertical", default=None)
    p_find.add_argument("--tag", default=None)
    p_find.add_argument("--min-rating", type=int, default=None, dest="min_rating")
    p_find.add_argument("--limit", type=int, default=10)
    p_find.set_defaults(func=cmd_find)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
