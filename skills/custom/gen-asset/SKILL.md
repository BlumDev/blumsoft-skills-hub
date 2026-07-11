---
name: gen-asset
description: >-
  Generiert Bild-Assets (später auch Videos) lokal über ComfyUI für die
  Entwicklung, wenn Platzhalter oder finale Assets gebraucht werden:
  Produktbilder, Landschaft (Winzer), Gastro/Food, Handwerk/Bau,
  Web-Animationen. Erkennt das Vertical, wählt Modell/LoRA, ruft die lokale
  ComfyUI-HTTP-API und prüft das Ergebnis per Vision-Loop, bevor es verwendet
  wird. Lokal, offline, kostenfrei. Use when the user or an agent needs an image
  or asset generated, created, rendered, or a placeholder produced during
  development, e.g. "generiere ein Bild von", "brauche ein Produktbild",
  "Hero-Bild für", "Platzhalterbild", "render an image for this component".
  Trigger: "generiere/erstelle Bild", "brauche ein Bild", "Produktbild",
  "Hero-Bild", "Platzhalter", "Asset generieren", "gen-asset".
---

# gen-asset

Erzeugt Bild-Assets lokal mit ComfyUI (Stability Matrix) und prüft sie selbst,
bevor sie im Projekt landen. Deutsche Antworten, echte Umlaute, knapp, Senior-Ton.

**Wichtig:** Dieser Skill ist erst voll lauffähig, wenn die Voraussetzungen
erfüllt sind (siehe unten). Bis dahin: Schritte benennen, nicht blind starten.
Voller Hintergrund und Setup stehen in [reference/plan.md](reference/plan.md).

**Wissensbasis (lebendes Wissen, vor dem Generieren konsultieren):**
- [reference/models.md](reference/models.md): Modell-Registry, Lizenzen, Vertical→Modell, Entscheidungen. Kommerziell frei ist Bedingung.
- [reference/learnings.md](reference/learnings.md): destillierte Erkenntnisse, welches Modell/Prompt/LoRA für welches Vertical funktioniert.
- `reference/ledger.jsonl`: Roh-Datenpunkte pro bewährtem Bild (via `scripts/ledger.py`).

Lernschleife ist Pflicht: vor dem Generieren lesen (models.md + learnings.md + Ledger-Recall),
nach einem auffälligen Ergebnis learnings.md ergänzen. So wird die Qualität über die Zeit besser.

## Voraussetzungen (einmalig prüfen)

1. **GPU-Torch:** Das ComfyUI-venv von Stability Matrix hatte initial
   `torch ...+cpu` (CPU-only, GPU ungenutzt). Vor Nutzung muss Torch auf
   `cu128` (Blackwell) bzw. `cu130` (für NVFP4) stehen. Check:
   `& "D:\Apps\Stability Matrix\Data\Packages\ComfyUI\venv\Scripts\python.exe" -c "import torch;print(torch.cuda.is_available())"`
   muss `True` liefern. Wenn `False`: erst Fix (siehe plan.md, Abschnitt Setup).
2. **ComfyUI läuft:** Muss nicht manuell in der GUI gestartet werden. Der Agent
   startet die Engine selbst headless via `scripts\ensure_comfyui.ps1` (prüft die
   API, startet ComfyUI im Hintergrund, wartet bis bereit). Default-API
   `http://127.0.0.1:8188`. Damit ist der Skill voll autonom, kein Stability-Matrix-
   Fenster nötig. Der Server bleibt warm (Modell im VRAM), Folgegenerierungen sind schnell.
3. **Modelle vorhanden:** SDXL (Juggernaut XL v8), FLUX.1-schnell (All-in-one) und
   Chroma1-HD (Q8 GGUF + t5xxl_fp8 + ae.safetensors) sind installiert und getestet.
   Chroma braucht die `ComfyUI-GGUF`-Node (installiert).

## Vertical → Modell

Quelle der Wahrheit inkl. Lizenzen: [reference/models.md](reference/models.md).

