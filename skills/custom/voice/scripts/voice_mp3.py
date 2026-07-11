"""Wandelt ein /voice-Hörskript (.txt) in Kapitel-MP3s um.

Nutzt edge-tts (Microsoft-Neural-Stimmen, kostenlos, Cloud-Endpunkt: keine
Kundendaten oder Hochsensibles einspeisen). Eine MP3 pro Kapitel, Ausgabe in
den Ordner "<Dateiname> MP3" neben der .txt. Vorspann vor Kapitel eins wird
zu "00 Überblick".

Aufruf (PowerShell):
  python voice_mp3.py "D:\\...\\Thema Voice-Skript.txt" [--voice de-DE-ConradNeural]

Stimmen anzeigen:  edge-tts --list-voices | findstr de-DE
"""
import argparse
import asyncio
import re
import sys
from pathlib import Path

import edge_tts

DEFAULT_VOICE = "de-DE-ConradNeural"
CHAPTER_RE = re.compile(r"^Kapitel\s+([a-zäöüß]+)\.\s*(.*)", re.IGNORECASE)


def split_chapters(text: str):
    """Liefert Liste (titel, sprechtext). Text vor Kapitel eins = Überblick."""
    chapters = []
    title, buf = "Überblick", []

    def flush():
        body = "\n".join(buf).strip()
        if body:
            chapters.append((title, body))

    for line in text.splitlines():
        m = CHAPTER_RE.match(line.strip())
        if m:
            flush()
            rest = m.group(2).strip()
            title = rest.split(".")[0].strip() or f"Kapitel {m.group(1)}"
            buf = [line.strip()]  # Kapitel-Zeile wird mitgesprochen
        else:
            buf.append(line)
    flush()
    return chapters


def safe_name(s: str) -> str:
    s = re.sub(r'[<>:"/\\|?*]', "", s)
    return re.sub(r"\s+", " ", s).strip()[:60]


async def synth(text: str, voice: str, out: Path):
    for attempt in (1, 2):
        try:
            await edge_tts.Communicate(text, voice).save(str(out))
            return
        except Exception as e:
            if attempt == 2:
                raise
            print(f"  Fehler ({e}), zweiter Versuch ...")


def main():
    ap = argparse.ArgumentParser(description="Voice-Skript .txt zu Kapitel-MP3s")
    ap.add_argument("txt", help="Pfad zum Voice-Skript (.txt)")
    ap.add_argument("--voice", default=DEFAULT_VOICE)
    args = ap.parse_args()

    src = Path(args.txt)
    chapters = split_chapters(src.read_text(encoding="utf-8-sig"))
    if not chapters:
        sys.exit("Keine Inhalte gefunden.")

    out_dir = src.parent / f"{src.stem} MP3"
    out_dir.mkdir(exist_ok=True)

    has_intro = chapters[0][0] == "Überblick"
    for i, (title, body) in enumerate(chapters):
        num = i if has_intro else i + 1
        out = out_dir / f"{num:02d} {safe_name(title)}.mp3"
        print(f"{out.name}  ({len(body)} Zeichen)")
        asyncio.run(synth(body, args.voice, out))

    print(f"\nFertig: {len(chapters)} Dateien in {out_dir}")


if __name__ == "__main__":
    main()
