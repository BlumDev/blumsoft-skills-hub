# gen-asset: Modell-Registry & Lizenzen

Lebendes Dokument, Quelle der Wahrheit für die Modellwahl. Regelmäßig aktualisieren.
Stand: 2026-09-19. Hardware: RTX 5070 Ti 16 GB (Blackwell).

**Lizenzregel (geändert am 27.08.2026):** Kommerziell frei ist keine Ausschlussbedingung
mehr. Jede Modell-/LoRA-Lizenz wird weiterhin einzeln geprüft und hier eingetragen, sie
entscheidet aber nicht mehr allein über die Aufnahme. Ergebnisqualität geht vor Lizenzstufe.
Bei Civitai gilt weiter: Permission-Flags der Modellseite lesen, nicht die
Download-Möglichkeit. Vor dem Einsatz in einem konkreten Kundenprojekt die Stufe des
verwendeten Modells nachsehen, Tier C bleibt begründungspflichtig.

## Empfohlener Stack (kommerziell frei, 16-GB-tauglich)

### Tier A: voll sauber (Apache 2.0, Modell UND Output frei)

| Modell | Staerke | NSFW | 16 GB | Status |
|---|---|---|---|---|
| FLUX.1-schnell | Realismus, Architektur, Produkt, Text-im-Bild | nein (zahm) | fp8 | **entfernt 19.09.2026** (Z-Image gewann 5 von 5, Cutout-Kette läuft auf Z-Image, Licht macht Qwen) |
| Chroma1-HD | Allrounder: Realismus + Anime + Furry + NSFW, FLUX-schnell-Basis, voll unzensiert | ja | Q8 GGUF (9 GB) | **entfernt 19.09.2026** (NSFW real: CyberRealistic Z-Image, Anime: WAI, echtes Negativ: Pony und WAI) |
| Z-Image-Turbo (6B) | Realismus in Architektur, Handwerk, Produkt UND Haut; 8 Steps; Landschaft abgegeben (Blindtest 28.09.2026: 1 von 16) | nein (zahm) | bf16 (12,3 GB) | **installiert + getestet 2026-08-27** |
| Qwen-Image-2512 (20B) | englischer Text im Bild, Lichtstimmung, Prompt-Treue | nein | Q4_K_M GGUF (11,4 GB) | **installiert + getestet 2026-08-28** |
| Qwen-Image-Edit-2511 (20B) | vorhandenes Bild gezielt ändern statt neu würfeln | nein | Q4_K_M GGUF (13,2 GB) | **installiert + getestet 2026-08-28** |

**Bestand am 20.09.2026: vier Bildmodell-Familien mit sieben Checkpoint-Dateien.**
Z-Image (Z-Image-Turbo, CyberRealistic Z-Image v7, teilen `qwen_3_4b` und `ae_zimage`),
Qwen-Image (2512, Edit-2511, teilen `qwen_2.5_vl_7b` und `qwen_image_vae`),
Illustrious/SDXL (WAI-illustrious v17, Illustrious Realism v4), Krea 2 (Turbo fp8, eigener Encoder `qwen3vl_4b`,
teilt `qwen_image_vae` mit Qwen). Dazu BiRefNet und 4x-UltraSharp als Helfer sowie
Wan 2.2 als getrennte Video-Linie (drei Dateien, Workflows `wan22_i2v_5b` und
`wan22_i2v_14b`). Am 22.09.2026 erstmals vermessen: die 14B Q5 hält die Komposition und
bewegt Nebel, Wolken und Kamera wie verlangt, 122 s auf 832x480 und 347 s auf 1280x704 je
5-Sekunden-Clip bei 13,7 bis 14,6 GB Spitze. Die 5B blieb am selben Motiv fast statisch und
ist damit ein Streichkandidat, sobald ein zweites Motiv das bestätigt. Zahlen in learnings.md. Wer im Ordner `DiffusionModels` acht Dateien sieht: davon sind drei Wan. Gestrichen wurden SD1.5-Zoo, FLUX.1-schnell, Chroma1-HD mit t5xxl und
Juggernaut XL (75,2 GB), Begründung und Vorab-Tests in learnings.md.
Seit 20.09.2026 zusätzlich Krea 2 Turbo (fp8, 18,3 GB mit Encoder) als Kandidat für den
Foto-Standard, A/B-Ergebnis in learnings.md, Entscheidung gegen Z-Image-Turbo offen.

### Zwischenstufe: Community-Lizenz mit Schwelle (frei unter 1 Mio USD Umsatz und 50 Seats)

| Modell | Staerke | NSFW | 16 GB | Status |
|---|---|---|---|---|
| Krea 2 Turbo (12B) | Foto- und Filmlook ohne Überschärfung, Menschen, Food, Innenräume, breite Stilspanne (Aquarell); 8 Steps, cfg 1, euler/simple | nein (zahm, LoRAs auf Civitai) | fp8_scaled (13,1 GB) + Encoder qwen3vl_4b fp8 (5,2 GB), VAE von Qwen-Image | **installiert + A/B gegen Z-Image 2026-09-20 (5:2 bei 4 Unentschieden), Entscheidung Ersatz offen** |

### Tier B: Output kommerziell ok, kein bezahlter Inferenz-Dienst (FAIPL 1.0)

| Modell | Staerke | Einschraenkung |
|---|---|---|
| Illustrious XL v0.1 | Anime-Spitze, riesiges LoRA-Oekosystem | Bilder verkaufen ok; Modell als Bezahl-Service nicht |

### Tier C: fuer kommerziell RAUS

- **Pony V6 XL**: modifizierte FAIPL, monetarisierte Inferenz untersagt (Graubereich). Nur mit Permission von PurpleSmartAI.
- **NoobAI**: Output kommerziell verboten.
- **FLUX.1-dev** + dev-basierte LoRAs: non-commercial ohne BFL-Lizenz.
- **XLabs flux-RealismLora** und die meisten Realism-LoRAs: dev-basiert / non-commercial.

### Freistellung / Matting (kein Generierungs-Modell)

| Modell | Zweck | Lizenz | Status |
|---|---|---|---|
| BiRefNet-General | Hintergrund-Segmentierung/Matting für freigestellte Motive, via Node `comfyui_layerstyle` | MIT, kommerziell frei | installiert + getestet (2026-08-13) |

