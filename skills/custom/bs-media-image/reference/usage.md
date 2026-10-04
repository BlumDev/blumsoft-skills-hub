# gen-asset: Kurzanleitung Kommandozeile

Für den Klickweg in der ComfyUI-Oberfläche stattdessen [bedienung.md](bedienung.md) lesen.

**Kein Repo**, sondern der Skill-Ordner: `C:\Users\Marcus\.claude\skills\bs-media-image`
**Terminal: PowerShell.** Python: `D:\SDKs\Python311\python.exe`. ComfyUI muss laufen.

Tipp: Pfade sind lang, am einfachsten Variablen setzen:
```powershell
$py  = "D:\SDKs\Python311\python.exe"
$ga  = "C:\Users\Marcus\.claude\skills\bs-media-image"
```

## 0. ComfyUI sicherstellen (headless, ohne SM-Fenster)
```powershell
powershell -File "$ga\scripts\ensure_comfyui.ps1"
```
Idempotent: startet ComfyUI nur, wenn nicht schon auf Port 8188 aktiv. Erster Start ~25 s.

## 1. Bild erzeugen
```powershell
& $py "$ga\scripts\comfy_generate.py" `
  --workflow "$ga\workflows\zimage_turbo_t2i.api.json" `
  --prompt "<englischer Prompt>" `
  --width 1216 --height 832
```
Stdout = Pfad in der Bildbibliothek (`Text2Img\<workflow>\`, Testreihen unter `Text2Img\_tests\<reihe>\`), keine zweite Kopie. Seed kommt auf stderr. `--out` ist optional: innerhalb der Bibliothek ein Hardlink (etwa `library\<vertical>\name.png`), sonst eine Kopie, nach `out\` wird es abgelehnt (Zweitkopie auf C:). Workflow je nach Zweck (siehe unten).

## 2. Ein bestehendes Bild exakt reproduzieren (`--reproduce`)
```powershell
& $py "$ga\scripts\comfy_generate.py" --reproduce "<bild>.png"
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
& $py "$ga\scripts\upscale.py" --image "<bild>.png" --upscale-by 2.0 --denoise 0.2
```
UltimateSDUpscale (CyberRealistic Pony als Refiner + 4x-UltraSharp), 37 s für 1024 auf 2048, Ergebnis unter `Text2Img\upscale\upscale_*.png` (Stdout).
`--denoise` niedrig (0.15) = originaltreuer, höher (0.35) = mehr erfundenes Detail. Das Bild
wird selbst in ComfyUIs input-Ordner kopiert, kein manuelles Hochladen nötig.

## Workflows (Stand 19.09.2026, fünf Modellfamilien)
- `zimage_turbo_t2i.api.json`: Default für Fotorealismus, 12 bis 17 s, kein Negativ-Prompt.
- `zimage_cutout.api.json`: freistehendes Motiv als RGBA-PNG (Z-Image + BiRefNet), etwa 20 s.
- `birefnet_matte.api.json`: vorhandenes Bild freistellen, `--image`, 2 bis 4 s.
- `upscale.api.json`: bestehendes Bild hochskalieren (siehe Abschnitt 5).
- `qwen_2512_t2i.api.json`: englischer Text im Bild, Lichtstimmung, 13 bis 30 s.
- `qwen_edit_2511.api.json`: vorhandenes Bild per Anweisung ändern, `--image`, 26 bis 33 s.
- `illustrious_t2i.api.json`: Anime, Danbooru-Tags, 40 Steps, etwa 20 s.
- `pony_t2i.api.json`: Menschen und Posen, Prompt mit `score_9, score_8_up, score_7_up,` beginnen.
- `zimage_nsfw_t2i.api.json`: nur für den Nutzer selbst, siehe Leitplanke in SKILL.md.

## ComfyUI manuell starten (GUI, zum Lernen/Optimieren)
1. Headless-Instanz stoppen, damit Port 8188 frei ist:
   ```powershell
   Get-Process python | Where-Object { $_.Path -like "*Stability Matrix*ComfyUI*" } | Stop-Process -Force
   ```
2. In Stability Matrix: Packages → ComfyUI → Launch (öffnet Web-UI).
3. Workflow ansehen: erzeugtes PNG in die Canvas ziehen (Graph lädt), oder Dev-Mode
   aktivieren (Settings → "Enable Dev mode Options") → "Load (API Format)" → eine `*.api.json`.
