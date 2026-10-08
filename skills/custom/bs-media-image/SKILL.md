---
name: bs-media-image
description: >-
  Generiert Bild-Assets lokal über ComfyUI für die Entwicklung, wenn
  Platzhalter oder finale Assets gebraucht werden: Produktbilder, Landschaft
  (Winzer), Gastro/Food, Handwerk/Bau. Erkennt das Vertical, wählt
  Modell/LoRA, ruft die lokale ComfyUI-HTTP-API und prüft das Ergebnis per
  Vision-Loop, bevor es verwendet wird. Lokal, offline, kostenfrei. Nur
  Standbilder, kein Video. Use when the user or an agent needs an image
  or asset generated, created, rendered, or a placeholder produced during
  development, e.g. "generiere ein Bild von", "brauche ein Produktbild",
  "Hero-Bild für", "Platzhalterbild", "render an image for this component".
  Trigger: "generiere/erstelle Bild", "brauche ein Bild", "Produktbild",
  "Hero-Bild", "Platzhalter", "Asset generieren", "bs-media-image".
---

# bs-media-image

Erzeugt Bild-Assets lokal mit ComfyUI (Stability Matrix) und prüft sie selbst,
bevor sie im Projekt landen. Deutsche Antworten, echte Umlaute, knapp, Senior-Ton.

**Wichtig:** Dieser Skill ist erst voll lauffähig, wenn die Voraussetzungen
erfüllt sind (siehe unten). Bis dahin: Schritte benennen, nicht blind starten.
Voller Hintergrund und Setup stehen in [reference/plan.md](reference/plan.md).