Standard-Freistellungsweg seit 2026-08-13 (Vergleichstest, siehe learnings.md), ersetzt
Chroma-Key als ersten Weg. `tools/keyout.py`-artiger Chroma-Key bleibt Offline-Fallback ohne
laufendes ComfyUI.

## Vertical -> Modellempfehlung

Aktualisiert am 2026-09-22: Pony aus den drei Alternativspalten entfernt (Modell gelöscht), Kinderbuch, Stil-LoRAs und Namensgrafik ergänzt. Am 2026-09-28 Landschaft nach dem Blindtest neu besetzt. Details in learnings.md.

| Vertical | Erste Wahl | Alternative |
|---|---|---|
| Landschaft / Winzer | Qwen-Image-2512 mit 30 Steps, cfg 4.0, ohne Turbo-LoRA (Workflow 17, etwa 100 s bei 1344x768) | Krea 2 Turbo als schnelle Alternative (Workflow 10, Detail 0.5, etwa 11 s) |
| Architektur / Web-Hero | Z-Image-Turbo (offen: gegen Krea und Qwen nie getestet, gegen FLUX am 27.08. nur 5:5) | Qwen-2512 (Blue Hour, dramatischer Himmel) |
| Produkt | Z-Image-Turbo | Qwen-2512 |
| Handwerk / Technik | Z-Image-Turbo | Qwen-2512 |
| Freigestelltes Motiv (Icon, Sprite, Produkt ohne Grund) | Z-Image-Turbo + BiRefNet | BiRefNet allein auf vorhandenem Bild |
| Englischer Text im Bild | Qwen-Image-2512 | - |
| Deutscher Text im Bild | kein Modell, Typografie im Layout setzen | - |
| Lichtstimmung laut Prompt (golden hour) | Qwen-Image-2512 | Z-Image mit ausdrücklichem Licht-Prompt |
| Vorhandenes Bild ändern | Qwen-Image-Edit-2511 | - |
| Menschen / Portrait (SFW) | Z-Image-Turbo | Illustrious Realism v4 (echter Negativ-Prompt) |
| Anime | WAI-illustrious v17 | - |
| NSFW realistisch | CyberRealistic Z-Image v7 | - |
| Upscale | 4x-UltraSharp + Z-Image-Turbo als Refiner | - |
| Kinderbuch / Illustration für Kinder | Krea 2 Turbo (ohne LoRA) | Z-Image (flache Vektoroptik, besser für Druck) |
| Sticker, Pop-up-Buch, Figurenblatt | Krea 2 + passende Stil-LoRA (Trigger-Wort nötig) | - |
| Namensgrafik, kurzer Name in Großbuchstaben | Qwen-Image-2512 | Krea 2 und Z-Image schreiben ihn ebenfalls korrekt |
| Namensposter im Ideogram-Stil (Name in gestalteter Szene) | Workflow 13: Krea 2 + Typnosis 1.5 + Licht- und Detailstapel | Qwen-2512 für realistische Dinos und Voxel-Schrift |
| Bild in Bewegung (Image-to-Video) | Wan 2.2 I2V 14B Q5, 832x480 für die Vorschau | dasselbe auf 1280x704 für Hero-Größe |

## NSFW-Kandidaten (Recherche 2026-08-28, nicht selbst getestet)

Der Nutzer generiert diese Bilder selbst, die Einstellungen stammen von den Modellseiten und
aus der Recherche, nicht aus eigenen Läufen. Vor dem ersten Einsatz also einmal gegenprüfen
und das Ergebnis hier eintragen. Civitai-Downloads laufen per API mit dem Token aus `~\.claude\.civitai-token`, der Token
gehört als URL-Parameter `?token=` an die `downloadUrl` der Datei, nicht in den
Authorization-Header (der liefert bei Modell-Downloads HTTP 400, bei Embeddings ging er noch).

### Fotorealistisch

| Modell | Basis | Größe | Settings | Lizenz laut Modellseite |
|---|---|---|---|---|
| **PerfecZion 4.0** | Z-Image-Turbo | BF16 11,5 GB, FP8 5,7 GB | 12 Steps, cfg 1.0, `dpmpp_3m_sde`, simple, shift 3.0 | Bilder verkaufen erlaubt, Derivate erlaubt, keine Namensnennung nötig |
| **CyberRealistic Z-Image v7.0** (26.08.2026) | Z-Image-Turbo | BF16 12,3 GB (installiert 19.09.2026); INT8 6,7 GB lief auf ComfyUI 0.25.1 NICHT (`KeyError: int8_tensorwise`), seit 0.36.0 ungetestet, BF16 bleibt der sichere Weg | wie Basis-Z-Image: 8 Steps, cfg 1.0, `res_multistep`, simple | Bilder verkaufen erlaubt |
| Chroma1-HD (entfernt 19.09.2026) | FLUX-schnell | Q8 9,1 GB | 26 Steps, cfg 4.0, euler, beta | Apache 2.0 |

Beide Z-Image-Finetunes sind reine Diffusion-Modelle wie die Basis, sie brauchen weiterhin
`qwen_3_4b.safetensors` und `ae_zimage.safetensors` und laufen im selben Graphen. Damit ist
der Wechsel ein Datei-Tausch im Knoten CHECKPOINT, kein neuer Workflow. Vorlage:
`zimage_nsfw_t2i.api.json`. Chroma bleibt der Weg, wenn ein echter Negativ-Prompt gebraucht
wird, die Z-Image-Linie kennt keinen (cfg 1.0).

### Anime

| Modell | Basis | Größe | Settings | Lizenz laut Modellseite |
|---|---|---|---|---|
| **Illustrious Realism v4.0** (15.05.2026, Civitai 2354628) | Illustrious XL 1.0 | 6,9 GB, VAE enthalten | eigener Workflow des Nutzers: 25 Steps, cfg 6, `dpmpp_2m_sde`, Clip Skip 2, 832 x 1216, Hires-Kette per Bypass zuschaltbar | Civitai-Bedingungen der Modellseite |
| **WAI-illustrious-SDXL v17.0** (23.04.2026) | Illustrious (SDXL) | 6,8 GB, VAE enthalten | 15 bis 30 Steps, cfg 5 bis 7, `euler_ancestral`, normal, Auflösung über 1024 | Bilder erlaubt, Modell-Weiterverkauf nicht |
| **CyberRealistic Pony v18.0 CoreShift** (08.05.2026) | Pony V6 (SDXL) | 6,9 GB, VAE enthalten | 30+ Steps, cfg 5, `dpmpp_sde` karras, Clip Skip 2, 896 x 1152, Präfix `score_9, score_8_up, score_7_up` | Pony-Basis: FAIPL, monetarisierte Inferenz untersagt (Tier C) |
| Hassaku SD1.5 (entfernt 19.09.2026 mit dem SD1.5-Zoo) | SD1.5 | 2,0 GB | 512 x 768 Basis, Hires-Pass | Civitai-Bedingungen prüfen |

