# gen-asset: Plan & Architektur

Lokale Bild- (später Video-) Generierung für die Entwicklung. Code-Agenten
erzeugen brauchbare Assets selbständig, prüfen sie per Vision und verwenden sie.
Lokal auf RTX 5070 Ti (16 GB, Blackwell), offline, kostenfrei.

Stand: 2026-06-22. Status: **produktiv für Bilder.** SDXL + FLUX.1-schnell laufen
end-to-end (GPU, Auto-Start, Vision-Verify, Self-Learning-Loop). Offen: 3 LoRAs, Video.

## 1. Warum nicht ChatGPT im Browser

Ursprungsidee war, ChatGPT im Browser zu steuern. Verworfen:
- ToS-Verstoß (OpenAI verbietet automatisierten Zugriff auf die ChatGPT-UI), Sperr-Risiko.
- Fragil (Login/2FA, Bot-Detection, wechselndes DOM), hoher Wartungsaufwand.
- Kein Mehrwert gegenüber lokaler Generierung.

Ersetzt durch: **Claude denkt (Prompt + Verify) + ComfyUI rendert lokal.**

## 2. Hardware-Verdikt

- **Bilder: exzellent.** FLUX im NVFP4-Format (Blackwell-exklusiv) ist ~84 % schneller
  als fp8, braucht ~7-11 GB VRAM, Qualität via SVDQuant nahe BF16. Realistisch
  ~5-8 s/Bild auf der 5070 Ti.
- **Video: machbar, langsamer.** 16 GB ist die praktische Untergrenze. LTX-2 passt
  locker und ist schnell; Wan 2.2 / HunyuanVideo 1.5 nur quantisiert (Q5) und langsam
  (~10-14 min pro 720p-Clip).

## 3. Stability Matrix: Ist-Zustand

Engine ist da: `D:\Apps\Stability Matrix\Data\Packages\ComfyUI` (Git-Checkout).
Weitere Packages: InvokeAI, Forge Neo, SwarmUI.

**Model-Mapping (`extra_model_paths.yaml`):**

