# gen-asset: Bedienung (Kurzanleitung)

**Kein Repo**, sondern der Skill-Ordner: `C:\Users\Marcus\.claude\skills\gen-asset`
**Terminal: PowerShell.** Python: `D:\SDKs\Python311\python.exe`. ComfyUI muss laufen.

Tipp: Pfade sind lang, am einfachsten Variablen setzen:
```powershell
$py  = "D:\SDKs\Python311\python.exe"
$ga  = "C:\Users\Marcus\.claude\skills\gen-asset"
```

## 0. ComfyUI sicherstellen (headless, ohne SM-Fenster)
```powershell
powershell -File "$ga\scripts\ensure_comfyui.ps1"
```
Idempotent: startet ComfyUI nur, wenn nicht schon auf Port 8188 aktiv. Erster Start ~25 s.

## 1. Bild erzeugen
```powershell
& $py "$ga\scripts\comfy_generate.py" `
  --workflow "$ga\workflows\flux_schnell_t2i.api.json" `
  --prompt "<englischer Prompt>" --negative "" `
  --width 1024 --height 1024 `
  --out "D:\Apps\Stability Matrix\Data\Images\library\<vertical>\name.png"
```
Stdout = finaler Bildpfad. Seed kommt auf stderr. Workflow je nach Zweck (siehe unten).

## 2. Ein bestehendes Bild exakt reproduzieren (`--reproduce`)
```powershell
& $py "$ga\scripts\comfy_generate.py" --reproduce "<bild>.png" --out "<neu>.png"
```
Liest den in der PNG eingebetteten ComfyUI-Graph und erzeugt das Bild neu (byte-identisch
bei gleichem Modell). **Nur bei ComfyUI-erzeugten PNGs** (A1111-Bilder haben keinen Graph).
Zum Ansehen/Editieren stattdessen: Bild in die ComfyUI-Canvas ziehen (GUI, siehe unten).

## 3. Recall: bewährte Bilder finden
```powershell
& $py "$ga\scripts\ledger.py" find --vertical menschen --min-rating 4
```

## 4. Gutes Bild merken (nach Vision-Verify, Rating 4-5)
```powershell
& $py "$ga\scripts\ledger.py" add --image "<bild>.png" --rating 5 --vertical menschen --tags "hero,portrait"
```

## 5. Bestehendes Bild hochskalieren

```powershell
& $py "$ga\scripts\upscale.py" --image "<bild>.png" --out "<bild>_2x.png" --upscale-by 2.0 --denoise 0.2
```
UltimateSDUpscale (SDXL-Juggernaut-Tiles + 4x-UltraSharp), ~40 s fuer 2x. `--denoise` niedrig
(0.15) = originaltreuer, hoeher (0.35) = mehr erfundenes Detail. Das Bild wird selbst in
ComfyUIs input-Ordner kopiert, kein manuelles Hochladen noetig.

## Workflows
- `flux_schnell_t2i.api.json`: schnell (~6 s), SFW (Landschaft/Architektur/Produkt).
- `chroma_t2i.api.json`: Menschen/Haut, Anime, NSFW, echtes Negativ (~50 s).
- `sdxl_hires.api.json` / `sdxl_t2i.api.json`: SDXL-Tests.
- `upscale.api.json`: bestehendes Bild hochskalieren (UltimateSDUpscale, siehe Abschnitt 5).

## ComfyUI manuell starten (GUI, zum Lernen/Optimieren)
1. Headless-Instanz stoppen, damit Port 8188 frei ist:
   ```powershell
   Get-Process python | Where-Object { $_.Path -like "*Stability Matrix*ComfyUI*" } | Stop-Process -Force
   ```
2. In Stability Matrix: Packages → ComfyUI → Launch (öffnet Web-UI).
3. Workflow ansehen: erzeugtes PNG in die Canvas ziehen (Graph lädt), oder Dev-Mode
   aktivieren (Settings → "Enable Dev mode Options") → "Load (API Format)" → eine `*.api.json`.
