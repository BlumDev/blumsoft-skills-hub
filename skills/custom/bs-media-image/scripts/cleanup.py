#!/usr/bin/env python3
"""Werkzeug von Hand, um Agenten-Testbilder wegzuräumen. Läuft nie automatisch.

Entscheidung vom 22.09.2026 (Nutzer): Agentenbilder verfallen NICHT. Sie tragen
ihren kompletten Workflow und dokumentieren auch Fehlversuche, deshalb bleiben
sie liegen. Unübersichtlichkeit wird in der Galerie gefiltert, nicht gelöscht.

Dieses Skript existiert nur noch für den ausdrücklichen Fall, dass eine bestimmte
Testreihe weg soll. Seit dem Umzug der Bildablage (Oktober 2026) liegen Testreihen unter
`Text2Img\\_tests\\<reihe>\\`, ohne Datumsordner: das Alter eines Bilds kommt aus dem Datum
im Namen (`fototest_07_2026-09-28_00001_.png`), sonst aus dem Dateidatum. Ohne `--apply`
zeigt es nur eine Vorschau, und es verschiebt ausschließlich nach `Images\\_papierkorb\\`.
Gelöscht wird nichts, auch kein leerer Ordner: ComfyUI schreibt im flachen Schema weiter in
denselben Ordner der Testreihe.

Verschont bleibt in jedem Fall jede Datei, die
  1. im Ledger des Skills steht (reference/ledger.jsonl),
  2. in reference/*.md namentlich zitiert wird,
  3. in den Daten der Bildgalerie vorkommt: markiert (Favorit, Beispiel, Bewertung, Notiz,
     Mängel oder NSFW-Einstufung von Hand), in einem Urteil samt Duellschritten, einer
     Gruppe, einer Trennung oder einem Learning (data/ der Galerie, wird nur gelesen),
  4. Quelle eines Vergleichsblatts ist (`sources` in einer modelle.json).

Nullbyte-Platzhalter `<name>.papierkorb` fasst es nie an und zählt sie nicht mit. Die
Galerie legt sie seit 28.09.2026 beim Papierkorb an, damit ComfyUI den Namen eines
gelöschten Bilds nicht neu vergibt (das Folgebild erbte sonst Gruppe, Urteile, Mängel,
NSFW-Einstufung und Stufen). Dasselbe tut dieses Skript nach dem Verschieben: je Ordner und
Prefix hält ein Platzhalter den höchsten verschobenen Namen, wenn kein Bild und kein
Platzhalter mit mindestens diesem Zähler bleibt. Namen mit Datum (`sweep_2026-09-28_00003_`)
zählt ComfyUI nicht fort, sie brauchen keinen.

Aufruf (PowerShell), Vorschau und dann echt. Ohne `--days` passiert nichts,
weil die Voreinstellung so hoch liegt, dass kein Bild sie erreicht:
  python cleanup.py --days 90
  python cleanup.py --days 90 --apply
"""
import argparse
import datetime
import json
import os
import re
import shutil
import sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY = r"D:\Apps\Stability Matrix\Data\Images"
IMAGES = os.path.join(LIBRARY, "Text2Img")
TESTS = os.path.join(IMAGES, "_tests")
TRASH = os.path.join(LIBRARY, "_papierkorb")
# Daten der Bildgalerie, nur gelesen. Die Datenkopien in Worktrees zählen nicht, sie veralten.
GALLERY_DATA = r"D:\Repos\comfy-gallery\data"
GALLERY_FILES = ("tags.json", "verdicts.json", "groups.json", "splits.json", "learnings.json")
MONTAGE_ROOTS = [os.path.join(SKILL, "out"), LIBRARY]
PLACEHOLDER = ".papierkorb"
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
# Name mit Zähler wie bei ComfyUI, wie NAME_COUNTER in comfy-gallery/gallery_graph.py: Prefix, Datum oder nichts, Zähler
NAME_COUNTER = re.compile(r"^(.*?)(?:_(\d{4}-\d{2}-\d{2}))?_(\d+)_?$")


def protected():
    """Dateinamen, die nicht angefasst werden dürfen, aus vier Quellen."""
    names, why = set(), {}

    def keep(name, source):
        name = os.path.basename(str(name).replace("\\", "/"))
        if name:
            names.add(name)
            why.setdefault(name, source)

    def images_in(value, source):
        """Jede Zeichenkette, die auf eine Bilddatei endet, ob Schlüssel, Pfad oder Name, auch als Schlüssel eines Dicts."""
        if isinstance(value, dict):
            for k, v in value.items():
                images_in(k, source)
                images_in(v, source)
        elif isinstance(value, list):
            for v in value:
                images_in(v, source)
        elif isinstance(value, str) and value.lower().endswith(IMAGE_EXT):
            keep(value, source)

    def load(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"Hinweis: {path} nicht lesbar ({exc}), diese Einträge bleiben außen vor.")
            return None

    ledger = os.path.join(SKILL, "reference", "ledger.jsonl")
    if os.path.exists(ledger):
        with open(ledger, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    keep(json.loads(line).get("image", ""), "Ledger")
                except json.JSONDecodeError:
                    continue

    ref = os.path.join(SKILL, "reference")
    if os.path.isdir(ref):
        for datei in os.listdir(ref):
            if not datei.endswith(".md"):
                continue
            with open(os.path.join(ref, datei), "r", encoding="utf-8") as fh:
                for hit in re.findall(r"[\w.\-]+\.(?:png|jpg|jpeg|webp)", fh.read()):
                    keep(hit, "zitiert in " + datei)

    for name in GALLERY_FILES:
        path = os.path.join(GALLERY_DATA, name)
        data = load(path) if os.path.exists(path) else None
        if data is None:
            continue
        if name == "tags.json":
            # showcase sind die von Hand gewählten Beispiele der Modellseiten, nsfw die Einstufung von Hand; geprüft allein
            # schützt nicht
            marked = [k for k, v in data.items() if isinstance(v, dict)
                      and (v.get("favorite") or v.get("showcase") or v.get("rating") or v.get("note") or v.get("issues")
                           or v.get("nsfw"))]
            images_in(marked, "in der Galerie markiert")
        else:
            images_in(data, f"in der Galerie ({name})")

    for root in MONTAGE_ROOTS:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d != "_papierkorb"]
            if "modelle.json" in filenames:
                data = load(os.path.join(dirpath, "modelle.json"))
                if isinstance(data, dict):
                    images_in([data.get("sources") or []] + [(e or {}).get("sources") or [] for e in (data.get("files") or {}).values()
                                                             if isinstance(e, dict)], "Quelle eines Vergleichsblatts")
    return names, why