| ComfyUI-Typ | Ordner unter `Data\Models\` |
|---|---|
| checkpoints | `StableDiffusion` |
| diffusion_models (FLUX-Unet) | `DiffusionModels` |
| clip / text encoders | `TextEncoders` |
| vae | `VAE` |
| loras | `Lora`, `LyCORIS` |
| clip_vision | `ClipVision` |
| controlnet | `ControlNet`, `T2IAdapter` |

**Schon vorhanden:** SDXL-Checkpoints, v.a. `juggernautXL_v8Rundiffusion.safetensors`
(realistisch), plus viele SD1.5. Kein FLUX, keine Video-Modelle, keine Ziel-LoRAs.

### Blocker (muss vor Nutzung gelöst werden)

Das ComfyUI-venv hatte `torch 2.12.1+cpu` (CPU-only, `cuda.is_available()=False`).
GPU wird so **nicht** genutzt. Fix nötig: Torch auf `cu128` (Blackwell) bzw.
`cu130` (für NVFP4-Autoerkennung).

## 4. Lizenz (kritisch, weil kommerzielle Kundenarbeit)

| Modell | Lizenz | Kommerziell |
|---|---|---|
| FLUX.1-**schnell** | Apache 2.0 | ja, sauber |
| FLUX.1-**dev** | BFL Non-Commercial | nein ohne BFL-Lizenz |
| Wan 2.2 | Apache 2.0 | ja |
| HunyuanVideo | Tencent Community License | eingeschränkt, prüfen |
| LTX-Video / LTX-2 | LTX Open License | meist ja, prüfen |
| Civitai-LoRAs | je Modell | einzeln prüfen, viele non-commercial |
| SDXL / Juggernaut XL | CreativeML OpenRAIL-M | i.d.R. ja, prüfen |

**Entscheidung getroffen:** FLUX.1-**schnell** (Apache 2.0) als Bild-Basis.

## 5. Kuratierter Stack (minimal, deckt alle Verticals)

**Bild-Basis:**
- FLUX.1-schnell, NVFP4 (oder fp8 als Fallback) → `Models\DiffusionModels`
- t5xxl (fp8) + clip_l → `Models\TextEncoders`
- ae.safetensors (FLUX-VAE) → `Models\VAE`

**LoRAs (nur 3, einzeln auf Lizenz prüfen):**
- Realism/UltraReal (alle Verticals)
- Food Photography (Gastro)
- Arch Realism (Handwerk/Bau)

Produkt und Landschaft (Winzer) kann FLUX-Basis ohne LoRA.

**Video (zweistufig, später):**
- LTX-2: schnelle Web-Animationen, Produkt-Turntables, Ambient-Motion (Daily Driver)
- Wan 2.2 I2V (Q5_K_M GGUF): Hero-Produktvideos (optional, langsam auf 16 GB)

## 6. Setup-Schritte (wenn freigegeben)

### Phase 0: GPU-Torch-Fix (Blocker)
In Stability Matrix: ComfyUI-Package → Einstellungen → PyTorch/CUDA-Variante auf
`cu128` (bzw. `cu130` für NVFP4) stellen und neu installieren lassen. Alternativ
manuell im venv:
```powershell
& "D:\Apps\Stability Matrix\Data\Packages\ComfyUI\venv\Scripts\python.exe" -m pip install --upgrade --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```
Verifikation:
```powershell
& "D:\Apps\Stability Matrix\Data\Packages\ComfyUI\venv\Scripts\python.exe" -c "import torch;print(torch.cuda.is_available(), torch.version.cuda)"
```
Muss `True` + eine CUDA-Version liefern. Optional danach SageAttention (Blackwell)
für ~30 % mehr Tempo.

### Phase A: Bilder (~14 GB)
FLUX.1-schnell (NVFP4/fp8) + t5xxl_fp8 + clip_l + ae.safetensors + 3 LoRAs in die
oben gemappten Ordner. Bequem über den SM-Model-Browser (HF/CivitAI). Danach
Dateinamen in `workflows\flux_schnell_t2i.api.json` an die echten Files anpassen.

### Phase B: Video schnell (~+10 GB)
LTX-2-Modell + Nodes. Workflow `workflows\ltx_i2v.api.json` ergänzen.

### Phase C: Video Qualität (~+18 GB)
Wan 2.2 I2V (Q5_K_M GGUF) + umt5-Encoder + VAE. Workflow ergänzen.

## 7. Bewährte Workflows (Quellen, keine Eigenexperimente)

- FLUX T2I: offizielle ComfyUI-Templates (in ComfyUI integriert).
- Wan 2.2 I2V Low-VRAM (Q5, 16 GB): Next Diffusion Tutorial; Cordux GitHub-Workflow.
- LTX I2V: offizielles ComfyUI-Tutorial.

FLUX-Workflow-Hinweis: schnell = 4 Steps, cfg 1.0, kein echter Negative-Prompt.
Falls Node-Signaturen abweichen, Workflow einmal in der ComfyUI-UI bauen und via
"Save (API Format)" re-exportieren.

## 8. Skill-Architektur

- `SKILL.md`: Trigger, Vertical→Modell/LoRA-Mapping, Ablauf inkl. Verify-Loop.
- `scripts\comfy_generate.py`: stdlib-only (urllib). Lädt Workflow-Template,
  injiziert Parameter per `_meta.title`-Marker (POSITIVE_PROMPT, NEGATIVE_PROMPT,
  LATENT, SAMPLER, CHECKPOINT, LORA), POST `/prompt`, pollt `/history`, lädt via
  `/view`. Stdout = finaler Pfad. Konfigurierbar über `--url` / `COMFYUI_URL`
  (Default `http://127.0.0.1:8188`).
- `workflows\*.api.json`: ComfyUI API-Format-Templates mit Titel-Markern.
  Vorhanden: `sdxl_t2i.api.json` (läuft heute mit Juggernaut XL), `flux_schnell_t2i.api.json`
  (nach Phase A, Dateinamen anpassen).
- Verify-Loop: Claude liest Output per `Read`-Tool (Vision), prüft Motiv,
  Seitenverhältnis, Artefakte, Text, Markenfit; bei Fehlschlag Prompt/Seed/LoRA
  nachschärfen, max. ~4 Iterationen.
- **Self-Learning-Loop (nativ + schlanker Recall-Index):**
  - **Reproduktion = nativ.** `comfy_generate.py` bettet den Workflow via
    `extra_pnginfo` in jedes PNG ein (zusätzlich zum `prompt`-Chunk, den ComfyUI eh
    setzt). Damit trägt jedes Bild sein Rezept selbst: in ComfyUI ziehen lädt den
    Graph, oder programmatisch aus den PNG-tEXt-Chunks lesen. KEIN Sidecar.
    Bewusste Entscheidung gegen ein eigenes recipe.json (wäre Dublette zur
    PNG-Metadaten, gegen KISS/Reuse).
  - **Recall = der einzige Zusatz**, den ComfyUI/SM nicht haben: `scripts\ledger.py`
    ist ein kuratierter, bewerteter, nach Vertical durchsuchbarer Index
    (`reference\ledger.jsonl`). `add --image ... --rating --vertical --tags` (liest
    Prompt/Seed aus den PNG-Metadaten), `find --vertical X --min-rating N` holt
    bewährte Bilder als Startpunkt. Eintrag zeigt aufs PNG (= Repro-Quelle).
  - Manuelles Sichten weiter über die Stability-Matrix-Galerie (`Data\Images`).

