# gen-asset: Lernschleife (empirische Erkenntnisse)

Wird mit jeder Generierung reicher. **Vor dem Generieren lesen, nach einem auffaellig
guten oder schlechten Ergebnis ergaenzen.** Roh-Datenpunkte (pro Bild: Modell, LoRA,
Vertical, Rating, Prompt, Seed) stehen im `ledger.jsonl`; hier die destillierten Muster.

Zweck: Bildqualitaet wird ueber die Zeit besser, weil wir wissen, welches Modell + welcher
Prompt + welche LoRA fuer welches Vertical gute Ausgaben liefert, und wofuer ein Modell
taugt oder eher nicht.

## Allgemein

- **FLUX.1-schnell:** 4 Steps, cfg 1.0, **ignoriert Negativ-Prompts** weitgehend. Steuerung
  laeuft ueber den Positiv-Prompt. Fuer echte Negativ-Kontrolle Chroma/SDXL nutzen.
- **Schaerfe:** Hires-Pass (Latent-Upscale 1.5x + 2. Sampler-Pass denoise ~0.45) statt nur
  groesserer Maße. Im Prompt `crisp sharp focus, fine detail`. Weichmacher
  (`haze, shallow depth of field, bokeh, soft`) nur wenn gewollt.

## Haut / Menschen (GELOEST mit Chroma)

- FLUX.1-schnell: Gesicht ok, aber Haut zu glatt/glaenzend ("KI-Look"). 4 Steps + kein
  echtes Negativ limitieren.
- **Chroma1-HD loest es:** echte Hauttextur, Poren, Film-Look, kein Plastik. Im direkten
  Vergleich (gleiche Szene) klar besser, Ledger: chroma_mensch 5* vs test_mensch (FLUX) 4*.
- Prompt-Hebel (hilft bei beiden): `visible skin pores, natural skin texture, subsurface
  scattering, slight imperfections, shot on 35mm film, Kodak Portra, analog photo, candid`.
- Vermeiden: `perfect, flawless, beautiful, smooth, glossy` (treiben Richtung Plastik).
- Bei Chroma echten Negativ-Prompt nutzen: `plastic skin, airbrushed, waxy, cgi, 3d render,
  doll, overprocessed, glossy, smooth`.

## Vertical-Verdikte (FLUX.1-schnell, Basis ohne LoRA, Stand 2026-06-23)

| Vertical | Verdikt | Rating |
|---|---|---|
| Landschaft / Winzer | exzellent | 5 |
| Architektur / Web-Hero | exzellent (Blue Hour, Glas, dramatischer Himmel) | 5 |
| Produkt | sauberes Studio-Bild, dezente Reflexion | 4 |
| Handwerk / Bau (Person) | authentisch; Gesicht/Details leicht weich | 4 |
| Menschen / Portrait | gut; Haut-Thema (siehe oben) | 4 |

## Pro Modell (waechst)

- **FLUX.1-schnell:** stark fuer Landschaft/Architektur/Produkt; schwach bei Haut; kein
  NSFW; kein echtes Negativ; sehr schnell (4 Steps).
- **Chroma1-HD (Q8 GGUF, installiert):** besser bei Haut/Realismus (Menschen), kann Anime,
  unzensiert (NSFW), echtes Negativ, kommerziell frei (Apache). Settings: 26 Steps, cfg 4.0,
  sampler euler, scheduler beta. Langsamer als schnell (9B, mehr Steps). Workflow:
  chroma_t2i.api.json. Modell laeuft via UnetLoaderGGUF, T5 via CLIPLoader type "chroma".

## FLUX-schnell vs Chroma (gemessen 2026-06-23)

- Gleiche Szene (Winzer, Architektur): Chroma-Qualitaet gleichwertig oder besser.
- **Tempo ist der Unterschied:** Chroma ~50 s/Bild, FLUX-schnell ~5-8 s/Bild (~8x). Grund:
  9B + 26 Steps vs 4 Steps.
- **Faustregel:** FLUX-schnell = schneller SFW-Allrounder (Landschaft/Architektur/Produkt,
  viele Iterationen, Batches). Chroma = wenn Menschen/Haut, Anime, NSFW oder maximale
  Flexibilitaet (echtes Negativ) gebraucht werden und Zeit egal ist. Komplementaer, beide behalten.

## Abstrakte Geometrie / exakte Anzahlen (FLUX-schnell, 2026-07-02)