def undated(name):
    """Name vor dem Umzug: Zitate in reference/*.md nennen foto_00007_.png, die Datei heißt jetzt foto_2026-09-21_00007_.png."""
    return re.sub(r"_\d{4}-\d{2}-\d{2}(?=_\d+_?\.)", "", name)


def counter_of(stem):
    """(Prefix in Kleinschrift, Zähler) eines Namens, wie ComfyUI ihn fortzählt, None ohne Zähler oder mit Datum davor."""
    m = NAME_COUNTER.match(stem)
    return (m.group(1).lower(), int(m.group(3))) if m and not m.group(2) else None


def hold_names(moved):
    """Je Ordner und Prefix ein Platzhalter für den höchsten verschobenen Namen, sofern dort kein Bild und kein Platzhalter mit
    mindestens diesem Zähler bleibt. Sonst vergäbe ComfyUI den Namen neu und das neue Bild erbte die Daten des alten."""
    best = {}
    for path in moved:
        stem = os.path.splitext(os.path.basename(path))[0]
        c = counter_of(stem)
        if c and c[1] > best.get((os.path.dirname(path), c[0]), (0, ""))[0]:
            best[(os.path.dirname(path), c[0])] = (c[1], stem)
    made = 0
    for (folder, prefix), (n, stem) in sorted(best.items()):
        os.makedirs(folder, exist_ok=True)
        have = [counter_of(os.path.splitext(f)[0]) for f in os.listdir(folder)]
        if any(c and c[0] == prefix and c[1] >= n for c in have):
            continue
        open(os.path.join(folder, stem + PLACEHOLDER), "ab").close()
        made += 1
    return made


def day_of(path, name):
    """Datum eines Bilds: aus dem Namen (seit dem Umzug), sonst das Dateidatum."""
    hit = DATE.search(name)
    if hit:
        return datetime.date.fromisoformat(hit.group(0))
    return datetime.date.fromtimestamp(os.path.getmtime(path))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # Absichtlich unerreichbar hoch: ohne ausdrückliches --days passiert nichts.
    p.add_argument("--days", type=int, default=100000,
                   help="älter als so viele Tage. Ohne Angabe wird nichts ausgewählt, "
                        "Agentenbilder verfallen nicht von allein.")
    p.add_argument("--apply", action="store_true", help="wirklich verschieben, sonst nur Vorschau")
    p.add_argument("--dir", dest="folder", default=TESTS, help="Testwurzel (Standard: _tests unter Text2Img)")
    a = p.parse_args()

    if not os.path.isdir(a.folder):
        sys.exit(f"Testordner fehlt: {a.folder}")

    keepers, why = protected()
    limit = datetime.date.today() - datetime.timedelta(days=a.days)
    doomed, young, spared = [], 0, []

    for root, _, files in os.walk(a.folder):
        for datei in files:
            if datei.endswith(PLACEHOLDER):
                continue
            path = os.path.join(root, datei)
            if day_of(path, datei) > limit:
                young += 1
            elif datei in keepers or undated(datei) in keepers:
                spared.append((datei, why.get(datei) or why[undated(datei)]))
            else:
                doomed.append(path)

    print(f"Grenze: alles vor {limit.isoformat()} ({a.days} Tage)")
    print(f"  {young} Dateien sind jünger und bleiben")
    print(f"  {len(spared)} Dateien sind älter, werden aber als Beleg verschont")
    for datei, source in spared[:20]:
        print(f"      {datei}  ({source})")
    if len(spared) > 20:
        print(f"      ... und {len(spared) - 20} weitere")
    print(f"  {len(doomed)} Dateien wandern in den Papierkorb")

    if not doomed:
        return
    if not a.apply:
        for datei in doomed[:20]:
            print(f"      {os.path.relpath(datei, IMAGES)}")
        if len(doomed) > 20:
            print(f"      ... und {len(doomed) - 20} weitere")
        print("\nVorschau. Mit --apply wirklich verschieben.")
        return

    for datei in doomed:
        target = os.path.join(TRASH, os.path.relpath(datei, LIBRARY))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if os.path.exists(target):
            stem, ext = os.path.splitext(target)
            target = f"{stem}_{datetime.datetime.now().strftime('%H%M%S')}{ext}"
        shutil.move(datei, target)
    made = hold_names(doomed)  # Ordner bleiben, auch leer: ComfyUI schreibt die Testreihe weiter dorthin
    print(f"\n{len(doomed)} Dateien nach {TRASH} verschoben, {made} Platzhalter halten ihre Namen.")


if __name__ == "__main__":
    main()
