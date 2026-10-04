"""Ablage nach Workflow für die Skripte von gen-asset (comfy_generate.py, upscale.py, comfy_matte.py).

Kommt beim Umzug der Bildablage als scripts/ablage.py nach gen-asset (tools/umzug_genasset.py im Repo comfy-gallery). Dieselbe
Regel wie target_folder und retarget_saves in comfy-gallery/gallery_graph.py, hier ohne Abhängigkeiten: die Skripte laufen mit
jedem Python. Renders liegen unter Text2Img/<workflow>/, Testreihen unter Text2Img/_tests/<reihe>/, ein Datum im Ordner gibt es
nicht mehr. Jeder Auftrag gibt die Quelle agent als extra_pnginfo mit, die Galerie liest sie als Chunk gallery_source."""
import re

TESTS_DIR = "_tests"
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}[ _-]*")
SOURCES = ("agent", "ui", "galerie")
# Testreihen: Name mit Nummer, Vorsilbe oder ganzer Workflow (wie TEST_SERIES in gallery_graph.py)
TEST_SERIES = (re.compile(r"^(fototest|qtest|itest|landtest|qwentest)_\d+$"), re.compile(r"^(loratest|kinder|refiner|zehen)-"))
TEST_WORKFLOWS = {"hebel", "mitlora", "luneva", "sweep"}
EXTRA = {"extra_pnginfo": {"gallery_source": "agent"}}
SAVE_TYPES = {"SaveImage", "Image Saver", "SaveImageWithMetaData"}  # wie gallery_store.SAVE_TYPES, Videoknoten bleiben


def test_series(workflow):
    for rx in TEST_SERIES:
        m = rx.match(workflow or "")
        if m:
            return m.group(1)
    return workflow if workflow in TEST_WORKFLOWS else None


def parts_of(prefix):
    return [p for p in str(prefix or "").replace("\\", "/").split("/") if p]


def basename(prefix):
    parts = parts_of(prefix)
    return parts[-1] if parts else ""


def clean_name(prefix):
    """Basisname ohne vorangestelltes Datum, None bei Platzhaltern wie %date%."""
    name = DATE_PREFIX.sub("", basename(prefix)).strip()
    return name if name and "%" not in name and "{" not in name else None


def workflow_of(prefix):
    """Workflow eines Prefix: im alten Schema nach der Quelle (agent/<datum>/foto), im neuen das erste Segment (foto/foto).
    Segmente mit _ vorn und Datumsteile zählen nicht."""
    parts = parts_of(prefix)
    if len(parts) >= 3 and parts[0] in SOURCES:
        parts.pop(0)
    for part in parts:
        if part.startswith("_"):
            continue
        part = DATE_PREFIX.sub("", part).strip()
        if part and "{" not in part and "%" not in part:
            return part
    return "unbekannt"


def folder_of(prefix):
    """Ordner unter Text2Img: _tests/<reihe> für Testreihen, sonst der Workflow."""
    parts = parts_of(prefix)
    if TESTS_DIR in parts[:-1]:
        rest = [p for p in parts[parts.index(TESTS_DIR) + 1:-1] if not DATE.fullmatch(p)]
        name = clean_name(prefix) or "unbekannt"
        return f"{TESTS_DIR}/{rest[0] if rest else test_series(name) or name}"
    workflow = workflow_of(prefix)
    series = test_series(workflow)
    return f"{TESTS_DIR}/{series}" if series else workflow


def normalisiere(workflow):
    """Jeder SaveImage-Prefix eines API-Graphen nach <ordner>/<basisname>, alle Stufen im Ordner der Basisstufe (kürzester
    Basisname): agent/%date:yyyy-MM-dd%/janku und …/janku-detail werden janku/janku und janku/janku-detail, eine Testreihe wie
    agent/2026-09-30/qtest_01 wird _tests/qtest/qtest_01. Ein Prefix der neuen Form bleibt, wie er ist."""
    saves = [node for node in workflow.values() if isinstance(node, dict) and node.get("class_type") in SAVE_TYPES
             and isinstance((node.get("inputs") or {}).get("filename_prefix"), str)]
    if not saves:
        return workflow
    first = min((n["inputs"]["filename_prefix"] for n in saves), key=lambda p: len(basename(p)))
    folder = folder_of(first)
    for node in saves:
        prefix = node["inputs"]["filename_prefix"]
        node["inputs"]["filename_prefix"] = f"{folder}/{clean_name(prefix) or folder.rsplit('/', 1)[-1]}"
    return workflow

