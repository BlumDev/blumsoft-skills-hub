"""Macht eine Textur nahtlos kachelbar, ohne Modell. Das Bild wird um die halbe Kante verschoben, dann liegen die alten
Außenkanten als Kreuz in der Mitte. Dort wird das unverschobene Original überblendet, das genau an dieser Stelle
durchgehend ist. Die Überblendung ist varianzerhaltend (Heitz und Neyret 2018): (T - mu) / sqrt(w1^2 + w2^2) + mu.
Workflow 19 (seamless_tile) macht dasselbe linear in ComfyUI und verliert dabei im Übergang rund ein Viertel des
Feinkorns (Aschekrone-Grund am 28.09.2026: 1,40 gegen 1,89 im Rest, hier 1,88).

Nur für Texturen ohne erkennbare Formen. Steine, Fugen oder Muster schienen im Kreuz doppelt durch.
Aufruf mit dem Python von ComfyUI (numpy, Pillow): python seamless_tile.py <eingang.png> <ausgang.png> [--band 160]
"""
import argparse

import numpy as np
from PIL import Image


def ramp(n, half):
    """1 in der Bildmitte, weich (smoothstep) auf 0 im Abstand half."""
    d = np.abs(np.arange(n) - n / 2 + 0.5)
    t = np.clip(1 - d / half, 0, 1)
    return t * t * (3 - 2 * t)


def seamless(img, half=160):
    o = np.asarray(img.convert("RGB")).astype(float)
    h, w, _ = o.shape
    r = np.roll(o, (h // 2, w // 2), axis=(0, 1))
    m = np.maximum(ramp(w, half)[None, :], ramp(h, half)[:, None])[..., None]
    mu = o.mean(axis=(0, 1))
    t = (r * (1 - m) + o * m - mu) / np.sqrt((1 - m) ** 2 + m ** 2) + mu
    return Image.fromarray(np.clip(np.rint(t), 0, 255).astype(np.uint8))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Textur nahtlos kachelbar machen, ohne Modell")
    p.add_argument("source")
    p.add_argument("target")
    p.add_argument("--band", type=int, default=160, help="halbe Breite des Überblendkreuzes in Pixeln")
    a = p.parse_args()
    seamless(Image.open(a.source), a.band).save(a.target)
    print(a.target)