Vorlage: `illustrious_t2i.api.json`, Negativ-Prompt ist mit dem üblichen Qualitäts-Set
vorbelegt. Illustrious und NoobAI erwarten Danbooru-Tags, keine Sätze. Pony V7 ist keine
SDXL-Ableitung mehr, sondern AuraFlow: eigener Workflow nötig und die vorhandenen
Pony-LoRAs passen nicht mehr. Deshalb hier nicht empfohlen, solange V6 reicht.

**Dateinamen nach dem Download prüfen.** Die Vorlagen tragen den Namen, den die Civitai-API
nennt (`perfeczionZImageTurbo_40BF16.safetensors`, `waiIllustriousSDXL_v170.safetensors`).
Weicht der tatsächliche Name ab, im Knoten CHECKPOINT anpassen, sonst bricht die Validierung ab.

## Compliance bei realistischem NSFW (zusaetzlich zur Modell-Lizenz)

Die Modell-Lizenz erlaubt das Generieren, regelt aber NICHT die Verbreitung. Bei echt
wirkenden Menschen kommen separate Pflichten dazu: keine real-person-Aehnlichkeit,
Alters-/Einwilligungsnachweis bei Verbreitung, Plattform-ToS, in DE/EU JuSchG/JMStV.
Eigener Compliance-Block, bevor das ein Geschaeftszweig wird.

## LoRAs: welches Modell trägt welche

Eine LoRA passt nur auf die Architektur, auf der sie trainiert wurde. Der Dateiname des Basismodells ist dabei egal, entscheidend sind die Schlüsselnamen in der Datei.

| LoRA | Architektur | Läuft auf | Läuft nicht auf |
|---|---|---|---|
| Midjourney Luneva Cinematic, [ZIT] Detail Slider | Z-Image (`diffusion_model.layers.*`, Metadatum `ss_base_model_version: zimage`) | Z-Image-Turbo, CyberRealistic Z-Image v7 | Krea 2, Qwen-Image, Qwen-Edit, WAI-illustrious, Illustrious Realism, CyberRealistic Pony |
| Wuli Turbo 2 Steps, Lightning 4 Steps | Qwen-Image | Qwen-Image-2512, Qwen-Image-Edit-2511 | alles andere |
| Illustrious-LoRAs von Civitai | SDXL/Illustrious | WAI-illustrious v17, Illustrious Realism v4 | Pony, Z-Image, Qwen, Krea 2 |

Installierte Detail-LoRAs der SDXL-Seite, beide Lizenz nur `RentCivit` (Bilderverkauf nicht gedeckt),
beide auf 0.0 in den Workflows 06 und 08: `StS-Illustrious-Detail-Slider-v1.0` (8 MB) und
`StS_PonyXL_Detail_Slider_v1.4_iteration_3` (17 MB). Beide heben vor allem den Hintergrund.
Für Qwen-Image existiert keine Detail-LoRA (Civitai-Suche am 22.09.2026, vier Begriffe, null Treffer).
| Krea-2-LoRAs von Civitai (Basis `Krea 2`) | Krea 2 (SingleStreamDiT) | Krea 2 Turbo | alles andere |

Installierte Krea-2-LoRAs (alle Lizenz Sell und SellMerge, ohne Namensnennung, Stand 21.09.2026):
Regler ohne Trigger-Wort, fest im Workflow, `Detailer-KREA2` seit 27.09.2026 auf 0.5, die übrigen auf 0.0: `Detailer-KREA2` (11 MB), `WarmLightSlider-KREA2_v1`
(7 MB, nutzbar +0,5 bis +1,5 statt der angegebenen -6 bis +3), `Afterlight_v1` (109 MB),
`WeightSlider-KREA2_v2` (7 MB, ganzer Bereich -2 bis +2 brauchbar) und `RealismSlider-v1`
(6 MB, nutzbar nur -1 bis +1).
Stil-LoRAs mit Trigger-Wort für den Knoten STYLE_LORA, je 218 MB: `Sticker_KREA2_V1` (`sticker`),
`CharacterDesign-KREA2_v1` (`Character design`), `Pop-up_book_KREA2` (`pop-up book`),
`Anatomy-Reveal-KREA2` (`Anatomy-reveal`). Seit 26.09.2026 dazu `Typnosis_Krea2` (435 MB, ohne Trigger, Typografie für Namensposter, Stärke 1,0 bis 2,0). Messwerte in learnings.md.
Ebenfalls lokal, vom Nutzer am 26.09.2026 geladen: `krea2-masterpieces-v51` (205 MB, Civitai 929497 Version 3077110 "Aesthetic Quality Modifiers - Masterpiece", SHA256 geprüft), Trigger `masterpiece, very aesthetic`, laut Autor auf Turbo Stärke 1,5. Lizenz: Bilder kommerziell frei, das Modell selbst nicht verkaufen. Versionen gibt es auch für Z-Image Turbo (166 MB), Illustrious (218 MB) und das ursprüngliche Qwen-Image (563 MB, nicht 2512), nicht installiert.

Passt eine LoRA nicht, bricht ComfyUI nicht ab: der Knoten lädt, die Schlüssel greifen ins Leere und das Bild kommt unverändert heraus. Das fällt im Ergebnis nicht auf, deshalb vor dem Einsatz das Feld `baseModel` auf der Civitai-Seite prüfen. Lokal lässt sich die Architektur aus dem Safetensors-Header lesen (`__metadata__.ss_base_model_version` und das Präfix der Tensornamen).

### LoRA-Kandidaten für Namensposter (Civitai-Recherche 2026-09-25, nicht installiert, nicht getestet)

Zahlen je Version, nicht je Modellseite: die Seitenzahlen mischen alle Basismodelle, bei den Redmond-LoRAs stammen sie fast nur aus der SDXL-Zeit. Einschätzung nach den jugendfreien Beispielbildern der jeweiligen Fassung.