## 9. Roadmap / Status

- [x] Recherche (Hardware, Modelle, Lizenz, Video)
- [x] Skill-Gerüst (SKILL.md, Script, SDXL- + FLUX-Workflow, Doc)
- [x] Phase 0: GPU-Torch erledigt durch ComfyUI-Update (torch 2.12.1+cu130, GPU ok)
- [x] Auto-Start-Helper (ensure_comfyui.ps1) + End-to-End-Test mit SDXL/Juggernaut XL
      bestanden (Winzer-Landschaft, vollautonom, Vision-Verify PASS)
- [x] Phase A (Bild): FLUX.1-schnell-fp8 (Comfy-Org All-in-one, 17 GB, Apache 2.0)
      geladen unter `StableDiffusion\flux1-schnell-fp8.safetensors`. Workflow auf
      CheckpointLoaderSimple umgestellt (All-in-one statt getrennter Encoder),
      End-to-End-Test bestanden (Winzer, Vision-Verify PASS, Prompt-Treue > SDXL).
- [x] Self-Learning-Loop: native Repro (Workflow in PNG-Metadaten) + schlanker
      kuratierter Recall-Index (ledger.py). Recipe-Sidecar/--from-recipe wieder
      entfernt (redundant zur PNG-Metadaten, KISS).
- [x] `.imagegen` (web-mvps) aufgeräumt: venv ~4,5 GB entfernt, Compositing-Rezept
      + Quellbilder nach `mvps/interactive-discovery/tools/imagegen/` gesichert.
- [x] Chroma1-HD (Q8 GGUF) installiert + getestet: löst Haut-Thema (Menschen 5* vs FLUX 4*),
      kann Anime, unzensiert (NSFW), kommerziell frei (Apache). Workflow chroma_t2i.api.json,
      ComfyUI-GGUF-Node + t5xxl_fp8 + extrahierte ae.safetensors.
- [ ] Optional: Illustrious XL v0.1 für reinen Anime-Look; LoRAs erst bei konkretem Fall.
- [ ] Reverse-Engineering einzelner Altbilder (Nutzer nennt Bilder).
- [ ] Phase B: LTX-2 I2V-Workflow
- [ ] Phase C: Wan 2.2 I2V-Workflow

## 10. Offene Punkte

- Port 8188 bestätigt (ComfyUI läuft dort, Auto-Start ok).
- FLUX läuft als All-in-one-fp8-Checkpoint (`flux1-schnell-fp8.safetensors`), keine
  getrennten Encoder nötig. NVFP4-Variante (Blackwell, ~84 % schneller) optional
  als späteres Upgrade, fp8 reicht und ist getestet.
- LoRA-Lizenzen einzeln vor kommerzieller Nutzung prüfen.
- `.imagegen` unter `D:\Repos\web-mvps` (~12,5 GB redundant) noch nicht aufgeräumt,
  wartet auf OK (Whisper-Modelle dort bleiben, sind unabhängig).

## Quellen

- [ComfyUI NVFP4 2026 Guide](https://runaihome.com/blog/comfyui-nvfp4-rtx-speed-guide-2026/)
- [NVIDIA: FP4 Image Generation auf Blackwell RTX 50](https://developer.nvidia.com/blog/nvidia-tensorrt-unlocks-fp4-image-generation-for-nvidia-blackwell-geforce-rtx-50-series-gpus/)
- [ComfyUI Blackwell Support-Thread (#6643)](https://github.com/Comfy-Org/ComfyUI/discussions/6643)
- [Blog: ComfyUI auf RTX 50 zum Laufen bringen](https://blog.comfy.org/p/how-to-get-comfyui-running-on-your)
- [SageAttention Blackwell (#11583)](https://github.com/Comfy-Org/ComfyUI/discussions/11583)
- [Local AI Video Generation 2026 (Wan/LTX/Hunyuan)](https://localaimaster.com/blog/local-ai-video-generation)
- [Open Source AI Video Models Vergleich 2026](https://www.aimagicx.com/blog/open-source-ai-video-models-comparison-2026)
- [Wan 2.2 I2V GGUF Low-VRAM Tutorial](https://www.nextdiffusion.ai/tutorials/how-to-run-wan22-image-to-video-gguf-models-in-comfyui-low-vram)
- [Wan 2.2 offizieller ComfyUI-Workflow](https://docs.comfy.org/tutorials/video/wan/wan2_2)
- [FLUX Arch Realism LoRA (Civitai)](https://civitai.com/models/709956/flux-arch-realism-lora)
- [Ultimate Food Photography LoRA (Civitai)](https://civitai.com/models/1202156/ultimate-high-resolution-food-photography-flux-or-realistic-food-lora)
