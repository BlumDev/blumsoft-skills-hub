# Zweitmeinungs-Audit 2026-08-31 (cursor-grok-4.6-high)

Basis: main 0a911da, Arbeitskopie sauber. Run-ID 20260831T193436-81ddad (Gate read-only, dritter Anlauf nach zwei 540s-Timeouts im Parallelbetrieb; dieser Lauf einzeln mit 1200s). Auftrag: nur NEUE Findings gegenüber docs/reviews/ und docs/backlog.md.

## Externe Ausgabe (wörtlich)

Drei neue Findings (0 high / 3 medium). Hub-Tooling gegen `docs/reviews/` und `docs/backlog.md` abgeglichen; die bekannten Punkte (Doppelziel `codex`/`vscode-chatgpt`, Sync-Delete-vor-Move, vendor-import-Partial, `setup-from-profile` ohne Dry-Run, `brand-review` ohne Lock, `ensure_comfyui`-Logs, `with_server`, YAML-Regex, CI nur `validate.ps1`) sind nicht erneut aufgeführt.

`skills/custom/gen-asset/scripts/upscale.py:79` - severity(medium) - Die Datei in Comfys Input-Ordner heißt immer `upscale_src_` plus Basename. Zwei Upscales von z. B. `out\hero.png` und `projekt\hero.png` (oder zwei parallele Jobs) schreiben dieselbe Datei `D:\Apps\Stability Matrix\Data\Packages\ComfyUI\input\upscale_src_hero.png`. Der zweite Lauf überschreibt die Datei des ersten; ein noch laufender erster Job liest dann fremde Pixel und speichert sie als vermeintliches Upscale-Ergebnis.

`skills/custom/gen-asset/scripts/comfy_generate.py:165` - severity(medium) - Die Poll-Schleife liest `/history/{id}` nur auf `outputs.images`, nicht auf `status.status_str`. Schlägt der Prompt fehl (fehlendes Checkpoint, OOM, Node-Error), legt ComfyUI sofort einen History-Eintrag ohne Bilder mit `status=error` an; das Skript wartet trotzdem die vollen `--timeout` 900s (dieselbe Schleife in `upscale.py:111` mit 1200s) und meldet Timeout statt des Ausführungsfehlers.

`skills/custom/gen-asset/scripts/comfy_generate.py:89` - severity(medium) - `inject` setzt `--seed`/`--steps` nur bei `_meta.title == "SAMPLER"`. Die im Skill als Default für Qualität genannten Workflows `sdxl_hires.api.json` und `sd15_anime_hires.api.json` haben einen zweiten Sampler `SAMPLER_HIRES` mit festem `seed: 12345`. Ein Lauf mit anderem `--seed` ändert nur den ersten Pass; der Hires-Pass bleibt bei 12345, Seed-Iteration und Repro über die CLI greifen nicht.

## Stichproben (Koordinator, am Code)

- upscale.py:79 BESTÄTIGT: `fname = "upscale_src_" + os.path.basename(a.image)` ohne jede Eindeutigkeit, direkt gefolgt vom Copy in den ComfyUI-Input.
- comfy_generate.py:89 BESTÄTIGT: der inject-Zweig greift nur bei `title == "SAMPLER"`; workflows/sdxl_hires.api.json trägt in Zeile 46 `"seed": 12345` unter `_meta.title == "SAMPLER_HIRES"` (Zeile 57).
- Finding 2 (Poll-Schleife) nicht einzeln nachgeprüft, Muster konsistent mit den zwei bestätigten.