| LoRA (Civitai-ID) | Basis | Größe | Auslöser | Version dl / Likes | Einschätzung |
|---|---|---|---|---|---|
| Balloon inflation font (2042948) | Qwen | 14 MB | keiner | 127 / 14 | Ballonschrift genau im gesuchten Look, nur drei Beispiele |
| Typnosis Typography (2840653) | Krea 2 | 436 MB | keiner | 347 / 38 | **installiert 26.09.**, wirkt: 1,0 bis 2,0 brauchbar, ab 3,0 kippt die Schrift |
| Definitive Disney Studios (404277) | ZImageTurbo | 162 MB | DisneyIZT | 9.047 / 638 | einheitlicher Disney-3D-Figurenlook, keine Schriftbeispiele |
| Chibi Animal Characters (1481162) | Krea 2 | 218 MB | keiner | 485 / 76 | niedliche Chibi-Tiere, eher Anime als 3D |
| Pixar Disney 3D Style (2831766) | Krea 2 | 218 MB | 3dpixar | 1.971 / 187 | sauberer 3D-Look, den Krea ohne LoRA schon weitgehend trifft |
| Qianwen 3D Fabric Cute (1977384) | Qwen | 563 MB | 布艺画风 | 208 / 18 | Filz- und Stofftextur, Plüsch schafft Z-Image schon ohne LoRA |
| Iridescent Glitter Overlay (2908976) | Krea 2 | 448 MB | keiner | 231 / 28 | verworfen: düstere Beispiele, kein rosa Glitzer |
| Storybook Folk Art (1321740) | Krea 2 | 218 MB | whimsical storybook illustration | 1.433 / 265 | verworfen: düstere Folk-Art, nicht kindgerecht |

Qwen-LoRAs sind auf Qwen-Image trainiert, 2512 hat dieselbe Architektur (60 Blöcke), die Wirkung dort ist ungeprüft. Vor dem Einsatz jede LoRA per Header-Check und Pixelvergleich bei gleichem Seed prüfen, ein Fehlgriff bleibt stumm.

## Entscheidungs-Log (append-only)

- 2026-10-04 (Nahttest 2): Stufe 2 von `illustrious_t2i` (WAI, damit auch Workflow 06) rechnet in einer
  Kachel: `tile_width` und `tile_height` 4096, `force_uniform_tiles` aus, Sicherung `.bak-20261004`. Mit
  1024er-Kacheln kamen leichte Streifen durch die Bildmitte (Nutzernotiz, im Test mit den alten Werten
  wiederholt). Eine Kachel gewann zwei von drei Bildern, Half Tile + Intersections eins, beide ohne
  Streifen. Eine Kachel ist dreimal schneller (26 bis 50 s gegen 92 bis 142 s). Gemessen bis 1920 x 3328
  ohne Speicherprobleme. `upscale.api.json` (Z-Image) bleibt unverändert, ungetestet.
- 2026-10-04: Sieben Krea-2-LoRAs für Stapeltest 2 Phase B geladen (Download-Ja des Nutzers), SHA256
  gegen Civitai geprüft, alle mit kommerzieller Bildnutzung ohne Namensnennung, unter `Lora`:
  `ultra_real_krea2_v2` (UltraReal KR2 V2 Pro, 218 MB, Civitai 2462105, Stärke 0.6 bis 0.8),
  `purelens_krea2` (PureLens Realism, 327 MB, 2728005, Trigger `purelens`, 0.6 bis 1.5),
  `inline-skin-lora-krea-2-raw` (Realistic Skin Texture, 183 MB, 2808600, Trigger
  `inline-skin-lora, detailed skin texture`, 0.6 bis 1.0), `skin_detail_slider_krea2_ZT-V1` (Skin
  Detail Slider Zero-Train, 1 MB, 2936275, nur ein Modul), `zy_BackgroundDetail_K2` (Background
  Detail Enhancer, 218 MB, 633524, 0.1 bis 0.75), `KGodRays` (God Rays & Volumetric Lighting, 218 MB,
  2809415, Trigger `KGodRays`, 1.0), `AfterHours_v2` (Low-Key-Studio, 224 MB, 2843967, 0.6 bis 1.0).
  Architektur geprüft: fünf treffen alle Krea-Module, der Slider sein eines. Die Skin-LoRA liegt im
  Diffusers-Format (`text_fusion.layerwise_blocks…`), ComfyUI bildet sie über `krea2_to_diffusers` ab:
  beim Laden kein „lora key not loaded“, eine Illustrious-LoRA als Gegenprobe gab 1038.
- 2026-10-03 (Abend): Nutzerentscheid nach Stapeltest 2 Phase A (18 Foto-Motive, blind): Krea-Standard
  ist Detail 0.5 plus Afterlight 0.35. Afterlight gewann 14 von 18 Gruppen (0.35 neunmal, 0.7 fünfmal),
  Detail 0.5 allein keine, direkt 9:0 für Afterlight 0.35. `krea2_turbo_t2i` trägt `AFTERLIGHT_LORA`
  0.35 (Sicherung `.bak-20261003`), damit auch UI-Workflow 10 und alle Krea-Ziele der Galerie außer
  Kinobanner. `krea2_kinobanner` bleibt bei Detail 1.0 mit Stimmung (Afterlight 0.35, Warm 0.5),
  Namensposter, Sprites und Regler-Vergleich bleiben unverändert. Realism +0.5 gewann bei Produkt im
  Abend- und Fensterlicht zweimal und bleibt Kandidat. Phase B (sieben neue Krea-LoRAs) tritt gegen den
  neuen Standard an, sobald der Nutzer den Download freigibt.
- 2026-10-03 (Nachmittag): Nach den Nutzerurteilen `janku_t2i` Stufe 1 auf 832x1216 (Ergebnis
  1248x1824), weil 1024x1536 bei Füßen und Händen Zehen und Füße verdoppelte. `DETAIL_LORA` in
  `zimage_turbo_t2i` und `zimage_nsfw_t2i` von 0.3 auf 0.6 (0.6 gewann 3 von 4). Anime-Upscaler 6B
  ohne Vorteil (2:2), Stufe 2 bleibt bei `RealESRGAN_x4plus`. Masterpiece auf Krea kein Standard.