**Der Nutzer generiert auch selbst, über die ComfyUI-Oberfläche.** Dieselben zwanzig Workflows
liegen dafür zusätzlich im UI-Format unter `ComfyUI\user\default\workflows\gen-asset\`
(sprechende Namen, Seed auf randomize), erzeugt aus den API-Vorlagen über
`scripts/api_to_ui_workflow.py`. Anleitung: [reference/bedienung.md](reference/bedienung.md).
Ändert sich eine Vorlage in `workflows/*.api.json`, den Konverter neu laufen lassen, sonst
zeigt die Oberfläche einen veralteten Graphen.

**Wissensbasis (lebendes Wissen, vor dem Generieren konsultieren):**
- [reference/models.md](reference/models.md): Modell-Registry, Lizenzen, Vertical→Modell, Entscheidungen. Kommerziell frei ist Bedingung.
- [reference/learnings.md](reference/learnings.md): destillierte Erkenntnisse, welches Modell/Prompt/LoRA für welches Vertical funktioniert.
- `reference/ledger.jsonl`: Roh-Datenpunkte pro bewährtem Bild (via `scripts/ledger.py`).

Lernschleife ist Pflicht: vor dem Generieren lesen (models.md + learnings.md + Ledger-Recall),
dazu die offenen Learnings aus der Bildgalerie einarbeiten (Ablauf, Schritt 1a), nach einem
auffälligen Ergebnis learnings.md ergänzen. So wird die Qualität über die Zeit besser.

**Testmaterial und seine Halbwertszeit.** Eigene Läufe landen unter `Text2Img\<workflow>\`, der
Ordner ist der Basisname des Knotens SAVE der Vorlage und alle Stufen eines Laufs liegen darin
(`janku\janku_00001_.png` und `janku\janku-detail_00001_.png`). Testreihen landen unter
`Text2Img\_tests\<reihe>\`: Blindtests mit dem Prefix `_tests/<reihe>/<reihe>_<nn>`, dazu alles mit
`fototest_NN`, `qtest_NN`, `itest_NN`, `landtest_NN`, `qwentest_NN`, den Vorsilben `loratest-`, `kinder-`,
`refiner-`, `zehen-` und die Workflows `hebel`, `mitlora`, `luneva`, `sweep`. Die Skripte setzen das selbst
(`scripts/ablage.py`): ein Prefix der alten Form `agent/%date:yyyy-MM-dd%/<name>` wird beim
Einreihen umgeschrieben. Jeder Auftrag gibt die Quelle `agent` als Chunk `gallery_source` mit,
daran erkennt die Bildgalerie in `D:\Repos\comfy-gallery` das Testmaterial. Ein Datum im Ordner
gibt es nicht mehr, Bilder von vor dem Umzug (Oktober 2026) tragen es im Namen
(`foto_2026-09-28_00004_.png`).

Ein Vergleichslauf endet nicht mit fünfzehn losen Einzelbildern, sondern mit einem montierten
Vergleichsblatt unter `out/<thema>/` (etwa `out/vergleich/`), einer `modelle.json` daneben und einem Eintrag in learnings.md. Das Rohmaterial bleibt trotzdem liegen:
der Nutzer hat am 22.09.2026 entschieden, dass Agentenbilder NICHT verfallen, weil sie ihren
Workflow tragen und auch Fehlversuche dokumentieren. Unübersichtlichkeit wird in der Galerie
gefiltert, nicht gelöscht. `scripts/cleanup.py` bleibt als Werkzeug von Hand für den Fall, dass
eine bestimmte Testreihe unter `_tests` weg soll. Ohne ausdrückliches `--days` tut es nichts. Es
verschiebt nur nach `Images\_papierkorb\` und verschont jedes Bild aus dem Ledger, aus Zitaten in
`reference/*.md` und aus den Daten der Galerie (Markierungen samt Mängeln und NSFW-Einstufung von Hand,
Urteile samt Duellschritten, Gruppen, Trennungen, Learnings) sowie jede Quelle eines Vergleichsblatts
(`sources` in `modelle.json`). Wer ein Bild als Beleg in learnings.md nennt, schützt es damit.
Nullbyte-Platzhalter `<name>.papierkorb` lässt es liegen und zählt sie nicht mit: die Galerie legt
sie seit 28.09.2026 beim Papierkorb an, damit ComfyUI den Namen eines gelöschten Bilds nicht neu
vergibt (das Folgebild erbte sonst Gruppe, Urteile und Stufen). Ordner löscht es nie, auch leere
nicht: ComfyUI schreibt die Testreihe weiter dorthin. Nach dem Verschieben hält es den höchsten
Namen je Prefix selbst mit einem Platzhalter, sonst erbte das nächste Bild Mängel, Einstufung und
Urteile.

## Voraussetzungen (einmalig prüfen)

1. **GPU-Torch:** Stand 2026-09-19 nach dem Update auf ComfyUI 0.36.0: `torch 2.14.0+cu130`,
   `torchvision 0.29.0+cu130`, `cuda.is_available() == True`, RTX 5070 Ti erkannt.
   **ComfyUI nie aktualisieren, solange der Server läuft** (auch die Headless-Instanz
   stoppen), sonst bricht uv mitten im Paketwechsel ab und torch fehlt; Hergang und
   Reparatur in learnings.md. Diagnose bei Verdacht auf Regression (nach jedem Update):
   `& "D:\Apps\Stability Matrix\Data\Packages\ComfyUI\venv\Scripts\python.exe" -c "import torch;print(torch.cuda.is_available())"`
   muss `True` liefern. Wenn `False`: Fix siehe plan.md, Abschnitt Setup (Phase 0).
2. **ComfyUI läuft:** Muss nicht manuell in der GUI gestartet werden. Der Agent
   startet die Engine selbst headless via `scripts\ensure_comfyui.ps1` (prüft die
   API, startet ComfyUI im Hintergrund, wartet bis bereit). Default-API
   `http://127.0.0.1:8188`. Damit ist der Skill voll autonom, kein Stability-Matrix-
   Fenster nötig. Der Server bleibt warm (Modell im VRAM), Folgegenerierungen sind schnell.
   **Kaltstart dauert seit `--enable-manager` mehrere Minuten:** der ComfyUI-Manager zieht
   beim Start die ComfyRegistry und blockiert dabei die HTTP-API (gemessen 2026-08-27:
   3 min 14 s und 4 min 25 s vom Prozessstart bis zum Ende des Fetches). Das Skript wartet
   deshalb bis zu 900 s nach Wanduhr. Ein Timeout heißt nicht automatisch, dass der Server
   fehlt, erst `curl http://127.0.0.1:8188/system_stats` prüfen.
3. **Modelle vorhanden (Stand der Konsolidierung 2026-09-19, fünf Familien):**
   Z-Image-Turbo (`z_image_turbo_bf16` + `qwen_3_4b` + `ae_zimage`) und CyberRealistic
   Z-Image v7 (`cyberrealisticZImage_v70_bf16`, gleicher Encoder und VAE), Qwen-Image-2512
   und Qwen-Image-Edit-2511 (beide Q4_K_M GGUF, `qwen_2.5_vl_7b_fp8_scaled`, `qwen_image_vae`,
   Turbo- und Lightning-LoRA) und die SDXL-Familie mit WAI-illustrious v17 und Illustrious Realism v4 (
   VAE im Checkpoint). Die GGUFs brauchen die `ComfyUI-GGUF`-Node (installiert). Für
   freigestellte Motive BiRefNet-General (MIT, `ComfyUI\models\BiRefNet\BiRefNet-General`)
   über die Node `comfyui_layerstyle`, fürs Upscale 4x-UltraSharp. FLUX, Chroma, Juggernaut
   und der SD1.5-Zoo sind seit 2026-09-19 gelöscht, Begründung in learnings.md.

## Vertical → Modell

Quelle der Wahrheit inkl. Lizenzen: [reference/models.md](reference/models.md).

| Anforderung | Modell | Default-Format |
|---|---|---|
| Landschaft / Winzer | Qwen-Image-2512 mit 30 Steps, cfg 4.0, ohne Turbo-LoRA, `qwen_2512_landschaft` (Blindtest 28.09.: 8 von 16 Prompts); schnell: Krea 2 (5 von 16) | 16:9 (1344x768), etwa 100 s (Krea 11 s) |
| Architektur / Web-Hero | Qwen-Image-2512 in Qualitätseinstellung, `qwen_2512_landschaft` (Fototest 28.09.: 3 von 4, Nutzerentscheid 03.10.); schnell: Krea 2 | 16:9 (1344x768), etwa 100 s |
| Produkt | Krea 2 mit PureLens, `krea2_produkt` (Nutzerentscheid 05.10. nach Stapeltest 2 Phase B: PureLens gewann 4 von 6 Produktmotiven) | 1:1 / 4:5 |
| Handwerk / Technik (Werkstatt, Schaltschrank) | Krea 2 mit PureLens, `krea2_produkt` (Nutzerentscheid 05.10., Phase B: 5 von 6) | 3:2 (1216x832) |
| Gastro / Food | Z-Image-Turbo (nicht im A/B geprüft) | 4:5 (896x1152) |
| Menschen / Portrait SFW | Krea 2, `krea2_turbo_t2i` (Fototest 28.09.: 4 von 4) | 4:5 (896x1152) |
| Lichtstimmung laut Prompt (Golden Hour, Blue Hour) | Qwen-Image-2512 | 1216x832 / 896x1152 |
| Englischer Text im Bild | Qwen-Image-2512 (deutsch kippt, Typografie im Layout) | nativ 1328x1328 |
| Vorhandenes Bild gezielt ändern | Qwen-Image-Edit-2511 | Format aus dem Eingangsbild |
| Flachgrafik / Icon / Spielasset (freistehend) | Z-Image-Turbo + BiRefNet-Matting | 1:1, Cutout siehe unten |
| Anime / Illustration | JANKU v5 + vier Stil-LoRAs, `janku_t2i` (Danbooru-Tags, seit 25.09. Erste Wahl) | 832x1216 (seit 03.10., Stufe 2 auf 1248x1824), Ganzkörper nie quadratisch |
| Anime für Kundenmaterial, abstrakte Konzepte (etwa `fractal art`) | WAI-illustrious v17, `illustrious_t2i` | 960x1664 |
| NSFW realistisch | CyberRealistic Z-Image v7 (nur Nutzer, siehe Leitplanke) | wie Z-Image |
| Upscale 2x | 4x-UltraSharp + Z-Image als Refiner | Eingang bis ~1 MP |
| Kinobanner / Key-Art 21:9 mit Titelfläche | Krea 2, `krea2_kinobanner` (Workflow 14): Detail 1.0, Stimmung standardmäßig an (Blindtest K4, Entscheid 03.10.), `--no-mood` für neutrale Motive; Z-Image über `zimage_kinobanner` (14b) als Alternative | 1568x672 (Z-Image 1680x720) |
| Icon-Serie im Stil eines abgenommenen Icons, freigestellt | Qwen-Image-Edit-2511 + BiRefNet, `qwen_edit_icon_set` (Referenz-Icon als Eingang) | Format der Vorlage, 1024x1024 |
| UI-Flächen (Kartenrahmen, Kartengrund) nach abgenommener Vorlage | Qwen-Image-Edit-2511, `qwen_edit_ui` mit gespiegeltem Zweitausgang; Rahmen ohne Vorlage: Krea 2 | 1024x1024 |
| Sprite-Bogen (eine Figur in drei Posen, Draufsicht) | Krea 2 aus Text, `krea2_sprites` (Workflow 18) mit dem Gerüst der Vertragsprompts; Varianten eines abgenommenen Bogens: Qwen-Edit über 05 mit denoise 0.8 | 1536x1024, drei Zellen |
| Nahtlose Kachel aus vorhandener Textur | kein Modell: `scripts/seamless_tile.py` (varianzerhaltend), in der Oberfläche `seamless_tile` (Workflow 19, linear) | Format der Vorlage, Workflow 19 fest 1024 |

Seit dem blinden Fototest vom 2026-09-28 (16 Prompts, vier Modelle, Nutzerentscheid 2026-10-03)
rechnet Architektur auf Qwen-2512 in Qualitätseinstellung, Produkt, Handwerk und Portrait auf
Krea 2. Z-Image-Turbo lag dort nur bei 3 von 16 Prompts vorn und ist nur noch die schnellste
Wahl. Krea hängt stark am LoRA-Stapel: Stapeltest 2 setzte Detail 0.5 und Afterlight 0.35 als
Standard, für Produkt und Handwerk kommt PureLens dazu (`krea2_produkt`). Zuvor galt
Z-Image als Erstwahl nach einem A/B gegen FLUX-schnell vom 2026-08-27, beurteilt von einem Agenten. Landschaft übernimmt seit dem Blindtest vom 2026-09-28 Qwen-2512 in
Qualitätseinstellung (8 von 16 Prompts, Krea 5, CyberRealistic 2, Z-Image 1). Am 2026-09-19 wurde der Bestand
auf diese fünf Modellfamilien konsolidiert: die Freistell-Kette läuft auf Z-Image (gleiche
Kantenqualität wie mit FLUX, hält sich zusätzlich an "no shadow"), dramatisches Licht kommt
von Qwen, ein echter Negativ-Prompt existiert nur noch bei Illustrious. Zahlen und
Vorab-Tests in learnings.md.

**Workflow nach Bedarf wählen:**
- `zimage_turbo_t2i.api.json`: **schnellste Wahl** (bis 03.10.2026 Default für Architektur, Produkt,
  Handwerk und Portrait, jetzt Qwen beziehungsweise Krea, siehe Tabelle). Z-Image-Turbo bf16, 8 Steps,
  cfg 1.0, `res_multistep`/simple, shift 3.0, 12 bis 17 s je Bild. Kein Negativ-Prompt
  (ConditioningZeroOut). Modelle: `z_image_turbo_bf16.safetensors`, `qwen_3_4b.safetensors`,
  `ae_zimage.safetensors`. `DETAIL_LORA` (Z-Image-Detail-Slider) steht seit 03.10.2026 auf 0.6
  (Nutzerurteil: 0.6 gewann 3 von 4 Vergleichen gegen 0.3 und ohne), kostet gemessen im Mittel
  14 Prozent Helligkeit, für helle Motive auf 0.3 oder 0 stellen.
- `zimage_cutout.api.json`: **Standard für freistehende Motive** (Figur, Symbol, Icon,
  Produkt ohne Hintergrund). Ein Graph, ein `comfy_generate.py`-Aufruf: Z-Image generiert,
  BiRefNet-Matting stellt direkt im selben Lauf frei, Ausgabe ist ein fertiges RGBA-PNG.
  Prompt weiterhin mit `flat plain pure green background, no shadow` bauen, etwa 20 s.
- `birefnet_matte.api.json`: nur freistellen, für ein vorhandenes Bild (`--image`), 2 bis 4 s.
- `upscale.api.json`: UltimateSDUpscale mit 4x-UltraSharp und Z-Image-Turbo als Refiner
  (denoise 0.2, Clip Skip 2 im Graphen). **Bei Porträts denoise auf 0.05 setzen und wissen, was
  man kauft:** die ESRGAN-Stufe hebt das Korn auf der Haut um ein Drittel, das Auge liest es als
  ältere Haut. Neue Falten entstehen nicht (learnings.md, 22.09.2026). 4x-UltraSharp ist von den
  drei vorhandenen Upscalern der mildeste. NMKD-Superscale legt einen Rausch-Teppich auf die Haut
  und ist raus, 1xSkinContrast vergrößert gar nicht und verliert überall Detail.
  Prompt mit `score_9, score_8_up, score_7_up,` beginnen und das Motiv beschreiben.
  1024 auf 2048 in 37 s. Für 4x `upscale_by` auf 4.0.
  **Herkunft wird mitgeschrieben:** jeder Lauf mit `--image` (Upscale, Edit, Freistellen) hängt seit
  dem 22.09.2026 die Chunks `gallery_src_key`, `gallery_src_model`, `gallery_src_prompt` und
  `gallery_src_method` (`detailpass`, `bearbeitet`, `freigestellt`) ans Ergebnis. Ohne sie steht ein
  Detailpass in der Bildgalerie als eigenes Bild des REFINERS, also unter Z-Image, obwohl die Basis
  etwa von WAI-illustrious stammt. Der Graph im PNG bleibt unangetastet, die Funktion `stamp_source`
  in `comfy_generate.py` schreibt nur zusätzliche Chunks.
- `qwen_2512_t2i.api.json`: Qwen-Image-2512 mit 2-Step-Turbo-LoRA für englischen Text im Bild
  und für Lichtstimmung laut Prompt, 13 bis 30 s. Deutscher Text kippt reproduzierbar
  (learnings.md), kein Negativ-Prompt.
- `qwen_edit_2511.api.json`: Qwen-Image-Edit-2511 mit 4-Step-Lightning-LoRA, Eingangsbild über
  `--image`, Anweisung als Befehl im Prompt. Hält Form, Licht und Umfeld, 26 bis 33 s.
- `zimage_nsfw_t2i.api.json`: wie `zimage_turbo_t2i`, aber mit CyberRealistic Z-Image v7 (BF16)
  im CHECKPOINT-Knoten. Nur für den Nutzer selbst, siehe Leitplanke. INT8-Fassungen laufen auf
  ComfyUI 0.25.1 nicht, auf 0.36.0 sind sie ungetestet. `DETAIL_LORA` ebenfalls auf 0.6 (seit 03.10.2026),
  dunkelt hier stärker ab (bei 0.6 um 21 Prozent, bei 0.3 um 8 Prozent).
- `illustrious_t2i.api.json`: WAI-illustrious v17 für Anime, ZWEISTUFIG (Basis nach `anime`,
  danach UltimateSDUpscale mit demselben Checkpoint als Refiner nach `anime-detail`, seit 04.10.2026
  in einer Kachel: Kachel 4096, `force_uniform_tiles` aus, weil 1024er-Kacheln leichte Streifen durch
  die Bildmitte zogen, Nahttest 2 in learnings.md). Mehr Detail
  bringt der Knoten DETAIL_LORA (StS Illustrious Detail Slider) über `--detail-strength 3.0`:
  Feinstruktur mehr als verdoppelt, sichtbar an Haar, Stoffmuster und Hintergrund, Arbeitspunkt
  3.0, ab 4.5 zerfällt der Hintergrund (Messung 22.09.2026 in learnings.md). Die frühere Aussage
  "Detail-LoRAs bringen nur zwei Prozent" beruhte auf Stärke 1.0 und ist widerlegt. Nebenwirkung:
  der Slider macht die Pose dynamischer. Etwa 55 s, Knoten UPSCALE per Bypass abschaltbar.
  Weicht von der Autorvorgabe für v17 ab (15 bis 30 Steps, 1024x1344, Hires 1,5 bei Denoise 0,35
  bis 0,5, nur drei Qualitäts-Tags, kurzes Negativ mit `nsfw`); autorkonform trifft das Kimono-
  Motiv die Vorlage deutlich besser, Vergleich in learnings.md vom 23.09.
  Danbooru-Tags statt Sätze,
  40 Steps, cfg 7.0, `euler_ancestral`/normal, 960x1664, VAE steckt im Checkpoint. Embeddings
  `lazyneg`, `lazypos`, `lazyhand` liegen bereit (`embedding:lazyneg` im Prompt).
- `janku_t2i.api.json`: JANKU v5 (Illustrious, Checkpoint trägt Gesicht, Augen und Haar) mit dem
  Stil-Stapel des Civitai-Autors akizukirei608: USNR 0,5, WSSKX 0,3, Smooth Booster v5 0,65,
  Stabilizer 0,25 (TRT und die Charakter-LoRA fehlen bewusst). Seit 25.09. Autorwerte der
  Modellseite: 30 Steps, CFG 5, Euler a/simple, dann Hires 1,5-fach (RealESRGAN, KSampler Denoise
  0,4), nach `janku-detail`. Stufe 1 seit 03.10.2026 in 832x1216 statt 1024x1536 (Ergebnis
  1248x1824): bei Civitai-Vorlagen mit Füßen und Händen im Bild gewann 832x1216 mit derselben
  Stufe 2, 1024x1536 verlor dort jede Gruppe mit sechs oder sieben Zehen und doppelten Füßen. Der
  Sieg der Autorwerte am 25.09. kam von der neuen Stufe 2, nicht von der Größe: das damalige alte
  Rezept rechnete Stufe 2 noch 2-fach bei 0,5 (karras).
  Positiv mit `embedding:lazypos, ` vor Danbooru-Tags, `--negative` immer mitgeben (ohne ist es
  leer), Vorschlag steht im Knoten NEGATIVE_PROMPT: `embedding:lazyloli` immer (Autor, v5),
  `embedding:lazynsfw` nur für jugendfreie Motive, sonst streichen. Ganzkörper NIE quadratisch,
  im Quadrat brach die Anatomie (25.09.). Landschaft ohne Figuren: `scenery, no humans`. KEINE Gesichtskorrektur: FaceDetailer malte auf
  JANKU Male und Farbflecken ins Gesicht, die Hires-Stufe war sauber (learnings.md 24.09.).
  Marcus fand das Ergebnis bei Civitai 101824003 "super".
- `illustrious_realism_t2i.api.json` (seit 30.09.2026): Illustrious Realism v4, ZWEISTUFIG nach dem
  UI-Workflow "Illustrious Realism v4". Basis: KSamplerAdvanced, 25 Steps, cfg 6, `dpmpp_2m_sde`/karras,
  clip skip 2, 832x1216, nach `illustrious-realism`. Hires: 4x-UltraSharp, dann 1xSkinContrast, lanczos
  0,32 und Vielfaches von 64 (1024x1536), KSampler 20 Steps, cfg 7, `dpmpp_2m_sde`/karras, denoise 0,45,
  Seed fest 10, nach `illustrious-realism-detail`. Der UI-Workflow nutzte 4x_NMKD-Superscale (gelöscht),
  hier 4x-UltraSharp. So gewann Hires im Blindtest vom 30.09. alle drei Motive gegen nur Basis und gegen
  FaceDetailer (learnings.md), Sicherung der reinen Basisvorlage `.bak-20260930`. Vorher rechnete die
  Galerie das Modell über `illustrious_t2i` mit WAI-Werten und UltimateSDUpscale 2-fach, das machte viele
  Bilder kaputt. Negativ mit `embedding:lazyloli` vorn. Keine Altersangabe mit "years old" und kein
  "mature female": daraus wurden Menschen über 60, "years young" geht.
- `krea2_turbo_t2i.api.json`: Krea 2 Turbo (fp8) mit sechs LoRA-Knoten. Standard sind `DETAIL_LORA`
  0.5 (seit 27.09.2026) und `AFTERLIGHT_LORA` 0.35 (seit 03.10.2026: im blinden Stapeltest 2 gewann
  Afterlight 14 von 18 Foto-Gruppen, 0.35 neunmal, Detail 0.5 allein keine, auch bei Tageslicht 5
  von 6). Die Galerie rechnet Krea in allen Zielen außer Kinobanner und Produkt und Handwerk über
  diese Vorlage. „Neu generieren“, Anpassen und Variationen behalten seit dem 05.10.2026 das Ziel
  des Ausgangsbilds (Nutzerentscheid): ein Bild aus `produkt/` rechnet mit Krea über
  `krea2_produkt`, eins aus `banner/` über die Kinobanner-Vorlage. Für Stile
  über `STYLE_LORA` (Sticker, Charakterbogen) `AFTERLIGHT_LORA` auf 0 setzen, dort ungetestet. Die
  übrigen Knoten stehen auf 0.0 und sind damit aus:
  `WARM_LORA` (Helligkeit und Wärme, +0.5 bis +1.5, einziger Hebel ohne Verlust an Feinstruktur),
  `DETAIL_LORA` (0.5 bis +2.0), `AFTERLIGHT_LORA` (goldenes Gegenlicht, 0.35 bis 1.0) und
  `STYLE_LORA` für vier Stile mit Trigger-Wort (sticker, Character design, pop-up book,
  Anatomy-reveal). Vier Knoten auf 0.0 sind nachgemessen neutral. Diese LoRAs laufen NUR auf
  Krea 2, die aus 09 passen nicht und umgekehrt, ein Fehlgriff bleibt stumm. Dazu `REALISM_LORA`
  (-1.0 bis +1.0, negativ Illustration, positiv Foto) und `WEIGHT_LORA` (-2.0 bis +2.0,
  Körperfülle, sauberster Regler der Sammlung). Sechs Knoten auf 0.0 sind nachgemessen neutral.
- `krea2_produkt.api.json`: **Produkt und Handwerk** (seit 05.10.2026). Graph von `krea2_turbo_t2i`,
  Knoten 19 heißt `PURELENS_LORA` und trägt PureLens 1.0 statt des Stil-Platzhalters, Ablage
  `produkt/produkt`. Das Auslösewort `purelens` steht als `_meta.trigger` am POSITIVE_PROMPT:
  `comfy_generate.py` und `upscale.py` setzen es genau einmal vorn ein, die Galerie speichert den
  Prompt ohne es, damit ein Motiv modellübergreifend vergleichbar bleibt. Im Stapeltest 2 Phase B
  gewann PureLens Produkt 4 von 6 und Handwerk 5 von 6, Porträt nur 1 von 6: Porträts bleiben bei
  `krea2_turbo_t2i`. Eine eigene Oberfläche gibt es noch nicht, in Workflow 10 geht es von Hand
  (`STYLE_LORA` auf `purelens_krea2` mit 1.0, Prompt mit `purelens, ` beginnen).
- `qwen_2512_landschaft.api.json`: **Erste Wahl für Fotolandschaft** (seit 28.09.2026, UI
  17-landschaft). Graph von `qwen_2512_t2i` mit TURBO_LORA 0.0, 30 Steps, cfg 4.0, 1344x768, etwa
  100 s je Bild. Gewann den Blindtest vom 28.09. (16 Prompts, vier Modelle, gleiche Seeds) mit 8
  Siegen vor Krea (5), CyberRealistic (2) und Z-Image (1). Prompt: Vorder-, Mittel- und Hintergrund
  je ein Satz, Lichtrichtung, Brennweite. Schnell geht es mit Krea 2 im selben Format (11 s).
  Nicht bitgenau reproduzierbar: ein Kontrolllauf mit identischem Graphen wich im Mittel um 2 von
  255 ab, bei gleicher Komposition.
- `krea2_kinobanner.api.json`: **Kinobanner 21:9** (seit 28.09.2026, UI 14-kinobanner). Graph von 10
  in 1568x672 mit DETAIL 1.0. Afterlight 0.35 und Warm 0.5 sind die **Stimmung** und stehen als
  `STIMMUNG_AFTERLIGHT` und `STIMMUNG_WARM` seit 03.10.2026 standardmäßig an (Blindtest K4: die
  Fassung ohne Stimmung gewann keines von sechs Motiven, drei gleich). `comfy_generate.py --no-mood`
  setzt sie auf 0: bei Produkt, Architektur, klarem Tageslicht und überall, wo Ränder scharf
  bleiben sollen (die Stimmung gibt Kontrast und Unschärfe hinten und außen). Die Titelfläche muss
  der Prompt bestellen (Motiv im rechten Drittel, links benennen, was dort ruhig steht). Kein
  "neon sign" und ähnliche Schilder bestellen, sonst steht Fantasietext im Bild. Qwen-2512 kann kein
  21:9. Ablage `banner/banner_*`, die Galerie ordnet über den Ordner zu.
- `zimage_kinobanner.api.json`: **Kinobanner auf Z-Image** (UI 14b-kinobanner-zimage), Alternative.
  Graph von 09 (Luneva 0.5, Detail 1.0) in 1680x720, einem trainierten Format von Z-Image. Verlor im
  Blindtest alle sechs Motive gegen Krea.
- `krea2_sprites.api.json`: **Sprite-Bogen** (seit 28.09.2026, UI 18-sprites). Graph von 10 in
  1536x1024, eine Figur in drei Zellen (Stand, Schritt links, Schritt rechts) auf flachem Grün. Prompt
  nach dem Gerüst der Aschekrone-Vertragsprompts (GAME PIECE, VIEW straight top-down, POSES, feste
  Größe mit grünem Rand). Ausrüstung je Zelle bestellen, dünne Teile als dicke Form beschreiben.
  Zweiter Ausgang `sprite-gespiegelt`: Zelle 3 ist das Spiegelbild von Zelle 2, für Tiere und
  Figuren ohne einseitige Ausrüstung (Krea malt Vierbeiner als Stand, Trab, Stand). Vierbeiner:
  Beine ausdrücklich seitlich aus dem Umriss bestellen, das hielt bei Hund und Wolf, beim Maultier
  verdecken Lasten die Vorderbeine. Krea malt statt #00ff00 ein Grün, dessen Ton je Bogen schwankt,
  den Farbschlüssel am Rand messen. Qwen-2512 aus Text malt aufrechte Tiere und Ansichten statt
  Draufsicht. Qwen-Edit mit einem Gate-Bogen als Vorlage drehte neue Figuren zu Vorder-, Seiten- und
  Rückansicht, taugt über 05 mit denoise 0.8 nur für Varianten eines abgenommenen Bogens.
- `seamless_tile.api.json`: **Kachel nahtlos machen**, ohne Modell (seit 28.09.2026, UI 19-kacheln).
  Verschiebt die Textur um die halbe Kante (LayerStyle ImageShift) und überblendet im Nahtkreuz das
  unverschobene Original, das dort durchgehend ist. Fest 1024 px. Linear, verliert im Übergang rund
  ein Fünftel des Feinkorns. Für Agentenläufe und fertige Assets deshalb `scripts/seamless_tile.py
  <eingang> <ausgang>` mit dem Python von ComfyUI: dasselbe Verfahren varianzerhaltend, jedes Format,
  Korn unverändert. Nur für Texturen ohne erkennbare Formen, Steine und Fugen schienen doppelt durch.
  Prüfung als 3x3-Wiederholung, vierfach aufgehellt. Das Kreuz mit Z-Image neu zu rechnen hinterließ
  ein sichtbares Gitter, die Qwen-2512 Fun ControlNet Union lädt in ComfyUI 0.36 nicht.
- `qwen_edit_icon_set.api.json`: **Icon-Serie nach Referenz** (seit 27.09.2026, UI 15-icon-set).
  Qwen-Edit-2511 tauscht im abgenommenen Referenz-Icon (auf hellgrauem Grund, per `--image`) nur das
  Motiv aus, BiRefNet stellt danach frei. Prompt "Replace the <X> with <Y>. Keep exactly the same
  material, light, size, position and background." Farben als matten Stoff beschreiben ("warm gold"
  wird metallisch mit Kante, "sunflower yellow" zitronengelb), weichen Glanz ausdrücklich bestellen.
  Erster Testsatz Blumilie (Vinyl), alle acht Motive bei 24 px unterscheidbar, Alpha-Zwischenwerte
  0,4 bis 0,8 Prozent. Z-Image ohne Referenz (01) blieb blasser und verfehlte zwei Motive.
- `qwen_edit_ui.api.json`: **UI-Element nach Referenz** (seit 27.09.2026, UI 16-ui-elemente). Graph
  von 05 plus ein zweiter Ausgang `ui-symmetrisch`, der das linke obere Viertel waagerecht und
  senkrecht spiegelt (exakte Symmetrie wie beim abgenommenen Aschekrone-Rahmen, setzt 1024x1024
  voraus). Für Rahmen den symmetrischen, für Gründe den rohen Ausgang. Farbverschiebungen nicht
  bestellen ("cooler" wurde blau), Striche kommen heller als in der Vorlage. Rahmen aus reinem Text
  trifft Krea, Qwen-2512 wird zu hell und dick. UI-Chrome nur, wo der Stilvertrag des Spiels es
  erlaubt (Blumilie schließt es aus).
- `krea2_namensposter.api.json`: **Standard für Namensposter** (Nutzerwahl 26.09.2026). Krea 2 mit
  Typnosis 1.5 im STYLE_LORA, dazu DETAIL 1.0, AFTERLIGHT 0.35, WARM 0.5, 1216x832. Prompt-Gerüst
  und Stolpersteine in der Notiz des Workflows und in learnings.md: keine Verbote im Prompt, kein
  "soft blurred background", Nebenfiguren links vom ersten Buchstaben, Voxel-Schrift auf Qwen.
- `krea2_slider_sweep.api.json`: rechnet denselben Prompt und Seed fünfmal mit den Stärken -2 bis
  +2 und legt die Bilder über `ImageConcatMulti` nebeneinander in eine Datei. Zum Ausmessen eines
  Reglers, etwa 50 s. Zu prüfende LoRA in allen fünf Knoten STUFE_1 bis STUFE_5 setzen.
- `zimage_cinematic_t2i.api.json`: wie `zimage_turbo_t2i`, aber mit zwei aufgesteckten LoRAs,
  Luneva Cinematic (0.5, Stil und Komposition) und Detail Slider (1.0, bipolar von -2 bis +2).
  Für Doppelbelichtung, Poster, Buchcover, Key-Art. Kein Trigger-Wort, 832x1216, 8 s.
  Achtung Lizenz: Luneva verlangt Namensnennung und verbietet Merges. Beide LoRAs laufen nur
  auf der Z-Image-Architektur, Tabelle in [reference/models.md](reference/models.md).
- `zimage_luneva_t2i.api.json`: **Z-Image in Qualität, zweistufig** (seit 06.10.2026, Kern des
  Luneva Infinite Details Workflows, Civitai 2226355, nur Bordmittel). `--width`/`--height` sind
  die Zielgröße, lange Seite höchstens 2048 (1152x2048, 2048x1152). Stufe 1 rechnet in halber
  Größe nur die Komposition (5 von 30 Schritten), Stufe 2 nach Latent 2x das ganze Bild neu
  (dpmpp_2s_ancestral eta 0.5, 6 Schritte, denoise 0.85), Detail 0.6, etwa 25 s. Pilot mit fünf
  Fototest-Motiven: schlug Standard und Standard plus Detailpass in 4 von 5, Keramik gleichauf,
  Werkbank schlug auch Krea, Studioporträt gleichauf mit Krea (learnings.md, 05.10.2026). Ändert
  die Komposition gegenüber `zimage_turbo_t2i` bei gleichem Seed. Ablage `foto/foto-luneva`.

## Freistellung (transparenter Hintergrund)

Standard seit dem Vergleichstest 2026-08-13 (Details, Zahlen, Bilder in
[reference/learnings.md](reference/learnings.md)): **BiRefNet-Matting statt Chroma-Key.**

```powershell
& "D:\SDKs\Python311\python.exe" "C:\Users\Marcus\.claude\skills\bs-media-image\scripts\comfy_generate.py" `
  --workflow "C:\Users\Marcus\.claude\skills\bs-media-image\workflows\zimage_cutout.api.json" `
  --prompt "<englischer Prompt, Motiv auf flachem Hintergrund>" `
  --negative "" `
  --width 1024 --height 1024
```

Ergebnis ist direkt ein RGBA-PNG (verifiziert 2026-08-13 mit FLUX, 2026-09-19 mit Z-Image:
84,7 % voll transparent, 0,3 % Halbtransparenz). Kein separater `keyout.py`-Lauf mehr nötig.

**Vier Regeln aus dem Vergleich vom 2026-09-22** (vier Motive, beide Wege, Abnahme am
1:1-Ausschnitt durch den Nutzer, Zahlen und Blätter in [reference/learnings.md](reference/learnings.md)):

- **Grund neutral hellgrau, nicht grün.** `isolated on a flat plain light grey background,
  even studio light, no shadow`. Grün färbt halbtransparente Ränder oliv: am Haarsaum sind
  58,7 % der Randpixel grünexzessiv gegen 0,0 % bei Grau.
- **Selbst erzeugen schlägt nachträglich freistellen.** Der flache Grund löst einzelne
  Haarsträhnen und die Zähnung filigraner Blätter, ein Szenenbild durch 02 zerhackt die
  Strähnen und zieht einen Saum der Umgebung mit. Nur bei harten Produktkanten gleichwertig.
- **`--matte-detail` nach dem Rand des Motivs setzen, nicht nach dem Weg.** Viele kleine
  Strukturen (Haar, Fell, Flaum) gewinnen mit GuidedFilter, klare Linien und harte Kanten
  verlieren, dort weicht er die Kante zu einem Glimmen auf. Acht von acht Urteilen fielen so.
  Der Schalter gilt für beide Wege, Voreinstellung ist aus.
- **Halbtransparenz kann diese Kette nicht.** Die Node setzt nur Alpha und entfernt die
  Grundfarbe nie aus dem RGB, Flaum, Glas und Rauch behalten den alten Hintergrund. Und die
  Maske rechnet immer bei 1024 x 1024: größer erzeugen bringt keine feinere Kante, für große
  Freisteller bei 1024 mattieren und danach durch 03 schicken.

- **Fallback `tools/keyout.py` (Chroma-Key, Rand-Flood-Fill):** nur wenn kein ComfyUI läuft
  (offline) oder als schneller Vergleichslauf. Braucht dafür einen flachen grünen Hintergrund
  im Motiv (Prompt weiterhin so bauen).
- **Grenze, ehrlich benannt:** BiRefNet ist kein garantierter Schattenentferner. Ein kräftiger,
  visuell auffälliger Schatten (z. B. ein gerendertes Flat-Design-Langschatten-Element) wird
  teils als Motivteil erkannt und bleibt stehen (Test-Befund V4, am 2026-08-13 bei der
  Materialisierung dieses Workflows mit einem eigenen Testbild reproduziert). Verify-Loop
  (Schritt 4) bleibt deshalb Pflicht, auch bei BiRefNet-Ausgaben.
- Voraussetzung ist einmalig installiert: BiRefNet-General (MIT, kommerziell frei) unter
  `ComfyUI\models\BiRefNet\BiRefNet-General`, Node-Paket `comfyui_layerstyle` (bereits vorhanden).

## Zweiter Weg: Codex (ohne laufendes ComfyUI)

Codex kann Bilder auch headless erzeugen, über sein eingebautes `image_gen`-System-Skill
(verifiziert 2026-08-11, taucht in der Plugin-Liste nicht auf):

```powershell
& "D:\SDKs\Nodejs\node.exe" "D:\SDKs\NodeGlobal\node_modules\@openai\codex\bin\codex.js" exec -s workspace-write -C "<zielordner>" --skip-git-repo-check "<englischer prompt>"
```

Codex legt das Bild unter `C:\Users\Marcus\.codex\generated_images\<id>\` ab und kopiert
es zusätzlich in den Zielordner. Ein Lauf dauert ein bis drei Minuten (Timeout großzügig
setzen). Mit `-i "<pfad-zum-referenzbild>"` hängt man ein Referenzbild an, das ist der Weg
zu Stil-Konsistenz. Transparente Hintergründe im Prompt ausdrücklich verlangen. Kein
API-Key nötig, läuft über das ChatGPT-Abo, verbraucht aber dessen Wochenkontingent. Der
Verify-Loop (Schritt 4 unten, Vision-Pflicht) und die Leitplanke gelten identisch.

**Entscheidungsregel:** ComfyUI ist lokal, kostenfrei und beliebig oft nutzbar, dafür muss
der Prompt zum Modell passen (siehe Vertical→Modell und learnings.md). Codex kostet
Wochenkontingent, ist dafür prompt-treuer, nimmt Referenzbilder an und braucht kein
laufendes ComfyUI. Default bleibt ComfyUI; kurz vor einem Kontingent-Reset (das
Wochenkontingent verfällt sonst ungenutzt) oder wenn Prompt-/Referenztreue wichtiger ist
als Tempo, Codex nutzen.

## Nachbau nach Vorlage (Civitai, Web): bindend

Eingeführt 22.09.2026, nachdem beides dreimal reklamiert werden musste.

1. **Original-Prompt holen, nicht selbst schreiben.** Die API v1 (`/api/v1/images`) liefert
   `meta: null`, das heißt NICHT, dass kein Prompt existiert. Vollständig kommen Prompt,
   Negativ, Seed, Steps, CFG, Sampler und alle Ressourcen mit Stärke über
   `https://civitai.com/api/trpc/image.getGenerationData?input={"json":{"id":<bildId>}}`.
   Erst wenn auch dort `prompt` leer ist (der Ersteller hat ihn entfernt), einen eigenen
   Prompt bauen und das im Ergebnis ausdrücklich so benennen.
   A1111- und Forge-Syntax vorher entfernen: `<lora:name:0.5>` und `[text:7]` versteht ComfyUI
   nicht, beides landet als Textrauschen im Prompt. Die LoRAs stattdessen als Knoten laden.
2. **Vorlage in die Galerie.** Das Original als PNG nach
   `Data\Images\referenz\civitai\civitai_<bildId>.png`, mit einem kleinen ComfyUI-Graphen im
   Chunk `prompt`, der Checkpoint, LoRAs mit Stärke, Prompt, Seed und Steps trägt. So zeigt die
   Galerie Modell und Prompt der Vorlage an. Vorlage: `civitai_<id>.png` in diesem Ordner.
   Die Knotentitel sind Schnittstelle zur Galerie: `CIVITAI_CHECKPOINT` für den Checkpoint und
   `CIVITAI_LORA` für jede LoRA. Nur mit diesem Titel bleibt der Civitai-Anzeigename einer LoRA
   ganz stehen, ohne ihn schneidet die Galerie alles vor dem letzten `/` als Ordner ab (aus
   "Stabilizer IL/NAI/CK" würde "CK"). Beim Checkpoint gilt der Schutz noch nicht, ein `/` im
   Namen würde dort abgeschnitten. Modell und LoRAs nach `modelType` der Civitai-Ressourcen trennen.
3. **Jeden Lauf gruppieren, beim Generieren.** `--group civ<bildId> --group-ref <Vorlage>` an
   `comfy_generate.py`: das Ergebnis landet in `D:\Repos\comfy-gallery\data\groups.json`, alle
   Läufe eines Motivs stehen in der Galerie als EINE Kachel, V vergleicht sie nebeneinander.
   Ohne Gruppe fasst die Galerie nur Läufe desselben Graphen und Vergleiche desselben Prompts
   über mindestens ZWEI Modelle zusammen, drei Anläufe auf Krea 2 stünden also einzeln da.
   Gilt auch für Serien ohne Vorlage (Regler-Sweeps, Varianten): dann nur `--group <name>`.
   **Eine Gruppe je Motiv, nie je Person oder Projekt.** Die Namensposter lagen bis 28.09. je
   Kind in einer Gruppe (`ideogram-<name>`), Fußball, Monstertruck, Bausteine und Superhelden
   gemischt, ein Bündel hatte 37 Bilder. Seither `namensposter-<name>-<motiv>` (etwa
   `namensposter-<name>-fußball`), Sticker `sticker-<name>`.
4. **Stil-LoRAs der Vorlage prüfen, bevor man den Checkpoint verdächtigt.** Bei den 16
   Vorlagen vom 22.09. kam der Look fast immer aus einer Stil-LoRA (AURENTH, Origami Style,
   ParchartXL, Dreamscape), der Original-Prompt allein trifft dann nicht.

## Ablauf

0. **Engine sicherstellen.** `powershell -File scripts\ensure_comfyui.ps1` ausführen
   (idempotent: startet ComfyUI nur, wenn es nicht schon läuft).
1. **Anforderung klären.** Motiv, Vertical, Seitenverhältnis, Zielpfad,
   Marken-/Stilvorgaben. Bei echter Mehrdeutigkeit kurz rückfragen, sonst Annahme
   benennen und weiter.
1a. **Galerie-Learnings einholen.** In der Bildgalerie (`D:\Repos\comfy-gallery`) hakt der Nutzer
   unter einer Notiz „als Learning übernehmen“ an. Nur diese Einträge kommen hier an, nichts
   wird nach Sternen mitgelesen. Erst die offenen holen (Liste mit `key`, `model`, `family`,
   `prompt` als Auszug, `rating`, `note`, `at`, `rev`, älteste zuerst), dann SOFORT als
   übernommen melden, erst danach einarbeiten. Die Meldung trägt je Eintrag `key` und `rev`, der
   Server markiert nur unveränderte und noch offene. So landet nichts doppelt, wenn zwei Läufe
   parallel holen. Ebenso wird keine Fassung eingefroren, die hier nie gelesen wurde.

   ```powershell
   $offen = @(Invoke-RestMethod http://127.0.0.1:8189/api/learnings)
   $claim = Invoke-RestMethod http://127.0.0.1:8189/api/learnings/done -Method Post `
     -ContentType "application/json; charset=utf-8" `
     -Body (@{ items = @($offen | ForEach-Object { @{ key = $_.key; rev = $_.rev } }) } | ConvertTo-Json -Depth 4)
   $claim.done      # nur diese Schlüssel einarbeiten
   $claim.skipped   # seitdem geändert (kommt beim nächsten Lauf neu) oder schon von einem anderen Lauf übernommen
   ```

   Ist `$offen` leer, entfällt die Meldung. `charset=utf-8` nicht weglassen: Windows PowerShell
   5.1 schickt sonst Latin-1, Schlüssel mit Umlaut kämen nicht an.

   Jeden Eintrag aus `$claim.done` in [reference/learnings.md](reference/learnings.md)
   einarbeiten: datierter Abschnitt, Belegbild mit seinem Schlüssel nennen (das schützt es
   zugleich vor `cleanup.py`), die Notiz des Nutzers sinngemäß, nicht als Rohzitat. Einträge mit
   `explizit: true` kommen ohne Prompt (Leitplanke unten): von ihnen nur den technischen Befund
   der Notiz übernehmen (Modell, Einstellung, Fehlerbild), nie eine Beschreibung des Bildinhalts.
   Das Bild selbst nicht öffnen. Betrifft ein Eintrag ein Modell, die Stolperfalle für dessen Karte
   in `D:\Repos\comfy-gallery\models.json` nur VORSCHLAGEN (im Ergebnis nennen), nicht selbst
   schreiben: models.json pflegt der Koordinator der Galerie. Das Panel der Galerie zeigt nach
   der Meldung „übernommen am …“.

   Einträge mit `key` `reihe:<name>` sind das Fazit einer Testreihe aus der Ansicht Pipeline, kein
   Bild: statt `model` und `prompt` tragen sie `series` (Name der Reihe, wie der Ordner unter
   `out\_tests\<name>\`), `images` (Zahl ihrer Bilder) und `note` (das Fazit). `explizit: true`
   steht dort, wenn ein Bild der Reihe nicht sicher ist, dann gilt dieselbe Regel wie oben. In
   learnings.md den Abschnitt nach der Reihe benennen und als Beleg den Testordner oder den
   Testplan nennen, keinen Bildschlüssel. Modellaussagen daraus wie oben nur als Vorschlag für die
   Karte melden.

   Antwortet 8189 nicht, läuft die Galerie nicht: den Schritt überspringen und das im Ergebnis
   sagen, die Einträge warten dort bis zum nächsten Lauf.
1b. **Recall (Gedächtnis nutzen).** Vor dem Promptbau `reference/learnings.md` +
   `reference/models.md` lesen (Modellwahl + bewährte Prompt-Muster fürs Vertical),
   dann prüfen, ob es schon ein bewährtes Bild gibt:

   ```powershell
   & "D:\SDKs\Python311\python.exe" "C:\Users\Marcus\.claude\skills\bs-media-image\scripts\ledger.py" find --vertical winzer --min-rating 4
   ```

   Treffer? Das gelistete PNG enthält seinen Workflow nativ in den Metadaten:
   in ComfyUI ziehen lädt den Graph, oder Prompt/Seed aus der Zeile als Startpunkt
   übernehmen und gezielt variieren, statt bei null anzufangen.
2. **Prompt bauen.** Konkret, fotografisch: Subjekt, Setting, Licht, Optik
   (z.B. "35mm, golden hour"), Stimmung. Für Schärfe `sharp focus, fine detail`
   rein. **Achtung:** `soft, haze, shallow depth of field, bokeh` machen das Bild
   bewusst weich, nur nutzen wenn gewollt, sonst in den Negative-Prompt. Kein
   Markenname ohne Grund. Einen Negativ-Prompt gibt es nur bei Illustrious und dem
   Upscale, die Z-Image- und Qwen-Graphen laufen mit cfg 1.0 ohne Negativ-Zweig.
3. **Generieren.** Skript aufrufen (PowerShell):

   ```powershell
   & "D:\SDKs\Python311\python.exe" "C:\Users\Marcus\.claude\skills\bs-media-image\scripts\comfy_generate.py" `
     --workflow "C:\Users\Marcus\.claude\skills\bs-media-image\workflows\zimage_turbo_t2i.api.json" `
     --prompt "<englischer Prompt>" `
     --width 1216 --height 832
   ```

   Für Text im Bild oder Lichtstimmung `--workflow ...\qwen_2512_t2i.api.json`. Für ein
   freistehendes Motiv (Figur/Symbol/Icon ohne Hintergrund) `--workflow ...\zimage_cutout.api.json`
   (siehe Abschnitt Freistellung), liefert direkt ein RGBA-PNG. Für das Ändern eines vorhandenen
   Bilds `--workflow ...\qwen_edit_2511.api.json --image <bild.png>`. Optional `--checkpoint`,
   `--lora`, `--lora-strength`, `--seed`, `--steps`. Stdout des Skripts = Pfad des Bilds in der
   Bildbibliothek (`Text2Img\<workflow>\`), eine zweite Kopie entsteht nicht mehr. `--out`
   ist optional (Hardlink innerhalb der Bibliothek, sonst Kopie) und beim Iterieren wegzulassen.
   Nach `out\` nimmt das Skript kein `--out` an (wäre eine Zweitkopie auf C:), dort liegen nur
   abgeleitete Dateien wie Vergleichsblätter; A/B-Läufe arbeiten mit den Bibliothekspfaden.

   **Vergleichsblatt montiert? Dann `modelle.json` daneben legen.** Blätter liegen unter
   `out\<thema>\` (etwa `out\vergleich\`), die `modelle.json` im selben Ordner. Eine Montage trägt keine
   ComfyUI-Metadaten, die Modellnamen stehen nur als Beschriftung im Bild. Die Galerie liest
   deshalb eine Datei `modelle.json` im selben Ordner und zeigt das Blatt danach unter jedem
   beteiligten Modell. Modellnamen genau wie in der Galerie schreiben (Z-Image-Turbo, Krea 2
   Turbo, CyberRealistic Z-Image v7, Flux.1 Schnell, Chroma1 HD). Gilt für den ganzen Ordner,
   `files` übersteuert je Datei, denn ein Ordner enthält oft mehrere Läufe:

   ```json
   {
     "models": ["Z-Image-Turbo"],
     "note": "LoRA-Versuche auf Z-Image-Turbo",
     "files": {
       "vergleich_flux.jpg": {
         "models": ["Flux.1 Schnell", "Z-Image-Turbo"],
         "note": "Original aus Flux.1 Schnell gegen Z-Image pur",
         "sources": ["images/library/landschaft/original.png", "images/Text2Img/foto/foto_2026-09-21_00007_.png"]
       }
     }
   }
   ```

   `sources` ist optional und nennt die Index-Schlüssel der gezeigten Einzelbilder in der
   Reihenfolge von links nach rechts, Vorlage zuerst. Das Blatt selbst hat keinen Prompt, und
   ein gemeinsamer wäre falsch, sobald ein altes Tag-Modell gegen ein neues Satz-Modell steht:
   über die Schlüssel zeigt die Lightbox eine Zeile "Einzelbilder" und springt zum Bild samt
   seinem eigenen Prompt. Der Schlüssel ist `images/` plus der Pfad unterhalb der Bildwurzel,
   mit Schrägstrichen.
4. **Verify-Loop (Pflicht).** Das erzeugte PNG mit dem `Read`-Tool öffnen
   (Vision) und gegen die Anforderung prüfen:
   - Motiv korrekt und vollständig?
   - Seitenverhältnis/Ausschnitt wie gewünscht?
   - Artefakte (verformte Hände/Objekte, Doppelungen, Matsch)?
   - Text im Bild lesbar/erwünscht? (Nur Qwen setzt Text zuverlässig, und nur englischen.)
   - Marken-/Stilfit?
   Bei Nichtbestehen: Prompt/Seed/LoRA-Stärke nachschärfen, neu generieren.
   Max. ~4 Iterationen, dann Zwischenstand zeigen und nachfragen.
5. **Verwenden / Ablage.** Erst nach bestandener Prüfung verwenden. Das Bild bleibt in der
   Bildbibliothek (`Text2Img\<workflow>\`), die Ablage nach Zweck erzeugt dort keine
   zweite Kopie:
   - persönliche Keeper → Hardlink nach `D:\Apps\Stability Matrix\Data\Images\library\<vertical>\`
     (landschaft/architektur/menschen/produkt/food/handwerk/anime/nsfw):
     `New-Item -ItemType HardLink -Path "<library>\<vertical>\<name>.png" -Target "<Bildpfad>"`,
   - Projekt-Assets → Kopie in den jeweiligen Projektordner (`Copy-Item`).
   `--out` beim Generieren tut dasselbe (Hardlink innerhalb der Bibliothek, sonst Kopie), nur
   sinnvoll ohne Iterationen. Pfad und kurze Begründung der Wahl nennen.
6. **Remember (Loop schließen).** Reproduktion ist nativ gelöst: jedes erzeugte PNG
   trägt seinen Workflow in den Metadaten (`comfy_generate.py` bettet ihn ein, wie ein
   GUI-Bild). Es braucht KEIN Sidecar. Nach bestandenem Verify nur noch in den
   Recall-Index eintragen, damit gute Bilder per Vertical wiederfindbar sind:

   ```powershell
   & "D:\SDKs\Python311\python.exe" "C:\Users\Marcus\.claude\skills\bs-media-image\scripts\ledger.py" add `
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

Maßstab ist, was durch Claudes Kontext läuft, nicht wo gerechnet wird.

- **Kein expliziter Inhalt im Kontext, das ist die harte Linie.** Kein `Read` auf solche Bilder, 
keine Ausgabe solcher Prompts oder Captions, keine eigenen expliziten Formulierungen, keine Verify-Schleife darauf.
- **Durchlauf ohne Wahrnehmung ist erlaubt** ein Massenlauf über vorhandenes Material darf explizite Quellen mitnehmen, 
solange Claude weder Quelle noch Prompt noch Ergebnis ansieht. Ausgewertet werden nur die NSFW-Stufen als Zahl, Stichproben nur aus Stufe `sicher`.
- **Legal und unkritisch ist ok:** Bikini, Unterwäsche, Produktbilder im normalen Kontext, Sichtprüfung eingeschlossen.
- **Absolute Grenze, auch im Durchlauf:** alles mit Minderjährigen, auch KI-generiert, ist strafbar (§184b StGB). Niemals, und kein Massenlauf hebt das auf.
- **Haftung liegt beim Nutzer**, nicht bei Claude. Die Lokalität (ComfyUI offline) ändert daran nichts, solange Claude im Loop ist.
- Keine real existierenden Personen / Promi-Ähnlichkeit ohne Einwilligung.

## Grenzen

- Video: Wan 2.2 I2V läuft und ist seit 22.09.2026 vermessen. **Erste Wahl ist
  `wan22_i2v_14b.api.json`**, es hält die Komposition des Eingangsbilds und bewegt Nebel,
  Wolken und Kamera wie im Prompt verlangt. Ein Clip hat 81 Bilder bei 16 fps, also 5,1 s.
  Kosten: 122 s auf 832x480 (Vorschau), 347 s auf 1280x704 (Hero-Größe), VRAM-Spitze 13,7
  bis 14,6 GB von 16,3. **`--width` und `--height` immer angeben**, sonst injiziert
  `comfy_generate.py` seine 1024x1024 und der Lauf kostet das Dreifache. **Quadratische
  Eingänge auf 944x944** (360 s, 15,2 GB Spitze), nie 1024x1024: dort fiel am 22.09. mitten im
  Lauf der Grafiktreiber aus (Code 43, 16,2 GB Spitze). `wan22_i2v_5b`
  blieb am Testmotiv fast statisch, `wan22_i2v_14b_loop` (nahtlose Schleife) ist ungetestet.
- Keine Marken-Logos/Markeninhalte ohne ausdrückliche Vorlage.
- Lizenz beachten: Z-Image und Qwen sind Apache 2.0, WAI-illustrious und CyberRealistic
  Illustrious tragen Civitai-Bedingungen (Tier B in models.md). Seit 27.08.2026 ist
  die Lizenz kein Ausschlusskriterium mehr, wird aber pro Modell dokumentiert.
