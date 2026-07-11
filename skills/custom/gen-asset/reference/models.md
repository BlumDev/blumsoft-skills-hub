# gen-asset: Modell-Registry & Lizenzen

Lebendes Dokument, Quelle der Wahrheit fuer die Modellwahl. Regelmaessig aktualisieren.
Stand: 2026-06-23. Hardware: RTX 5070 Ti 16 GB (Blackwell).

**Harte Regel: kommerziell frei nutzbar ist Bedingung.** "Gratis ladbar" ist NICHT
"kommerziell frei". Jede Modell-/LoRA-Lizenz einzeln pruefen; bei Civitai die
Permission-Flags der Modellseite, nicht die Download-Moeglichkeit.

## Empfohlener Stack (kommerziell frei, 16-GB-tauglich)

### Tier A: voll sauber (Apache 2.0, Modell UND Output frei)

| Modell | Staerke | NSFW | 16 GB | Status |
|---|---|---|---|---|
| FLUX.1-schnell | Realismus, Architektur, Produkt, Text-im-Bild | nein (zahm) | fp8 | installiert |
| Chroma1-HD | Allrounder: Realismus + Anime + Furry + NSFW, FLUX-schnell-Basis, voll unzensiert | ja | Q8 GGUF (9 GB) | **installiert + getestet** |
| Qwen-Image / Z-Image-Turbo | neuere Realism-Basis; Qwen stark bei Text-im-Bild, Z-Image sehr schnell | nein | ja | optional |

**Chroma1-HD ist das Kernmodell fuer NSFW/Anime:** das einzige wirklich breite, voll
unzensierte Modell unter Apache 2.0. Deckt kommerziell sauber ab, was sonst nur
lizenzbelastete Pony/Illustrious-Finetunes koennen.

### Tier B: Output kommerziell ok, kein bezahlter Inferenz-Dienst (FAIPL 1.0)

| Modell | Staerke | Einschraenkung |
|---|---|---|
| Illustrious XL v0.1 | Anime-Spitze, riesiges LoRA-Oekosystem | Bilder verkaufen ok; Modell als Bezahl-Service nicht |

### Tier C: fuer kommerziell RAUS

- **Pony V6 XL**: modifizierte FAIPL, monetarisierte Inferenz untersagt (Graubereich). Nur mit Permission von PurpleSmartAI.
- **NoobAI**: Output kommerziell verboten.
- **FLUX.1-dev** + dev-basierte LoRAs: non-commercial ohne BFL-Lizenz.
- **XLabs flux-RealismLora** und die meisten Realism-LoRAs: dev-basiert / non-commercial.

## Vertical -> Modellempfehlung

| Vertical | Erste Wahl | Alternative |
|---|---|---|
| Landschaft / Winzer | FLUX.1-schnell | Chroma |
| Architektur / Web-Hero | FLUX.1-schnell | Chroma |
| Produkt | FLUX.1-schnell | Qwen-Image (Label/Text) |
| Menschen / Portrait | Chroma (Haut besser) | FLUX.1-schnell + Prompt-Tuning |
| Anime | Illustrious XL v0.1 | Chroma |
| NSFW (real/anime) | Chroma | - |

## Compliance bei realistischem NSFW (zusaetzlich zur Modell-Lizenz)

Die Modell-Lizenz erlaubt das Generieren, regelt aber NICHT die Verbreitung. Bei echt
wirkenden Menschen kommen separate Pflichten dazu: keine real-person-Aehnlichkeit,
Alters-/Einwilligungsnachweis bei Verbreitung, Plattform-ToS, in DE/EU JuSchG/JMStV.
Eigener Compliance-Block, bevor das ein Geschaeftszweig wird.

## Entscheidungs-Log (append-only)

- 2026-06-21: Bild-Basis FLUX.1-schnell (Apache) statt FLUX.1-dev (non-commercial).
- 2026-06-22: ComfyUI via Stability Matrix als Engine (statt InvokeAI/SwarmUI/Forge Neo).
- 2026-06-23: Chroma1-HD als kommerziell-freies Kern-Modell fuer NSFW/Anime/Realismus
  gewaehlt (einziges breit unzensiertes Apache-Modell). Pony/NoobAI verworfen (Lizenz).
- 2026-06-23: Reproduktion nativ ueber PNG-Metadaten; Ledger nur als kuratierter
  Recall-Index. Wissensbasis lebt im Skill (reference/), nicht im cwd D:\Repos.
- 2026-06-23: Chroma1-HD Q8 GGUF installiert (DiffusionModels) + t5xxl_fp8 (TextEncoders)
  + ae.safetensors lokal aus dem FLUX-All-in-one extrahiert (VAE). ComfyUI-GGUF-Node
  installiert. Getestet: Chroma loest das Haut-Thema (5* vs FLUX 4*) und kann Anime.

## Quellen

- [Chroma (Apache, uncensored)](https://www.nowadais.com/chroma-model-training-ai-image-generation/)
- [Chroma VRAM](https://willitrunai.com/image-models/chroma-1)
- [Pony V6 FAIPL](https://ponydiffusion.com/faq)
- [Illustrious vs NoobAI Lizenz](https://note.com/kazuya_bros/n/n84fa6fe9360b?hl=en)
- [Z-Image / Qwen Apache](https://www.bentoml.com/blog/a-guide-to-open-source-image-generation-models)