- 2026-10-03: Entscheidungen des Nutzers nach Fototest und K4. Architektur rechnet auf Qwen-2512
  in Qualitätseinstellung (`qwen_2512_landschaft`), Produkt, Handwerk und Portrait auf Krea 2
  (`krea2_turbo_t2i`), Z-Image-Turbo ist nur noch die schnellste Wahl. Hinweis des Nutzers: bei Krea
  entscheidet der LoRA-Stapel viel, ein Stapeltest je Bereich läuft. Kinobanner: die Stimmung
  (Afterlight 0.35, Warm 0.5) ist in `krea2_kinobanner` jetzt Standard, `--no-mood` schaltet sie
  ab. Die ungenutzte Qwen-2512 Fun ControlNet Union (3,3 GB) liegt im Papierkorb. Geladen und
  geprüft: Masterpiece `illustrious_masterpieces_v3` (218 MB, Civitai-Version 2247497) und
  `zimage_masterpieces_v3.2` (166 MB, Version 2622701) unter `Lora`, dazu
  `RealESRGAN_x4plus_anime_6B.pth` (17.938.799 Byte, offizielles Real-ESRGAN-Release v0.2.2.4, SHA256
  f872d837d3c9…) unter `Models\ESRGAN`, Test in Stufe 2 von JANKU läuft. Weitere LoRAs für die
  übrigen Civitai-Vorlagen lädt der Nutzer ausdrücklich nicht.