| Anforderung | Modell | Default-Format |
|---|---|---|
| Landschaft / Architektur / Web-Hero | FLUX.1-schnell | 16:9 (1344x768) |
| Produkt | FLUX.1-schnell | 1:1 / 4:5 |
| Gastro / Food | FLUX.1-schnell | 4:5 (896x1152) |
| Menschen / Portrait (Haut!) | Chroma1-HD | 4:5 (896x1152) |
| Anime / Illustration | Chroma1-HD | 1:1 |
| NSFW (real/anime) | Chroma1-HD | je nach Motiv |
| Schneller SFW-Test | SDXL (Juggernaut XL) | 1024x1024 |

Alle kommerziell frei nutzbar. Für realistische Menschen/Haut und Anime/NSFW Chroma
(echtes Negativ, mehr Steps), für Landschaft/Architektur/Produkt FLUX-schnell (schneller).

**Workflow nach Bedarf wählen:**
- `sdxl_t2i.api.json`: schnell, ~1 MP, für Vorschau/Tests.
- `sdxl_hires.api.json`: Basis + Hires-Pass (Latent-Upscale 1.5x, 2. Sampler-Pass
  denoise 0.45), ~2.3 MP, scharf, für finale Web-Assets. Default für Qualität.
- `flux_schnell_t2i.api.json`: höchste Fidelity bei Landschaft/Architektur/Produkt, schnell.
- `chroma_t2i.api.json`: Chroma1-HD (GGUF) für Menschen/Haut, Anime, NSFW. 26 Steps, cfg 4.0,
  echter Negativ-Prompt (anders als FLUX-schnell), langsamer. Kommerziell frei (Apache).
- Noch größer (4K+): `scale_by` in der UPSCALE-Node erhöhen oder UltimateSDUpscale
  (Custom-Node ist installiert) gekachelt nutzen.

## Ablauf

0. **Engine sicherstellen.** `powershell -File scripts\ensure_comfyui.ps1` ausführen
   (idempotent: startet ComfyUI nur, wenn es nicht schon läuft).
1. **Anforderung klären.** Motiv, Vertical, Seitenverhältnis, Zielpfad,
   Marken-/Stilvorgaben. Bei echter Mehrdeutigkeit kurz rückfragen, sonst Annahme
   benennen und weiter.
1b. **Recall (Gedächtnis nutzen).** Vor dem Promptbau `reference/learnings.md` +
   `reference/models.md` lesen (Modellwahl + bewährte Prompt-Muster fürs Vertical),
   dann prüfen, ob es schon ein bewährtes Bild gibt:

   ```powershell
   & "D:\SDKs\Python311\python.exe" "C:\Users\Marcus\.claude\skills\gen-asset\scripts\ledger.py" find --vertical winzer --min-rating 4
   ```

   Treffer? Das gelistete PNG enthält seinen Workflow nativ in den Metadaten:
   in ComfyUI ziehen lädt den Graph, oder Prompt/Seed aus der Zeile als Startpunkt
   übernehmen und gezielt variieren, statt bei null anzufangen.
2. **Prompt bauen.** Konkret, fotografisch: Subjekt, Setting, Licht, Optik
   (z.B. "35mm, golden hour"), Stimmung. Für Schärfe `sharp focus, fine detail`
   rein. **Achtung:** `soft, haze, shallow depth of field, bokeh` machen das Bild
   bewusst weich, nur nutzen wenn gewollt, sonst in den Negative-Prompt. Kein
   Markenname ohne Grund. Negative-Prompt nur bei SDXL sinnvoll.