- **FLUX kann nicht zaehlen:** "exactly eight petals" liefert 9-20 Blaetter. Wortwahl
  hilft nur bedingt ("mandala" triggert VIELE Blaetter -> vermeiden; "compass rose,
  45 degree spacing, wide gaps between petals" hilft Richtung wenige).
- **Seed-Lotterie funktioniert:** gleicher Prompt, 3-5 Seeds a ~6 s, Blaetter im
  Vision-Verify zaehlen. Trefferquote exakt-8 lag bei ~1/5 (Seed 22222 traf).
- **Farbvariante bei gleicher Komposition:** gleicher Seed + nur Farbwoerter im Prompt
  tauschen ergibt aehnliche (nicht identische) Komposition mit gleicher Blattzahl.
- Neon-Plexus-Look auf near-black: "almost black very dark navy background that fades
  to pure darkness at all image edges" noetig, sonst hellblauer Verlaufs-Hintergrund
  (bricht Seamless-Einbettung in dunkle Websites). Rezept-Bilder: ledger vertical=web.
- **Chroma1-HD schlaegt FLUX-schnell fuer Neon-Plexus-/Partikel-Art deutlich**
  (User-Verdikt 2026-07-02): FLUX-Ergebnisse wirken flach/sticker-artig, Chroma
  (26 Steps, echtes Negativ "flat, low detail, plain, simple...") liefert dichte
  Partikel-Faserstroeme, Volumen-Glow, GPT-Bildmodell-Niveau. Die frueheren
  FLUX-Ledger-Eintraege (sym-violet 5*, sym-green 4*) sind damit relativiert;
  Referenz ist hero-bloom-chroma-violet. Kosten: ~50 s statt ~6 s pro Bild.

## Upscaling

- `scripts/upscale.py` + `workflows/upscale.api.json`: UltimateSDUpscale, re-diffundiert
  Kacheln mit SDXL Juggernaut + 4x-UltraSharp. ~40 s fuer 2x (1216x832 -> 2432x1664),
  schaerft + ergaenzt Mikro-Detail ohne Stilbruch. `--denoise` 0.15 (treu) bis 0.35 (mehr Detail).
- Alte mehrstufige SD1.5-Upscale-/FaceDetailer-Workflows (ptdv3) NICHT resurrecten: FLUX/Chroma
  loesen nativ hoch auf, Face-Fix kaum noetig. Fuer >nativ: upscale.py. Fuer Maximal-Foto-Detail
  waere SUPIR die schwerere Alternative (noch nicht aufgesetzt).

## Anime: dediziertes Modell schlaegt Generalist (wichtig)

- Polierte Anime-Originale (GhostMix, CelestReal3) sind dedizierte Anime-Merges, oft +
  Detail-LoRA + Hires-Fix. Chroma (Generalist) trifft den Stil, aber nicht die letzte Politur.
- **Bewiesen:** GhostMix + "Add More Details"-LoRA + Hires (Workflow sd15_anime_hires.api.json)
  liefert klar mehr Detail/Politur als Chroma. SD1.5 BRAUCHT Negativ-Prompts (anders als FLUX).
- ABER roher GhostMix driftet schnell suggestiv (Cleavage/cheesecake) und weg von einer modesten
  Vorlage -> Prompt eng fuehren (Pose/Kleidung explizit) + ggf. Negativ `cleavage, revealing`.
- Workflow sd15_anime_hires.api.json: GhostMix + Detail-LoRA (0.7) + Hires 1.8x (512x768 ->
  920x1384). Fuer Catgirl-Typ (CelestReal nicht installiert) PerfectDeliberate-Anime oder GhostMix testen.
- Lizenz: GhostMix u.a. SD1.5-Merges = Civitai-Permissions pruefen vor kommerzieller Nutzung.
- **GhostMix cheesecake-Bias:** figur-/koerper-fokussierte Prompts (goddess, gown, beautiful woman)
  erzwingen Dekollete/freizuegig TROTZ starkem Negativ (cleavage, bare shoulders...). Gegenmittel:
  (a) fractal-/szene-DOMINANTER Prompt statt koerper-fokussiert (so entstand das modeste Original),
  (b) Chroma fuer garantiert modest, (c) SFW-leaning Anime-Modell (Illustrious). Catgirl-Typ mit
  PerfectDeliberate-Anime klappte modest + poliert (bestes Catgirl-Ergebnis).
- **Anatomie:** SD1.5-Anime-Modelle (PerfectDel-Anime, GhostMix) neigen zu extra Armen / falschen
  Fingern bei komplexen Posen. Negativ um `extra arms, extra limbs, bad hands, missing fingers,
  fused fingers` erweitern, sonst rerollen oder Hand-Fix. Décolleté ist KEIN Tabu (legal/unkritisch).
- **Pixelig/Aufloesung:** hoher Latent-Hires (>2x bislerp) kann Glitch-Baender erzeugen. Besser:
  moderat hires + danach `upscale.py --checkpoint <anime-model>` (anime-konsistente Tile-Refine,
  z.B. Catgirl v5 920x1384 -> 1472x2216 sauber).

## Chroma vs Anime-Modell, wann was
- Realismus/Menschen/Haut, Landschaft (mit FLUX), Produkt: Chroma/FLUX.
- Polierter Anime/Illustration: dediziertes Anime-Modell (GhostMix/Illustrious) + Detail-LoRA + Hires.

## Iterationen / Versionierung (Prozess-Regel)

- Bei Optimierungs-Iterationen die Datei NIE ueberschreiben. Sonst geht der Entwicklungsstand
  verloren und eine fruehere Version war evtl. besser. Stattdessen versionieren:
  `<name>_v2.png`, `_v3.png` ... und jede via `ledger.py add` mit Rating festhalten, damit
  klar bleibt, welche Version die beste ist.
- Rueckfall-Archiv: ComfyUI speichert ohnehin JEDE Generierung als
  `Data\Packages\ComfyUI\output\genasset_NNNNN.png` (durchnummeriert, mit eingebettetem Prompt).
  Daraus lassen sich verlorene Versionen rekonstruieren.

## Erotische Motive -> SFW (Migration)

- Nicht Begriffe umbenennen (gleiches Bild), sondern den sexuellen/Anatomie-Fokus ENTFERNEN und
  nur den legitimen Kern behalten (Strand/Cyberpunk/Magierin/Goettin in normaler Kleidung).
  Negativ-Prompt mit `nsfw, nude, revealing, suggestive, cleavage` absichern. Ergebnis echt SFW.