- 2026-10-02: Fünf Illustrious-LoRAs für den Nachbau von Civitai-Vorlagen geladen (Freigabe des Nutzers
  "alle laden"), SHA256 gegen Civitai geprüft: `TRT(Illust)0.1v` 218 MB (Civitai "STYLES |
  Illustrious/Noob", der Stil-Hebel der Vorlagen des Kimono-Autors, früher bewusst weggelassen),
  `lightingSlider` 45 MB, `Cabyss - Heavy` 243 MB, `Glowing_illustrious` 218 MB, alle mit
  kommerzieller Bildnutzung. Dazu Xu Er Thick Paint 650 MB, Lizenz ohne kommerzielle Bildnutzung,
  liegt als `XuEr_ThickPaint_Illustrious_V3.safetensors` (Originalname chinesisch). "HL's Styles -
  WAI" auf Civitai ist unser `WSSKX_WAI`. Nicht geladen: Kaela, Sweetfrilldress und die LoRAs, die
  nur je eine Vorlage nutzt.
- 2026-09-28: Vierbeiner als Sprites bleiben auf Krea (Workflow 18), mit einem zweiten Ausgang, der
  Zelle 3 als Spiegelbild von Zelle 2 setzt (Krea malt Stand, Trab, Stand). Hund und Wolf zeigen
  mit seitlich bestellten Beinen alle vier Beine, das Maultier bleibt offen. Qwen-2512 aus Text in
  Qualitätseinstellung scheidet für Draufsicht-Sprites aus: aufrechte Tiere, Ansichten, Konturen.
- 2026-09-28: Kacheln (Workflow 19 `seamless_tile`) ohne Modell: verschieben und im Nahtkreuz das
  Original überblenden, für Agentenläufe varianzerhaltend über `scripts/seamless_tile.py`. Die
  Z-Image-Nahtreparatur ließ in allen sechs Fassungen ein sichtbares Kreuz. Korrektur zum Eintrag
  darunter: die Qwen-2512 Fun ControlNet Union 2602 lädt in ComfyUI 0.36 NICHT, `ModelPatchLoader`
  kennt ihr Format (`control_blocks.*`) nicht, `QwenImageDiffsynthControlnet` gehört zur
  DiffSynth-Blockwise-Fassung. Die 3,3 GB liegen ungenutzt, Löschen nur nach Nutzerfreigabe. Die
  Stylized-Textures-LoRA milderte die Z-Image-Reparatur, aus Text lag sie weit über der Palette.
- 2026-09-28: Sprites (Workflow 18 `krea2_sprites`) auf Krea 2 aus Text: Draufsicht in 23 von 23
  Bögen. Qwen-Edit mit dem Gate-Bogen als Vorlage drehte neue Figuren in 9 von 12 Bögen zu Vorder-,
  Seiten- und Rückansicht und bleibt nur für Varianten eines abgenommenen Bogens (05, denoise 0.8).
  Multiple-Angles-LoRA auf dem Posenbogen ohne sichtbare Wirkung, laut Modellkarte ohnehin nur bis
  60 Grad Höhe, keine Draufsicht.
- 2026-09-28: Kinobanner auf Krea: Workflow 14 ist `krea2_kinobanner` mit Detail 1.0, Afterlight und
  Warm als zuschaltbare Stimmung (`STIMMUNG_*` auf 0, `comfy_generate.py --mood`). Blindurteil: K0
  gewann alle sechs Motive gegen leichtere Stufen und Z-Image, der Nutzer will die Stimmung aber
  nicht in jedem Bild. Z-Image-Fassung als 14b. Blindtest K4 (Stimmung aus) läuft.
- 2026-09-28: Drei Downloads für Sprites und Kacheln, vom Nutzer freigegeben, SHA256 jeweils
  gegen die Quelle geprüft: `qwen-image-edit-2511-multiple-angles-lora.safetensors` (281 MB,
  Civitai 2588352, Qwen-Edit-2511, Trigger `<sks> [azimuth] [elevation] [distance]`) und
  `StylizedTexture_ZIT.safetensors` (172 MB, Civitai 2550731, Z-Image Turbo, Prompt-Gerüst "A
  seamless tileable 2D texture pattern of ...") unter `Lora`, dazu
  `Qwen-Image-2512-Fun-Controlnet-Union-2602.safetensors` (3,3 GB, alibaba-pai auf Hugging Face,
  neuere Fassung mit zusätzlicher Gray-Steuerung) unter `ModelPatches`, geladen über die
  Kernknoten `ModelPatchLoader` und `QwenImageDiffsynthControlnet`. Noch ungetestet.
- 2026-09-28: Landschaft neu besetzt nach blindem Nutzertest (16 Prompts, vier Modelle, gleicher
  Seed und gleiche Größe je Prompt): Qwen-2512 mit 30 Steps, cfg 4.0 und ohne Turbo-LoRA gewann 8
  Prompts, Krea 2 5, CyberRealistic 2, Z-Image 1. Neuer Workflow 17 `qwen_2512_landschaft`, Krea
  als schnelle Alternative, Z-Image für Landschaft gestrichen. Die alte Empfehlung stammte aus
  einem 5:5 gegen FLUX-schnell vom 27.08., beurteilt von einem Agenten.
- 2026-09-27: Detail ist standardmäßig an, auf Nutzerwunsch ("leichter Detail", "kleine Stufe"):
  `krea2_turbo_t2i` DETAIL_LORA 0.5, `zimage_turbo_t2i` und `zimage_nsfw_t2i` DETAIL_LORA 0.3.
  Grundlage: 16 Bilder mit drei Sternen und ohne LoRA aus dem eigenen Graphen nachgerechnet, nur
  die LoRA-Stärke geändert (Kontrolle bei Krea pixelgleich, bei Z-Image 0,7 bis 1,0 von 255
  Abweichung). Mittlere Helligkeit: Krea 0.5 minus 4 Prozent, Z-Image 0.3 minus 5 Prozent,
  CyberRealistic 0.3 minus 8 Prozent, Komposition jeweils gleich. Doppelte Stärke kostete 14 bis
  21 Prozent. Der volle Krea-Stapel (Detail 1.0, Warm 0.5, Afterlight 0.35) änderte die Komposition
  sichtbar und verdeckte in einem Namensbild einen Buchstaben, er bleibt Workflow 13 vorbehalten.
  Die Stärken sind vorläufig, das Urteil des Nutzers zum Vergleichsblatt steht aus.
- 2026-09-22: CyberRealistic Pony v18 und Workflow 08 gelöscht (Nutzerfreigabe, 6,5 GB).
  Belege: verliert drei von drei Prompt-Treue-Tests gegen Krea 2 und Z-Image auf seinem
  eigenen Gebiet (Menschen, Posen, Hände), sexualisiert auch harmlose Prompts, ein einziger
  von 90 Ledger-Einträgen, eine einzige Pony-LoRA installiert, für NSFW laut Nutzer nicht
  gebraucht. Die letzte technische Abhängigkeit war der Refiner in Workflow 03, der vorher
  ersetzt wurde.
- 2026-09-22: Workflow 03 refined jetzt mit Z-Image-Turbo. Erst war Krea 2 gesetzt, weil es
  als einziges die Detail-Messung über das Ausgangsbild hob (44,4 gegen 40,9). Der Nutzer hat
  widersprochen: Krea übertreibt sichtbar, besonders im Haar, Z-Image wirkt echter. **Die
  Wahrnehmung entscheidet, nicht die Kennzahl.** Eine Kantenmessung belohnt jede zusätzliche
  Struktur und kann Überschärfung nicht von echtem Detail trennen, sie ist für die Frage
  natürlich gegen überzeichnet also untauglich. Notiert in learnings.md, damit die Zahl nicht
  erneut als Urteil genommen wird. Umbau: UNETLoader plus CLIPLoader `lumina2` plus VAELoader,
  cfg 1.0, genulltes Negativ, 8 Steps res_multistep/simple, 44 s. Die score-Tag-Automatik in
  `upscale.py` ist entfallen.
- 2026-09-22 (Korrektur am selben Tag): die Aussage im nächsten Eintrag ist falsch, sie beruhte
  auf Stärke 1.0. Der StS Illustrious Detail Slider wirkt auf WAI ab 3.0 deutlich, Arbeitspunkt
  3.0, Messung in learnings.md unter "Korrektur: Detail-Slider auf WAI".
- 2026-09-22: Detail-LoRAs für die SDXL-Modelle geprüft und eingebaut, aber mit klarer
  Einschränkung. Die zwei Slider (Illustrious, Pony) greifen nachweislich, heben aber fast nur
  den Hintergrund. Bei WAI liegt der Gewinn mit zwei Prozent im Rauschen und ist im Bild nicht
  zu sehen, bei Pony ist er sichtbar. Auch die 435 MB grosse Detailed-Perfection-LoRA brachte
  bei WAI nur ein Prozent. Was dort wirklich Details bringt, ist der zweite Durchgang: Upscale
  über Workflow 03 mit dem Anime-Checkpoint als Refiner ergibt fünfzehn Prozent mehr
  Feinstruktur, sichtbar an Haar, Augen und Schrift. Empfehlung an den Nutzer entsprechend
  geändert: bei Illustrious nicht am Regler drehen, sondern durch 03 schicken. Die Slider
  bleiben auf 0.0 in 06 und 08, sie kosten nichts. Lizenz beachten, alle drei erlauben nur
  `RentCivit`, der Verkauf erzeugter Bilder ist nicht gedeckt, anders als bei den Krea-LoRAs.
  Methodischer Nebenbefund: zwei Messinstrumente fielen vorher durch die Gegenprobe. Der
  statische Tensornamen-Abgleich versagt bei SDXL (andere Namensform, ComfyUI übersetzt erst
  beim Laden), und `user/comfyui.log` wird seit Juni nicht mehr beschrieben, die Log-Prüfung
  hätte jedem Lauf Erfolg bescheinigt. Tragfähig ist der Bildvergleich bei gleichem Seed.
- 2026-09-21: Zwei weitere Krea-2-Regler (Weight, Realism) in `krea2_turbo_t2i.api.json`,
  damit sechs LoRA-Knoten, alle auf 0.0 und nachgemessen neutral (Pixel-Prüfsumme identisch
  mit dem Vier-Knoten-Stand). Dazu der neue Workflow `krea2_slider_sweep.api.json` (UI:
  11-regler-vergleich): rechnet denselben Prompt und Seed fünfmal mit -2 bis +2 und legt die
  Bilder über `ImageConcatMulti` zu einem Blatt zusammen, etwa 50 s. Grund für den eigenen
  Workflow statt eines Schalters: eine Reglerwirkung sieht man nur im direkten Nebeneinander
  bei gleichem Seed, und fünf Einzelläufe von Hand zu vergleichen ist genau die Arbeit, die
  der Nutzer nicht machen soll. Trade-off: die zu prüfende LoRA muss in allen fünf Knoten
  gesetzt werden, weil ComfyUI ohne Zusatzknoten keinen gemeinsamen Dateiparameter kennt.
  Nebenbefund zur Qualität der Civitai-Angaben: bei drei von fünf Reglern war der auf der
  Modellseite genannte Bereich zu weit, die Ränder liefern unbrauchbare Bilder. Bereiche also
  selbst ausmessen, nicht übernehmen.
- 2026-09-21: Sieben Krea-2-LoRAs installiert (Nutzerauswahl), drei davon fest in
  `krea2_turbo_t2i.api.json` als Regler auf 0.0, dazu ein Platz STYLE_LORA für die vier
  Stil-LoRAs. Vorher geprüft, dass vier LoRA-Knoten auf Stärke 0.0 neutral sind: Bild mit
  und ohne die Knoten byte-identisch, Laufzeit unverändert bei 11 s. Wichtigster Befund:
  der Warm Light Slider hebt die Helligkeit von 103 auf 144, ohne Feinstruktur zu kosten,
  und ist damit der bessere Hebel gegen dunkle Bilder als Prompt-Formulierungen oder der
  Detail-Slider. Sein nutzbarer Bereich ist +0,5 bis +1,5, nicht die auf der Modellseite
  angegebenen -6 bis +3: bei +3 ist das Bild orange und ausgefressen, bei -3 fast schwarz.
  Nebenbefund, der eine offene Frage des Nutzers klärt: der vorhandene Z-Image-Detail-Slider
  wirkt auf Krea 2 nicht, gleiche Bezeichnung, andere Architektur, null Überschneidung der
  Gewichtsnamen. Die Prüfung geht ohne GPU über den Safetensors-Header.
- 2026-09-21: Testmaterial bekommt eine Halbwertszeit, aber nicht über den Ordnernamen.
  Vergleichsläufe hinterlassen viel Rohmaterial (fünfzehn Wasserzeichen-Seeds, sieben
  Helligkeitsstufen derselben Wiese), das im Raster der neuen Bildgalerie die Sicht des Nutzers
  auf seine eigenen Bilder verstellt. Erste Idee war, `Text2Img\agent\` in `_agent\` umzubenennen,
  weil die Galerie Ordner mit führendem Unterstrich als Archiv ausblendet. Umgesetzt und wieder
  zurückgebaut, nachdem die Galerie-Session widersprochen hat. Ihre Gründe, beide nachgeprüft:
  `classify_prefix` (comfy-gallery, seit 27.09.2026 in gallery_graph.py) liest die Quelle am ersten Pfadsegment und kennt nur `agent`
  und `ui`, mit Unterstrich fallen Quelle UND Workflow-Zweck auf unbekannt; dazu zeigen sieben
  Ledger-Pfade auf `Text2Img\agent\...` und liefen ins Leere. Stattdessen hat die Galerie einen
  Filter Quelle (Agent, UI, unbekannt) mit gemerkter Auswahl bekommen, seit Commit 36206db auf
  master. Damit ist das Rohmaterial mit einem Klick weg und Archiv bleibt für Altes reserviert. Der Ordnername `agent` ist damit bindend.
  Geblieben ist `scripts/cleanup.py`: verschiebt Testordner älter als 30 Tage nach
  `Images\_papierkorb\` und verschont, was im Ledger steht, in `reference/*.md` namentlich zitiert
  wird, oder in der Galerie einen Favoriten, ein Beispiel, eine Bewertung oder eine Notiz trägt
  (beide tags.json-Stände werden gelesen). Verschieben statt löschen, weil jedes PNG seinen
  Workflow trägt. Lehre aus dem Hin und Her: vor einer Umbenennung in `Data\Images` erst die
  Session fragen, die den Index baut, nicht erst danach.
- 2026-09-20: Zwei Z-Image-LoRAs aus einer Civitai-Vorlage geprüft. `[ZIT] Detail Slider`
  war schon installiert (`zimage_detail_slider.safetensors`, SHA256 identisch), neu geladen wurde
  `ZIT_Midjourney_Luneva_Cinematic_v1_r128.safetensors` (649 MB, Stärke 0,5, kein Trigger-Wort).
  Wirkung im A/B/C belegt (learnings.md). Lizenz beachten: Luneva erlaubt kommerzielle Bilder,
  verlangt aber Namensnennung und verbietet Ableitungen und Merges, der Detail Slider ist voll frei.
- 2026-09-20: Krea 2 Turbo installiert (`krea2_turbo_fp8_scaled` in DiffusionModels,
  `qwen3vl_4b_fp8_scaled` in TextEncoders, VAE `qwen_image_vae` geteilt mit Qwen-Image),
  Workflow `krea2_turbo_t2i.api.json` nach der offiziellen Vorlage (8 Steps, cfg 1, euler/simple,
  shift 1.15 im Modellprofil, kein Negativ-Prompt). A/B gegen Z-Image-Turbo auf 11 Motiven mit
  gleichem Seed: 5:2 für Krea 2 bei 4 Unentschieden, Krea liefert den natürlicheren Fotolook
  und die breitere Stilspanne, Z-Image gewinnt Fell und Chrom sowie Prompttreue in vollen
  Szenen und ist 3 bis 4 s schneller. Die Knoten `Krea2ImageNode` und `Krea2StyleReferenceNode`
  sind Cloud-API-Knoten, lokal läuft Krea 2 über die Standardknoten. Entscheidung offen:
  Krea 2 als Standard in 00 und 01 und Z-Image-Turbo (12,3 GB) streichen oder beide behalten.
- 2026-06-21: Bild-Basis FLUX.1-schnell (Apache) statt FLUX.1-dev (non-commercial).
- 2026-06-22: ComfyUI via Stability Matrix als Engine (statt InvokeAI/SwarmUI/Forge Neo).
- 2026-06-23: Chroma1-HD als kommerziell-freies Kern-Modell fuer NSFW/Anime/Realismus
  gewaehlt (einziges breit unzensiertes Apache-Modell). Pony/NoobAI verworfen (Lizenz).
- 2026-06-23: Reproduktion nativ ueber PNG-Metadaten; Ledger nur als kuratierter
  Recall-Index. Wissensbasis lebt im Skill (reference/), nicht im cwd D:\Repos.
- 2026-06-23: Chroma1-HD Q8 GGUF installiert (DiffusionModels) + t5xxl_fp8 (TextEncoders)
  + ae.safetensors lokal aus dem FLUX-All-in-one extrahiert (VAE). ComfyUI-GGUF-Node
  installiert. Getestet: Chroma loest das Haut-Thema (5* vs FLUX 4*) und kann Anime.
- 2026-09-19: Illustrious Realism v4.0 installiert (StableDiffusion), v3.0 nach A/B mit vier
  Prompts bei gleichen Seeds gelöscht (Nutzerentscheidung: v4 gefällt besser; gemessen rendert v4
  bei allen vier Motiven dunkler). Läuft in seinem eigenen Workflow "Illustrious Realism v3"
  (Name geblieben), Hires- und Post-Kette dort als Gruppe bypassed, per Rechtsklick zuschaltbar.
- 2026-09-19: ComfyUI 0.25.1 auf 0.36.0 (Stability Matrix 2.16.4), torch 2.14.0+cu130. Das
  SM-Update brach ab, weil der Server lief, und ließ die venv ohne torch zurück; Reparatur und
  Regeln in learnings.md. Damit sind Krea 2 (Support seit 23.06.2026) und INT8-Quantisierungen
  grundsätzlich möglich, beides noch ungetestet.
- 2026-09-19: Ablage vereinheitlicht. ComfyUI schreibt direkt in die Stability-Matrix-Bibliothek
  (`Data\Images\Text2Img` ist derselbe Ordner wie `ComfyUI\output`). Oberfläche: ein Zweckordner je
  Workflow plus Tagesordner (`foto/2026-09-19/foto_00001_.png`), Agentenläufe gebündelt unter
  `agent/<datum>/`, Root bleibt leer. 203 lose Altdateien (fast alles Agenten-Duplikate) liegen in
  `_alt-bis-2026-09-19/`. Ebenfalls gelöscht: SD1.5-LoRAs, -Embeddings und -VAE sowie die FLUX-VAE
  (53 Dateien, 1,0 GB), behalten wurde nur `Website logo design` (Basis Qwen laut Civitai-Info).
- 2026-09-19: Konsolidierung auf fünf Modellfamilien (Nutzerentscheidung: wenige Modelle, breite
  Abdeckung, einfache Bedienung). Gestrichen nach zwei bestandenen Vorab-Tests: SD1.5-Zoo,
  FLUX.1-schnell, Chroma1-HD mit t5xxl, Juggernaut XL, zusammen 53 Dateien und 75,2 GB. Die
  Freistell-Kette läuft seither auf Z-Image (`zimage_cutout.api.json`), der Upscale-Refiner ist
  CyberRealistic Pony. Neun Workflows, neu nummeriert 00 bis 08. Nebenbefund: CyberRealistic
  Z-Image als INT8 scheitert auf ComfyUI 0.25.1 (`int8_tensorwise` unbekannt), BF16 installiert.
- 2026-09-19: CyberRealistic Pony v18.0 installiert (StableDiffusion) als drittes NSFW-Standbein für
  Menschen, Posen und das Pony-LoRA-Ökosystem, Workflow `pony_t2i.api.json` (13). Nicht als
  Ersatz für die Z-Image-Linie gedacht: ältere SDXL-Architektur, bei Hautrealismus liegt Z-Image
  vorn, bei Szenerie Illustrious. Nutzerwunsch dahinter: wenige Modelle, breite Abdeckung,
  einfache Bedienung, Konsolidierung steht als Entscheidung an.
- 2026-08-28: Qwen-Image-2512 als Q4_K_M-GGUF installiert, Standardweg ist die 2-Step-Turbo-LoRA
  (`Wuli-Qwen-Image-2512-Turbo-LoRA-2steps-V1.0-bf16`), Workflow `qwen_2512_t2i.api.json`.
  Der volle Weg mit 50 Steps (`qwen_2512_t2i_quality.api.json`) kostet Faktor 11 an Zeit ohne
  sichtbaren Gewinn und bleibt nur als Rückfallebene liegen. Englischer Text im Bild sitzt,
  deutscher Text kippt reproduzierbar in einzelnen Buchstaben (4 von 4, Details learnings.md).
- 2026-08-27: Z-Image-Turbo bf16 installiert (DiffusionModels) plus Text-Encoder
  `qwen_3_4b.safetensors` (TextEncoders) und eigene VAE `ae_zimage.safetensors`. Die
  vorhandene `ae.safetensors` wurde NICHT überschrieben, sie ist 472 Byte kleiner als die
  Z-Image-VAE, also nicht dieselbe Datei. Im A/B gegen FLUX-schnell (gleicher Prompt, Seed,
  Format) gewinnt Z-Image in allen fünf getesteten Verticals, neue Erstwahl für SFW.
  Workflow: `zimage_turbo_t2i.api.json`. Läuft ohne ComfyUI-Update, Support ist seit
  Dezember 2025 nativ drin.
- 2026-08-27: Lizenzregel gelockert (Nutzerentscheidung). "Kommerziell frei ist Bedingung"
  fällt als Ausschlusskriterium weg, Lizenzstufe wird nur noch dokumentiert. Auslöser:
  Krea 2 (12B, Juni 2026) liefert Spitzenqualität, steht aber unter einer Community-Lizenz
  mit Schwelle (frei unter 1 Mio USD Umsatz und 50 Seats) statt unter Apache. Trade-off:
  ein Modell der Stufe Tier B/C kann in einem Kundenprojekt eine Lizenzprüfung nötig machen,
  deshalb bleibt die Stufe pro Modell eingetragen.
- 2026-08-27: Recherchestand der Alternativen. Qwen-Image-3.0 (21.07.2026) gibt es NICHT
  als Gewichte, nur über Qwen Chat, die lokale Linie endet bei Qwen-Image-2512 (20B, Apache).
  FLUX.2 [dev] bleibt non-commercial. Chroma1-Radiance ist laut Modellkarte noch im Training,
  Chroma1-HD bleibt gesetzt. Qwen-Image-Layered (RGBA-Ebenen) braucht laut Doku 45 GB Peak,
  auf 16 GB unpraktikabel, BiRefNet bleibt Freistellungsweg.
- 2026-08-13: BiRefNet-General (MIT) installiert für Freistellung, schlägt Chroma-Key im
  A/B-Test klar (Details learnings.md). Neuer Standard für freigestellte Motive, Chroma-Key
  bleibt Offline-Fallback. Chroma1-HD im selben Test für flach-vektorielle Stile
  unterlegen (5x Zeit, Schattenproblem nicht gelöst, Symbol/Hintergrund verfehlt);
  Empfehlung für Haut/Anime/NSFW oben bleibt unverändert.

## Quellen

- [Chroma (Apache, uncensored)](https://www.nowadais.com/chroma-model-training-ai-image-generation/)
- [Chroma VRAM](https://willitrunai.com/image-models/chroma-1)
- [Pony V6 FAIPL](https://ponydiffusion.com/faq)
- [Illustrious vs NoobAI Lizenz](https://note.com/kazuya_bros/n/n84fa6fe9360b?hl=en)
- [Z-Image / Qwen Apache](https://www.bentoml.com/blog/a-guide-to-open-source-image-generation-models)