3. **Generieren.** Skript aufrufen (PowerShell):

   ```powershell
   & "D:\SDKs\Python311\python.exe" "C:\Users\Marcus\.claude\skills\gen-asset\scripts\comfy_generate.py" `
     --workflow "C:\Users\Marcus\.claude\skills\gen-asset\workflows\sdxl_t2i.api.json" `
     --prompt "<englischer Prompt>" `
     --negative "blurry, lowres, watermark, text, deformed" `
     --width 1024 --height 1024 `
     --out "<Zielpfad>\asset.png"
   ```

   Für FLUX `--workflow ...\flux_schnell_t2i.api.json` und `--negative ""`.
   Optional `--checkpoint`, `--lora`, `--lora-strength`, `--seed`, `--steps`.
   Stdout des Skripts = finaler Bildpfad.
4. **Verify-Loop (Pflicht).** Das erzeugte PNG mit dem `Read`-Tool öffnen
   (Vision) und gegen die Anforderung prüfen:
   - Motiv korrekt und vollständig?
   - Seitenverhältnis/Ausschnitt wie gewünscht?
   - Artefakte (verformte Hände/Objekte, Doppelungen, Matsch)?
   - Text im Bild lesbar/erwünscht? (FLUX kann Text, SDXL meist nicht.)
   - Marken-/Stilfit?
   Bei Nichtbestehen: Prompt/Seed/LoRA-Stärke nachschärfen, neu generieren.
   Max. ~4 Iterationen, dann Zwischenstand zeigen und nachfragen.
5. **Verwenden / Ablage.** Erst nach bestandener Prüfung verwenden. Zielpfad (`--out`)
   nach Zweck wählen, damit beim Generieren sortiert wird statt nachträglich:
   - persönliche Keeper → `D:\Apps\Stability Matrix\Data\Images\library\<vertical>\`
     (landschaft/architektur/menschen/produkt/food/handwerk/anime/nsfw),
   - Projekt-Assets → in den jeweiligen Projektordner.
   Pfad und kurze Begründung der Wahl nennen.
6. **Remember (Loop schließen).** Reproduktion ist nativ gelöst: jedes erzeugte PNG
   trägt seinen Workflow in den Metadaten (`comfy_generate.py` bettet ihn ein, wie ein
   GUI-Bild). Es braucht KEIN Sidecar. Nach bestandenem Verify nur noch in den
   Recall-Index eintragen, damit gute Bilder per Vertical wiederfindbar sind:

   ```powershell
   & "D:\SDKs\Python311\python.exe" "C:\Users\Marcus\.claude\skills\gen-asset\scripts\ledger.py" add `
     --image "<bild>.png" --rating 5 --vertical winzer --tags "hero,landscape" --note "kurz, was gut war"
   ```

   Index liegt in `reference/ledger.jsonl` (append-only, zeigt aufs PNG; Prompt/Seed
   werden aus den PNG-Metadaten gelesen). Nur bestandene Bilder eintragen (Rating 4-5),
   damit Recall wertvoll bleibt. Stability Matrix' eigene Galerie
   (`Data\Images`) bleibt parallel für manuelles Sichten nutzbar.
7. **Lernen (Loop schließen).** Wenn du etwas Allgemeines gelernt hast (Modell X taugt
   gut/schlecht für Vertical Y, ein Prompt-Trick, eine LoRA-Wirkung), ergänze es in
   [reference/learnings.md](reference/learnings.md). Der Ledger sammelt Datenpunkte,
   learnings.md destilliert daraus die Muster.

## Inhalts- und Rechts-Leitplanke (verbindlich)

Gilt immer, wenn Claude im Loop ist (Prompt bauen, generieren, verifizieren):

- **Explizit/erotisch: tabu.** Claude promptet, generiert und verifiziert KEINE
  pornografischen/expliziten Inhalte. Solche Bilder macht der Nutzer selbst,
  vollständig ohne Claude.
- **Legal und unkritisch ist ok:** Bikini, Unterwäsche, Produktbilder im normalen
  Kontext. Hier ist der Agent-Workflow problemlos.
- **Absolute Grenze, keine Ausnahme:** Alles mit Minderjährigen, auch KI-generiert,
  ist strafbar (§184b StGB). Niemals, unter keinen Umständen, auch nicht andeutungsweise.
- **Haftung liegt beim Nutzer**, nicht bei Claude. Die Lokalität (ComfyUI offline)
  ändert daran nichts, solange Claude im Loop ist.
- Keine real existierenden Personen / Promi-Ähnlichkeit ohne Einwilligung.

## Grenzen

- Nur Bilder. Video (LTX-2 / Wan 2.2 I2V) ist geplant, noch nicht implementiert
  (siehe plan.md, Roadmap).
- Keine Marken-Logos/Markeninhalte ohne ausdrückliche Vorlage.
- Lizenz beachten: FLUX.1-schnell (Apache 2.0) ist kommerziell sauber, FLUX.1-dev
  und viele Civitai-LoRAs nicht. Im Zweifel plan.md prüfen.
