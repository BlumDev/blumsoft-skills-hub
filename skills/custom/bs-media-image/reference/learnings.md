# gen-asset: Lernschleife (empirische Erkenntnisse)

Wird mit jeder Generierung reicher. **Vor dem Generieren lesen, nach einem auffaellig
guten oder schlechten Ergebnis ergaenzen.** Roh-Datenpunkte (pro Bild: Modell, LoRA,
Vertical, Rating, Prompt, Seed) stehen im `ledger.jsonl`; hier die destillierten Muster.

Zweck: Bildqualitaet wird ueber die Zeit besser, weil wir wissen, welches Modell + welcher
Prompt + welche LoRA fuer welches Vertical gute Ausgaben liefert, und wofuer ein Modell
taugt oder eher nicht.

## Allgemein

- **FLUX.1-schnell:** 4 Steps, cfg 1.0, **ignoriert Negativ-Prompts** weitgehend. Steuerung
  laeuft ueber den Positiv-Prompt. Für echte Negativ-Kontrolle Chroma/SDXL nutzen.
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
  loesen nativ hoch auf, Face-Fix kaum noetig. Für >nativ: upscale.py. Für Maximal-Foto-Detail
  waere SUPIR die schwerere Alternative (noch nicht aufgesetzt).

## Anime: dediziertes Modell schlaegt Generalist (wichtig)

- Polierte Anime-Originale (GhostMix, CelestReal3) sind dedizierte Anime-Merges, oft +
  Detail-LoRA + Hires-Fix. Chroma (Generalist) trifft den Stil, aber nicht die letzte Politur.
- **Bewiesen:** GhostMix + "Add More Details"-LoRA + Hires (Workflow sd15_anime_hires.api.json)
  liefert klar mehr Detail/Politur als Chroma. SD1.5 BRAUCHT Negativ-Prompts (anders als FLUX).
- ABER roher GhostMix driftet schnell suggestiv (Cleavage/cheesecake) und weg von einer modesten
  Vorlage -> Prompt eng fuehren (Pose/Kleidung explizit) + ggf. Negativ `cleavage, revealing`.
- Workflow sd15_anime_hires.api.json: GhostMix + Detail-LoRA (0.7) + Hires 1.8x (512x768 ->
  920x1384). Für Catgirl-Typ (CelestReal nicht installiert) PerfectDeliberate-Anime oder GhostMix testen.
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

## Freistellung: BiRefNet-Matting schlägt Chroma-Key (2026-08-13, bildstil-lab-Vergleichstest)

Kontrollierter A/B-Test am fixen Motiv-Set (FIGUR 40 px, SYMBOL 24 px, HINTERGRUND
vollflächig, flachvektor-Prompt, Seeds fix), vier Varianten: FLUX+keyout (Baseline),
FLUX+BiRefNet, Chroma1-HD (40 Steps, cfg 3.0, echter Negativ-Prompt)+keyout,
Chroma+BiRefNet. Vollständiger Bericht mit Bildern, Montagen und allen Messwerten:
`D:\Repos\bildstil-lab\docs\vergleich-2026-08-13\vergleich.md`.

- **Freistellung, Sieger BiRefNet:** entfernt den bekannten FLUX-Bodenschatten fast
  vollständig (Figur: 199 011 auf 191 005 sichtbare px) und den grünen Sprenkelsaum an
  Kontur-Kanten (Symbol bei 24 px im Zoom grünsaumfrei, Baseline nicht). Kostet ~1,5-3 s
  Matting-Mehrzeit pro Bild, dafür weichere Kante (Alpha-Härte 4,1 % statt 2,4 %).
  **Neuer Standard für freigestellte Motive**, materialisiert als
  `workflows/flux_schnell_cutout.api.json` (ein Graph: FLUX-schnell-Generierung +
  BiRefNetUltraV2 + ImageCombineAlpha, ein `comfy_generate.py`-Aufruf, Ausgabe direkt
  RGBA). `tools/keyout.py` bleibt Offline-Fallback ohne ComfyUI.
- **Modellwahl bleibt FLUX-schnell, auch mit Freistellung:** Chroma1-HD verliert alle
  drei Prüfmotive trotz seines echten Negativ-Prompts (der technische Hauptvorteil
  gegenüber FLUX). Bei der Figur bleibt der Bodenschatten trotz Negativ-Prompt stehen,
  beim Symbol rendert Chroma sogar einen zusätzlichen dunkelgrünen Flat-Design-
  Langschatten (359 280 statt ~76 000 sichtbare Pixel nach dem Key, unbrauchbar), beim
  Hintergrund verfehlt Chroma das verbindliche Nacht-Motiv (liest sich als
  Sonnenuntergang). Dazu ~5x Generierungszeit (78-92 s statt 15-21 s je Bild). Diese
  Verlierer-Rolle gilt für dieses flach-vektorielle Stil-Set, NICHT allgemein: die
  Chroma-Empfehlung für Haut/Menschen/Anime/NSFW weiter oben bleibt unverändert, dort
  war Chroma nicht Gegenstand dieses Tests.
- **BiRefNet ist kein garantierter Schattenentferner:** bei Chroma+BiRefNet (V4) hat
  BiRefNet den kräftigeren Chroma-Langschatten als Motivteil klassifiziert und komplett
  behalten, beim Symbol blieb zusätzlich ein grüner Fransenrest. Bei der Materialisierung
  des Workflows am 2026-08-13 mit einem eigenen Testmotiv (Herz-Icon) reproduziert: ein
  ungewollt mitgerendertes grünes Flat-Design-Langschatten-Element wurde von BiRefNet als
  Vordergrund erkannt und blieb opak stehen, obwohl der reine Hintergrund sauber entfernt
  wurde. Verify-Loop bleibt deshalb Pflicht, auch bei BiRefNet-Ausgaben.
- **Betriebs-Kanten von BiRefNet-General, einmalig gelöst:** Auto-Download in
  `comfyui_layerstyle` ist für diese Version kaputt (toter elif-Zweig), manueller
  `snapshot_download` nötig; das venv hat `timm 0.6.13` ohne `timm.layers`, `birefnet.py`
  im Modellordner lokal auf `timm.models.layers` gepatcht; Gewichte kamen als fp16, die
  LayerStyle-Node braucht fp32, einmalig konvertiert. Nach einem fehlgeschlagenen
  Ladeversuch cached ComfyUI die Loader-Node über die Node-ID hinweg, erst `POST /free`
  erzwingt den Neu-Load. Alles bereits erledigt, nur bei einer Neuinstallation relevant.
- **Entscheidungsregel:** freistehendes Motiv + ComfyUI läuft -> `flux_schnell_cutout.api.json`
  (FLUX-schnell + BiRefNet). Kein ComfyUI erreichbar -> FLUX-Raw generieren + `keyout.py`.
  Haut/Menschen/Anime/NSFW -> weiterhin Chroma1-HD (von diesem Test nicht widerlegt), dort
  aber bei freistehenden Motiven zusätzlich vorsichtig sein: Chroma neigt bei flachen
  Icon-/Symbol-Stilen zu selbstgerendertem Langschatten, den auch BiRefNet nicht
  zuverlässig entfernt.

## Freistellung: BiRefNet ist kein Pauschalrezept (2026-08-15, bildstil-lab-Katalog)

Umsetzung der Empfehlung von oben auf 16 Bestandsstile (44 freigestellte Motive). Vollständiger
Bericht: `D:\Repos\bildstil-lab\docs\freistellung-2026-08-15.md`.

- **Roh-Bilder muss man nicht neu erzeugen.** ComfyUI archiviert jede Generierung als
  `Data\Packages\ComfyUI\output\genasset_NNNNN.png`. Da `keyout.py` per Flood-Fill nur
  randzusammenhängende Pixel ändert, lässt sich zu einem fertigen Cutout das zugehörige Roh-Bild
  über einen exakten RGB-Vergleich an 400 zufälligen opaken Koordinaten eindeutig finden (44 von 48
  Treffern, Nicht-Treffer waren nachbearbeitete Bilder). Neu-Matten statt Neu-Generieren spart die
  Modell-Lotterie komplett.
- **Neues Werkzeug `scripts/comfy_matte.py` + `workflows/birefnet_matte.api.json`:** mattet ein
  BESTEHENDES Bild (Upload über `/upload/image`, LoadImage → BiRefNetUltraV2 → ImageCombineAlpha).
  Gegenstück zu `comfy_generate.py`, nur Stdlib, 2 bis 4 s pro Bild. Determinismus belegt: das
  Ergebnis ist pixelidentisch mit der V2-Variante des Vergleichstests.
- **Drei belegte Fälle, in denen der Chroma-Key GEWINNT** (Ergänzung zur Grenze "kein garantierter
  Schattenentferner"): (1) offene Linienstile, BiRefNet nimmt die Silhouette als Vordergrund und
  füllt die Zwischenräume der Zeichnung mit dem Hintergrund-Grün (Blaupause, Holzschnitt: Schild
  wird flächig grün); (2) heller Grund statt Grün, dort hält BiRefNet den Papiergrund für Motiv
  (Tuschezeichnung: 106 410 auf 362 246 sichtbare Pixel); (3) spiegelnde Ränder behalten die
  Key-Farbe als Tönung. Faustregel: BiRefNet für geschlossene, plastische Motive, Chroma-Key für
  offene Linienzeichnungen.
- **Umgekehrt behebt BiRefNet Fehler, die der Key prinzipbedingt nicht kann:** helle Motivteile, die
  farblich nah am Key liegen, frisst der Flood-Fill weg (ein Turm hatte ein Loch von 40 000 Pixeln
  in der beleuchteten Wand); ein Leucht-Motiv strahlt in den Key ab und behält einen grünen Hof
  (42 863 auf 411 grün-dominante Pixel). Beide Fälle brauchten vorher motivweises Toleranz-Tuning,
  das entfällt jetzt.
- **Die naheliegende Kennzahl trägt das Urteil nicht.** "Grün-dominante sichtbare Pixel" steigt bei
  Motiven, die selbst grün sind (grüne Spielfiguren, Moos-Türme), obwohl der Freistellungsrest
  verschwindet. Messen ja, entscheiden am Bild.

## API-Workflow in einen UI-Workflow wandeln (2026-08-15)

Damit der Nutzer dieselben Workflows anklicken kann, statt sie über die Kommandozeile zu
fahren: `scripts/api_to_ui_workflow.py` baut aus jeder `workflows/*.api.json` einen
UI-Graphen nach `ComfyUI\user\default\workflows\gen-asset\`. Zwei Fallen, beide durch einen
Rückwärtstest gefunden, nicht durch Hinsehen:

- **Widget-Reihenfolge verrutscht lautlos.** Die Oberfläche hängt hinter jeden INT namens
  `seed` oder `noise_seed` ein zweites Widget (`control_after_generate`). `object_info` meldet
  das Flag aber nur für Kern-Nodes: UltimateSDUpscale hat es nicht im Schema und bekommt das
  Widget trotzdem. Fehlt es in der erzeugten Datei, rutschen ALLE weiteren Werte des Knotens
  um eine Position (steps bekam den cfg-Wert, cfg den Sampler-Namen). Nichts stürzt ab, das
  Bild wird nur falsch. Regel: Flag ODER Name in (seed, noise_seed).
- **Eigene Widget-Typen erkennt keine Typenliste.** LoadImage hat `upload` vom Typ IMAGEUPLOAD.
  Verlässlicher als jede Liste ist: liefert der API-Graph für einen Eingang einen festen Wert
  statt einer Verlinkung, ist es ein Widget.
- **Der Test, der beides gefunden hat:** die erzeugte UI-Datei im laufenden Frontend laden und
  von dort zurückrechnen lassen, dann gegen das Original vergleichen. Im Browser:
  `await app.loadGraphData(wf); (await app.graphToPrompt()).output`. Das prüft gegen die echte
  Oberfläche statt gegen meine Annahme über sie. Danach zusätzlich zwei Workflows per
  `app.queuePrompt(0)` wirklich laufen lassen und die Bilder ansehen.
- **Zum Anschauen der Oberfläche:** Screenshots über die Browser-Leiste scheitern, wenn das
  Fenster nicht sichtbar ist, `javascript_tool` und `fetch` gegen die ComfyUI-API funktionieren
  in derselben Lage weiter. Für das reine Bild `~\.claude\scripts\shot.js` nehmen.

## ComfyUI-venv: opencv-Kollision (2026-08-15, einmalig gelöst)

- **Symptom:** `import cv2; cv2.__version__` wirft AttributeError, fünf Node-Pakete laden nicht
  (was-ns, impact-pack, impact-subpack, advancedliveportrait, prompt-reader-node), in
  `comfyui_layerstyle` fällt `guidedFilter` aus.
- **Ursache:** `opencv-python`, `opencv-python-headless` und `opencv-contrib-python` lagen
  gleichzeitig im venv (alle 4.13.0.92). Alle drei installieren in dasselbe Verzeichnis
  `site-packages\cv2`, die letzte Deinstallation hatte dessen `__init__.py` mitgenommen und nur
  tilde-Reste (`~arcode`, `~ruco`, `~uda`) hinterlassen. Die Kollision entsteht von selbst, weil
  verschiedene Node-Pakete verschiedene Distributionen in ihrer `requirements.txt` fordern.
- **Fix:** alle drei deinstallieren, den verwaisten `cv2`-Ordner löschen, EINE Distribution
  installieren: `opencv-contrib-python` (Obermenge, liefert `cv2.ximgproc.guidedFilter` für
  LayerStyle und die GUI-Symbole für Preprocessor-Debugcode). Danach laden alle Pakete fehlerfrei.
  `pip check` meckert weiter über die fehlenden Distributionsnamen, das ist reines Metadaten-Rauschen,
  zur Laufzeit importiert alles `cv2`.
- **Vorher `pip freeze` sichern.** Der Diff nach dem Fix zeigte exakt zwei entfernte Zeilen, sonst nichts.
- **Zweiter, unabhängiger Ladefehler im selben Paketstapel:** `comfyui-prompt-reader-node` scheiterte
  an einem fehlenden Git-Submodul (`stable_diffusion_prompt_reader`), nicht an opencv. Das Paket war
  als Kopie statt als Clone installiert. `git clone --depth 1
  https://github.com/receyuki/stable-diffusion-prompt-reader.git stable_diffusion_prompt_reader` im
  Node-Ordner löst es. Lehre: nicht jeder Fehler in einer Fehlerliste hat dieselbe Ursache.

## Iterationen / Versionierung (Prozess-Regel)

- Bei Optimierungs-Iterationen die Datei NIE ueberschreiben. Sonst geht der Entwicklungsstand
  verloren und eine fruehere Version war evtl. besser. Stattdessen versionieren:
  `<name>_v2.png`, `_v3.png` ... und jede via `ledger.py add` mit Rating festhalten, damit
  klar bleibt, welche Version die beste ist.
- Rueckfall-Archiv: ComfyUI speichert ohnehin JEDE Generierung als
  `Data\Packages\ComfyUI\output\genasset_NNNNN.png` (durchnummeriert, mit eingebettetem Prompt).
  Daraus lassen sich verlorene Versionen rekonstruieren.

## Musik-Cover / Album-Art (2026-07-24, 8 Genre-Cover für sound-studio)

- **Text im Bild ist der Hauptkiller bei Cover-Motiven.** FLUX-schnell erfindet ungefragt
  Schriftzüge überall dort, wo eine beschriftbare Fläche im Motiv steckt: Ladenschilder
  und Billboards (Stadtszene), Bühnen-Emblem und LED-Wände (Festival), Mittellabel einer
  Schallplatte. Negativ-Prompt hilft bei FLUX nicht (wird ignoriert).
- **Zwei Gegenmittel, in dieser Reihenfolge:** (a) Motiv so bauen, dass es keine
  beschriftbare Fläche gibt (Asphalt/Landschaft dominant, `plain blank unprinted paper
  center label`, `bare steel trusses` statt Bühnenwand), hat bei lo-fi und hardstyle
  gereicht; (b) wenn Schilder/Screens zum Motiv gehören: auf **Chroma1-HD wechseln** und
  echten Negativ-Prompt `text, letters, lettering, words, signage, billboards, logo,
  watermark` setzen. Bei dance-pop scheiterten 3 FLUX-Anläufe (immer neue Fantasieschrift
  wie "PUCTUM", "GORINY EL"), Chroma war auf Anhieb völlig schriftfrei.
- **Fantasy-Kreaturen in Menschenmengen: Chroma statt FLUX.** "crowd of orc warriors with
  bright green skin, tusks, pointed ears" ergibt bei FLUX-schnell eine Menge kahler
  Menschen in grünem Scheinwerferlicht (Spezies nur über die Beleuchtung angedeutet);
  Chroma liefert echte grüne Haut, spitze Ohren und Hauer bei gleicher Crowd-Komposition.
- **"Rave/Lightshow" muss wörtlich als Bühnenlicht formuliert werden:**
  `powerful beams of concert stage light shooting up through fog`. Mit `aurora` /
  `northern lights` kommt eine ruhige Naturlandschaft heraus, keine Energie.
- **Personen ausschließen geht bei FLUX über den Positiv-Prompt:** `empty meadow with
  nobody around, only objects and plants, no people, no characters, no faces` lieferte im
  ersten Versuch eine sichere personenfreie Kinderbuch-Szene.
- **Verify-Disziplin:** Pseudotext und Logos sitzen in kleinen Bildbereichen (Plattenlabel,
  LED-Wand, Bühnenmitte) und sind in der 1024er-Gesamtansicht unsichtbar. Verdächtige
  Regionen mit PIL croppen und 2-4x hochskaliert nochmal per Vision prüfen, sonst fällt
  der Fehler erst im Produkt auf.
- Prompt-Vorsichtsmaßnahme (ungetestet, aber konsistent mit dem Text-Bias): die Wörter
  `album cover`, `poster`, `flyer` im Prompt vermeiden, sie ziehen Typografie an. Motiv
  beschreiben, nicht das Medium.

## Spiel-/Web-Hintergründe hinter Text (2026-08-10, Kristallwacht)

- **Chroma1-HD trifft dunkle Fantasy-Stimmung auf Anhieb.** Menü-Hintergrund, Hochformat-
  Zuschnitt und zwei Overlay-Stimmungen (Sieg/Niederlage) waren je EIN Lauf, kein Rerollen,
  kein Text im Bild, keine Artefakte. Bestätigt das Verdikt von 2026-07-02: für Glow-,
  Nebel- und Partikel-Motive auf Near-Black ist Chroma FLUX-schnell klar überlegen.
- **Rezept, das sofort saß** (übernehmbar für jedes dunkle UI): `wide cinematic fantasy
  digital painting on an almost black very dark navy background that fades to pure darkness
  at all image edges` + Motiv + `deep atmospheric perspective, volumetric light shafts,
  crisp sharp focus, fine detail, painterly concept art, restrained palette of <2-3 Farben>,
  empty landscape with nobody around`. Negativ: `text, letters, lettering, words, signage,
  logo, watermark, signature, people, faces, buildings, warm orange, sunset, bright sky,
  daylight, flat, low detail, blurry, frame, border`.
- **Ein Hintergrund für Text braucht eine ruhige Zone, und die muss man bestellen.** Beim
  Prompt festlegen, WO das Motiv sitzt („in the upper third of the frame“, „rising out of
  rock in the middle distance“) und der Rest bleibt dunkel. Von drei Seeds war der
  brauchbarste der, dessen helles Nebelband NICHT dort lag, wo die Knopfspalte sitzt: das
  hübscheste Bild ist nicht automatisch das beste Hintergrundbild.
- **Hochformat separat generieren, nicht croppen.** `background-size: cover` schneidet bei
  16:9 auf 9:19 die Seiten weg und halbiert das Motiv. Ein eigener Lauf mit 768x1344 und
  „high in the upper third“ kostet 50 s und löst es sauber.
- **Ein Schleier gehört zum Asset, nicht zur Kür.** Zwei bis drei gestapelte
  `linear-gradient`-Stufen über dem Bild (0.5 bis 0.9 Deckung, dunkelste Stufe unten). Ein
  dunkles Motiv (erloschener Kristall im Nebel) braucht einen SCHWÄCHEREN Schleier als ein
  helles, sonst ist es einfach weg.
- **WebP statt PNG für solche Flächen:** 1344x768 Chroma-PNG = 1,5 MB, als WebP bei 1600 px
  Breite und q78 = 20 KB, ohne sichtbaren Verlust (weiche Verläufe, kein Text im Bild).
  Konvertierung mit PIL: `img.save(dst, "WEBP", quality=78, method=6)`.
- **Text ins Bild NICHT vom Modell malen lassen, auch nicht beim OG-Bild.** Stattdessen den
  Hintergrund generieren und Titel/Claim in einer HTML-Vorlage darüberlegen, die dieselben
  Schriften und Farben nutzt wie das Produkt, dann mit `shot.js --viewport 1200x630 --dsf 1`
  abfotografieren. Ergebnis ist scharfe echte Typografie statt Fantasieschrift und passt
  garantiert zur Marke.

## Erotische Motive -> SFW (Migration)

- Nicht Begriffe umbenennen (gleiches Bild), sondern den sexuellen/Anatomie-Fokus ENTFERNEN und
  nur den legitimen Kern behalten (Strand/Cyberpunk/Magierin/Goettin in normaler Kleidung).
  Negativ-Prompt mit `nsfw, nude, revealing, suggestive, cleavage` absichern. Ergebnis echt SFW.

## Zweiter Bildweg: Codex CLI (2026-08-11)

- Codex kann headless Bilder erzeugen (System-Skill `imagegen` unter `$CODEX_HOME\skills\.system\`,
  kein Plugin-Eintrag): `codex exec -s workspace-write -C <ordner> --skip-git-repo-check "<prompt>"`.
  Kein API-Key, läuft über das ChatGPT-Abo, verbraucht dessen Wochenkontingent statt freier GPU-Zeit.
- Testmotiv (fotorealistischer Sonnenuntergang, Person am Strand): 2,3 MB PNG, korrekte
  Anatomie, glaubwürdiges Gegenlicht, hohe Qualität auf Anhieb, kein Reroll nötig.
- `-i <bild>` hängt ein Referenzbild an, damit erzwingt man Stil-Konsistenz zu bestehenden
  Assets direkter als über ComfyUI (kein IP-Adapter/LoRA-Aufwand nötig).
- Wirkt prompt-treuer als FLUX-schnell (das Negativ-Prompts weitgehend ignoriert, siehe oben),
  kostet dafür 1-3 Minuten statt 5-50 Sekunden pro Bild und zehrt vom Wochenkontingent.
- Einordnung: Default bleibt ComfyUI (kostenfrei, beliebig oft, siehe SKILL.md
  Entscheidungsregel). Codex ist die Wahl kurz vor Kontingent-Reset oder wenn Prompt-/
  Referenztreue wichtiger ist als Tempo oder Kosten.

### Codex-Bildprompt: das Rezept, das trägt (zwei Serien am 11.08.2026)

- **Flag-Falle:** `-i <pfad>` ist ein Mehrwert-Flag und schluckt den nachfolgenden Prompt mit
  ("No prompt provided via stdin"). Richtig ist `--image=<pfad>`. Mehrere Referenzen gehen
  komma-getrennt, und genau das ist der stärkste Hebel: Figur plus eine bereits abgenommene
  Platte als zweite Referenz plus dem Satz, das neue Bild gehöre zur selben Reihe.
- **Prompt in sieben Blöcken**, Reihenfolge zählt: (1) Auftrag in einem Satz mit Dateiname und
  Ablageort. (2) WHAT IT IS, Zweck plus die nötigen Verbote. (3) SCENE mit expliziter Platzierung
  jedes Elements, sonst landet alles mittig. (4) STYLE, Verweis auf die Referenz plus ausgeschriebene
  Beschreibung plus Negativliste. (5) PALETTE, zwei bis vier Kernfarben plus Helligkeitsvorgabe.
  (6) COMPOSITION mit den reservierten Zonen. (7) OUTPUT, Dateiname und Hintergrund wiederholen
  ("transparent background, no ground shadow" bzw. "opaque").
- **Die Negativliste trägt mehr als die Positivliste.** "NO black outlines, no line art, no brush
  strokes, no pixel art, no flat vector look" wirkt stärker als jede Stilbeschreibung.
- **Begründung mitliefern schlägt reine Anweisung.** Nicht "keep the lower third empty", sondern
  "keep it empty because the character stands there and a dark caption is drawn over it".
- **Bei Hintergründen das Verbot nicht vergessen:** ohne "the attached character must NOT appear
  in the image" malt das Modell die Referenzfigur mit hinein.
- **Abnahme gehört an die Montage, nicht ans Einzelbild.** Ein Skript, das Figur plus Bildunterschrift
  in echter Zielgröße auf jede Platte setzt, deckt Fehler auf, die das Einzelbild verbirgt.
- **Vor dem Prompt den Zielstil MESSEN, nicht schätzen.** In insel-imperium hatten die selbst
  gezeichneten Assets 5 bis 7 Farben, hartes Alpha und Kontur #201010, die vorher generierten
  1900 bis 2250 Farben mit weicher Schattierung. Letztere zerfallen bei 39 px Zellgröße zu Klecksen
  und kämpfen mit dem Fraktionsring. Farbanzahl und Alpha-Härte sind zählbar, also zählen.

## Album-Cover via Codex (gpt-5.6-sol image_gen), 2026-08-19

- **Trefferquote 10 von 10 beim ersten Versuch** (sound-studio, Genre- und Familien-Cover).
  Keine Iteration nötig, kein verformtes Detail, kein Text im Bild. Verglichen mit der
  FLUX-Runde vom 2026-07-24 (gleiche Bildserie, siehe Ledger `musik-cover`) ist die
  Prompt-Treue deutlich höher: mehrteilige Szenen ("Akkordeon UND Fiedel auf Fässern,
  Fackeln, Kriegstrommeln, Mond") kommen vollständig, statt dass Elemente wegfallen.
- **Kosten/Tempo:** ~2 min je Bild, drei Läufe parallel laufen problemlos. 9 Bilder in
  ~6 min. Ausgabe 1024x1024 RGBA-PNG, 1,4 bis 3,0 MB.
- **Aufruf, der funktioniert** (je Bild ein eigener Unterordner, sonst räumt der Agent
  fremde Dateien mit auf; stdin schließen, sonst hängt der Lauf):
  `node codex.js exec -s workspace-write -m gpt-5.6-sol -C <ordner> --skip-git-repo-check "<prompt>" < /dev/null`
- **Prompt-Rahmen, der Text zuverlässig verhindert:** "Generate ONE image and save it in the
  current working directory as <slug>.png. Square 1:1, 1024x1024, album cover artwork,
  absolutely no text, no letters, no numbers, no logos, no watermark, no signature. Motif: ..."
  Codex prüft danach selbst die Maße nach (skaliert notfalls auf 1024) und meldet das Ergebnis.
- **Grenze:** kein Seed, keine ComfyUI-Metadaten im PNG. Reproduktion geht nur über den
  Prompt, deshalb beim Ledger-Eintrag `--prompt` explizit mitgeben.
- **Recall-Falle:** das Vertical heißt `musik-cover`. Eine Suche nach `music` liefert nichts,
  obwohl acht bewährte Einträge da sind. Bei leerem Recall Synonyme probieren oder direkt
  in `ledger.jsonl` grep'en.
- **Hinweis zu den Alt-Einträgen:** die FLUX-Zeilen von 2026-07-24 zeigen auf dieselben
  Dateinamen, die am 2026-08-19 überschrieben wurden. Die alten Bilder liegen in
  `outputs/covers/_alt/`, die Prompts der Zeilen bleiben gültig, das Bild dahinter ist neu.

## Grund-Farbwechsel und FLUX-Umgebungsanpassung (bildstil-lab Entgrünungs-Kampagne), 2026-08-26

- **FLUX passt Motivfarben der Grundfarbe an, in beide Richtungen.** Chroma-Grün färbt Material
  und Licht des Motivs ein (bis 83 % grün-exzessive Pixel, deshalb repo-weit auf neutrales
  Hellgrau #d9d9d9 plus BiRefNet umgestellt). Der Rückweg passiert genauso: auf Magenta-Key
  druckte ein Holzschnitt-Stil die Schattenseite in der Grundfarbe, auf Hellgrau wurde eine
  schwarze Scherenschnitt-Silhouette hellgrau. Gegenmittel, das dreimal sofort trug: die
  gewünschte Motiv-Palette wörtlich in den Prompt ("printed in cream ivory and forest green
  ink colors", "cut entirely from solid black paper"), nicht nur Verbote.
- **Neutralgrau statt Key ist der Grund, warum der Stich verschwindet:** ein unbunter Grund
  kann keine Sättigung spiegeln. Für dunkle Motive auf hellem Grund und weiße Linienstile
  auf dunklem Grund (#404040) gilt dasselbe Prinzip; Grün-Exzess fiel überall auf 0,0 %.
- **BiRefNet erreicht eingeschlossene Flächen nicht** (Zahnrad-Loch bleibt gefüllt, wenn der
  Grund dort hell ist). Deterministische Nachschritte statt Seed-Lotterie: Flood-Fill vom
  Lochzentrum im Cutout; mitgerenderte Randrahmen (Blaupausen-Bordüre) über ein 48-72-px-
  Randband entfernen, wenn die Komposition Rand-Abstand garantiert.
- **Pixel-Art-Kette ohne Key:** Farben aus `pixelate.py` auf dem Rohbild, Alpha aus der
  BiRefNet-Matte des ROHBILDS, dann je Rasterzelle auf ganz/gar nicht runden. Entfernt auch
  die früheren grünen Mischzellen an der Motivkante, Alpha-Härte bleibt 0,0 %.

## Z-Image-Turbo schlägt FLUX-schnell in 5 von 5 Verticals (A/B 2026-08-27)

Aufbau: dieselben fünf Ledger-Prompts, dieselben Seeds, dieselben Bildformate wie die
FLUX-schnell-Referenzen von 2026-06-23. Modell Z-Image-Turbo bf16 (6B, Apache 2.0),
8 Steps, cfg 1.0, `res_multistep`/simple, shift 3.0, Workflow `zimage_turbo_t2i.api.json`.

| Vertical | FLUX-schnell (alt) | Z-Image-Turbo | Befund am Bild |
|---|---|---|---|
| Landschaft/Winzer | 5 | 5 | Z-Image zeigt Spalierdraht, Pfosten, Stämme, offenen Boden. FLUX macht Laubwülste ohne Erziehungssystem und starke Tilt-Shift-Unschärfe. |
| Architektur | 5 | 5 | FLUX halluziniert Schrift auf der Fassade und verzieht das Raster. Z-Image hält Geschosse, Pfosten-Riegel-Raster und Umfeldbebauung sauber. |
| Handwerk | 4 | 5 | Z-Image: Reihenklemmen, LS-Automaten, Hutschiene, Klemmenplan an der Tür, beide Hände korrekt. FLUX: Kabelsalat ohne Bauteile, Fake-Label "AUSTRICAL", deformierte Werkzeuge. |
| Menschen | 4 | 5 | **Das Haut-Thema ist gelöst.** Z-Image liefert Poren, Unregelmäßigkeiten, echte Zähne. FLUX bleibt beim wachsartigen Retusche-Look. |
| Produkt | 4 | 5 | Z-Image: matte Glasur mit Korn, unglasierter Fußring, sauberer Henkelansatz, weiche Standreflexion. FLUX wirkt wie ein 3D-Render, Henkel verwaschen. |

**Richtigstellung vom 28.09.2026:** die Überschrift "5 von 5" stimmt nicht. Z-Image gewann Handwerk, Menschen und Produkt, bei Landschaft und Architektur stand es 5:5, beurteilt hat ein Agent. Gegen Krea und Qwen wurde Landschaft hier nie getestet. Der Blindtest vom 28.09.2026 weiter unten hat Landschaft neu besetzt.

- **Tempo (gemessen, RTX 5070 Ti, jeweils bei etwa 1 MP):** Z-Image 12 bis 17 s pro Bild
  inklusive Modell-Ladezeit im ersten Lauf. Zum Vergleich aus der alten Messung:
  FLUX-schnell 5 bis 8 s, Chroma etwa 50 s. Z-Image liegt also zwischen beiden.
- **Wo FLUX noch gewinnt:** dramatische Lichtstimmung. Der Prompt sagte "golden hour, warm
  evening light", FLUX setzt das kräftig um, Z-Image bleibt neutraler und flacher. Wer
  Postkarten-Licht will, muss es bei Z-Image härter prompten (Lichtrichtung, Farbtemperatur,
  Gegenlicht) oder FLUX nehmen.
- **Konsequenz für Menschen/Haut:** Chroma bleibt nötig für NSFW, Anime und echtes Negativ,
  aber nicht mehr für Hautqualität allein. Für SFW-Portraits ist Z-Image viermal schneller
  bei mindestens gleichem Realismus.
- Kein Negativ-Prompt möglich: der Graph zieht das Negativ über `ConditioningZeroOut`, cfg
  ist 1.0. Wie bei FLUX-schnell steuert nur der positive Prompt.

## Qwen-Image-2512: englischer Text ja, deutscher Text nein (2026-08-28)

Aufbau: `Qwen-Image-2512-Q4_K_M.gguf` (11,4 GB) plus Text-Encoder `qwen_2.5_vl_7b_fp8_scaled`
und `qwen_image_vae`. Zwei Wege getestet, beide mit shift 3.0 bzw. 3.1, euler/simple:
Turbo-LoRA mit 2 Steps und cfg 1.0 (`qwen_2512_t2i.api.json`) gegen den vollen Weg mit
50 Steps und cfg 4.0 ohne LoRA (`qwen_2512_t2i_quality.api.json`).

- **Tempo:** 2 Steps 13 bis 30 s je Bild (Modell-Ladezeit im ersten Lauf), 50 Steps 2 min 40 s.
  Das ist Faktor 11 für einen Qualitätsunterschied, den ich am Bild nicht sehe. Der volle Weg
  lohnt sich nach diesem Test nicht, die Turbo-LoRA ist der Default.
- **Englischer Text sitzt:** "VINEYARD OPEN DAILY" fehlerfrei, sauber ins Holz geschnitten,
  bei 2 Steps.
- **Deutscher Text scheitert reproduzierbar, 4 von 4 Versuchen:** "Weingut Blumora" wurde zu
  "Weengrut", "Weegrut", "Weengut" und in Großbuchstaben "WEENGUT". Getestet über zwei Seeds,
  beide Sampling-Wege und Groß- wie Kleinschreibung. Ein anderes Wort, "BÄCKEREI SONNE", kam
  als "BÄRKEREI SONNE" heraus: der Umlaut Ä stimmt, ein Konsonant kippt. Muster: einzelne
  Buchstaben in deutschen Wörtern kippen, nicht das ganze Wort.
- **Ursache offen.** Kandidaten: die Q4-Quantisierung (nicht gegengeprüft, Q6/Q8 passen mit
  17 bzw. 22 GB nicht auf die Karte) oder schlicht die Trainingssprache (Qwen ist auf
  Englisch und Chinesisch ausgelegt). Nicht als "Modell kann kein Deutsch" verallgemeinern,
  ohne einen größeren Quant geprüft zu haben.
- **Praxisregel:** deutsche Schrift im Bild nie ungeprüft übernehmen. Für Kundenassets ist
  echte Typografie im Layout ohnehin der sauberere Weg, das Modell liefert dann den
  Hintergrund ohne Text.
- **Nebenbefund, unerwartet:** beim Referenz-Prompt Landschaft (gleicher Seed wie im
  Z-Image-A/B) trifft Qwen die Lichtstimmung "golden hour" deutlich besser als Z-Image, das
  dort neutral bleibt. Beim Portrait sind beide gleichauf, bei Handwerk bleibt Z-Image bei
  den technischen Details und den Händen vorn. Qwen ist damit kein reines Text-Modell,
  sondern eine echte Alternative, wenn die Lichtstimmung im Prompt steht.

## Qwen-Image-Edit-2511: gezieltes Ändern funktioniert, deutscher Text weiterhin nicht (2026-08-28)

Aufbau: `qwen-image-edit-2511-Q4_K_M.gguf` plus Lightning-LoRA mit 4 Steps, cfg 1.0, euler/simple,
shift 3.1, CFGNorm 1.0, Referenz-Methode `index_timestep_zero`. Workflow `qwen_edit_2511.api.json`,
Eingangsbild über den neuen Schalter `--image` (lädt per `/upload/image` nach ComfyUI hoch und
setzt den Knoten INPUT_IMAGE).

- **Farbe tauschen, Rest halten:** graue Tasse zu dunkelgrün, 33 s inklusive Modell-Ladezeit.
  Form, Henkelansatz, unglasierter Fußring, Hintergrund, Schatten und Standreflexion sind
  unverändert. Das ist die Fähigkeit, die dem Stack bisher gefehlt hat: ändern statt neu würfeln.
- **Text ersetzen, englisch:** "Weengrut Blumora" auf dem Holzschild wurde sauber zu
  "GREEN VALLEY", Holzmaserung, Kerbenschnitt, Weinberg und Licht blieben stehen, 26 s.
- **Text korrigieren, deutsch: gescheitert.** Die Anweisung, exakt "Weingut Blumora" zu
  schreiben, ließ das Bild praktisch unverändert, der Fehler blieb stehen. Zusammen mit dem
  T2I-Befund von heute heißt das: die Grenze liegt beim deutschen Wort, nicht beim Editieren.
  Der englische Kontrollversuch mit demselben Bild, demselben Seed und derselben Anweisung
  funktionierte, damit ist die Fähigkeit belegt und die Sprache als Ursache eingegrenzt.
- **Konsequenz:** deutsche Schrift im Bild ist mit diesem Stack kein Weg, weder erzeugen noch
  reparieren. Für Kundenmaterial Hintergrund generieren und die Typografie im Layout setzen.

## Konsolidierung auf fünf Modellfamilien (2026-09-19)

Nutzerwunsch: wenige Modelle, breite Abdeckung, einfache Bedienung. Vor dem Streichen zwei
Abhängigkeiten geprüft, beide bestanden:

- **Freistell-Kette auf Z-Image statt FLUX** (`zimage_cutout.api.json`, gleicher Prompt und Seed
  wie die FLUX-Referenz): RGBA mit 84,7 % voll transparent und 0,3 % Halbtransparenz gegen
  83,2 % und 0,4 % bei FLUX, also gleiche Kantenqualität. Z-Image hielt sich zusätzlich an
  "no shadow", FLUX malte trotz Verbot einen langen Schlagschatten, den die Matte dann
  mitnimmt. 20 s gegen 15 s, der Unterschied sind 8 statt 4 Steps.
- **Upscale-Refiner von Juggernaut XL auf CyberRealistic Pony** (Score-Tags im Prompt, Clip Skip 2
  im Graphen, denoise 0.2 unverändert): 1024 auf 2048 in 37 s, Details sauber nachgerechnet,
  keine Kachelnähte am Beispielbild.

Gestrichen daraufhin 53 Dateien mit 75,2 GB: der komplette SD1.5-Zoo (14 Checkpoints samt
Sidecars), FLUX.1-schnell, Chroma1-HD mit t5xxl-Encoder, Juggernaut XL. Dazu die Workflows
FLUX-T2I, FLUX-Cutout, Chroma, SDXL-Schnelltest, SDXL-Hires, SD1.5-Anime und die
50-Step-Qwen-Rückfallebene. Was damit wegfällt: der SD1.5-LoRA-Bestand hat kein Modell mehr,
Chroma als einziges unzensiertes Modell mit echtem Negativ ist durch Pony (Menschen) und
Illustrious (Anime) ersetzt, beide mit echtem Negativ, dramatisches Licht kommt statt FLUX von
Qwen. Bleibt: Z-Image-Turbo, CyberRealistic Z-Image, Qwen-2512 mit Edit-2511, WAI-illustrious,
CyberRealistic Pony, dazu BiRefNet und 4x-UltraSharp. Neun Workflows, neu durchnummeriert 00 bis 08.

Nebenbefund zu Civitai-Formaten: die INT8-Fassung von CyberRealistic Z-Image scheitert auf
ComfyUI 0.25.1 mit `KeyError: int8_tensorwise`, `comfy/quant_ops.py` kennt dort nur
`float8_e4m3fn`, `float8_e5m2` und `nvfp4`. BF16-Fassung läuft, Nullprobe 11 s.

## ComfyUI-Update 0.25.1 auf 0.36.0: was schiefging und wie es repariert wurde (2026-09-19)

Der Update-Knopf in Stability Matrix 2.16.4 wurde gedrückt, während ComfyUI lief. Git zog den
Code sauber auf v0.36.0, danach erneuerte uv die Pakete mit `--upgrade` und brach mitten im
Ersetzen ab: `tokenizers.pyd` war vom laufenden Server gesperrt (`Zugriff verweigert`). Zu dem
Zeitpunkt waren `torch`, `torchvision` und `Pillow` bereits entfernt, die Ersatzpakete noch nicht
installiert. Der laufende Server merkte nichts (alles im Speicher), ein Neustart wäre mit
`No module named 'torch'` gescheitert. Zweite Falle: uv hätte torch von PyPI geholt, das ist der
CPU-Build, weil Stability Matrix dem uv-Aufruf keinen CUDA-Index mitgibt (geprüft im
`app.log`: nur `UV_CACHE_DIR` und `UV_BUILD_CONSTRAINT` gesetzt). Dritte Falle: der Aufruf
enthielt `numpy<2`, das hätte numpy 2.4.4 auf 1.x zurückgedreht.

Reparatur, in dieser Reihenfolge: Server stoppen; torch, torchvision, torchaudio ausdrücklich aus
`https://download.pytorch.org/whl/cu130` (vorher per `pip download` in den Scratchpad geholt,
dann `--no-index --find-links`); kaputte Pakete (`tokenizers`, `Pillow`, `sentencepiece`) mit
`--force-reinstall --no-deps` neu, bei `tokenizers` vorher die halb entfernten Reste
(`tokenizers/`, `tokenizers-*.dist-info`, das umbenannte `~il` von Pillow) von Hand löschen,
sonst meldet transformers `found=None`; dann `requirements.txt` und `manager_requirements.txt`
ohne `--upgrade`; numpy auf 2.4.4 belassen. Ergebnis: torch 2.14.0+cu130, torchvision
0.29.0+cu130, `cuda.is_available()` True, 33 Custom-Nodes ohne Import-Fehler, Probebild ok.

Regeln daraus: ComfyUI nie aktualisieren, solange der Server läuft (erst stoppen, auch die
Headless-Instanz des Skills). Nach einem Stability-Matrix-Update immer
`python -c "import torch; print(torch.__version__, torch.cuda.is_available())"` in der venv
prüfen, bevor der Server neu startet; steht dort kein `+cu130`, ist es der CPU-Build. Die
Torch-Wheels liegen nach dem Download im uv- bzw. pip-Cache, ein zweiter Versuch ist billig.

Nebenbefund derselben Session: `%date:yyyy-MM-dd%` im SaveImage-Prefix ersetzt nur die
Oberfläche im Browser. Über die HTTP-API kommt der Platzhalter wörtlich an, Windows lehnt
`%` und `:` im Ordnernamen ab (`WinError 267`), der Lauf endet ohne Bild. Die drei
Skripte (`comfy_generate.py`, `upscale.py`, `comfy_matte.py`) setzen das Datum deshalb
jetzt selbst ein (`expand_dates`), bevor sie den Graphen abschicken.

## Illustrious Realism v3 gegen v4 (2026-09-19)

Vier Prompts (Portrait, Handwerker, Straßenszene, Fantasy), identische Seeds, Settings aus
`illustrious_t2i.api.json` (40 Steps, cfg 7, `euler_ancestral`, 896 x 1152, Qualitäts-Tags plus
`embedding:lazypos`, Negativ mit `embedding:lazyneg`). Nutzerurteil: v4 gefällt besser, v3 gelöscht.
Gemessen, ohne Wertung: v4 liegt bei allen vier Motiven in der mittleren Helligkeit unter v3
(65 bis 87 gegen 69 bis 110), wer helle Bilder will, promptet das Licht bei v4 ausdrücklich.
14 bis 19 s je Bild.

Zum Hires-Zweig in Civitai-Workflows dieser Familie: er ist kein Upscale, sondern ein Detailpass
(4x NMKD, Hautkontrast-Filter, zurück auf das 1,28-fache, 20 Schritte neu sampeln, danach CRT
Post-Process mit UltraSharp), etwa 5 min je Bild gegen 30 s für die Basis. Unser 03 (Denoise 0.2)
ersetzt ihn nicht, er vergrößert nur. Deshalb: Zweig als Gruppe bypassed lassen, Motive in der
Basis suchen, Treffer einmal mit eingeschalteter Gruppe nachrechnen.

## Smoke-Tests 06 und 08, Stand Krea 2 (2026-09-20)

- 06 (WAI-illustrious v17, 960 x 1664, 40 Steps): 29 s je Aufruf über die API, Bild `agent/2026-09-19/anime_00009_.png`. Neon-Straße mit Silberhaar-Figur sauber, Leuchtreklamen tragen Pseudo-Schrift, wie bei SDXL üblich.
- 08 (CyberRealistic Pony v18, 896 x 1152, 30 Steps): 31 s, Bild `agent/2026-09-19/pony_00001_.png`. Fotorealistisches Café-Porträt, Hände korrekt, Kreidetafel-Text unleserlich (SDXL-typisch, für Text im Bild 04 nehmen).
- Beide Zeiten enthalten einen möglichen Modellwechsel, sind also obere Grenze. Ablage in `agent/<datum>/` bestätigt, Prefixe greifen auch nach dem Update auf 0.36.0.
- Krea 2 auf 0.36.0: nativ unterstützt (`comfy/supported_models.py` Klasse Krea2, CLIPLoader-Typ `krea2`, shift 1.15 im Modellprofil hinterlegt, Latent-Format Wan21 wie Qwen-Image). Die Knoten `Krea2ImageNode` und `Krea2StyleReferenceNode` in der Node-Liste sind API-Knoten (`comfy_api_nodes/nodes_krea.py`, Cloud, kostenpflichtig), nicht der lokale Weg.
- Lokaler Graph für Krea 2 Turbo: UNETLoader + CLIPLoader (`krea2`) + VAELoader (`qwen_image_vae.safetensors`, liegt schon vor) + CLIPTextEncode + EmptySD3LatentImage + KSampler, 8 Steps, cfg 1.0 mit ConditioningZeroOut (offiziell cfg 0, mu 1.15, bis 2048 x 2048), kein Negativ-Prompt.
- Dateien bei `Comfy-Org/Krea-2`: `krea2_turbo_fp8_scaled.safetensors` 13,1 GB, `qwen3vl_4b_fp8_scaled.safetensors` 5,2 GB (bf16 8,9 GB), dazu `krea2_turbo_nvfp4.safetensors` 7,7 GB (Blackwell-nativ, Qualität ungetestet) und `krea2_turbo_int8_convrot.safetensors` 13,5 GB. Empfehlung fp8_scaled plus Encoder fp8, zusammen 18,3 GB.

## Krea 2 Turbo gegen Z-Image-Turbo (A/B 2026-09-20)

Setup: gleicher Prompt, gleicher Seed, gleiches Format, 11 Motive plus Freistell-Probe. Krea 2 Turbo als `krea2_turbo_fp8_scaled` (13,1 GB) mit `qwen3vl_4b_fp8_scaled` und `qwen_image_vae`, 8 Steps, cfg 1.0, euler/simple, shift 1.15 im Modellprofil. Z-Image-Turbo bf16 wie in `zimage_turbo_t2i.api.json`. Bilder: `out/ab_krea/<motiv>_{zimage,krea2}.png`, Gegenüberstellungen `vergleich_<motiv>.png`, Gesamtblatt `vergleich_alle.jpg`.

| Motiv | Sieger | Begründung |
|---|---|---|
| Landschaft | unentschieden, Tendenz Krea | Z-Image schärfer und kontrastreicher (HDR-Look), Krea natürlicher mit Alpenglühen und Nebel |
| Auto | Z-Image | stimmige Karosserie und Licht, Krea mischt Formen und wirkt vorne verzerrt |
| Fantasy | Krea | geschlossene Komposition, plausible Drachenanatomie, Z-Image überladen |
| Porträt | unentschieden, Tendenz Krea | Z-Image mehr Hautdetail, Krea wie ein echtes Foto mit Bokeh |
| Frau am Strand | Krea | natürliche Gehpose, Gegenlicht, Reflexe im Sand, Hände sauber |
| Tier (Fuchs) | Z-Image | Fellzeichnung auf Wildlife-Niveau, Krea weicher und plüschig |
| Stadt (Regen, Neon) | unentschieden, Tendenz Z-Image | Z-Image erfüllt den Prompt (Schirme, Neonreflexe), Krea stimmungsvoller mit weniger Prompttreue |
| Essen (Spaghetti) | Krea | Food-Styling mit Leinen, Besteck, Schale, Z-Image-Sauce wirkt aufgesetzt |
| Innenraum | Krea | warmes Licht, Vorhänge, Tiefe, Z-Image wirkt wie ein Render |
| Aquarell | Krea | echte Papierstruktur und lockerer Pinsel wie verlangt, Z-Image sauber aber glatt |
| Produkt mit Text | unentschieden | beide schreiben MORNING ROAST korrekt, Kleintext bei beiden Kauderwelsch |

Bilanz 5:2 für Krea 2 bei 4 Unentschieden. Krea 2 liefert durchgehend den Foto- und Filmlook (weniger Überschärfung, bessere Lichtführung, breitere Stilspanne), Z-Image gewinnt bei feinsten Strukturen (Fell, Chrom) und bei der Prompttreue in vollen Szenen. Freistell-Probe (Flasche auf flachem Grün): beide liefern gleichmäßiges Grün, Z-Image flach wie ein Icon, Krea plastischer mit leichter Körnung im Grün, für BiRefNet unerheblich.

Zeiten auf der 5070 Ti: Z-Image 8 bis 12 s, Krea 2 fp8 11 bis 16 s je Bild bei 1 bis 1,2 Megapixel, Erstladen je 21 s. Beide passen mit Encoder in 16 GB. Kurzer englischer Text im Bild funktioniert bei beiden, Qwen bleibt für längere Schilder zuständig.

## Die zwei LoRAs aus dem Civitai-Doppelbelichtungsbild (2026-09-20)

Vorlage war ein Civitai-Bild auf Z-Image-Turbo mit zwei LoRAs und dem Upscaler Remacri. Beide LoRAs geprüft, eine lag schon hier.

- **[ZIT] Detail Slider** (Civitai 2234266, Datei `Z-Detail-Slider.safetensors`, 20,3 MB): war bereits als `zimage_detail_slider.safetensors` installiert, SHA256 byte-genau identisch. Bipolar, laut Autor gut zwischen -2 und +2, über +2 wird das Bild dunkler, unter -2 heller. Kein Trigger-Wort. Lizenz voll offen (verkaufen und mergen erlaubt, keine Namensnennung nötig).
- **Midjourney Luneva Cinematic** (Civitai 2185167, Datei `ZIT_Midjourney_Luneva_Cinematic_v1_r128.safetensors`, 649 MB): neu geladen, Prüfsumme stimmt. Rang 128, 40 Bilder, 5000 Steps. Kein Trigger-Wort, Stärke 0,5 im Vorlagenbild, bei sehr langen Prompts empfiehlt der Autor 0,6 bis 1,0. Lizenz enger: Bilder dürfen kommerziell genutzt werden, aber Namensnennung ist Pflicht und Ableitungen oder Merges sind untersagt.

A/B/C mit identischem Prompt, Seed und Format (832 x 1216, Bilder in `out/ab_luneva/`): ohne LoRA sitzt die Komposition, das Einsatzbild bleibt aber ein aufgesetzter ovaler Fleck, Rüstung und Haar sind generisch. Mit Luneva 0,5 wächst das Einsatzbild in den Schnitt der Kleidung hinein, Stoff, Filigran und Farbstimmung werden filmisch. Mit beiden LoRAs kommen Ornamente auf der Rüstung, mehr Türme und Wasserfälle im Einsatzbild, wehender Schal und feinere Haarsträhnen dazu. Klare Reihenfolge ohne < mit < beide.

Zeit unverändert bei 8 s je Bild, die LoRAs kosten nichts an Tempo. Der Warnhinweis der Luneva-Seite zu FlowMatch und `--fp32-unet` stammt von ComfyUI 0.3.77 (Dezember 2025) und trifft auf 0.36.0 nicht zu: die Bilder sind ohne das Flag rauschfrei. Der Upscaler Remacri aus dem Vorlagenbild ist nicht installiert, 4x-UltraSharp aus Workflow 03 stammt aus derselben ESRGAN-Linie.

Nebenbefund: Z-Image-Turbo kann Anime und Illustration deutlich besser, als der Stack bisher annimmt. Workflow 06 führt dafür WAI-illustrious. Für den Doppelbelichtungs- und Cinematic-Look ist Z-Image plus Luneva der kürzere Weg.

### Gegenprobe: laufen die zwei LoRAs auch auf CyberRealistic Z-Image? (2026-09-20)

Ja. Gleicher Prompt, gleicher Seed, einmal ohne und einmal mit beiden LoRAs auf `cyberrealisticZImage_v70_bf16`: das Bild ändert sich vollständig, Bokeh wird kräftiger, die Hauttextur bekommt Poren, Sommersprossen und Feuchtigkeit, die Farbgebung wird filmisch. Bilder `agent/2026-09-20/loratest-cyber_{ohne,loras}_00001_.png`, Blatt `out/ab_luneva/vergleich_cyberrealistic.jpg`.

**Wichtige Nebenwirkung:** die mittlere Helligkeit fällt von 57 auf 30. Der Detail Slider auf 1.0 plus Luneva auf 0.5 verdunkelt CyberRealistic spürbar stärker als Z-Image-Turbo. Für helle Motive dort den Detail Slider auf 0.5 oder negativ stellen, er ist bipolar.

**Warum es passt:** beide Modelle haben exakt dieselbe Tensorstruktur (453 Tensoren, `layers.N.attention.qkv`), CyberRealistic trägt nur das Checkpoint-Präfix `model.diffusion_model.` davor, das ComfyUI beim Laden abschneidet. Krea 2 dagegen hat 686 Tensoren unter `blocks.N.attn.*`, null Überschneidung. Die Prüfung geht ohne GPU: Safetensors-Header lesen und die Schlüssel der LoRA gegen die des Modells halten.

### Workflow 09 an drei Bibliotheks-Prompts (2026-09-20)

Test mit fremden Motiven statt Doppelbelichtung: drei Prompts aus `Images/library` durch 09 und zum Vergleich durch 00 (pures Z-Image), gleicher Seed 31337. Blätter `out/ab_luneva/test09_*.jpg`.

- **Bergpanorama** (`landschaft/reveng_mountain_flux.png`, 832 x 1216): 09 bringt mehr Tiefenstaffelung, Bäume auf den Graten und ein wärmeres Gegenlicht, wird aber merklich dunkler. Unentschieden, je nach gewünschter Stimmung.
- **Splash-Art Kriegerin** (`fantasy/reveng_warrior_daggers.png`, 832 x 1024): klarer Gewinn für 09. Rüstung mit Ornamenten und Lederstruktur, dramatischeres Licht, Hintergrund mit Ruinen statt leerer Fläche. Das ist die Disziplin, für die der Workflow gedacht ist.
- **Menü-Hintergrund Kristallwacht** (`web/kristallwacht-menu-bg-v1.png`, 1344 x 768): 09 liefert den feinsten Kristall und die dunkelsten Ränder, wird damit aber unruhiger als das Chroma-Original. Für einen Hintergrund, über dem Text stehen soll, ist die ruhigere Fassung die bessere. Hier gewinnt nicht der detailreichere Workflow.

**Gemessen: beide LoRAs verdunkeln, additiv.** Mittlere Helligkeit am selben Bergmotiv (0 schwarz, 255 weiß):

| Einstellung | Helligkeit |
|---|---|
| keine LoRA | 132 |
| nur Detail Slider 1.0 | 107 |
| nur Luneva 0.5 | 115 |
| Luneva 0.5 + Slider 1.0 (Voreinstellung) | 87 |
| Luneva 0.5 + Slider -1.0 | 137 |

Der Detail Slider ist der stärkere Verdunkler und zugleich das Gegenmittel, weil er bipolar ist. Faustregel: dunkle Motive mit der Voreinstellung, helle Motive (Tageslandschaft, Schnee, Strand, Produkt auf Weiß) mit Slider auf 0 oder -1.0. Er tauscht Helligkeit gegen Feinstruktur, bei -1.0 fallen Kleindetails weg. Dieselbe Verdunklung zeigte sich vorher auf CyberRealistic Z-Image (57 auf 30), dort also genauso gegensteuern.

Nebenbefund aus dem Test: die API-Vorlage hatte beim Bau versehentlich das Präfix `cinematic/` statt `agent/` und wich damit von den anderen acht Vorlagen ab. Korrigiert. Regel bleibt: API-Vorlagen schreiben nach `agent/<datum>/`, die Zweck-Ordner vergibt der Konverter über UI_PREFIX nur für die UI-Workflows.

### Zwei Leuchtfarben im selben Bild: Drachentest (2026-09-20)

Frage war, ob ein Modell zwei verschiedene Leuchtfarben sauber auseinanderhält, ohne sie zu vermischen: blau glühende Augen und roter Feueratem. Prompt mit ausdrücklicher Zuordnung je Farbe (`eyes glowing intense electric blue`, `torrent of bright red and orange fire`, dazu `cold blue rim light` gegen `red firelight reflecting`), 1216 x 832, drei Seeds durch 09 plus je einmal 00 und Krea 2.

- **Farbtrennung hält bei allen fünf Bildern.** Kein Ausbluten, die Augen bleiben blau, das Feuer bleibt rot. Das Rezept dafür: jeder Farbe ausdrücklich ein Objekt zuweisen und zusätzlich die Lichtrichtung trennen (kaltes Kantenlicht gegen warmes Feuerlicht).
- **09 gegen 00:** 09 liefert mehr Schuppenstruktur, glühende Adern im Körper und dunklere Umgebung, 00 das sauberere und längere Feuerstrahl-Bild mit kräftigerem Rot. Für Key-Art 09, für ein klares Kreaturenportrait 00.
- **Krea 2 weicht ab:** malerischer, mit blauem Nebelleuchten in den Flügeln, aber der Feueratem bleibt im Maul statt als Strahl herauszukommen. Prompttreue hier schwächer als bei Z-Image, passt zum A/B-Befund vom selben Tag.

**Fund mit Folgen: die Luneva-LoRA backt gelegentlich ein Wasserzeichen ein.** In Seed 101 steht rechts unten ein kleiner gerahmter Signaturblock, in Seed 202 und 303 sowie im puren Z-Image nicht. Also sporadisch, hier 1 von 3. Die LoRA ist auf Midjourney-Ästhetik trainiert, offenbar mit signierten Vorlagen. Gegenmittel: Ecken des fertigen Bildes prüfen, bei Befund anderen Seed nehmen oder beschneiden. Über einen Negativ-Prompt geht es nicht, der Graph läuft auf cfg 1.0 ohne Negativ. Blatt `out/ab_luneva/drache_ecken.jpg`.

### Wasserzeichen der Luneva-LoRA: wie oft? (2026-09-21)

15 Bilder, alle vier Ecken geprüft, Blätter `out/ab_luneva/wm_blatt{1,2,3}.jpg`. Aufteilung: 6 Seeds Drache mit der Voreinstellung, 3 Seeds Hafen mit der Voreinstellung, 3 Seeds nur Detail Slider (Luneva aus), 3 Seeds Luneva auf 1.0 ohne Slider.

**Ergebnis: 1 von 15, und zwar nur Seed 101.** Alle anderen 14 Bilder sind in allen vier Ecken sauber. Auch Luneva auf voller Stärke 1.0 hat in drei Versuchen kein Wasserzeichen erzeugt. Es hängt also am Seed und nicht an der LoRA-Stärke oder am Motiv. Dass ausgerechnet Seed 101 es erneut brachte, passt dazu: derselbe Seed liefert reproduzierbar denselben Fehler.

Praktische Folge: nicht jedes Bild prüfen müssen, aber vor dem Weitergeben eines Bildes kurz die Ecken ansehen. Taucht eines auf, Seed um eins weiterdrehen, dann ist es weg.

### Gegen die Verdunklung: Prompt schlägt Regler (2026-09-21)

Aufgabe war ein sonniges, fröhliches Bild aus Workflow 09 (Blumenwiese, Frau im gelben Kleid, Mittagslicht). Sieben Wege, gleicher Seed 2424, 1216 x 832. Detail ist die Standardabweichung der Kantenantwort, also ein Maß für Feinstruktur. Blatt `out/ab_luneva/hell_leiter.jpg`.

| Weg | Helligkeit | Detail | Pixel über 200 |
|---|---|---|---|
| 00 pur (Referenz) | 131 | 58,0 | 4,9 % |
| 09 Voreinstellung 0.5 / 1.0 | 104 | 57,2 | 2,3 % |
| 09 Slider -1.0 | 172 | 37,9 | 18,8 % |
| 09 Slider -2.0 | 192 | 23,5 | 34,2 % |
| 09 Luneva 0.3 / Slider -1.5 | 182 | 32,8 | 27,7 % |
| **09 Voreinstellung + Hell-Wörter im Prompt** | **152** | **55,6** | 12,9 % |
| 09 Slider -1.0 + Hell-Wörter | 198 | 29,7 | 55,9 % |

**Der Prompt ist der bessere Hebel.** Hell-Wörter im Prompt heben die Helligkeit um 48 Punkte und kosten dabei nur 3 Prozent Feinstruktur (57,2 auf 55,6). Der Slider auf -1.0 hebt sie um 68 Punkte, kostet aber 34 Prozent Feinstruktur (57,2 auf 37,9), die Wiese verliert sichtbar Blüten und wird dunstig. Bei -2.0 ist ein Drittel des Bildes ausgefressen.

Die Wortliste, die gewirkt hat: `high key lighting, bright and airy, luminous, sun-drenched, glowing white highlights, light pastel palette, cheerful and joyful mood`. Beides zusammen (Slider -1.0 plus Hell-Wörter) überzieht: 56 Prozent der Pixel über 200, das Bild ist ausgewaschen.

**Regel für 09:** erst die Hell-Wörter in den Prompt, Regler unangetastet lassen. Reicht das nicht, den Detail Slider in Schritten von 0,5 senken und dabei zusehen, wo die Feinstruktur kippt. Der Slider ist das grobe Werkzeug, der Prompt das feine.

### Helligkeit auf CyberRealistic Z-Image: die Hell-Wörter wirken dort noch besser (2026-09-21)

Gegenprobe zum Wiesen-Test, diesmal auf `cyberrealisticZImage_v70_bf16` mit beiden LoRAs und dem Prompt des Referenzbildes `agent/2026-09-20/loratest-cyber_loras_00001_.png` (Nachtporträt am Fenster, Seed 555, 832 x 1216). Erschwerend: der Prompt sagt selbst `at night`, Helligkeit arbeitet hier gegen den Bildinhalt. Blatt `out/ab_luneva/cyber_hell.jpg`.

| Weg | Helligkeit | Detail | Pixel unter 30 |
|---|---|---|---|
| A Referenz 0.5 / 1.0, Originalprompt | 30 | 23,9 | 69,2 % |
| **B + allgemeine Hell-Wörter** | **99** | **40,0** | 23,1 % |
| C + nachtgerechte Hell-Wörter | 56 | 24,8 | 41,5 % |
| D Slider -1.0, Originalprompt | 121 | 16,0 | 5,9 % |
| E Slider -1.0 + Nacht-Wörter | 149 | 15,6 | 4,0 % |
| F Voreinstellung, Prompt ohne `at night` | 142 | 43,2 | 6,1 % |
| G ohne LoRA, Originalprompt | 57 | 17,6 | 41,4 % |

**Der Prompt gewinnt hier noch deutlicher als auf Z-Image-Turbo.** Die allgemeinen Hell-Wörter heben die Helligkeit von 30 auf 99 und steigern die sichtbare Textur zugleich von 23,9 auf 40,0. Der Grund ist im Bild zu sehen: die LoRAs setzen `high key lighting` als Gegenlicht um, Haarsträhnen und Stoff bekommen Kanten statt flächig aufgehellt zu werden. Der Slider auf -1.0 kommt zwar auf 121, drückt die Textur aber von 23,9 auf 16,0, die Haut wirkt retuschiert.

**Zwei Befunde gegen die Intuition:**
- Die vorsichtig formulierte nachtgerechte Wortliste (`bright even exposure, lifted shadows, soft luminous light on her face`) wirkt mit 56 deutlich schwächer als die pauschale Liste mit 99. Die pauschalen Begriffe sind offenbar das, was im Training steht, eigene Umschreibungen greifen nicht.
- Die Hell-Wörter löschen die Nacht nicht. In Variante B stehen die Neon-Bokehs weiter im Hintergrund, `high key lighting` wird als Lichtführung gelesen und nicht als Tageszeit. Wer wirklich Tageslicht will, muss `at night` aus dem Prompt nehmen (Variante F).

Zu beachten: die Hell-Wörter verschieben auch Pose und Ausdruck, nicht nur die Belichtung. Gleicher Seed, trotzdem andere Haltung. Wer eine bestehende Komposition nur aufhellen will, ist mit dem Upscale-Workflow oder einer Bildbearbeitung besser bedient als mit einem neuen Lauf.

## Krea-2-LoRAs: drei Regler im Workflow, vier Stile zum Tauschen (2026-09-21)

Sieben LoRAs vom Nutzer ausgesucht, alle Basis Krea 2, alle mit voll offener Lizenz (Sell, SellMerge, ohne Namensnennung). Geladen und prüfsummengeprüft, zusammen etwa 1 GB. Architektur vorab geprüft: alle sieben treffen 100 Prozent der Krea-2-Gewichte und null Prozent der Z-Image-Gewichte.

**Damit ist die Frage des Nutzers beantwortet: der vorhandene Z-Image-Detail-Slider wirkt auf Krea 2 nicht.** Gleicher Name, andere Architektur, null Überschneidung. Für Krea braucht es den eigenen.

Fest im Workflow `krea2_turbo_t2i.api.json`, alle auf 0.0 und damit aus:

| Knoten | Datei | Wirkung |
|---|---|---|
| DETAIL_LORA | `Detailer-KREA2.safetensors` (11 MB) | bei +2.0 Feinstruktur 33 auf 41, leicht dunkler |
| WARM_LORA | `WarmLightSlider-KREA2_v1.safetensors` (7 MB) | Helligkeit und Wärme, ohne Verlust an Feinstruktur |
| AFTERLIGHT_LORA | `Afterlight_v1.safetensors` (109 MB) | goldenes Gegenlicht, Dunst, Bokeh, höchste Feinstruktur |
| STYLE_LORA | wechselnd | Platz für die vier Stil-LoRAs, jede mit Trigger-Wort |

Stil-LoRAs für den STYLE_LORA-Knoten, je 218 MB: `Sticker_KREA2_V1` (Trigger `sticker`), `CharacterDesign-KREA2_v1` (`Character design`, Charakterbögen mit Vorder-, Seiten- und Rückansicht), `Pop-up_book_KREA2` (`pop-up book`), `Anatomy-Reveal-KREA2` (`Anatomy-reveal`, Querschnitte mit Knochen und Organen).

**Vier Knoten auf 0.0 sind wirklich neutral.** Bild mit den vier Knoten und Bild ohne sie waren byte-identisch (gleiche MD5 über die Pixel), die Laufzeit blieb bei 11 s. Die Knoten dürfen also dauerhaft im Graphen stehen.

Messreihe an einem Fischer am Hafen, Seed 7777, 1216 x 832 (Blätter `out/ab_luneva/krea_loras.jpg` und `krea_fein.jpg`). Helligkeit, Feinstruktur und Wärme als Differenz Rot minus Blau:

| Einstellung | Helligkeit | Detail | Wärme |
|---|---|---|---|
| alles aus | 103 | 33,2 | 14 |
| Warm +0,5 | 116 | 33,3 | 25 |
| Warm +1,0 | 134 | 32,7 | 39 |
| Warm +1,5 | 144 | 32,2 | 57 |
| Warm +3,0 | 185 | 17,3 | 132 |
| Warm -3,0 | 22 | 10,5 | -18 |
| Detail +2,0 | 92 | 40,9 | 5 |
| Afterlight 0,4 | 91 | 41,9 | 11 |
| Afterlight 0,8 | 80 | 42,0 | 13 |
| Afterlight 1,0 | 77 | 41,3 | 13 |
| Afterlight 0,6 + Detail 1,0 | 79 | 44,8 | 9 |

**Der Warm Light Slider ist der saubere Helligkeits-Hebel.** Zwischen +0,5 und +1,5 steigt die Helligkeit von 103 auf 144, die Feinstruktur bleibt dabei praktisch unverändert (33,3 auf 32,2). Das ist der Unterschied zum Z-Image-Detail-Slider, der Helligkeit nur gegen Detail eintauscht. Damit ist er die bessere Antwort auf dunkle Bilder als jede Prompt-Formulierung.

**Der Nutzbereich ist aber viel enger, als die Modellseite angibt.** Dort steht -6 bis +3. Gemessen ist +3 vollständig orange und ausgefressen (Wärme 132, Detail bricht auf 17 ein), -3 fast schwarz (Helligkeit 22). Brauchbar ist +0,5 bis +1,5, für kalt und dunkel -0,5 bis -1,5.

**Afterlight ist kein Aufheller, sondern ein Look.** Es verdunkelt (103 auf 77), hebt aber die Feinstruktur am stärksten von allen (33 auf 42) und bringt Gegenlicht, Glitzer auf dem Wasser und Dunst. Zusammen mit dem Detail-Slider auf 1,0 ergibt sich der höchste gemessene Detailwert der ganzen Reihe (44,8).

### Weight Slider und Realism Slider, dazu ein Sweep-Workflow (2026-09-21)

Zwei weitere Krea-2-Regler vom Nutzer ausgesucht, beide ohne Trigger-Wort, beide winzig und mit voll offener Lizenz: `WeightSlider-KREA2_v2.safetensors` (7 MB, Civitai 2751675) und `RealismSlider-v1.safetensors` (6 MB, Civitai 2781697). Beide hängen jetzt in `krea2_turbo_t2i.api.json` als `WEIGHT_LORA` und `REALISM_LORA` auf 0.0.

- **Weight Slider: ganzer Bereich -2 bis +2 brauchbar.** Die Figur geht sauber von sehr schlank nach kräftig, und zwar ohne Nebenwirkungen: Pose, Kleidung, Hintergrund, Licht und Gesicht bleiben stehen. Das ist das sauberste Slider-Verhalten der ganzen Sammlung. Blatt `out/ab_luneva/krea_weight.jpg`.
- **Realism Slider: nur -1 bis +1 brauchbar.** Gemessen an einem Ritter in einer Ruine (Helligkeit und Feinstruktur): -2 ergibt 162 und 46,0, zerfällt aber in abstrakte Farbflächen ohne lesbares Motiv. -1 ergibt 144 und 50,0, eine saubere flache Comic-Zeichnung. 0 ergibt 81 und 36,6, gemalte Fantasy-Illustration. +1 ergibt 63 und 22,2, fotografisch und dunkel. +2 ergibt 64 und 17,5, matschig. Die Ränder sind also nicht nur geschmacklich daneben, sie verlieren messbar Struktur. Blatt `out/ab_luneva/krea_realism.jpg`.

**Neuer Workflow `krea2_slider_sweep.api.json` (UI: 11-regler-vergleich).** Er beantwortet die Frage, wie ein Regler wirkt, in einem einzigen Lauf: derselbe Prompt und Seed fünfmal gerechnet mit -2, -1, 0, +1, +2, danach über `ImageConcatMulti` (kjnodes) zu einem Blatt nebeneinandergelegt und als eine Datei gespeichert. 23 Knoten, etwa 50 s, also fünfmal die Zeit eines Einzelbildes. Alle fünf Sampler tragen den Titel SAMPLER, deshalb setzt die Injektion des Skripts automatisch denselben Seed in alle fünf, was genau die Voraussetzung für einen gültigen Vergleich ist.

Die zu prüfende LoRA steht in den fünf Knoten STUFE_1 bis STUFE_5 und muss beim Wechsel fünfmal gesetzt werden. Das ist der Preis dafür, dass ComfyUI ohne Zusatzknoten keinen gemeinsamen Dateiparameter kennt.

**Sechs LoRA-Knoten auf 0.0 bleiben neutral.** Nach dem Einhängen der zwei neuen Regler kam bei gleichem Seed dasselbe Bild heraus wie mit vier Knoten, Pixel-Prüfsumme identisch (75c933311dcb). Die Kette darf also weiter wachsen, ohne dass das Grundbild kippt.

## Alte Bilder neu rendern: der alte Prompt entscheidet, nicht das Modell (2026-09-21)

Probelauf für Etappe 4 der Bildgalerie: zehn Motive aus `library\` mit verschwundenen Modellen (Flux.1 Schnell, Chroma1 HD, PerfectWorld v6, GhostMix v2, PerfectDeliberate-Anime), je zwei heutige Zielmodelle, 20 Bilder in einem Lauf, kein Fehlschlag. Zeiten auf der 5070 Ti: Z-Image 7,6 s, CyberRealistic Z-Image 7,7 s, Krea 2 10,6 bis 12 s, Qwen 12 s, WAI-illustrious 9 bis 11 s, Illustrious Realism 10,7 s, dazu einmalig 6 bis 21 s Modellladen je Familie. Blätter unter `out/regen_2026-09-21/`.

**Gewonnen hat das neue Modell dort, wo der alte Prompt das Bild wirklich beschreibt.** Beim Cyberpunk-Porträt (Chroma, ganze Sätze) liefern CyberRealistic Z-Image und Krea 2 echte Fotos, wo das Original illustrativ blieb. Beim Anime-Paar (PerfectDeliberate-Anime, Tags) trägt WAI-illustrious die Tag-Sprache unverändert und wirkt sauberer als das Original, Illustrious Realism kippt dasselbe Motiv ins Halbrealistische und verliert dabei Prompt-Details (grüne Augen).

**Verloren hat es dort, wo der alte Prompt vage war.** Die PerfectWorld-Landschaft besteht aus sieben generischen Tags (`breathtaking mountain landscape at sunrise, volumetric light, detailed rocks`). Das Original zeigt eine markante Felsnadel über dem Nebelmeer mit einer Figur, die neuen Modelle bauen daraus ein beliebiges Tal. Das Modell ist nicht schlechter, der Prompt beschreibt das Bild nur nicht. Genau dafür ist der Captioning-Schritt gedacht (Florence2 über das Quellbild), die Gewichte liegen lokal aber noch nicht, nur der Node `comfyui-florence2`.

**Doppelbelichtung braucht den Cinematic-Workflow.** Der Flux-Prompt `double exposure photography, side profile silhouette filled with a pine forest` ergibt auf Z-Image pur einen Mann, dem der Wald aus dem Kopf wächst, Qwen trifft die Idee besser, füllt die Silhouette aber unsauber. Das Flux-Original bleibt klar vorn. Für diesen Look ist `zimage_cinematic_t2i.api.json` (Luneva) der richtige Weg, nicht der Standard-Turbo-Graph.

**Zweck schlägt Bildqualität.** Der Menü-Hintergrund `kristallwacht` lebt davon, dass das Motiv klein ist und die Ränder ins Schwarz auslaufen. Z-Image und Qwen rendern detailreicher und heller, setzen die Kristalle aber groß in die Mitte und taugen damit schlechter als UI-Hintergrund. Beim Neu-Rendern von Assets also den Verwendungszweck mitprüfen, nicht nur das Bild.

## Detail-Regler bei gleichem Seed gemessen (2026-09-21)

Zwölf Paare aus dem Regenerationslauf, je zweimal derselbe Prompt und derselbe Seed, einmal ohne Regler und einmal mit. Gemessen wurde die mittlere Helligkeit und die Varianz des Kantenbildes als Maß für Feinstruktur.

**Mittel über alle zwölf: Feinstruktur plus 12,5 Prozent, Helligkeit minus 11,9 Punkte.** Der Regler zahlt also Struktur mit Dunkelheit, wie die älteren Messungen es schon andeuteten, und jetzt mit festem Seed belegt.

Nach Modell getrennt: **Krea 2 mit Detailer auf 1,5 profitiert deutlich** (Landschaft plus 29 Prozent, Bergpanorama plus 31, Wohnzimmer plus 12, Cyberpunk plus 20, Strand plus 7). **Z-Image mit 0,5 bis 1,0 profitiert schwach** (plus 1 bis plus 15 Prozent). Der Krea-Detailer ist der wirksamere der beiden, der Z-Image-Slider eher ein Feinschliff.

**Gegenbeispiel, das die Regel bestätigt:** beim dunkelsten Motiv (Menü-Hintergrund `kristallwacht`, Ausgangshelligkeit 28) fällt die Feinstruktur mit dem Slider auf 1,0 um 5 Prozent und die Helligkeit auf 19. Bei ohnehin dunklen Bildern wirkt der Regler also gegen sich selbst, dort gehört er auf 0 oder ins Negative.

**Wichtig für jeden künftigen Reglervergleich: ohne festen Seed ist er wertlos.** Der erste Durchgang lief ohne `--seed`, dort unterschieden sich die Bilder durch Seed und Regler gleichzeitig und der Effekt war nicht ablesbar. Der Seed steht im PNG-Graphen und lässt sich von dort übernehmen.

## Florence-2 läuft nicht mehr in der ComfyUI-venv (2026-09-21)

Für das Neu-Rendern alter Bilder wird eine Bildbeschreibung gebraucht, wenn der alte Prompt zu vage ist. Geladen wurde `MiaoshouAI/Florence-2-large-PromptGen-v2.0` nach `ComfyUI\models\LLM\` (3,3 GB, nicht die oft genannten 1 GB, die Gewichte liegen in fp32).

**Das Custom Node `comfyui-florence2` ist mit ComfyUI 0.36.0 nicht mehr lauffähig**, weil dort transformers 5.12 liegt. Drei verschiedene Brüche nacheinander: `Florence2LanguageConfig` hat kein `forced_bos_token_id` mehr (transformers 5 hat die Generierungsfelder aus der Config entfernt), `_tied_weights_keys` muss ein Dict sein statt einer Liste, und der Node-eigene Pfad für neuere transformers greift nur für das Modell, nicht für den Processor. Einzelpatches zur Laufzeit reichen nicht, das ist echte API-Drift.

**Lösung ohne Eingriff in ComfyUI:** eine eigene venv `D:\Repos\comfy-gallery\.venv-caption` mit transformers 4.49, die sich die GPU-torch aus der ComfyUI-venv borgt, indem deren `site-packages` im Skript per `sys.path.append` ANS ENDE gehängt wird. Die venv findet dann ihr eigenes transformers zuerst und torch 2.14+cu130 danach, `cuda.is_available()` bleibt True. `--system-site-packages` allein reicht nicht, weil eine venv aus einer venv nicht transitiv erbt. Zweiter Fallstrick: die venv darf nicht im Scratchpad-Verzeichnis liegen, der Pfad wird für `pip` zu lang (MAX_PATH).

**Qualität:** die Beschreibung trifft Motiv, Bildausschnitt und Stimmung gut und liefert genau die Satzform, die Z-Image und Krea 2 wollen. Sie erfindet aber Details: beim Catgirl-Motiv ein gestreiftes Kleid, das im Original weiß mit blauer Schleife ist, beim Rooftop-Motiv rote Augen, die es nicht gibt. Also als Rohstoff nehmen und gegenlesen, nicht blind einsetzen. Etwa zwei Sekunden je Bild auf der 5070 Ti.

## Detail-LoRAs für die SDXL-Modelle: geprüft, aber kein Ersatz für den Upscale (2026-09-22)

Auftrag war, für die übrigen Modelle Detail-LoRAs zu suchen, einzubauen und zu testen. Anlass: dem Nutzer fallen bei WAI-illustrious fehlende Details auf.

**Für Qwen-Image gibt es keine.** Vier Suchbegriffe (detail, detailer, sharp, realism) über die Civitai-API, null Treffer bei Basis Qwen. Die vorhandenen Qwen-LoRAs sind Edit-Helfer und Realismus-Stile, kein Detail-Regler.

Installiert und geprüft wurden drei Kandidaten, alle mit engerer Lizenz als die Krea-LoRAs (`allowCommercialUse: ['RentCivit']`, keine Namensnennung erlaubt, keine Ableitungen): der Verkauf erzeugter Bilder ist davon nicht gedeckt.

| LoRA | Basis | Größe | Wirkung im Test |
|---|---|---|---|
| `StS-Illustrious-Detail-Slider-v1.0` | Illustrious | 8 MB | greift, Effekt aber im Rauschen |
| `StS_PonyXL_Detail_Slider_v1.4_iteration_3` | Pony | 17 MB | greift, hebt sichtbar den Hintergrund |
| `detailed skin style illustriousXL v1` (Detailed Perfection) | Illustrious | 435 MB | greift, ändert die Komposition, hebt das Detail nicht |

### Das Messinstrument musste zweimal gewechselt werden

Erster Versuch war ein statischer Abgleich der Tensornamen wie bei den Z-Image- und Krea-LoRAs. Er meldete für ALLE Kombinationen "passt nicht", auch für Modelle, die sicher passen. Grund: SDXL-LoRAs benutzen die Diffusers-Namensform (`lora_unet_down_blocks_0_...`), der Checkpoint die ursprüngliche (`model.diffusion_model.input_blocks...`), ComfyUI übersetzt erst beim Laden. Der Abgleich taugt also nur innerhalb derselben Namensfamilie.

Zweiter Versuch war das ComfyUI-Log auf "lora key not loaded". Die Gegenprobe (Z-Image-Slider auf Krea 2, bekannt unwirksam) schlug NICHT an. Ursache: `user/comfyui.log` wird seit dem 23.06.2026 nicht mehr beschrieben, die Datei ist tot. Ohne die Gegenprobe hätte dieses Instrument jedem Lauf "greift" bescheinigt.

Drittes und tragfähiges Instrument: Bildvergleich bei gleichem Seed. Greift eine LoRA nicht, ist das Ergebnis pixelgleich mit dem Lauf ohne sie. Kontrolliert an zwei Fällen mit bekanntem Ausgang, Negativfall identisch und Positivfall abweichend, beide wie erwartet. Erst danach galten die Messungen.

### Was tatsächlich Details bringt

Gemessen an demselben WAI-Motiv, Detail als Standardabweichung der Kantenantwort:

| Weg | Detail | Änderung |
|---|---|---|
| WAI direkt | 42,9 | Referenz |
| Detail-Slider +1,0 | 43,9 | +2 % |
| Detailed Perfection 0,8 | 43,3 | +1 % |
| Upscale 2x über Workflow 03, auf Ausgangsgröße zurückgerechnet | 49,2 | **+15 %** |

Die zwei Prozent der LoRAs sind auch im Bild nicht zu sehen, die fünfzehn Prozent des Upscale schon: feinere Haarsträhnen, schärfere Iris mit Lichtern, lesbarere Neonschrift. Blätter `out/ab_luneva/detail_upscale.jpg` und `detail_wai_vergleich.jpg`.

**Schlussfolgerung für die Praxis:** bei Illustrious kommt Detail aus dem zweiten Durchgang, nicht aus einer LoRA. Wer mehr Details will, nimmt das fertige Bild und schickt es durch 03 mit dem Anime-Checkpoint als Refiner (`--checkpoint waiIllustriousSDXL_v170.safetensors`, denoise 0,25, 55 s). Die Slider stecken trotzdem in 06 und 08 auf 0.0, sie kosten nichts und heben bei Pony sichtbar den Hintergrund.

**Wichtiger Unterschied zu Krea 2: bei SDXL ist ein LoRA-Knoten auf 0.0 nicht neutral.** Gemessen am selben WAI-Motiv mit gleichem Seed weichen rund zehn Prozent der Pixel um mehr als 8 von 255 ab, sichtbar am Schnitt der Jacke. Ursache ist vermutlich der Umweg über die Patch-Berechnung, der die Gewichte einmal durch eine andere Genauigkeit schickt; über 40 Sampling-Schritte verstärkt sich das. Bei Krea 2 waren sechs Knoten auf 0.0 dagegen pixelgenau neutral. Folge für die Bedienung: wer in 06 oder 08 exakt das Bild von vorher will, muss den Knoten per Strg+B bypassen statt ihn auf 0.0 zu stellen. Das steht als Hinweis in beiden Workflow-Notizen.


### Illustrious zweistufig: Detail gehört in den Workflow, nicht in eine LoRA (2026-09-22)

Konsequenz aus dem Detail-LoRA-Test: Workflow 06 rechnet jetzt zwei Durchgänge in einem Lauf. Stufe 1 ist unverändert (960 x 1664, etwa 20 s, Ablage `anime`), Stufe 2 schickt das decodierte Bild durch UltimateSDUpscale mit demselben Checkpoint als Refiner (4x-UltraSharp, denoise 0,25, 20 Steps, cfg 7, euler_ancestral/normal) und speichert nach `anime-detail` in 1920 x 3328.

| Weg | Detail (auf Ausgangsgröße gerechnet) |
|---|---|
| Stufe 1 allein | 42,9 |
| Stufe 2 im selben Workflow | **50,9** |
| separat über Workflow 03 mit Pony-Refiner | 49,2 |

Die eingebaute Stufe schlägt den separaten Lauf über 03, weil der Refiner derselbe Anime-Checkpoint ist und die Sampler-Werte zum Modell passen. Sichtbar an einzelnen Haarsträhnen, scharfer Iris mit Lichtern, Regentropfen im Haar und lesbarerer Neonschrift.

Zwei Anpassungen, die dazugehören:
- `comfy_generate.py` gibt bei mehrstufigen Workflows jetzt die letzte Stufe zurück. Erkannt wird sie am Titel `SAVE_DETAIL`, fehlt der, bleibt es bei der ersten Ausgabe wie bisher.
- Der Konverter hängt `-detail` an den Ablagepfad eines `SAVE_DETAIL`-Knotens. Sonst hätten beide Stufen in denselben Zähler geschrieben und wären nicht auseinanderzuhalten.

Wer nur Varianten durchprobieren will, bypasst den Knoten UPSCALE mit Strg+B und ist wieder bei 20 s. Dass 08 (Pony) dieselbe Behandlung bekommt, ist offen: dort wirkt der Detail-Slider bereits sichtbar und der Nutzer hat keinen Mangel gemeldet.

### Ist CyberRealistic Pony noch gerechtfertigt? (2026-09-22)

Nutzerfrage, deshalb nachgemessen statt aus dem Bauch beantwortet. Pony wurde am 19.09. als drittes Standbein für Menschen, Posen und das Pony-LoRA-Ökosystem installiert. Getestet wurde genau das: drei Motive mit Menschen und Händen, gleicher Seed, je gegen Krea 2 und Z-Image, Pony mit seinen score-Tags und vollem Negativ-Prompt, also unter Idealbedingungen.

| Motiv | Befund |
|---|---|
| Frau winkend vor Studiohintergrund | Pony ignoriert `plain studio backdrop` und setzt sie auf eine Straße. Krea und Z-Image liefern beide den geforderten Studiogrund. |
| Tanzendes Paar, Tango | Pony zieht die Frau in Dessous statt Tanzkleidung und erfindet ein Publikum. Krea und Z-Image liefern beide ein korrektes Tangopaar. |
| Töpferhände an der Scheibe | Pony verfehlt das Motiv vollständig, es entsteht ein Wagenrad statt einer Töpferscheibe, kein Ton, keine Schale. Krea und Z-Image treffen beide inklusive nasser Tonhände. |

**Pony verliert drei von drei bei der Prompt-Treue**, und zwar deutlich. Dazu kommt eine Tendenz zur Sexualisierung auch bei harmlosen Prompts (Tango-Motiv).

**Warnung zur Kennzahl:** der Detailwert spricht scheinbar für Pony (24,5 gegen 19,2 und 19,7 beim Posen-Motiv, 27,8 gegen 16,4 und 18,0 bei den Händen). Das misst hier aber nur, dass Ponys Bilder voller sind (Straße statt leerer Studiogrund, Publikum statt leere Bühne). Ein volleres Bild ist kein besseres Bild, wenn der Prompt etwas anderes verlangt hat. Schulbeispiel dafür, dass die Metrik Diagnose ist und nicht Urteil.

**Was trotzdem gegen ein sofortiges Löschen spricht:**
- Pony ist der Refiner in Workflow 03 (Upscale). Ohne Ersatz bricht 03 weg. Für Anime ist der Ersatz seit heute belegt (eigener Checkpoint als Refiner schlägt Pony, 50,9 gegen 49,2), für Foto-Upscale ist es ungetestet.
- Das Pony-LoRA-Ökosystem war der eigentliche Installationsgrund. Genutzt wird es bisher nicht: 1 von 90 Ledger-Einträgen, eine einzige Pony-LoRA auf der Platte.
- Der NSFW-Fall ist hier nicht gemessen. Der Nutzer generiert das selbst, die Tests oben sind alle SFW. Ob Pony dort gegen CyberRealistic Z-Image verliert, ist offen.

Stand: Kandidat für die Streichliste (6,5 GB), aber erst nach einem Refiner-Test für den Foto-Upscale und einer Aussage des Nutzers zum NSFW-Fall. Nicht eigenmächtig entfernt.

### Refiner-Vergleich für den Foto-Upscale: Krea 2 gewinnt (2026-09-22)

Letzte technische Abhängigkeit von Pony geprüft. Testbild war bewusst ein altes FLUX-Bild aus `library/menschen` (Modell nicht mehr installiert), damit kein Kandidat sein eigenes Werk nachschärft. Gemessen wurde die Feinstruktur, auf die Ausgangsgröße zurückgerechnet, damit nicht bloße Pixelzahl gewinnt.

| Refiner | Detail | gegen das Original |
|---|---|---|
| Original ohne Upscale | 40,9 | Referenz |
| **Krea 2 Turbo** | **44,4** | **besser** |
| CyberRealistic Pony v18 (bisher) | 40,0 | schlechter |
| Z-Image-Turbo | 38,5 | schlechter |
| Illustrious Realism v4 | 37,7 | schlechter |

Krea 2 ist der einzige Kandidat, der über das Ausgangsbild hinauskommt, und man sieht es: Hautporen, Sommersprossen, einzelne Wimpern, Haarsträhnen mit Struktur, Stoffbindung am Kragen. Die anderen drei glätten mehr, als sie nachrechnen.

Workflow 03 läuft seither auf Krea 2. Umbau: `CheckpointLoaderSimple` ersetzt durch `UNETLoader` plus `CLIPLoader` (Typ `krea2`) plus `VAELoader`, Negativ über `ConditioningZeroOut` genullt, cfg 1.0, 8 Steps, euler/simple. 50 s für 768 x 1024 auf das Doppelte. In `upscale.py` fiel dabei die Automatik weg, die jedem Prompt `score_9, score_8_up, score_7_up` voranstellte, und `--checkpoint` bedient jetzt beide Loader-Arten.

Stolperstein beim Umbau: `UltimateSDUpscale` verlangt `batch_size` als Pflichtfeld, sonst antwortet ComfyUI mit HTTP 400 und der Meldung `Required input is missing batch_size`. Die Fehlermeldung steht nur in der Antwort auf `/prompt`, nicht im Ausgabetext der Skripte.

**Damit hängt an CyberRealistic Pony nur noch Workflow 08.** Der Nutzer hat am 22.09. bestätigt, dass er es für NSFW nicht braucht. Pony verliert drei von drei Prompt-Treue-Tests, wird in einem von 90 Ledger-Einträgen genutzt, und eine einzige Pony-LoRA liegt auf der Platte. Streichung vorgeschlagen, 6,5 GB, aber nicht eigenmächtig ausgeführt.

### Korrektur: die Detail-Kennzahl taugt nicht als Urteil über Natürlichkeit (2026-09-22)

Ich hatte Krea 2 als besten Foto-Refiner empfohlen, gestützt auf die Standardabweichung der Kantenantwort: 44,4 gegen 40,9 beim Original, als einziger Kandidat darüber. Der Nutzer hat widersprochen, Krea übertreibe sichtbar, besonders im Haar, Z-Image wirke echter. **Die Wahrnehmung gewinnt, die Messung war untauglich für diese Frage.**

Der Grund liegt in der Natur der Kennzahl: sie zählt Kantenenergie. Ein Refiner, der zu viel Struktur erfindet, erzeugt genau davon mehr, und zwar umso mehr, je künstlicher er wird. Überschärfung und echtes Detail sind für dieses Maß dasselbe. Es kann anzeigen, DASS ein Refiner arbeitet, aber nicht, ob das Ergebnis natürlich aussieht.

Konsequenz für künftige Refiner- und Schärfe-Tests: die Zahl nur noch als Diagnose berichten, nie als Ranking. Die Reihenfolge bestimmt der Blick auf den Ausschnitt in Originalgröße, bei Haaren, Haut und Stoff. Und eine Messung, die genau in die Richtung zeigt, die ein Fehlerbild erzeugt, gehört als solche gekennzeichnet.

Workflow 03 läuft seit dieser Korrektur auf Z-Image-Turbo (UNETLoader plus CLIPLoader `lumina2` plus VAELoader, cfg 1.0, genulltes Negativ, 8 Steps res_multistep/simple, 44 s für 768 x 1024 auf das Doppelte).

## Anime auf Ansage: alle Satzmodelle können es, ein Modell kann es nicht (A/B 2026-09-22)

Drei Motive (Catgirl am Teich, Agentin auf dem Dach, Magierin im Wald), sechs installierte Modelle, 896 x 1344, Regler aus, jedes Modell in seiner Prompt-Sprache: Sätze plus ausdrückliche Stilangabe (`anime illustration in a clean cel-shaded style, bold lineart, flat vivid colours, large expressive eyes, japanese animation look, not photorealistic`) für Z-Image, CyberRealistic Z-Image, Krea 2 und Qwen, Danbooru-Tags mit `embedding:lazypos` für die Illustrious-Linie. Blätter: `out/ab_anime_2026-09-22/anime_<motiv>.jpg`.

**Der Befund widerspricht der Tabelle in models.md.** Dort führt WAI-illustrious als einziges Anime-Modell. Tatsächlich liefern alle vier Satzmodelle sauberes Cel-Shading, sobald der Stil im Prompt steht, keines fällt ins Fotorealistische zurück. **Auf Stilebene sieht das zunächst nach einem Gleichstand aus, auf Detailebene nicht.** Nutzerurteil, an Ausschnitten nachgeprüft: Qwen-Image liegt vorn, es liefert die detailreichsten Anime-Bilder und als einziges der Satzmodelle saubere Hände (Agentin: fünf klar modellierte Finger im Handschuh). Krea 2 folgt mit dem markantesten Stilgriff (harte Farbflächen, Animationsfilm-Look). Z-Image und CyberRealistic Z-Image treffen den Stil, patzen aber in den Details: aufgesetzt wirkende Katzenohren mit hartem Fellabsatz, Füße im Teich ohne Brechung und ohne Spiegelung, bei der Agentin eine Hand aus fünf gleichlangen Stäben (CyberRealistic) und eine nicht auflösbare Bein-Hand-Silhouette (Z-Image). Wer Anime auf einem Satzmodell rendert, nimmt also Qwen oder Krea 2 und prueft Hände und Wasserlinien. WAI-illustrious ist am nächsten am Genre, patzte aber bei der Agentin (Kopf gesenkt, Gesicht verdeckt).

**Illustrious Realism v4 kann kein Anime, auch nicht auf Ansage.** Bei allen drei Motiven kam Fotorealismus heraus, beim Catgirl mit aufgesetzt wirkenden Katzenohren. Das Modell gehört zu halbrealistischen Figuren, nicht ins Anime-Fach. Wer es dort einsetzt, misst nicht Modellqualität, sondern die falsche Werkzeugwahl: in der Bildgalerie waren dadurch 70 Bilder aus Anime-Vorlagen mit ihm gerendert und hätten jedes Duell gegen WAI verloren.

Zeiten je Bild: Z-Image 9,5 s, CyberRealistic 18,2 s, Krea 2 22,7 s, Qwen 34,7 s, WAI 56,4 s, Illustrious Realism 58,8 s (jeweils erster Lauf inklusive Modellladen).

## Krea 2: der Realism-Slider ist ein Stilregler, auch ohne Stilwort im Prompt (2026-09-22)

**Der Regler gehört an realistische Prompts, nicht an solche, die ohnehin nach Anime fragen** (Nutzerentscheidung 22.09.2026): steht der Stil schon im Prompt, misst man nur, wie weit der Regler ihn zusätzlich verflacht, und das ist keine brauchbare Frage. Maßgeblich ist deshalb der zweite Durchgang. Aufbau: `RealismSlider-v1` im Knoten REALISM_LORA von `krea2_turbo_t2i`, Stufen 0, -0,5, -1,0 und -1,5, sonst alles unverändert, drei nüchterne Fotobriefs ohne jedes Stilwort (Winzer im Weinberg, Straßencafe, Werkstatt). Der erste Durchgang lief auf den Anime-Motiven von oben und bleibt nur als Beleg für die Verflachung liegen. Blätter: `out/ab_anime_2026-09-22/krea_realism_<motiv>.jpg` und `krea_foto_<motiv>.jpg`.

**Der Regler allein macht aus einem reinen Fotoprompt Illustration, das Stilwort ist dafür nicht nötig.** Die Stufen wirken sehr gleichmäßig: 0 ist ein echtes Foto, -0,5 eine gemalte Illustration mit realistischen Proportionen, -1,0 eine flächige Vektor-Illustration mit klaren Farbflächen, -1,5 fast Plakat oder Kinderbuch, dort gehen Gesichtszüge und Kleindetails verloren.

**Welcher Illustrationsstil bei -0,5 herauskommt, hängt am Motiv.** Der Winzer wurde ein Ölgemälde, die Werkstattszene ein klarer Anime-Look im Ghibli-Register. Wer einen bestimmten Stil will, nennt ihn weiterhin im Prompt, der Regler steuert nur, wie weit weg vom Foto das Bild landet.

**Praktischer Nutzen:** -0,5 bis -1,0 ist der schnellste Weg von einem vorhandenen Fotoprompt zu einer Illustrationsfassung desselben Motivs, ohne den Prompt anzufassen. Unter -1,0 wird es dekorativ, für Figuren mit erkennbarem Gesicht zu grob.

## Qwen-Anime: Steps und Licht bringen die Qualität, Auflösung allein nicht (2026-09-22)

Der Nutzer stellte fest, dass die neu gerenderten Anime-Bilder nur knapp an die alte PerfectDeliberate-Vorlage herankommen und dass Licht, Schatten und Feindetail fehlen. Vier Varianten desselben Motivs, je ein Hebel verändert, Blatt `out/regen_qwen_2026-09-22/qwen_qualitaet_catgirl.jpg`:

| Variante | Zeit | Wirkung |
|---|---|---|
| Turbo-LoRA, 2 Steps, cfg 1.0, 1,2 MP (Serienlauf) | 12 s | flach, wenig Textur, blasse Blütendetails |
| dieselbe Turbo-Kette bei 2,2 MP | 17 s | kaum besser, **Auflösung allein bringt fast nichts** |
| Turbo aus, 30 Steps, cfg 4.0, 1,2 MP | 111 s | **der große Sprung**: Sättigung, Stoffmuster, Blütenstruktur |
| dasselbe bei 2,2 MP | 242 s | nochmals etwas mehr Hintergrunddetail |
| 2,2 MP plus Licht- und Schattenworte im Prompt | 233 s | Gegenlicht im Haar, Spiegelung auf dem Wasser, Sonnenuntergang |

**Die Turbo-LoRA ist der Grund für den Qualitätsabstand, nicht das Modell.** Zwei Schritte reichen für Komposition und Farbe, nicht für Feinstruktur. Wer ein Ergebnis behalten will, rechnet es mit Turbo auf 0.0, 30 Steps und cfg 4.0 nach, das kostet etwa den Faktor zehn an Zeit. Ein eigener Qualitäts-Workflow existiert seit der Konsolidierung nicht mehr, die drei Werte werden im Graphen gesetzt (Knoten TURBO_LORA und SAMPLER).

**Licht gehört ausdrücklich in den Prompt.** Florence-2 beschreibt Motive nutzbar, nennt Lichtführung aber selten. Eine angehängte Zeile (`soft warm sunset light from the side, gentle rim light, soft shadows, reflected light`) kostet nichts und ist bei diesem Test der sichtbarste Einzelgewinn nach den Steps.

**Was auch so nicht zurückkommt:** die Vorlage zeigt die Figur bis zu den Knien IM Teich, mit Blütenblättern auf dem Wasser und feiner Linienführung. Alle Qwen-Fassungen zeigen ein Halbporträt am Ufer in kräftigerem Digital-Anime. Ursache ist die Beschreibung: Florence-2 schrieb "standing by a serene river", nicht "wading in a shallow pond". Wo die Komposition zählt, muss die Caption gegengelesen und der Bildausschnitt ergänzt werden, sonst verschiebt sich das Motiv unbemerkt.

## Caption gegenlesen ist der größte Einzelhebel, nicht die Sampler-Einstellung (2026-09-22)

Acht vom Nutzer mit zwei oder drei Sternen bewertete Bilder neu gerechnet, je mit geprüfter Beschreibung, angehängter Lichtzeile und anschließendem Detailpass (`upscale.api.json`, UltimateSDUpscale, denoise 0,2, das Gegenstück zum Hires-Fix der alten SD1.5-Bilder). Blätter: `out/nachrechnen_2026-09-22/`.

**Drei von vier geprüften Beschreibungen waren sachlich falsch, und der Fehler stand unbemerkt im Bild.** Beim Logo-Motiv schrieb Florence-2 "bear head", die Vorlage zeigt einen Tigerkopf: das bewertete Bild war folglich ein Bär. Beim Catgirl-Motiv wurde aus einem weiß-hellblauen Rüschenkleid mit Blumenmuster ein "blue and white striped dress" und aus "knöcheltief im Kanal stehend" ein "standing by a serene river", weshalb alle Fassungen ein Halbporträt am Ufer zeigten. Bei der Landschaft rückte die Caption die winzige Figur ins Zentrum und verschwieg die Felsnadeln, die das Bild ausmachen.

Nach der Korrektur stimmen Tier, Kleidung, Standort und Bildausschnitt. Das ist ein größerer Gewinn als jede Reglerstellung: ein technisch besseres Bild vom falschen Motiv bleibt falsch.

**Merksatz für künftige Läufe:** die Caption ist Rohstoff, kein Prompt. Vor einem Lauf, dessen Ergebnis behalten werden soll, gehört sie gegen das Quellbild gelesen, mindestens auf Motiv, Kleidung, Standort und Bildausschnitt. Bei Massenläufen, die nur sichten sollen, ist das unnötig.

**Detailpass:** er bringt sichtbar Feinstruktur (Stoffmuster, Blüten, Fell) und kostet 30 bis 60 s je Bild. Den Stilcharakter der alten SD1.5-Anime-Modelle (weiche, handgemalte Textur, dichter Faltenwurf) erreicht er nicht, der kommt aus dem Modell, nicht aus der Auflösung.

## Kinderbuchillustration kann Krea 2 bereits, Illustrious kann es nicht (2026-09-22)

Sieben installierte Varianten auf denselben Prompt und Seed 7301, Blatt `out/vergleich_kinder.png`. Anlass war die Annahme, hier klaffe die größte Lücke im Bestand und es brauche ein zusätzliches Modell.

**Krea 2 ohne jede LoRA gewinnt.** Beide Figuren groß im Bild, klare Silhouetten, warmes Licht, saubere Anatomie: eine fertige Kinderbuchseite. Dafür braucht es keinen Download.

**Die Stil-LoRAs verschieben den Stil, sie heben nicht die Qualität.** Character Design 0.8 zieht die Linien klarer und hellt auf, schreibt aber unaufgefordert "TORED MATS" als Fantasietext ins Gras. Für Druckmaterial ist das ein echter Mangel, weil solche Buchstabenreste erst beim Korrekturlesen auffallen. Pop-up book 0.8 liefert genau das Versprochene, also ein abfotografiertes aufgeklapptes Buch, und ist damit ein Spezialeffekt statt eines Illustrationsstils. Realism Slider -1.0 flacht Richtung Kleinkindbuch ab und kostet Anatomie: Dinoarm und Fuchsschwanz verschmelzen.

**Z-Image trifft den Stil, verfehlt aber die Bildaufteilung.** Flache moderne Vektoroptik, die für Druck gut taugt, die Figuren stehen jedoch klein und weit auseinander und dem Dino fehlen die Arme.

**Qwen-Image-2512 wird dritter:** hübsches Licht, aber gerenderte 3D-Optik statt Illustration und ein fast fotografischer Fuchs.

**WAI-illustrious fällt durch.** Kein Dinosaurier im Bild, nur ein Fuchs in rosa Wald, trotz passender Danbooru-Tags. Das Modell bleibt für Anime, sonst nichts.

**Folge für den Bestand:** Kinderillustration ist keine Lücke. Krea 2 deckt sie ab, die vier Stil-LoRAs sind Effekte für den Sonderfall.

## Kurzer Text im Bild ist kein Alleinstellungsmerkmal von Qwen mehr (2026-09-22)

Blatt `out/vergleich_leon.png`, gleicher Prompt und Seed 7301. **Alle drei getesteten Modelle schreiben LEON korrekt.**

Qwen-Image-2512 setzt die Buchstaben tatsächlich aus Dinosauriern zusammen, zweizeilig als LE über ON, und trifft die Aufgabe am genauesten. Krea 2 schreibt LEON einzeilig in fetter Schrift und stellt die Dinosaurier daneben statt hinein, hat dafür die saubersten Buchstabenkanten. Z-Image liefert die flachste Vektoroptik und ist damit die beste Vorlage zum Nachbauen als SVG.

**Einschränkung:** vier Großbuchstaben eines geläufigen Vornamens sind der leichte Fall. Für deutschen Text kippt Qwen reproduzierbar (Befund weiter oben), längere Wortmarken sind ungetestet. Für Namensgrafiken reicht also jedes der drei Modelle, für Werbetext im Bild gilt der alte Befund weiter.

## Freistell-Kette am heutigen Modellstand geprüft (2026-09-22)

Anlass war die Frage, ob die Freistellungen aus der bildstil-lab-Zeit noch dem heutigen Stand entsprechen. Aufbau: vier Motive mit unterschiedlichem Rand (Haarsaum, harte Produktkante mit Henkelloch, filigraner Farnwedel, halbtransparente Pusteblume), je gleicher Motivtext und gleicher Seed, 1024 x 1024. Weg A ist Workflow 01, also flacher einfarbiger Grund mit BiRefNet im selben Graphen. Weg B ist Workflow 00 mit echter Szene und danach Workflow 02. Entschieden wurde am 1:1-Ausschnitt an der Stelle mit der höchsten Dichte halbtransparenter Pixel, jeweils auf Hellgrau, auf Dunkel und als Alpha-Maske. Blätter: `out/freistellung_2026-09-22/`.

**Weg A gewinnt dort, wo der Rand schwierig ist.** Beim Haar löst der flache Grund einzelne Strähnen bis in die feinen Spitzen, Weg B zerhackt dieselben Strähnen in einzelne Striche und legt einen hellen Halo um die Silhouette. Beim Farn löst Weg A die Zähnung der Fiederblätter, Weg B rundet sie ab und zieht einen dunklen Saum vom Waldboden mit (Saum-RGB 38/52/19 gegen 124/159/83 im Blattinneren). Bei der harten Produktkante liegen beide gleichauf: beide tragen einen hellen Ein-Pixel-Saum vom jeweiligen Grund (Saum-RGB 175/174/168 bei Weg A gegen 96/112/95 im Motiv, 161/146/127 bei Weg B gegen 77/85/64), bei Weg A neutral grau, bei Weg B warm vom Holztisch. Auf einer harten Kante fällt das in beiden Fällen nicht ins Gewicht. Die Wahl zwischen 01 und 02 ist damit keine Geschmacksfrage: wo es geht, gehört das Motiv auf einen flachen Grund erzeugt.

**Der grüne Grund färbt den Haarsaum oliv, der graue nicht.** Gemessen am selben Motiv und Seed, nur das Hintergrundwort getauscht: der halbtransparente Randsaum ist bei Grün zu 58,7 Prozent grünexzessiv, bei Hellgrau zu 0,0 Prozent, das Motivinnere in beiden Fällen bei 0,1 Prozent. Im Bild sind die dünnen Locken bei Grün khakifarben statt kupfern. Die `note` im Ziel "Freigestelltes Motiv" der `models.json` des Bildgalerie-Repos empfiehlt trotzdem bis heute `flat plain pure green background`. Das ist der Stand vor der Entgrünungs-Kampagne vom 26.08.2026 und gehört korrigiert.

**Die naheliegende Kennzahl trägt beim Farn wieder nicht.** Grünexzess im Saum: 99,9 Prozent bei grünem Grund, 20,0 Prozent bei grauem. Das Blatt ist selbst grün, die Zahl misst dort das Motiv und nicht den Freistellungsrest. Gleicher Fehler wie am 15.08.2026, deshalb auch diesmal am Bild entschieden.

**Der Kantenverfeinerer gehört an den Rand des Motivs, nicht an die Quelle** (Abnahme des Nutzers am 22.09.2026, acht Urteile in der Vergleichsfunktion der Bildgalerie, je Motiv und Quellweg eines). In beiden Workflows steht `process_detail` auf false. Geprüft wurde an denselben Quellbildern mit GuidedFilter und PyMatting; VITMatte selbst geht nicht, die Gewichte von `hustvl/vitmatte-small-composition-1k` liegen nicht lokal und der Knoten steht auf `VITMatte(local)`.

| Motiv | Rand | flacher Grund | echte Szene |
|---|---|---|---|
| Haar | feinste Strähnen | GuidedFilter 4/2 | GuidedFilter 4/2 |
| Pusteblume | Flaum, halbtransparent | GuidedFilter 4/2 | GuidedFilter 4/2 |
| Tasse | harte Kante | Verfeinerung aus | Verfeinerung aus |
| Farn | scharf begrenzte Fiederzähne | Verfeinerung aus | Verfeinerung aus |

**Acht von acht fallen nach dem Motiv, nicht nach dem Quellweg.** Hat das Objekt viele kleine Strukturen (Haar, Fell, Flaum), gewinnt GuidedFilter; hat es klare Linien, gewinnt die Verfeinerung aus, weil sie eine saubere Kante nur zu einem Glimmen aufweicht. Das breitere Trimap-Band (erode 12, dilate 8) hat kein einziges Urteil gewonnen, es zieht sichtbar Hintergrund mit. Kosten der Verfeinerung 1 bis 2 Sekunden je Bild.

**Meine erste Lesart war in zwei Punkten falsch, beide in dieselbe Richtung.** Ich hatte die Regel am Quellweg festgemacht (bei flachem Grund aus, bei echter Szene an) und bei den Haaren PyMatting vorgezogen. Der Nutzer entschied beide Male anders: der Quellweg ist gleichgültig, und wo verfeinert wird, gewinnt GuidedFilter. PyMatting löst mehr einzelne Strähnen auf, legt dabei aber einen hellen Saum um die Silhouette; ich hatte die aufgelösten Strähnen als besser gelesen. Derselbe Fehler wie beim Refiner-Vergleich weiter oben: mehr sichtbare Struktur ist nicht echter.

Der Mechanismus dahinter steht im Quelltext: `process_detail` baut aus der groben Maske über erode und dilate ein Trimap und löst Alpha nur im schmalen unbekannten Band neu, alles außerhalb wird hart auf 0 oder 1 gezwungen. Das erklärt beide Seiten: an einer harten Kante bringt das Neulösen nichts und verwischt nur, an einem Haarsaum ist genau dieses Band die Stelle, an der die Information steckt.

**Halbtransparenz löst diese Kette nicht, auf keinem der beiden Wege.** Die Node setzt ausschließlich Alpha, sie entfernt die Grundfarbe nie aus dem RGB (`RGB2RGBA(orig_image, mask)`). Jeder halbtransparente Pixel behält damit die Mischung aus Motiv und altem Hintergrund. Bei einem opaken Motiv mit dünnem Saum fällt das nicht auf, bei der Pusteblume wird der ganze Samenstand zum grauen Schleier, auf der Wiese zum warmen Fleck. Wer Flaum, Glas, Rauch oder Schleier freistellen will, braucht ein Verfahren mit Farbentgiftung, nicht diese Kette.

**Zwei alte Befunde reproduzieren nicht.** Das Henkelloch der Tasse ist auf beiden Wegen offen, die eingeschlossene Fläche vom 26.08.2026 (gefülltes Zahnrad-Loch) tritt hier nicht auf. Und die dünne Pusteblume auf flachem Grund war schon so generiert, nicht vom Matting zerstört. Das RGB eines RGBA-Ergebnisses ist das Bild vor der Freistellung, damit lässt sich Generierung von Matting ohne zweiten Lauf trennen. Das ist der schnellste Weg, bei einem misslungenen Freisteller die Schuldfrage zu klären, und er hat hier direkt eine falsche Erstdeutung korrigiert.

**Mehr als 1024 Pixel bringen der Maske nichts.** Die Node rechnet die Segmentierung immer bei 1024 x 1024 und skaliert die Maske danach bilinear auf die Bildgröße. Gegenprobe mit derselben Quelle als 2x-Kopie: die Maske bekommt keine feineren Kanten, sie wird weicher (mittlerer Gradient im Saum 41,8 gegen 48,8). Folge für große Freisteller: bei 1024 mattieren und danach über Workflow 03 hochskalieren, nicht gleich groß erzeugen und auf eine feinere Maske hoffen.

**Zeiten:** Weg A 8 bis 20 s je Bild, Weg B 8 s Generierung plus 3 bis 4 s Matte. Kein Unterschied, der die Wahl trägt.

## Wan 2.2 vermessen: 14B liefert, 5B steht fast still (2026-09-22)

Seit dem 20.09.2026 installiert, drei Workflows, neun Clips, aber kein einziger Ledger-Eintrag und keine Zahl. Nachgeholt mit gleichem Eingangsbild und Seed 4242, Blätter `out/vergleich_wan.png` und `out/vergleich_wan_arbeitspunkte.png`. Vor jedem Lauf `/free`, sonst misst die VRAM-Spitze den Vorlauf mit.

**Bildtreue entscheidet den Vergleich, nicht die Zeit.** Der 14B-Clip macht genau das Verlangte: Bild 1 ist identisch mit dem Eingang, danach zieht Nebel durchs Tal, Lichtstrahlen brechen durch, Wolken wandern, die Kamera schiebt langsam vor. Felsnadeln, Baum und die Vogelsilhouette auf dem Fels bleiben erhalten. Der 5B steht zwischen Bild 1 und Bild 121 praktisch still, obwohl "statisch" wörtlich im Negativ-Prompt steht. Ein Motiv ist kein Beweis, aber ein deutlicher Hinweis: vor einer Entscheidung über die 9,3 GB des 5B gehört ein zweites Motiv gerechnet.

**Arbeitspunkte der 14B Q5** (81 Bilder, 16 fps, also 5,1 s Clip, vier Sampler-Schritte mit den lightx2v-LoRAs):

| Auflösung | Zeit | VRAM-Spitze | je Sekunde Video |
|---|---|---|---|
| 832x480 (nativ, Vorschau) | 122 s | 13,7 GB | 24 s |
| 1280x704 (Hero) | 347 s | 14,6 GB | 69 s |
| 1024x1024 (quadratisch) | 443 s | 15,6 GB | 87 s |

Der 5B brauchte auf 1024x1024 mit 30 Schritten 511 s bei 15,8 GB Spitze.

**Der Engpass ist der Speicher, nicht die Rechenzeit.** Bei 1024x1024 bleiben von 16,3 GB noch 0,7 GB frei, zwei 10-GB-GGUF-Modelle plus 6,7-GB-Text-Encoder werden dauernd nachgeladen. Deshalb wächst die Zeit stärker als die Pixelzahl: von 832x480 auf 1280x704 sind es 2,3-fache Pixel, aber 2,8-fache Zeit.

**Merksatz für die Messung selbst:** `comfy_generate.py` injiziert seine Standardgröße 1024x1024 in den LATENT-Knoten, auch bei Video. Ohne ausdrückliches `--width`/`--height` misst man nicht die native Auflösung des Workflows. Der erste Durchgang lief deshalb auf 2,6-facher Pixelzahl der 14B und war als Planungsgrundlage unbrauchbar.

### Freigestellte Bilder waren in der Galerie anonym, `comfy_matte.py` schreibt jetzt die Herkunft (2026-09-22)

Beim Sichten der Testbilder fiel auf, dass jedes mattierte Bild in der Bildgalerie ohne Modell, ohne Modelldatei und ohne Prompt steht. Das ist kein Anzeigefehler: der Graph, den ComfyUI in ein Ergebnis von Workflow 02 schreibt, besteht aus LoadImage, BiRefNet und SaveImage. Darin gibt es keinen Modell-Loader und keinen Textknoten, also kann die Galerie beim besten Willen nichts anzeigen. Betroffen sind alle 38 Bilder des heutigen Vergleichs, dieselbe Ursache erklärt auch die 151 namenlosen BiRefNet-Bilder im Archiv.

**Die Galerie hat dafür längst ein Feld, es wurde nur nie beschrieben.** Sie liest fünf eigene tEXt-Chunks aus dem PNG: `gallery_src_key`, `gallery_src_model`, `gallery_src_prompt`, `gallery_src_method` sowie `gallery_src_prompt_hash`. Daraus baut die Lightbox den Abschnitt "Vorlage" mit Sprung-Link zum Quellbild. Über den Prompt-Hash fällt das abgeleitete Bild in den Vergleichssatz seiner Vorlage. Gedacht war das für neu gerenderte Altbilder, es passt aber genauso auf Freisteller.

`comfy_matte.py` schreibt die fünf Chunks jetzt selbst: es liest den Graphen des Quellbildes, zieht Modelldatei und positiven Prompt heraus, bildet den Prompt-Hash mit derselben Normalisierung wie die Galerie (`\W+` zu Leerzeichen, klein, sha1, 12 Zeichen) und hängt alles an das Ergebnis an. `gallery_src_method` trägt die Einstellung, mit der freigestellt wurde (`BiRefNet-General, PyMatting`), sonst wären zwei Ergebnisse derselben Vorlage nicht zu unterscheiden.

**Geschrieben wird auf dem Chunk-Strom, nicht über eine Bildbibliothek.** Der Chunk wird vor IEND eingefügt, die Pixel werden nicht neu komprimiert und die Chunks von ComfyUI (`prompt`, `workflow`) bleiben Byte für Byte stehen. Über Pillow neu zu speichern hätte beides angefasst. Der Schritt läuft vor `deliver`, damit auch ein Hardlink oder eine Kopie die Chunks trägt. Reines Stdlib, der Skript-Grundsatz bleibt.

**Korrektur am selben Tag: iTXt statt tEXt.** Zuerst schrieb das Skript tEXt-Chunks mit UTF-8-Bytes im Wert. Das geht nur gut, weil `chunk_text` in der Galerie UTF-8 zuerst versucht; laut PNG-Spezifikation ist ein tEXt-Wert Latin-1, fremde Werkzeuge hätten aus einem deutschen Prompt Buchstabensalat gemacht. Aufgefallen ist es über die Koordination, während eine andere Session genau diese Dekodierung anfasste. Jetzt iTXt wie im Schwesterskript `comfy_generate.py`: Schlüssel, Trenner, Kompression aus, Methode 0, leere Sprache, leerer Zweitname, dann UTF-8. Geprüft mit einem Wert aus äöüß, hin und zurück über beide Leser, Pixel und eingebetteter Graph unverändert. Beim Ersetzen werden tEXt, iTXt und zTXt desselben Schlüssels entfernt, ein zweiter Lauf verdoppelt also auch über den Artwechsel hinweg nichts.

**Die Chunks allein reichten nicht, die Galerie musste mitziehen** (Nutzerhinweis, dass das Verfahren in den Metadaten weiter fehlte und die Bilder nicht als Vergleich zusammenfanden). Zwei Ergänzungen in `gallery.py`, Branch `claude/keen-villani-0d8879`: `matte_info()` liest die BiRefNet-Knoten aus dem eingebetteten Graphen und füllt ein neues Feld `matte` (`BiRefNet-General, PyMatting 4/2`), und BiRefNet zählt als `model_file`, wenn es sonst keins gibt. Der Punkt dabei: die Angabe kommt aus dem Bild selbst, nicht aus meinen Chunks, gilt also auch für die 151 Archivbilder und für Workflow 01, der in einem Graphen erst generiert und dann freistellt. Dort gewinnt weiterhin das Generierungsmodell, die Freistellung steht daneben.

**Damit greift die eingebaute Vergleichsfunktion.** Sie gruppiert nach Prompt-Hash und verlangt mindestens zwei verschiedene Modelle in der Gruppe. Da ein Freisteller jetzt BiRefNet-General trägt und über `src_prompt_hash` beim Prompt seiner Vorlage hängt, entsteht je Quellbild eine Gruppe aus dem Original plus seinen Freistell-Varianten, im Test acht Gruppen mit fünf bis sieben Bildern. Innerhalb der Gruppe trennt `cmpSet` die Varianten über `src_method`, weshalb `comfy_matte.py` dort nur noch das Unterscheidende schreibt (`PyMatting 4/2`), nicht den Modellnamen: den liest die Galerie selbst. Als Rückfall für ältere Bilder ohne Chunks nimmt `cmpSet` jetzt `src_method || matte`.

**Merksatz:** ein Bild ohne Modell fällt in dieser Galerie nicht nur optisch auf, es fällt aus der Vergleichsfunktion heraus. Wer eine Verarbeitungsstufe hinzufügt, muss ihr ein Modell und eine Kennung geben, sonst ist das Ergebnis nicht mehr beurteilbar.

## Afterlight hat zwei Arbeitspunkte, nicht einen (2026-09-22)

Nachbau eines Flux-Fantasy-Porträts (Civitai 78632690, dort Flux.1 D mit zhongfenghuaStyle und Midjourney SemiReal Dream) auf Krea 2 Turbo, gleicher Prompt und Seed 777, drei Stärken gemessen. Blatt: `out/vergleich_krea2_fantasy_nachbau.jpg`, Einzelbilder `Text2Img/agent/2026-09-22/krea_00034_` bis `krea_00037_`.

- **0.0 (aus):** Ornamentik und Filigranrüstung klar gezeichnet, Licht flach, Funken liegen nur als Punkte neben der Figur.
- **0.35:** bester Treffer gegen die Vorlage. Struktur bleibt vollständig, dazu Dunst, Glanzpunkte und ein warmer Randlichtsaum. Das Gesicht wirkt weicher und fotografischer als pur.
- **0.8:** Bokeh übernimmt das Bild. Krone, Ranken und Ornament lösen sich in Lichtkreise auf, der Kontrast fällt zusammen.

**Regel:** die 0.8 bis 1.0 aus der LoRA-Messung vom 21.09. gelten für Motive, die von Dunst leben (Landschaft, Gegenlicht, Figur vor Weite). Bei ornamentreichen Motiven ist 0.3 bis 0.4 die Obergrenze, darüber frisst der Dunst genau die Details, wegen derer man das Motiv gewählt hat.

**Prompt-Detail nebenbei:** `molten ember light glowing inside the cracks of the tendrils` legt die Glut IN die Ranken, `glowing sparks scattered along the tendrils` streut sie nur daneben. Krea 2 nimmt die Präposition ernst. Der enge Ausschnitt (`head and shoulders filling the frame`) bringt mehr Pinselduktus, verzeichnete im Test aber die Schulterpartie.

**Befund zur Vorlage:** der Look solcher Civitai-Treffer sitzt fast immer in den Stil-LoRAs, nicht im Checkpoint. Für einen Nachbau lohnt der Blick auf die Ressourcenliste des Bildes über `/api/v1/images?imageId=<id>`, bevor ein 12-GB-Modell geladen wird.

## Warm Light gleicht den Detail-Slider aus, aber nur bis 0.5 (2026-09-22)

Fortsetzung des Nachbaus oben, alles auf Seed 777, gemessen als mittlere Helligkeit (0 bis 255) und Feinstruktur (Varianz eines 3x3-Laplace) sowie R minus B als Maß für die Farbstimmung.

| Stufe | Helligkeit | Feinstruktur | R-B |
|---|---|---|---|
| eng + Afterlight 0.35 | 48,9 | 204 | -5,5 |
| + Detail-Slider 1.5 | 44,9 | 257 | -9,2 |
| + Warm Light 0.5 | 55,9 | 296 | -2,7 |
| + Warm Light 1.0 | 74,0 | 293 | +16,1 |

**Der Detail-Slider verdunkelt messbar** (48,9 auf 44,9), während er die Feinstruktur um ein Viertel hebt. **Warm Light 0.5 holt die Helligkeit zurück und kostet dabei nichts**, die Feinstruktur steigt sogar weiter auf 296. Das bestätigt den Befund vom 21.09., jetzt mit Zahlen an einem zweiten Motiv.

**Die Obergrenze liegt aber tiefer als gedacht:** bei 1.0 springt R-B von -2,7 auf +16,1, das Bild kippt komplett ins Kupferne. Schwarze Ranken werden orange, der kalt-blaue Charakter der Vorlage ist weg. Für ein Motiv, das von der Spannung kalt gegen glutwarm lebt, ist **0.5 der Arbeitspunkt**, nicht die +0,5 bis +1,5 aus der ersten Messung. Als eigener Look (Glut-Königin) ist 1.0 trotzdem brauchbar.

**Rezept, das am Ende stand:** `krea2_turbo_t2i.api.json` mit AFTERLIGHT_LORA 0.35, DETAIL_LORA 1.5, WARM_LORA 0.5, 896x1344, 8 Steps, Seed 777. Ergebnis `Text2Img/agent/2026-09-22/krea_00040_.png`, Blatt `out/vergleich_krea2_fantasy_feinschliff.jpg`.

## Sechzehn Civitai-Vorlagen gegen den lokalen Stack (2026-09-22)

Der Nutzer hat sechzehn Bilder als Referenz geschickt, quer durch alle Stile. Vierzehn davon nachgebaut (zwei Drachen-Motive waren Varianten desselben Looks), Blätter `out/vergleich_referenzen_nachbau.jpg` und `..._2.jpg`.

**Was auf Anhieb sitzt:** Magier auf schwebender Insel (Krea 2, Aufbau fast deckungsgleich mit dem ChatGPT-Original), Pergamentseite mit dem Titel ALCHEMIST BREW (Qwen setzt den Text sauber, Fließtext bleibt Pseudo-Schrift wie in der Vorlage), Blumenvogel, Ölklecks-Seestück, Sumi-e-Drache, Leuchtturm im Sturm. Alles Krea 2 pur, kein einziges dieser Motive brauchte eine LoRA.

**Was zwei Anläufe brauchte:** ein Motiv, das von EINEM kleinen Element lebt. Beim Tiger mit Falter fiel der Falter im ersten Lauf ganz aus. Erst `the butterfly is the only bright light source` zog ihn ins Bild. Gleiches Muster bei der Schriftrolle: `rising out of the paper like a diorama` plus `pouring over the lower edge into empty space` brachte die Tiefe, die `growing out of the paper` nicht liefert. **Regel: ein Bildelement, das die Vorlage trägt, braucht eine Lichtrolle oder eine räumliche Beziehung im Prompt, keine bloße Nennung.**

**Wo WAI-illustrious v17 abfällt:** genau bei den beiden Vorlagen, die auf JANKU und Obsidian Anise beruhen. Die ornamentale (explodierende Goldwirbel um die Figur) und die Pastell-Traumszene kamen statischer und ärmer heraus als das Original, während das dritte Anime-Motiv (Kimono mit Katze) gut traf. Das ist das erste belastbare Argument für einen zweiten Anime-Checkpoint oder für Stil-LoRAs auf Illustrious, nicht die Detailfrage, die ursprünglich der Anlass war.

## Qwen kann Anime besser als gedacht, und Afterlight hängt am Motiv (2026-09-22)

Drei Anime-Vorlagen und der Magier auf Qwen-Image-2512 gegengerechnet, Prompts von Danbooru-Tags in Sätze übersetzt, 896x1152, Seed 777. Blatt `out/vergleich_qwen_gegen_wai.jpg`.

- **Qwen gewinnt bei Prompttreue und Dekor.** Beim Kimono-Motiv traf es blondes Haar, kurzen Pferdeschwanz, rote Augen, Katze im Schoß, roten Teppich und Korb, während WAI die Haarfarbe auf Orange verschob. Bei der Goldornamentik kam Qwen der üppigen Vorlage deutlich näher als das statische, symmetrische Bild von WAI.
- **WAI gewinnt beim Anime-Idiom.** Linienführung, Posendynamik und das flirrende Licht der Pastell-Szene bleiben seine Domäne, Qwen zeichnet dort ruhiger und proportional realistischer.
- **Beim Magier hält Krea 2 die Silhouette**, also die Figur als Schatten mit nur zwei leuchtenden Augen unter der Hutkrempe. Qwen zeigt ein ausmodelliertes Gesicht und verliert damit genau die Pointe der Vorlage.
- **Praktische Folge:** für Anime-Motive, die von Requisiten und exakten Merkmalen leben, ist Qwen die bessere Wahl. Für den klassischen Anime-Look bleibt es WAI. Eine Tag-Liste muss dafür in Sätze umgeschrieben werden.

**Afterlight am Blumenvogel gemessen** (Macro, weiches Bokeh): Helligkeit 118,6 auf 109,1 auf 102,2 bei pur, 0.35 und 0.8, Feinstruktur dagegen 84 auf 153 auf **364**. Bei diesem Motiv ist 0.8 brauchbar und sogar reizvoll, anders als beim ornamentreichen Porträt weiter oben, wo dieselbe Stärke die Krone auflöste.

**Wichtige Einschränkung zur Kennzahl:** die Laplace-Varianz misst Kantenenergie, nicht Motivdetail. Afterlight hebt sie immer, weil Bokeh-Kreise und Funken selbst Kanten sind. Beim Porträt stieg sie auf 432, während das Bild sichtbar schlechter wurde. **Die Zahl taugt als Vergleich innerhalb einer Serie, sie ersetzt das Hinsehen nicht.**

## Das Altern im Detailpass ist Korn, nicht Faltenstruktur (2026-09-22)

Der Nutzer hatte gemeldet, dass die Frau in `upscale_00012_.png` deutlich älter wirkt als im Ausgangsbild `krea_00033_.png`. Nachgemessen am Winzer-Porträt `krea_00020_.png` (Krea 2, 1216x832), zwei Hautfelder (Stirn, Wange), alle Varianten vor der Messung auf die Feldhöhe des Originals zurückskaliert.

| Variante (denoise 0,05) | Stirn | Wange | Korn | Struktur |
|---|---|---|---|---|
| Original Krea 2 | 328 | 142 | +0 % | +0 % |
| nur Lanczos 2x | 331 | | +1 % | |
| 4x-UltraSharp | 759 (+131 %) | 342 (+141 %) | +34 % | +2 % |
| RealESRGAN x4plus | 838 (+155 %) | 381 (+168 %) | +46 % | +2 % |
| 4x_NMKD-Superscale | 1403 (+328 %) | 582 (+310 %) | +72 % | +2 % |

**Der Denoise-Wert ist nicht die Ursache.** UltraSharp liegt bei denoise 0,05 auf 759, bei 0,1 auf 743 und bei 0,2 auf 775, also praktisch gleich. Die ESRGAN-Stufe selbst bringt den Sprung, der Sampler danach verschiebt nur zusätzlich die Gesichtszüge. Eine reine Lanczos-Vergrößerung ohne Modell landet bei +1 % und erfindet damit nichts.

**Kantenvarianz allein führt in die Irre**, weil Haare und Konturen sie dominieren. Deshalb die letzten zwei Spalten: "Struktur" ist das Frequenzband zwischen einem 1px- und einem 4px-Weichzeichner (Falten, Konturen), "Korn" alles oberhalb davon (Poren, Rauschen). Struktur bleibt bei allen drei Modellen bei +2 %. **Kein Upscaler erfindet neue Falten.** Was steigt, ist ausschließlich das Korn auf der Haut, und genau das liest das Auge als ältere Haut.

**Rangfolge:** 4x-UltraSharp ist von den dreien der mildeste und bleibt gesetzt. NMKD-Superscale legt einen sichtbaren Rausch-Teppich über die Wange und ist damit raus. RealESRGAN wirkt im Gesicht weicher, misst aber mehr Korn, weil es Haare und Kanten härter zeichnet.

**Praktische Folge:** bei Porträts ist der Detailpass kein kostenloser Gewinn. Wer die Hautwirkung erhalten will, lässt ihn weg oder blendet das Ergebnis mit einer reinen Lanczos-Vergrößerung über. Skripte: `upscaler_messung.py`, `haut_messung.py`, `korn_messung.py` im Sitzungs-Scratchpad.

## 1xSkinContrast ist kein Upscaler, sondern ein Weichzeichner (2026-09-22)

Direkt im Anschluss geprüft, ob `1xSkinContrast-High-SuperUltraCompact` als EIN Upscaler für alles taugt. Zwei Motive: das Winzer-Porträt (Haut) und ein Tiger auf einem bemoosten Stamm (Fell, Moos, Schmetterlingsflügel, Schnurrhaare), beide bei denoise 0,05.

| Feld | UltraSharp | SkinContrast |
|---|---|---|
| Stirn (Haut) | +131 % | -33 % |
| Wange (Haut) | +141 % | -24 % |
| Fell | +130 % | -41 % |
| Moos | +118 % | -40 % |
| Schmetterlingsflügel | +53 % | -21 % |

**Der Grund steckt im Namen:** das Modell ist ein 1x-Modell, es vergrößert nicht. UltimateSDUpscale skaliert trotzdem auf `upscale_by`, also kommt die Vergrößerung aus reiner Interpolation und SkinContrast wirkt nur als Filter darüber. Das Ergebnis liegt in JEDEM Feld unter dem Original, auch bei der Haut.

**Für die Haut ist das genau das gewünschte Verhalten** (kein Korn, kein Altern, Kennzahl sogar unter dem Original), für alles andere ist es ein Verlust. Im Blatt sieht man es sofort: beim Tiger zeichnet UltraSharp einzelne Haare am Stirnfell und schärft die Schnurrhaare, SkinContrast liefert ein Bild, das vom Original kaum zu unterscheiden ist, nur etwas weicher.

**Entscheidung:** `4x-UltraSharp` bei denoise 0,05 bleibt der Upscaler für alles. `4x_NMKD-Superscale` ist raus. SkinContrast wäre nur als maskierter Zweitdurchlauf auf Gesichtern sinnvoll, was den Graphen deutlich verkompliziert. Skript `skin_auswertung.py` im Sitzungs-Scratchpad.

## ComfyUI hing drei Stunden, GPU-Prüfung ohne nvidia-smi (2026-09-22)

Die API antwortete ab 16:14 nicht mehr, der Prozess lief weiter und verbrauchte CPU-Zeit. Behoben durch Beenden und Neustart um 19:27.

- **Vermutete Ursache, nicht bewiesen:** ein vorheriger Aufruf von `GET /object_info`. Der Endpunkt listet jede Node samt Eingängen, bei der Menge installierter Custom Nodes ist das eine große Antwort, und das Log endet genau in diesem Zeitraum. **Gegenregel:** Modelllisten nicht über `object_info` abfragen, sondern die Ordner unter `Data\Models\` im Dateisystem lesen.
- **nvidia-smi ist auf dieser Maschine ohne Adminrechte gesperrt** (das erklärt auch den Crystools-Fehler im ComfyUI-Log). Ob die GPU frei ist, zeigen die Windows-Leistungsindikatoren ohne Sonderrechte: `Get-Counter "\GPU Engine(*)\Utilization Percentage"` (Compute-Engines mit Last) und `Get-Counter "\GPU Process Memory(*)\Local Usage"` (VRAM je Prozess). Compute-Engine ohne Last und kein Prozess über 500 MB VRAM heißt: niemand generiert, ein Neustart verliert keinen laufenden Auftrag.

## Korrektur: Detail-Slider auf WAI wirkt, nur nicht bei Stärke 1.0 (2026-09-22)

Die Aussage weiter oben ("bei Illustrious kommt Detail aus dem zweiten Durchgang, nicht aus einer LoRA", Detail-Slider +2 %) ist falsch. Sie beruhte auf Stärke 1.0. Der Autor des StS Illustrious Detail Slider (Civitai 1122976) empfiehlt 3.0 bis 4.5.

Neu gemessen mit dem Original-Prompt von Civitai 111059061 auf WAI v17, Seed der Vorlage, volle Kette aus Basis und Refiner, Feinstruktur als Varianz des 3x3-Laplace (in Klammern die Standardabweichung, vergleichbar mit der alten Tabelle):

| Stufe | ganzes Bild | 1:1-Ausschnitt Kopf |
|---|---|---|
| ohne LoRA | 181 (13,5) | 579 |
| Detail-Slider 1.0 | 276 (16,6, +23 %) | 692 |
| Detail-Slider 3.0 | 381 (19,5, +45 %) | 908 |
| Detail-Slider 4.5 | 540 (23,2, +73 %) | 871 |
| detailed skin style 0.8 | 263 (16,2) | 813 |

Im Bild: bei 3.0 deutlich mehr Haarsträhnen, Glanzlichter, Stickerei am Kragen, Troddeln an den Haarbändern. Bei 4.5 zerfällt der Hintergrund in Farbspritzer und die Augen glühen, im Ausschnitt sinkt der Wert schon wieder. **Arbeitspunkt 3.0.** Nebenwirkung ab 1.0: die Pose wird dynamischer, die Komposition ändert sich also mit. Blätter `out/vergleich_wai_detailslider.jpg` und `..._ausschnitt.jpg`.

Unterschied zur alten Messung auch im Aufbau: damals nur die Basisstufe, jetzt die volle Kette, in der DETAIL_LORA auch den Refiner speist. Der zweite Durchgang bleibt nützlich, er ersetzt den Slider aber nicht.

## Original-Prompt gegen eigenen Prompt (2026-09-22)

Zwölf der sechzehn Civitai-Vorlagen des Nutzers tragen ihren Prompt, abrufbar über tRPC `image.getGenerationData` (die API v1 meldet dort `meta: null`). Mit Original-Prompt, Original-Seed und Steps neu gerechnet, Blätter `out/vergleich_originalprompts.jpg` und `..._anime.jpg`:

- **Original-Prompt gewinnt klar, wo der Look aus Basismodell und Prompt kommt.** Tiger, Leuchtturm, Schriftrolle und Z-Image-Drache kommen der Vorlage fast deckungsgleich nahe, der Tiger bei gleichem Seed auf Krea 2 nahezu identisch. Beim Anime-Kimono trifft WAI mit Original-Prompt Haarfarbe, Katze im Schoß und den Farbverlauf des Rocks, was der eigene Prompt nicht schaffte.
- **Original-Prompt allein hilft nicht, wo eine Stil-LoRA den Look trägt.** Origami: ohne `TQ - Origami Style XL` wird aus dem Papiervogel ein echter Kolibri. Pergament: der kurze Original-Prompt nennt den Titel nicht, Qwen erfindet Buchstabensalat, der eigene Prompt mit `ALCHEMIST BREW` war besser. Goldornamentik und Pastell-Szene: ohne AURENTH (Trigger `auR_1nTh9` steht im Prompt) weder Gold noch Farbe, die Pastell-Szene kommt sogar fast grau heraus.
- **Regel:** erst Original-Prompt, dann Ressourcenliste lesen. Fehlt eine Stil-LoRA, ist sie der eigentliche Nachbau-Schritt, nicht ein neuer Checkpoint.

**Nachtrag 23.09.2026, Sweep 0 bis 4 an zwei Motiven** (Blatt `out/vergleich_wai_detailslider_0-4.jpg`, Stufen 0, 1 und 3 von gestern wiederverwendet, eine Wiederholung war pixelgleich): die Wirkung hängt am Motiv. Bei der dekorativen Goldornamentik steigt die Feinstruktur von 181 über 276, 332 und 381 auf 564, sichtbar an Haar, Ärmelmuster und Hintergrund, die Pose kippt aber schon bei 1.0 von stehend auf springend. Beim Kimono mit Katze (flacher Tag-Anime, viel Himmel) bleibt sie bei 274 bis 297, im Gesichtsausschnitt ändert sich praktisch nichts außer einer leichten Verschiebung der Komposition, das Bild wird nur heller (183 auf 194). **Folge:** kein fester Standardwert im Workflow. 2.0 bis 3.0 für dichte, dekorative Motive, bei klarem Flächen-Anime bringt der Slider nichts, dort helfen nur Stil-LoRAs oder ein anderer Checkpoint.

## WAI v17 nach Autorvorgabe gefahren (2026-09-23)

Die Modellseite (Civitai 827184) gibt für v16 und v17 vor: Steps 15 bis 30, CFG 5 bis 7, Euler a, Format über 1024x1024 mit Beispielen in 1024x1344, Hires-Fix 1,5-fach mit 20 Steps, Upscaler R-ESRGAN 4x+ Anime6B und Denoise 0,35 bis 0,5. Positiv nur `masterpiece,best quality,amazing quality,`, Negativ nur `bad quality,worst quality,worst detail,sketch,censor,` plus `nsfw` für jugendfreie Bilder. Ausdrücklich: viele Qualitäts- und Ästhetik-Tags oder lange Negative machen das Bild unschärfer. Die Angabe 25 bis 40 Steps gilt nur für v5 bis v15.

`illustrious_t2i` weicht davon ab: 40 Steps, 960x1664, 2-fach UltimateSDUpscale in Kacheln bei Denoise 0,25, langes Negativ, dazu `lazypos` und `lazyneg`. Autorkonform gegengerechnet (28 Steps, CFG 6, 1024x1344, eine Kachel 1,5-fach bei 0,4 als Ersatz für den Hires-Fix, RealESRGAN_x4plus statt des fehlenden Anime6B, DETAIL_LORA aus dem Graphen entfernt), Blatt `out/vergleich_wai_autorvorgabe.jpg`:

- **Kimono mit Katze kommt der Vorlage deutlich näher:** sitzende Figur, die das Bild füllt, Katze im Schoß, Kimonojacke, Farbverlauf und Spitzensaum am Rock, weiches Licht. Im alten Format 960x1664 war die Figur klein und das halbe Bild Himmel. Fehler: zwei Katzen, weil `petting cat` und `cat on lap` zusammen stehen.
- **Goldornamentik:** dynamischer und näher am Bildausschnitt der Vorlage, aber weiterhin bunt statt schwarz-gold (fehlende AURENTH-LoRA), ein Arm angeschnitten.
- Strukturwerte sind zwischen 1920x3328 und 1536x2016 nicht vergleichbar, das Urteil ist hier nur das Auge.

**Zweiter Fehler, der erst beim genauen Lesen auffiel:** Civitai-Prompts aus A1111 oder Forge enthalten `<lora:name:0.5>` und Prompt-Editing wie `[clouds:7]`. ComfyUI wertet beides nicht aus, es landet als Text im Prompt. Die Läufe "Original-Prompt" des Kimono-Motivs vom 22.09. (inklusive Slider-Sweep) liefen deshalb mit fünf LoRA-Namen als Textrauschen und ohne die LoRAs selbst. Beim Übernehmen immer entfernen und die LoRAs als Knoten laden.

## Gesichts- und Handkorrektur auf WAI (2026-09-23)

Auslöser: der Hinweis eines Civitai-Nutzers, die guten Bilder entstünden mit ADetailer und Hires-Fix (2-fach, Denoise 0,2, Anime6B). Die Kimono-Vorlage 102250756 lief tatsächlich mit ADetailer: face_yolov9c bei Denoise 0,4, hand_yolov8n bei 0,35. In ComfyUI entspricht das FaceDetailer aus dem Impact Pack. Die Detektoren liegen NICHT in `Data\Models\Ultralytics\` (leer), sondern in `Data\Packages\ComfyUI\models\ultralytics\bbox\`: face_yolov8m, hand_yolov8s, dazu person_yolov8m-seg und SAM vit_b.

Gemessen auf WAI nach Autorvorgabe, gleicher Seed, Blätter `out/vergleich_wai_detailer.jpg` und `out/vergleich_wai_detailer_nah.jpg`:

- Die Korrektur zeichnet Gesicht und Hände wirklich neu: im Gesicht ändern sich 40 bis 56 Prozent der Pixel, an den Händen 38 bis 59 Prozent, im ganzen Bild 3 bis 7 Prozent.
- **Sichtbar wird davon vor allem das Auge:** schärfere Iris, Lichter, Wimpern. Hände werden etwas sauberer, waren vorher aber schon korrekt. Bei Gesichtern um 300 Pixel, also Brustbild in 1024x1344, ist der Gewinn klein. Die Korrektur lohnt sich vor allem, wo Gesichter klein sind: Ganzkörper, Gruppen, Weitwinkel.
- **Fehlgriffe des Handdetektors bei Schwelle 0,25:** beim Kimono traf er die Füße in Socken und den Kopf der Katze. Das Neuzeichnen hat dort nichts beschädigt, kann bei anderen Motiven aber Formen verändern. Hand-Schwelle 0,35 oder höher.
- **Hires 2-fach bei 0,2 (Kommentar) gegen 1,5-fach bei 0,4 (Autor):** der 2-fache Lauf bringt vor allem Auflösung (2048x2688) und etwas härtere Linien, keine neuen Details. Getestet mit RealESRGAN_x4plus, Anime6B liegt noch nicht lokal.
- **Fazit:** weder Gesichtskorrektur noch Hires-Variante schließen den Abstand zu den Vorlagen, der steckt im Stil (LoRAs) und im Checkpoint. Gesichtskorrektur ist trotzdem ein sinnvoller fester Schritt für Anime, Handkorrektur nur mit höherer Schwelle.

## Wie gute WAI-Bilder auf Civitai entstehen: Stichprobe (2026-09-23)

Über die Civitai-API (`/api/v1/images?modelVersionId=…&sort=Most Reactions`, nur jugendfreie Bilder, Metadaten über tRPC `image.getGenerationData`) die bestbewerteten Bilder mit Prompt ausgewertet. Downloads je Version am 23.09.: v14 307.000, v16 243.000, v15 233.000, v17 175.000 (v17 erst seit April).

- **v14, 26 Bilder:** 22 nutzen mindestens eine LoRA (Median eine, höchstens sechs), fast alle Stil-LoRAs. Median 30 Steps, CFG 5, Sampler Euler a, Prompt im Median 393 Zeichen, Negativ 161, drei Qualitäts-Tags.
- **v17, 15 Bilder:** nur 4 mit LoRA, Median 30 Steps, CFG 7, Euler a, Prompt 508 Zeichen, Negativ 343.
- **Hires-Fix bei 5 von 15 (v17) und 6 von 26 (v14), ADetailer bei 0 und 1.** Einschränkung: die Erkennung sieht nur die Metadaten-Felder von A1111 und Forge; Bilder aus ComfyUI oder dem Civitai-Generator tragen diese Felder nicht, die echten Anteile können höher liegen.

Folge: der Stil der Community-Bilder kommt vor allem aus Stil-LoRAs, nicht aus Nachbearbeitung.

## Stil-LoRAs auf WAI und das Rezept von akizukirei608 (2026-09-24)

Neue LoRAs in `Data\Models\Lora\` (alle SDXL-Schlüssel geprüft): AURENTH (Trigger `auR_1nTh9`, Autor 0,4 bis 1,5), Ha9siro (Trigger `h49s1r0`), WSSKX_WAI (HL's Styles, Autor 0,6 bis 0,85, "tricky"), Smooth_Booster_v5, AddMicroDetails_Illustrious_v7 (Trigger `addmicrodetails`). Die Lazy-Embeddings `lazypos`, `lazyneg`, `lazyhand` liegen in `Data\Models\Embeddings\`, in ComfyUI als `embedding:lazypos` schreiben.

**tRPC `image.getGenerationData` liefert seit 23.09. anonym 401** ("Please use the public API instead"). Ersatz: `/api/v1/images?imageId=…` liefert `meta: null`, aber `modelVersionIds` (alle Ressourcen, über `/api/v1/model-versions/<id>` auflösbar) und die Original-URL. Die Originaldatei ist oft ein PNG mit dem vollständigen A1111-`parameters`-Chunk (Prompt, LoRA-Stärken, Seed, Hires, ADetailer), auch wenn sie auf `.jpeg` endet. Also erst die Datei lesen, dann erst aufgeben.

**Civitai 101824003 und die Kimono-Vorlage 102250756 sind dasselbe Rezept** (Autor akizukirei608): JANKU v5 + TRT 0,65 + USNR 0,5 + WSSKX 0,3 + Smooth Booster v3 0,65 bis 0,75 + Stabilizer 0,25 bis 0,35 + Charakter-LoRA Kaela 0,35, Lazy-Embeddings, 30 Steps Euler a, CFG 5, 832x1216, Hires 2-fach bei 0,5, ADetailer Gesicht 0,4 mit eigenem Prompt. Die vielen LoRAs sind ein fester Stapel, kein Einzelbau je Bild.

Gemessen auf WAI v17 mit Originalparametern (Hires als eine Kachel UltimateSDUpscale, FaceDetailer mit ADetailer-Prompt), Blätter `out/rezept_<id>.jpg`, Kantenenergie in Klammern (Vorlage / ohne LoRA / mit LoRA):

- **Vorhandener Teil des Stapels (WSSKX 0,3 + Smooth Booster v5):** Garten 1642 / 1556 / 1262, Kimono 1867 / 1731 / 1701. Die Kantenenergie sinkt, trotzdem ist es eine leichte Verbesserung (Urteil Marcus, im Bild nachvollziehbar): WSSKX heißt "Aesthetic Bloom" und bringt Gegenlicht, Lens Flare und Glühen wie in der Vorlage, das weicht Kanten auf. **Kantenenergie misst Schärfe, nicht Licht und Atmosphäre: für Bloom- und Licht-LoRAs taugt sie nicht als Urteil.** Dass der Garten-Lauf ohne LoRA Pose und Schloss besser traf, ist Seed-Streuung (die LoRA verschiebt die Rauschbahn). Der Rest des Vorlagen-Looks hängt am fehlenden Teil (JANKU, TRT, USNR, Stabilizer).
- **Add Micro Details 0,8 kommt beim Kimono der Vorlage am nächsten** (2133): rote Picknickdecke, schwarze Jacke, kräftiger Himmel statt WAI-Kirschblüten-Rosa. Bei der Goldornamentik erzeugt es dagegen drei Figuren: kein Standard, nur je Motiv.
- **AURENTH ist der Hebel für schwarz-gold** (Goldornamentik 5528 / 2158 / 0,7: 3212 / 1,0: 2909): Goldring, Goldstickerei, dunkler Grund. 0,7 besser als 1,0. Die Goldwirbel der Vorlage kommen nicht, die hängen vermutlich am Checkpoint Obsidian Anise.
- **Ha9siro 0,8:** meiste Kanten (Kimono 2420, Gold 2776) und dynamischste Pose, färbt aber blass-lavendel. Für kühle, mythische Motive, nicht als Standard.
**JANKU v5 mit dem Stapel ohne TRT und Kaela (Marcus hat beide ausgelassen), Weglassprobe je LoRA, ein Seed je Motiv, Blätter `out/janku_rezept_<id>.jpg`:**

- **Der Checkpoint trägt den Großteil des Looks.** JANKU ohne jede LoRA trifft schon Gesicht, Augen und Haar der Vorlage, was WAI mit keiner LoRA erreicht hat. Mit Stapel kommen Lens Flare, Stickerei am Rock und beim Kimono die goldbestickte Jacke dazu, das Ergebnis liegt sehr nah an der Vorlage. Pose und Hintergrund weichen trotz gleichem Seed ab: A1111 mit `RNG: CPU` erzeugt anderes Rauschen als ComfyUI.
- **WSSKX sieht man am deutlichsten** (ohne: kräftigere Farben, weniger Glühen, anderer Rock). **USNR** zeigt sich beim Kimono (ohne: rosa Himmel, zweite Katze), beim Garten kaum.
- **Smooth Booster und Stabilizer ändern bei einem Seed wenig.** Kandidaten zum Weglassen, belegt ist das erst mit zwei bis drei weiteren Seeds.
**Male im Gesicht kommen von der Gesichtskorrektur, nicht von JANKU oder den LoRAs.** Beim Kimono trugen alle JANKU-Läufe (auch ohne LoRA) Flecken im Gesicht, Marcus hat es bemerkt. Basisstufe und Hires-Stufe sind sauber, erst FaceDetailer (Denoise 0,4, Ausschnitt auf 1024 hochgerechnet) malt hinein: mit `kaela20` im Gesichts-Prompt (Charakter-Token ohne die Charakter-LoRA) einen roten Farbfleck, ohne das Token noch schwarze Punkte. JANKU kennt viele Gacha-Figuren mit Gesichtsmarken, bei kleinen Gesichtern im Profil schlägt das durch. Folge: `janku_t2i` ohne Gesichtskorrektur. Charakter-Tokens aus Vorlagen-Prompts nie ohne ihre LoRA übernehmen.
**Voller Stapel gegen gekürzten, Blindurteil Marcus (24.09.):** je drei neue Seeds für Garten und Kimono, voller Stapel gegen JANKU + USNR + WSSKX. Der volle Stapel gewann alle sechs Paare. Smooth Booster und Stabilizer bleiben also drin, obwohl die Weglassprobe bei einem Seed kaum Unterschied zeigte: im Paarvergleich sieht man ihn. `janku_t2i` gibt es seitdem auch als UI-Workflow `12-anime-janku` (Konverter `api_to_ui_workflow.py --in`, der jetzt auch einzeln Notiz, Ablage und Beispiel-Prompt setzt).
## JANKU: Anatomie, Format und Vorgaben des Autors (2026-09-25)

**Quadrat bricht die Anatomie, Hochformat nicht.** Zwei NSFW-Fehlschläge (gleicher Prompt, zwei Seeds, 1024x1024 plus Hires 2-fach, Marcus: 1 Stern, Mangel Anatomie) liefen noch einmal mit Hires 0,35 und im Hochformat 832x1216. Hochformat: beide 3 Sterne, einmal Sieger vor WAI. Hires 0,35: einmal 3 Sterne, einmal weiter Anatomie. Ursache ist also vor allem das Format bei Ganzkörperposen, Hires 0,5 verstärkt es. Ganzkörper mit JANKU immer im Hochformat.

**Modellseite (Civitai 1277670, v5.0), Vorgaben des Autors:** 25 bis 30 Steps, CFG 3 bis 5, Euler oder Euler a, Scheduler normal, simple (sein Standard) oder sgm_uniform. Auflösungen 768x1344, 832x1216, 768x1280, 704x1408 und 1024x1536 (sein Standard, "no need for up-scaling"), stabil bis 1536x1536. VAE im Checkpoint. Prompt: `lazypos`, dann Figur, Details, Hintergrund; Negativ `lazyneg`. Künstlerstile mit `by <name>`. Für v5 empfiehlt er ohne Charakter-Tags ausdrücklich `lazyloli` im Negativ, damit Figuren erwachsener wirken; `lazynsfw` im Negativ hält NSFW heraus, `lazywet` nimmt glänzende Haut weg. Die drei liegen noch nicht lokal (Lazy Embeddings, Civitai 1302719: lazyloli v1833199, lazynsfw v1601074, lazywet v2512494). Gesichtskorrektur nur bei fernen Figuren, deckt sich mit dem Befund vom 24.09. Er wirbt mit "LoRA-frei", Marcus' Blindurteil bevorzugt trotzdem den Stapel.
**Alte PerfectWorld/PerfectDeliberate-Vorlagen mit JANKU (25.09.):** acht Vorlagen, JANKU gewann sieben Bündelurteile, alle sieben mit 3 Sternen. Die Landschaft (pw_00006) bekam nur 2 Sterne, Notiz Marcus: Vorlage eher realistisch, warum stehen `realism, realistic` im Negativ, und kleine Figuren im Bild. Antwort: das Negativ stammt aus dem Anime-Rezept und schiebt bewusst weg vom Fotolook, für realistische Vorlagen ist JANKU das falsche Modell. Landschaft braucht `scenery, no humans` im Prompt, sonst setzt ein Anime-Modell Figuren hinein. Die Embeddings `lazyloli`, `lazynsfw`, `lazywet` legte Marcus in den LoRA-Ordner, sie gehören nach `Data\Models\Embeddings` (verschoben). `janku_t2i` hat seitdem `embedding:lazyloli` und `embedding:lazynsfw` im vorbelegten Negativ. Das Fraktal-Konzept fehlt auch mit den Autorwerten (1024x1536, simple): Modellwissen, nicht Einstellung.
**Autorwerte gewinnen, mit Hires (25.09., Blindurteil Marcus an drei Problembildern):** 1024x1536 mit simple und danach Hires 1,5-fach bei 0,4 gewann alle drei Bündel (Fraktal, NSFW-Anatomie, NSFW-Hände), gegen das alte Rezept (832x1216, karras, Hires 2-fach bei 0,5), gegen dessen Hochformat-Variante und gegen den Autorwert ohne Hires. Der Durchgang ohne Hires, den der Autor selbst empfiehlt, war unsauber: Zeigefingernagel, Augen, Intimbereich. `janku_t2i` steht seitdem auf diesen Werten, 53 s je Bild, Ergebnis 1536x2304. Das größere Format zeigt Ganzkörperfiguren vollständig statt angeschnitten.
## Breiter Lauf über dünn besetzte Motive und Modelle (2026-09-25)

Dreißig Bilder in einem Rutsch (Kinder-Tierbilder, neue Landschaften, drei Qwen-Edits guter Bilder, Frauen in neuen Posen und Stilen), Blätter in der Galerie unter `Text2Img\agent\2026-09-25\`. Sechsundzwanzig standen im ersten Anlauf, vier brauchten einen zweiten (Gruppen `neu-*`).

- **Character-Design-LoRA auf Krea 2 schreibt einen Titel ins Blatt**, im Anlauf `krea_00003_` „BRAVE COYSS“ aus „brave penguin“. `wordless sheet without any text or lettering` und ein schlichter Grund im Prompt lösen es (`krea_00009_`), Krea hat keinen Negativ-Zweig.
- **Afterlight 0,9 auf einer Tageslicht-Landschaft kippt sie ins Dunkle** und verdrängt das Hauptmotiv an den Rand (`krea_00006_`, Eiche als Silhouette oben links). Warm Light 1,0 plus Detail 1,0 und „in the centre of the frame“ lieferten die Wiese hell und mit dem Baum in der Mitte (`krea_00010_`). Afterlight bleibt der Hebel für Gegenlicht-Stimmung, nicht für helle Landschaften.
- **Sprung-Posen auf Illustrious Realism brechen die Anatomie.** `grand jete, jumping, leg split` ergab einen stehenden Spagat mit verformter Hüfte und einer zusätzlichen Hand am Fuß (`anime-detail_00001_`). Dieselbe Tänzerin als Arabeske en pointe auf CyberRealistic Z-Image v7 mit knielangem Tutu war sauber (`foto_00008_`).
- **Qwen-2512 zeichnet eine Ukiyo-e-Figur ohne klare Angaben als Mann auf einem Boot** (`qwen_00003_`). Geschlecht, Haar, Kleidung und „standing upright on a long wooden surfboard with bent knees“ ausschreiben (`qwen_00004_`).
- **Stil-LoRAs von Krea 2 für Kinder-Tierbilder tragen:** Pop-up book 1,0 (Igel-Picknick) und Sticker 1,0 (Seeotter) trafen den Stil im ersten Anlauf. Z-Image kann Filzfiguren als Makro-Diorama (`foto_00002_`), Qwen-2512 Aquarell-Bilderbuch (`qwen_00002_`).
- **Qwen-Edit hält beim Wechsel von Jahreszeit oder Tageszeit die Komposition, den Stil nicht immer** (Vergleich vorher gegen nachher, je rund 30 s): Nebeltal zu Winter und Straßencafé zu Weihnachtsmarkt behalten Bildaufbau, Figuren und Zeichenstil. Der Impasto-Leuchtturm (`krea_00044_` vom 22.09.) verliert als Milchstraßen-Nacht seine pastose Pinseltextur und wird glatter, fast fotografisch, obwohl der Prompt den Stil ausdrücklich halten sollte.

## JANKU: „top down view“ stellt das Bild auf den Kopf (2026-09-25)

Nutzerbefund: Auf JANKU v5 ergibt `top down view` keine Aufsicht von oben, sondern ein auf dem Kopf stehendes Bild. Die Ursache ist nicht geprüft. Vermutung: JANKU liest Danbooru-Tags, dort ist „top down“ kein Kamerabegriff und kommt dem Tag `upside-down` nahe. Für eine Aufsicht den Danbooru-Tag `from above` nehmen. Ob der die senkrechte Draufsicht trifft, ist noch nicht gegengeprüft, beim nächsten Lauf mit Aufsicht beide Fassungen nebeneinander rechnen.

## Namensgrafiken und Schrift im Bild: was beim ersten Wurf hält und was nicht (2026-09-25)

Drei Vornamen mit vier und fünf Buchstaben in sieben 3D-Stilen auf Qwen-Image-2512, dazu ein Repertoire über sechs Bereiche. Blätter `out/namen_3d.png` und `out/repertoire.png`, jede Serie per `--group` gebündelt (`namen-*`, `repertoire-*`).

**Qwen schreibt kurze Namen in fast jedem 3D-Stil beim ersten Wurf richtig.** Hochglanz, Chrom, Galaxie, Neon, Graffiti und Stadion mit Fußballtextur waren durchweg korrekt, je rund 14 s. Krea 2 schreibt denselben Namen in Hochglanz ebenfalls korrekt. Gemeint ist die Rechtschreibung, nicht die Gestaltung.

**Ausnahme ist der Klötzchen-Stil in isometrischer Ansicht.** Die Schrägsicht verzerrt die Buchstaben, ein Name war unlesbar, einer grenzwertig. Mit "seen straight from the front, each letter large and clearly readable" im Prompt stimmten alle drei mit Seed 5201, der zweite Seed kippte trotzdem bei zwei von drei (Q statt O, K statt N). Klötzchen-Schrift also frontal und immer mit zwei Seeds rechnen.

**Kleine Nebentexte sind das eigentliche Risiko, nicht das Hauptwort.** Beim Badge-Logo stimmte "BlumSoft" jedes Mal, die Ringschrift darum herum war Fantasie ("Software bu:ble", "ard IT consulting"), und auch ohne Ring schrieb ein Seed "ad" statt "and". Auf einer Weinflasche erfindet Z-Image ein Etikett ("BIOLLEAIS"), obwohl "no text" im Prompt steht. Abhilfe: den Nebentext ausdrücklich verbieten ("no other text anywhere") oder das Objekt leer beschreiben ("plain blank label without any writing"). Echte Beschriftung kommt später im Layout oder als SVG.

**Repertoire, und was diese Prüfung nicht leistet:** 14 von 16 Bildern hatten beim ersten Wurf keinen Schreibfehler und keinen offensichtlichen Defekt, beide Ausfälle waren Schrift. Das ist eine Defektprüfung, kein Qualitätsurteil: der Nutzer fand die neuen Bilder insgesamt nicht besonders gut, auch die ohne Mangel. Was ihnen fehlt, ist noch offen. Sichtbar ist schon, dass die drei Cinematic-Motive aus Workflow 09 wieder sehr dunkel geraten sind, die Nachtstraße fast schwarz, obwohl die Verdunkelung durch die Luneva-LoRA bekannt war.

**Merksatz:** fehlerfrei heißt nicht gut. Eine Serie gilt erst als gelungen, wenn der Nutzer sie so bewertet. Dasselbe Muster wie beim Refiner-Vergleich vom 22.09., nur diesmal mit einer Mängelliste statt einer Schärfemessung.

**Wan auf quadratischem Eingang:** 944x944 (891.136 Pixel, knapp unter 1280x704) lief auf dem bestbewerteten Cinematic-Bild (`foto_00028`) in 360 s mit 15,2 GB Spitze durch und hielt die Komposition. Bei 1024x1024 fiel am 22.09. der Grafiktreiber mitten im Lauf aus (Code 43), die Spitze lag dort bei 16,2 von 16,3 GB. Der Zusammenhang ist naheliegend, bewiesen ist er nicht. Quadratische Clips deshalb auf 944x944 begrenzen.

## Namensbilder im Ideogram-Stil: Rezept und Stolpersteine (2026-09-25)

Nutzervorgabe: Ideogram-Stil, also gestaltete Szenen mit dem Namen als Hauptmotiv, passend zu typischen Mädchen- und Jungenthemen ab sechs Jahren. Die erste Serie (Schrift mit Textur auf Hintergrund) verfehlte das, einzig das 3D-Graffiti fand Zustimmung. Referenz über eine Bildersuche zerlegt, dann eine Probe auf Qwen-2512 und Krea 2 mit gleichem Seed, Blatt `out/namen_ideogram_probe.png`, Galerie-Gruppen `ideogram-*`.

**Merkmale der Referenz**, gegen die jedes Bild geprüft wurde: Name groß und zentral, Buchstaben als Objekt mit reichem Material, Szene mit der Schrift verschränkt (Figur sitzt auf Buchstaben, Pflanzen wachsen hindurch), eine Figur im 3D-Animationslook, Partikel, satte Farben mit Glanzlichtern, ruhiger unscharfer Hintergrund, Schriftart passend zum Thema.

**Prompt-Gerüst**, das auf beiden Modellen trägt: `a vibrant 3D name art poster, the name "X" as the large centered hero of the image, in <Material> 3D letters, <Figur und Szene verschränkt mit den Buchstaben>, <Partikel>, polished Pixar style 3D render, saturated colours, glossy highlights, soft blurred background, cool and stylish for a <girl/boy> aged six to ten, not babyish, no other text`. Alle zwölf Szenenbilder schrieben den Namen beim ersten Wurf richtig, auf beiden Modellen.

**Stolpersteine, alle im ersten Anlauf aufgetreten:**
- "bicycle kick" nimmt Qwen wörtlich und zeichnet ein Fahrrad. "overhead kick in mid-air" löst es.
- Ein Name, der zugleich Stadt- oder Vereinsname ist, ergibt mit passenden Trikotfarben einen Vereinsbezug. Trikot neutral beschreiben: "plain light blue shirt without stripes or logos".
- Krea 2 schreibt bei "poster" Fantasie-Untertitel ins Bild, "no other text" reicht nicht. Hilft im Positiv-Prompt: "the name is the only text in the image, no captions, no small print, no signature".
- Die Pop-up-LoRA liefert Bastelbuch in Beige statt satter Farben, Figuren geraten als steife Pappaufsteller, und ein Dino verdeckte einen Buchstaben halb. Gegen das Verdecken hilft "all letters fully visible and nothing covering them". Brauchbar als Sonderstil, nicht als Hauptlinie.

Ob die Probe gefällt, entscheidet der Nutzer, das Urteil steht noch aus.

## Namensposter nach Wunschthemen: Modellwahl je Thema (2026-09-25)

Neun Themen für drei Kinder (sechs und acht Jahre), jedes auf zwei Modellen mit gleichem Seed, nach dem Rezept aus dem Abschnitt davor. Blatt `out/namen_themen.png`, Gruppen `ideogram-*`.

- **Nach Modell sortieren spart die Hälfte.** Erst alle Qwen-, dann alle Krea-Läufe: nach dem ersten Bild rund 12 s je Bild statt 20 bis 28 s beim Wechsel zwischen den Modellen.
- **Markenwörter weglassen reicht, der Look kommt trotzdem.** Ohne die Wörter für Klemmbausteine und das Voxel-Spiel zeichnete Qwen die typische Minifigur und die typische Spielfigur mit Spitzhacke, ein Logo tauchte in keinem Bild auf. Superhelden wurden beim Namen genannt und kamen als Chibi-Figuren.
- **Der Textverbot-Zusatz im Positiv-Prompt wirkt:** mit "the name is the only text in the image, no captions, no small print, no logos" schrieb Krea in neun Bildern keinen Fantasie-Untertitel mehr.
- **Krea scheitert reproduzierbar an zwei Dingen:** Voxel-Buchstaben (drei von drei Anläufen unlesbar, das O wird zu Q oder D) und einer Figur neben dem Namen (dreimal stand der Junge vor dem letzten Buchstaben, trotz "nothing covering them"). Qwen löste beides im ersten Anlauf. Im Comic-Stil setzte Krea einmal einen Zusatzbuchstaben ans Namensende und einmal unscharfe Geisterbuchstaben in den Hintergrund, der dritte Seed war sauber.
- **Z-Image für Plüsch:** Buchstaben und Kuscheltiere tragen sichtbare Fellstruktur, die Schrift stimmte beim ersten Wurf.
- **Sticker-LoRA auf Krea 2:** gestanzter Sticker mit weißem Rand und korrekter Schrift im ersten Anlauf.

Das Urteil über die Bilder steht beim Nutzer noch aus.

## Civitai recherchieren: Zahlen je Version, Bilder über die API (2026-09-25)

- Download- und Like-Zahlen der Suchliste gelten für die ganze Modellseite über alle Basismodelle. Logo.Redmond zeigt 74.507 Downloads, die Z-Image-Fassung davon 2.023. Zur Bewertung `modelVersions[].stats` der passenden Fassung nehmen (`/api/v1/models/<id>`).
- Die Modellseiten liegen hinter einem Einwilligungsbanner, `shot.js` sieht nur das Banner. Beispielbilder kommen sauber über `/api/v1/images?modelVersionId=<vid>&nsfw=None&sort=Most Reactions`, als Vorschau mit `/width=450` statt `/original=true` in der URL.
- Basisnamen bei Civitai: `Krea 2`, `Qwen` (Qwen-Image), `ZImageTurbo`, `ZImageBase` und `Qwen 2` für Qwen-Image 2.x. Ob unser 2512 dort mitgezählt wird, ist offen.
- Ergebnis der Recherche für Namensposter steht als Kandidatentabelle in `models.md`.

## Kritik am Prompt-Gerüst und Typnosis im Test (2026-09-26)

Nutzerkritik am Gerüst vom 25.09.: der Zusatz mit Zielgruppe und Verboten gehöre nicht in den Positiv-Prompt, Krea zeige Text und Figuren doppelt verschwommen im Hintergrund, Qwen lasse Objekte durch die Schrift laufen, die Bausteine seien Duplo statt Lego. Nachgerechnet mit denselben Seeds, Blatt `out/vergleich_typnosis.png`.

- **Ein Negativ-Prompt wirkt bei Qwen-2512, Krea 2 und Z-Image nicht:** alle drei Workflows laufen mit cfg 1.0, dann rechnet der Sampler den Negativ-Zweig gar nicht. Verbote gehören trotzdem nicht in den Positiv-Prompt, sie ziehen das Verbotene eher ins Bild. Besser das Gewünschte positiv beschreiben: "clean composition with the single word X", "the letters are solid and complete".
- **"soft blurred background" verursacht bei Krea die Geisterbilder.** Mit dem Zusatz standen ein zweiter, verschwommener T-Rex und Geisterbuchstaben im Hintergrund. Ersetzt durch einen konkreten Hintergrund und "sharp focus throughout" verschwanden sie in beiden Fällen bei gleichem Seed.
- **Die Altersangabe zog die Bausteine zu Kleinkindsteinen.** Ohne "made for a boy aged six" und mit "small classic interlocking toy bricks with fine studs" plus "brick-built minifigure" lieferten alle drei Varianten Steine im Lego-Maßstab mit Minifiguren.
- **Offen geblieben:** Qwen stellt den Fußballer trotz "beside the name" mitten in das O und malte beim Einhorn zwei statt einem. Krea stellte den Fußballer zum vierten Mal vor das O.
- **Typnosis (Krea 2, 435 MB, Civitai 2840653) wirkt:** Schlüsselstruktur gleich der Sticker-LoRA, Basis krea2, SHA256 gegen Civitai geprüft. Sweep am Dino-Motiv: 1,0 und 1,5 heben die Buchstaben als Material hervor, 2,0 macht daraus ein Spieltitel-Logo, bei 3,0 kippt die Schrift (Punkt auf dem I). Brauchbar 1,0 bis 2,0, wie der Autor angibt. Bei den Bausteinen standen mit Typnosis 1,5 alle Buchstaben frei, der Dino dahinter statt davor.

Ob die neuen Fassungen gefallen, entscheidet der Nutzer.

## Typnosis 1,0 gegen 1,5 über alle Themen, Platzierung bei Krea (2026-09-26)

Acht Themen auf Krea 2 mit Typnosis 1,0 und 1,5 bei gleichem Seed, zwei davon zusätzlich mit 2,0, die Dinos auf Qwen. Prompt ohne "Pixar style", mit Kinolicht, heroischen Posen statt "cute kid version" und realistischen Dinos, weil der Nutzer die Bilder weniger kindlich wollte. Blatt `out/namen_typnosis.png`.

- **Platzierung bei Krea ist einseitig:** Figuren oder Fahrzeuge "to the right of the last letter" landen vor dem letzten Buchstaben (Jeep zwei von zwei, Fußballer vorher vier von vier). "To the left of the first letter" hielt jedes Mal (Fußballer zwei von zwei, Jeep zwei von zwei). Nebenobjekte bei Krea deshalb links anordnen.
- **Steht eine Figur auf dem I, setzt Krea gern einen abgesetzten Stein darüber**, das I liest sich dann als kleines i mit Punkt (zwei von vier Baustein-Bildern).
- **Voxel-Schrift kann Krea nicht, auch mit Typnosis nicht:** null von fünf lesbar, der erste Buchstabe wird zum N. Qwen schaffte es mit "the first letter is a clear blocky K" und der Figur "at the far left edge of the image apart from the letters" in zwei von zwei Fällen.
- **Typnosis 1,0 und 1,5 schrieben in allen übrigen Themen korrekt**, 2,0 ebenfalls in beiden Proben. Welche Stärke gefällt, entscheidet der Nutzer.

## Namensposter-Standard: Typnosis 1,5 mit Licht- und Detailstapel (2026-09-26)

Der Nutzer wählte Typnosis 1,5 als Standard und verlangte dazu Detail-Slider und leichtes Afterlight. Umgesetzt als Workflow 13 (`krea2_namensposter.api.json`) mit dem gemessenen Rezept vom 22. September, den Detail-Slider aber auf 1,0 statt 1,5. Blatt `out/vergleich_stapel.png`.

- **Wirkung des Stapels bei gleichem Seed:** mittlere Helligkeit 6 bis 9 Prozent niedriger bei Monstertruck, Einhorn, Glitzer und Kuscheltieren, 1 Prozent bei den Bausteinen, bei den Superhelden 9 Prozent höher. Der schwerere Eindruck kommt vor allem von Kontrast und Dunst, weniger von der Helligkeit.
- **Bausteine mit Stapel setzen einen i-Punkt:** das I bekommt einen abgesetzten Stein darüber, zweimal von zwei, auch mit der Minifigur auf dem ersten Buchstaben. Ohne Stapel stand das I beim selben Seed gerade. Der Nutzer sieht dort keinen runden Punkt und nimmt die Stapelfassung an (Urteil vom 26.09.2026), wie vorher schon das Graffiti mit kleinem i.
- **"a young European boy with fair skin and short light brown hair"** gab in zwei von zwei Seeds den gewünschten Jungen, der Platz links vom ersten Buchstaben blieb erhalten.
- **Mit mehreren aktiven LoRAs ist Krea nicht bitgenau reproduzierbar.** Derselbe Graph mit gleichem Seed lieferte beim zweiten Lauf dieselbe Komposition mit anderen Details (Umhang, Hand, Kanten), mittlere Abweichung 12 von 255. Die Läufe danach waren untereinander pixelgleich. Vermutete Ursache: Krea fp8, Text-Encoder und vier LoRAs überschreiten 16 GB, ComfyUI lagert Schichten aus und rechnet deren LoRA-Patches anders, je nachdem was vorher im Speicher lag. Bei Stärke 0.0 gilt die Byte-Gleichheit vom 21.09. weiter, dort wird nichts gepatcht.
- **Prüfung des neuen Workflows:** der Graph-Diff gegen den Teststapel zeigt nur Ablage und Standardformat, das Ergebnis war pixelgleich zum zweiten Stapel-Lauf.

## Detail als Standard, Promptlänge, Masterpiece-LoRA und Sticker (2026-09-27)

Auf Nutzerwunsch ist Detail jetzt in allen Foto-Workflows in kleiner Stufe an. Dazu kamen ein Promptlängen-Test auf drei Modellen, die Masterpiece-LoRA auf Krea und Namensposter als Sticker. Messwerte sind Diagnose, die Urteile zu den Blättern stehen aus.

- **Nachgerechnet statt neu erfunden:** 16 Bilder mit drei Sternen und ohne aktive LoRA (11 Krea, 3 Z-Image, 2 CyberRealistic) aus dem Graphen im eigenen PNG, nur die LoRA-Stärke geändert. Die Kontrolle ohne Änderung war bei Krea pixelgleich zum Original vom 22.09., bei Z-Image und CyberRealistic wich sie um 0,7 bis 1,0 von 255 ab (unsichtbar). Upscales und Detailpässe führen über `src_key` zum erzeugenden Bild, andere `src_key` zeigen auf Vorlagen (Civitai, Nachbau) und sind nicht das Original.
- **Kleine Stufen halten die Komposition:** mittlere Helligkeit und Kantenenergie (Mittel über FIND_EDGES) gegen das Original: Krea Detail 0.5 minus 4 und plus 5 Prozent, Z-Image 0.3 minus 5 und plus 2 Prozent, CyberRealistic 0.3 minus 8 und minus 1 Prozent. Doppelte Stärke kostete 14 (Z-Image) und 21 Prozent (CyberRealistic) Helligkeit, auf CyberRealistic bringt der Slider vor allem Dunkelheit. Daraus die Voreinstellungen Krea 0.5, Z-Image und CyberRealistic 0.3. Blätter `out/sterne_27_mitlora_krea.png` und `out/sterne_27_mitlora_zimage.png`.
- **Der volle Krea-Stapel (Detail 1.0, Warm 0.5, Afterlight 0.35) ist kein Standard für beliebige Motive:** Kantenenergie im Mittel plus 56 Prozent. Dafür ändern sich Blüten, Schriftrolle und Figurengrößen sichtbar, in einem Namensbild schob sich die Figur über den letzten Buchstaben. Er bleibt Workflow 13 vorbehalten.
- **Sticker-LoRA für Namen zum Ausdrucken:** Sticker 1.0 mit Detail 0.5, einmal zusätzlich Typnosis 1.0 im freien REALISM-Knoten. Weißer Stanzrand und hellgrauer Grund kamen in allen Fällen, jedes I stand gerade. "To the left of the first letter" verdeckte hier den ersten Buchstaben in vier von vier Bildern, "jumping over the letters" und "leaping over the letters" ließen alle Buchstaben frei (acht von acht). Bei Stickern die Figur über die Schrift springen lassen. Blatt `out/namen_27_sticker.png`.
- **Typnosis lädt nur auf Krea, die Verbindung mit Qwen läuft über das Bild:** Qwen-Edit-2511 auf dem fertigen Typnosis-Poster, "Turn the two cartoon dinosaurs into photorealistic prehistoric animals ... Keep the letters ... exactly the same", hielt Schrift, Vulkan und Himmel. Ohne Größenvorgabe wuchs das kleine Tier und verdeckte den letzten Buchstaben. Mit "keep both dinosaurs at exactly the same size and position ... does not cover any letter" zwei von zwei sauber. Blatt `out/namen_27_dino_edit.png`.
- **Workflow 13 schreibt ein I im Graffiti wieder als kleines i** (zwei von zwei), wie am 25.09. auf Qwen.
- **Promptlänge, gleiche Seeds, knapp (etwa 18 Wörter) gegen ausführlich (etwa 110 Wörter, gleicher Inhalt plus Licht, Kamera, Komposition, Material):** der ausführliche Prompt setzt die genannten Details um (Trauben im Vordergrund, Fensterlicht von links, Hobel mit Spänen). Knapp entscheidet das Modell selbst. Z-Image griff dabei zweimal von zwei daneben: der Schreiner ohne Kopf im Anschnitt, mit Säge oder Messer statt Hobel. Qwen zeichnete knapp einen Hobel in Fantasieform, Krea blieb knapp stimmig. Blätter `out/prompt_27_krea.png`, `..._zimage.png`, `..._qwen.png`.
- **Was die Hersteller sagen** (Recherche 27.09., Primärquellen): Krea nennt lange detaillierte Prompts am besten, knappe gehen auch. Das Z-Image-Team schreibt, Turbo arbeite am besten mit langen detaillierten Prompts. Im Feintuning hat es jeden Prompt durch seinen Prompt-Enhancer geschickt. Qwens Enhancer für 2512 zielt bei Porträts auf etwa 200 Wörter. Alle drei Referenz-Pipelines schneiden bei 512 Tokens ab (etwa 380 englische Wörter), ComfyUI schneidet nie ab. Qualitäts-Tags: der Z-Image-Enhancer verbietet "8K" und "masterpiece", Qwen hat den Anhang ", Ultra HD, 4K, cinematic composition." mit 2512 gestrichen, Krea schweigt dazu.
- **Die offizielle ComfyUI-Vorlage für Krea 2 Turbo erweitert jeden Prompt vorher**, standardmäßig eingeschaltet: der Text-Encoder Qwen3-VL-4B schreibt als Sprachmodell (Knoten `TextGenerate`, System-Prompt nach Kreas `docs/expansion.txt`, `max_length` 512) den ausführlichen Prompt. Unser Workflow 10 hat diesen Schritt nicht. Nachgebaut mit Greedy-Decoding (`sampling_mode` off, damit reproduzierbar): aus 16 bis 18 Wörtern wurden 86 bis 162, in 28 bis 36 s einschließlich Laden. Die Bilder wurden dunkler und stimmungsvoller, weil die Erweiterung Licht wie "dimly lit" und "warm glow" ergänzt. Zweistufig gebaut (erst Text über `PreviewAny` holen, dann rechnen), damit der erweiterte Prompt in den PNG-Metadaten steht.
- **Masterpiece-LoRA auf Krea (1.5, Trigger `masterpiece, very aesthetic`):** knapp, knapp mit Tags ohne LoRA, knapp mit LoRA ohne Tags, knapp mit LoRA und Tags, gleicher Seed. Schon die Tags allein verändern das Bild deutlich (andere Requisiten, mehr Sättigung, anderer Ausschnitt), die LoRA zieht zu kräftigeren Farben und frontalerem Aufbau. Ob das besser ist, entscheidet der Nutzer am Blatt `out/prompt_27_krea.png`.

## Kinobanner 21:9, Workflow 14 (2026-09-27)

Erste Art aus dem Plan Spielegrafik und Kinobanner (Auftrag des Galerie-Koordinators). Sechs Motive (Drache, Raumschiff, Noir, Tempel, Leuchtturm, Fuchs), je einmal Z-Image über den neuen Workflow `zimage_kinobanner` (Graph von 09 in 1680x720) und Krea 2 in 1568x672 mit Detail 1.0, Afterlight 0.35 und Warm 0.5. Blatt `out/banner_27_test.png`, Galerie-Gruppen `kinobanner-<motiv>`.

- **Formate:** 1680x720 und 2016x864 gehören laut Z-Image-Team zu den trainierten Formaten, 1568x672 ist Kreas eigenes 21:9 in der App. Beide rechneten sauber ohne Wiederholungen oder Doppelungen am Rand. Qwen-2512 hat kein 21:9-Format, dort 16:9 und zuschneiden.
- **Zeiten auf der 5070 Ti:** Z-Image 9,3 bis 9,8 s, Krea mit Stapel 11 bis 12 s, dazu einmalig rund 10 s Modellladen.
- **Die Titelfläche muss bestellt werden.** "The main subject sits in the right third ... The left half ... reserved for the movie title" plus ein Satz, was links steht. Krea hielt die linke Hälfte in sechs von sechs frei, Z-Image in vier von sechs. Beim Tempel füllte Z-Image auch links mit Ruinen, bis der Prompt sagte "The explorers and the temple entrance fill the right third. The left half is filled with soft hazy jungle mist".
- **Schilder schreiben Fantasietext.** "a flickering neon sign" gab auf beiden Modellen Buchstabensalat, "a flickering pink neon light above a doorway" auf Z-Image weiterhin ein beschriftetes Schild, auf Krea eine Röhre ohne Schrift. "a single bare horizontal pink neon tube" war auf Z-Image frei von Text.
- **"soft even gradient" nimmt Z-Image wörtlich:** beim Noir-Motiv malte es links einen türkisen Lichthof statt einer ruhigen Wand. Der Satz, was links konkret steht, wirkt stärker als die allgemeine Titelformel.
- **Nutzerurteil (27.09., über den Galerie-Koordinator):** Krea gefällt deutlich besser, der Stapel (Detail 1.0, Afterlight 0.35, Warm 0.5) war aber etwas zu stark. Die Z-Image-Banner fand er schwach, vor allem die Felsen am Leuchtturm. Das Ziel Kinobanner steht seither auf Krea als Erster Wahl (Detail vorläufig 0.5), Z-Image ist Alternative. Ein kontrollierter Test zu Krea-Stufen und zu Landschaft auf Z-Image gegen Krea ist beim Nutzer angefragt.
- **Bündelurteil vom 28.09.2026 in der Galerie (alle sieben Fassungen je Motiv):** In allen sechs Motiven hat der Nutzer K0 als Sieger gesetzt, also Krea mit Detail 1.0, Afterlight 0.35 und Warm 0.5. Z-Image gewann keines. Die Sterne sind lückenhaft vergeben und trennen die Krea-Stufen kaum. Das widerspricht dem Urteil vom Vortag, der Stapel sei etwas zu stark. Aufgelöst am selben Tag, siehe den Abschnitt zu Workflow 14 weiter unten. Ausgelesen über `/api/verdicts` und `/api/duel/stats?prefix=banner_`.

## Icon-Serie nach Referenz, Workflow 15, Testsatz Blumilie (2026-09-27)

Zweite Art aus dem Plan Spielegrafik. Der Nutzer hat Blumilie als Testspiel gewählt, dessen Stilvertrag (`D:\Repos\blumilie\docs\BILDSTIL.md`) verlangt mattes Vinyl ohne Kontur, Glanz nur als breite kontrastarme Cremefläche, lesbar bei 24 px, und schickt bei jeder Generierung die abgenommene Beere als Materialreferenz mit. Die abgenommenen Symbole des Spiels entstanden über Codex mit Referenzbild. Lokal übernimmt Qwen-Image-Edit-2511 diese Rolle: neuer Workflow `qwen_edit_icon_set` (Graph von 05 plus die BiRefNet-Kette von 01), Eingang ist die Referenzbeere auf hellgrauem Grund (#D0D0D0), der Prompt tauscht nur das Motiv. Vier Motive mit abgenommenem Gegenstück (Stern, Tropfen, Wolke, Mond) und vier neue (Blume, Pilz, Kleeblatt, Muschel), je zwei Seeds, dazu Z-Image über 01 ohne Referenz zum Vergleich. Blätter `out/icons_27_blumilie.png` und `out/icons_27_blumilie_24px.png`, Galerie-Gruppen `icon-blumilie-<motiv>`.

- **Die Referenz trägt Material und Licht.** Weiche Schattierung, Lichtrichtung von links oben und die ruhige Sättigung der Beere kamen in allen 16 Qwen-Bildern mit. Z-Image ohne Referenz wurde blasser (Stern und Mond fast cremeweiß), setzte der Wolke eine dunkle Randlinie (Konturverbot verletzt) und malte beim vierblättrigen Kleeblatt drei Blätter.
- **Farbnamen verführen zu Materialien.** "warm gold" ergab metallisches Gold mit abgesetzter Kante (Stern, Mond, Blütenmitte, sechs von sechs), "matte sunflower yellow ... not metallic" ein kaltes Zitronengelb. Getroffen hat erst "a warm marigold orange-yellow (#ECA532) like egg yolk, made of exactly the same matte material as the berry, not lemon yellow, not metallic" (vier von vier). Hex-Werte allein hält Qwen nicht ein, der Vergleich mit einem bekannten Stoff wirkt.
- **Glanz weich bestellen.** "one broad low-contrast cream sheen patch" wurde beim Tropfen ein harter heller Streif. "The only light on it is one broad soft blurry cream sheen on the upper left, exactly as soft as on the berry, no sharp white streak" traf es bei einem von zwei Seeds.
- **Qwen hat ein eigenes Bild von einer Wolke:** viele kleine Kugeln statt drei großer Buckel, auch mit ausdrücklicher Formbeschreibung (vier von vier). Erst "shaped like a soft plush cushion ... all merged into one smooth shape with a flat bottom ... without separate balls or bubbles" ergab bei einem von zwei Seeds die glatte Kissenform des Bestands.
- **Messwerte des Endstands:** Alpha-Zwischenwerte 0,4 bis 0,8 Prozent (Vertrag unter 2), Deckungsgrad 30 bis 47 Prozent (Referenz 32,8), Motivhöhe 72 bis 83 Prozent, die breite Wolke 52, bei mindestens 8 Prozent Rand (Vertrag etwa 85 bei mindestens 6). Bei 24 px auf den drei App-Hintergründen und Kartenhell alle acht erkennbar und unterscheidbar, die Wolke wie im Bestand am kontrastschwächsten.
- **Zeiten und ein Hänger:** etwa 20 s je Icon, der erste Lauf mit Laden von Qwen-Edit und BiRefNet 41 s. Ein Lauf blieb nach dem Modellwechsel im Sampler bei 0 von 4 Schritten stehen und lief 15 Minuten ins Timeout, `POST /interrupt` löste die Warteschlange, der Prozess musste nicht neu starten. Beim Wechsel von Z-Image zurück zu Qwen-Edit dauerte ein Lauf 97 bis 275 s statt 20.
- **Fehler im UI-Konverter behoben:** `api_to_ui_workflow.py` schrieb den Beispiel-Prompt immer ins Feld `text`, Qwen-Edit-Knoten heißen `prompt`. Workflow 05 zeigte deshalb seit dem 19.09. nur "placeholder". Jetzt wie in `inject()` von `comfy_generate.py`, 05 und 15 neu erzeugt.
- **Offen für den Nutzer:** ob die lokalen Icons neben den Codex-Icons des Spiels bestehen, entscheidet der Vergleich in der Galerie. Zwanzig vertragswidrige Zwischenstände liegen im Papierkorb der Galerie.

## UI-Elemente nach Referenz, Workflow 16, Testsatz Aschekrone (2026-09-27)

Dritte Art aus dem Plan Spielegrafik. Blumilie schließt UI im Bildstil in seinem Vertrag aus ("UI-Chrome ... bleibt Token-basiert flach"), der Nutzer hat deshalb Aschekrone gewählt. Dessen Vertrag (`D:\Repos\aschekrone\docs\BILDSTIL.md`) erlaubt als UI-Flächen nur Kartenrahmen und Gründe, Knöpfe, HUD und Symbole bleiben geometrisch. Geprüft gegen die abgenommenen Master mit denselben Kennzahlen wie im Vertrag. Das Prüfskript trifft die dort dokumentierten Werte (Grund im Mittel 17,5/15,5/13,0, Rahmen mit Mitte 0 und Asymmetrie 0,0), taugt also als Maßstab. Blatt `out/ui_27_aschekrone_hell4.png` (vierfach aufgehellt, sonst ist nichts zu sehen), Galerie-Gruppen `ui-aschekrone-rahmen` und `ui-aschekrone-grund`.

- **Rahmen nach Vorlage (Qwen-Edit):** Mitte bleibt schwarz, Band bei 87 bis 100 px wie im Master (Vertrag: innerhalb 140). Zusätzliche Rauten auf den Seitenmitten gelangen, das Ersetzen der Eckrauten durch Kreise oder Quadrate nur teilweise: Qwen setzte die neuen Formen oft zusätzlich nach innen. Die Striche kamen heller als im Master (Mittel 85 bis 125 gegen 78, hellster Wert bis 173 gegen 116).
- **Der abgenommene Rahmen ist exakt gespiegelt** (Asymmetrie 0,0), erzeugte Rahmen lagen bei 0,5 bis 1,2. Workflow 16 hat deshalb einen zweiten Ausgang, der das linke obere Viertel waagerecht und senkrecht spiegelt (Kernknoten ImageCrop, ImageFlip, ImageStitch), vier von vier danach bei 0,00.
- **Rahmen ohne Vorlage:** Krea (Detail 0.5) traf aus dem Vertragsprompt Palette (Strich im Mittel 86/80/68), Band (73 px) und Aufbau fast wie der Master. Qwen-2512 zeichnete dicke hellweiße Mehrfachlinien, Mitte nicht schwarz, Asymmetrie 11, also unbrauchbar für diesen Stil.
- **Gründe:** "Remove all the tiny warm specks" auf dem Master ergab eine ruhigere Kartenfläche mit fast gleichem Mittelwert (16,0/13,8/11,3), ohne harte Kanten, ohne Flecken ab 8 px. "One tone darker and slightly cooler" machte den Grund blau (Mittel 18/22/27, Blau ist im Vertrag verboten). Aus reinem Text lagen Z-Image (52/46/41, papierhell mit Rändern) und Krea (39/35/30, 45 Flecken) weit über dem Soll. Helligkeit und Farbton lieber rechnen als bestellen.
- **UI-Konverter erweitert:** ein zweiter Speicherknoten mit Titel `SAVE_<ZUSATZ>` bekommt in der Oberfläche den Zusatz als Suffix im Dateinamen (bisher nur `SAVE_DETAIL`).
- Neun vertragswidrige Testbilder liegen im Papierkorb der Galerie (blaue Gründe, helle Text-Gründe, Qwen-2512-Rahmen, misslungene Eckformen).

## Blinder Landschaftstest und Kinobanner-Stufen (2026-09-27, Auftrag des Galerie-Koordinators)

Anlass: die Empfehlung "Z-Image für Landschaft" beruhte nur auf dem A/B gegen FLUX-schnell vom 27.08., gegen Krea und Qwen war Landschaft nie gezielt getestet, und der Nutzer fand die Z-Image-Weinberge und die Z-Image-Banner schwach. Dieser Abschnitt hält nur den Aufbau fest, das Urteil fällt der Nutzer blind im Duell.

- **Aufbau Teil 1:** 16 Prompts (8 Motive mit je zwei Fassungen, 92 bis 112 Wörter, Vorder-, Mittel- und Hintergrund, Lichtrichtung, Brennweite, keine Qualitätsformeln), je Prompt ein Seed (8101 bis 8116) für alle Modelle, 1344x768. Z-Image (Detail 0.3), CyberRealistic Z-Image (Detail 0.3), Krea (Detail 0.5, sonst alle LoRAs 0), Qwen-2512 in Qualitätseinstellung (Turbo-LoRA 0.0, 30 Steps, cfg 4.0). Jedes Bild genau einmal. Dateien `landtest_NN` mit zufälliger Nummer, ohne Gruppe. Zuordnung und Prompts: `out/landtest27_zuordnung.csv` und `out/landtest27_prompts.py`.
- **Illustrious Realism nicht dabei:** SDXL auf Illustrious-Basis, CLIP liest 100-Wort-Prompts nur in 77-Token-Blöcken, und am 21.09. kippte es ein Motiv ins Halbrealistische.
- **Zeiten:** Z-Image und CyberRealistic 7,8 s, Krea 10,8 s, Qwen in Qualitätseinstellung 97,5 s je Bild (Median, 1344x768).
- **Teil 2, Kinobanner-Stufen:** gleiche Prompts und Seeds wie die vorhandenen Bilder, aus deren Metadaten gelesen. Krea in 1568x672: K1 Detail 0.5 / Afterlight 0.35 / Warm 0.5, K2 0.5 / 0.2 / 0.5, K3 0.5 / 0 / 0 (vorhanden K0 1.0 / 0.35 / 0.5). Z-Image in 1680x720: Z1 Luneva 0.5 / Detail 0.3, Z2 Luneva 0 / Detail 0.3 (vorhanden Z0 0.5 / 1.0). Z2 klärt beim Leuchtturm, ob die Trümmer vom Modell oder vom Stapel kommen. Galerie-Gruppen `kinobanner-<motiv>`, vorher die toten Schlüssel über die Galerie-API entfernt (Gruppe auflösen und mit den lebenden Mitgliedern neu anlegen, nur wo kein Urteil hängt).

## Landschaft: Blindtest ausgewertet, Qwen-2512 in Qualitätseinstellung vorn (2026-09-28)

Der Nutzer hat alle 16 Landschaftsprompts aus dem Abschnitt davor blind beurteilt, je Prompt vier Bilder mit gleichem Seed und gleicher Größe, ohne aufgedeckte Schritte (Galerie `/api/duel/stats?prefix=landtest_`, Zahlen dort nachgeprüft).

- **Siege je Prompt (Hauptkennzahl):** Qwen-Image-2512 8, Krea 2 5, CyberRealistic Z-Image 2, Z-Image-Turbo 1.
- **Wer welches Motiv gewann:** Qwen den Pfälzer Weinberg, die Felsküste mit Leuchtturm, den Bergsee, den Felsgrat, den Nadelwald im Nebel, die Heide, die Burgruine und den Wasserfall. Krea den Mosel-Steilhang, den Sturm an der Küste, die Steinbrücke, das Wintertal und den Raureif. CyberRealistic das Kornfeld und den See mit Steg, Z-Image den Buchenwald.
- **Paarweise (Nebenkennzahl, aus König des Hügels):** Qwen gegen Krea 9:5, Qwen gegen Z-Image 9:1, Krea gegen Z-Image 4:1, CyberRealistic gegen Krea 1:7, gegen Qwen 2:6, gegen Z-Image 2:1. Der Ablauf begünstigt Modelle mit schwankender Qualität, deshalb zählen die Siege je Prompt.
- **Gewonnen hat eine langsame Einstellung:** Qwen lief ohne Turbo-LoRA mit 30 Steps und cfg 4.0, etwa 100 s je Bild bei 1344x768, rund zehnmal so lang wie Krea (11 s) und Z-Image (8 s). Krea bleibt die schnelle Alternative. Die bisher empfohlene Turbo-Fassung von Qwen (2 Steps) war nicht im Test.
- **Folgen:** Landschaft steht jetzt auf Qwen-2512 in Qualitätseinstellung (neuer Workflow 17 `qwen_2512_landschaft`), Krea als schnelle Alternative, Z-Image ist dort gestrichen. Z-Image bleibt Erste Wahl für Architektur, Produkt, Handwerk und Portrait, diese Verticals sind gegen Krea und Qwen ebenfalls noch nicht blind getestet.
- **Workflow 17 geprüft:** mit Prompt und Seed des Bergsee-Bildes neu gerechnet, der eingebettete Graph ist bis auf den Dateinamen identisch mit dem Testbild. Die Pixel wichen im Mittel um 2 von 255 ab, die Komposition war gleich. Qwen als GGUF ist über verschiedene Speicherzustände nicht bitgenau reproduzierbar, wie Krea mit mehreren LoRAs.

## Kinobanner: Stufen entschieden, Workflow 14 auf Krea mit zuschaltbarer Stimmung (2026-09-28)

- **Blindurteil (über den Galerie-Koordinator):** K0 (Detail 1.0, Afterlight 0.35, Warm 0.5) gewann alle sechs Motive gegen K1 bis K3 und gegen Z0 bis Z2. Der Nutzer dazu: Detail hoch gehört in den Standard. Afterlight und Warm geben jedem Bild mehr Kontrast und Unschärfe hinten und außen, das passt nicht zu jedem Bild.
- **Umgesetzt:** neuer Workflow `krea2_kinobanner` (UI 14-kinobanner) mit Detail 1.0, Afterlight und Warm als Knoten `STIMMUNG_AFTERLIGHT` und `STIMMUNG_WARM` auf 0. `comfy_generate.py --mood` setzt 0.35 und 0.5 und bricht ab, wenn ein Workflow die Knoten nicht hat. Die Z-Image-Fassung heißt jetzt 14b. Faustregel in SKILL.md.
- **Blindtest K4:** gleiche Prompts und Seeds 7901 bis 7906, Detail 1.0, Stimmung aus, über den neuen Workflow 14. Je Motiv ein Bild in `kinobanner-<motiv>` (`agent/2026-09-28/banner_00001` bis `00006`), dort tritt es gegen den stehenden Sieger K0 an. Klärt, ob die Stimmung oder das Detail den Sieg ausgemacht hat. **Ausgewertet am 2026-10-03:** K0 mit Stimmung gewann drei Motive (Drache, Raumschiff, Tempel), drei endeten unentschieden (Leuchtturm, Fuchs, Noir), K4 ohne Stimmung gewann keines, alle Schritte blind. Der Nutzer hat die Stimmung daraufhin zum Standard gemacht, `--no-mood` schaltet sie ab.
- **Stolperstein:** der Galerie-Index führt den Seed als Text, wer ihn weiterreicht, muss ihn in eine Zahl wandeln.

## Sprites nach dem Aschekrone-Vertrag, Workflow 18 (2026-09-28)

Vierte Art aus dem Plan Spielegrafik. Nutzerwahl über den Galerie-Koordinator: Aschekrone, orientiert an den Gate-Bögen `gate-figur-r1.png` und `gate-fusssoldat-r1.png` (drei Posen in Draufsicht, 1536x1024 auf flachem Grün, Vertrag `docs/BILDSTIL.md`, Abschnitt „Gemalte Figuren“). Vier neue Gegner aus GAME-DESIGN Abschnitt 4 mit ihrer Funktionsfarbe: Armbrustschütze, Schildträger, Brandstifter, Kriegshund. Blätter `out/sprites_28_aschekrone.png` (alle Wege) und `out/sprites_28_zielgröße.png` (Testsatz in Zielgröße auf dem abgenommenen Grund, 1x und dreifach), Galerie-Gruppen `sprite-aschekrone-<motiv>`.

- **Qwen-Edit mit einem Gate-Bogen als Vorlage (der geplante Weg) hält den Vertrag bei neuen Figuren nicht.** Aufbau, Grün und Maßstab bleiben. In 9 von 12 Bögen mit Menschen drehte Qwen die Figur aber über die Zellen zu Vorder-, Seiten- und Rückansicht, mit dem ausdrücklichen Verbot ("They are not a front, side and back view") in 6 von 6, ohne es in 3 von 6. Dazu Gesichter, Finger, dünne Sehnen und beim Brandstifter und beim Hund gezogene Konturen (Randhelligkeit 0,31 bis 0,39 des Innern, Gate 0,61 und 0,69). Den Hund malte es in 4 von 4 Bögen aufrecht von hinten.
- **denoise unter 1 rettet das nicht:** bei 4 Lightning-Schritten rechnet denoise 0.9 genau wie 1.0 (`int(4/0.9)` ergibt wieder 4 Schritte, die Bilder waren identisch). 0.8 überspringt einen von fünf Schritten, behält Stil, Haltung und Draufsicht des Gate-Bogens und tauscht das Motiv nur teilweise (roter Helm auf knochenweißem Soldaten, Armbrust in zwei von drei Zellen). Das taugt für Varianten eines abgenommenen Bogens, nicht für neue Figuren.
- **Multiple-Angles-LoRA (0.9) ohne sichtbare Wirkung** auf dem Bogen: 60 und 30 Grad ergaben fast den Ausgangsbogen. Laut Modellkarte reicht sie nur bis 60 Grad Höhe ("high-angle shot"), eine echte Draufsicht kann sie nicht. Für Aschekrone überflüssig, der Renderer dreht die Figur in Laufrichtung.
- **Krea 2 aus Text trifft die Draufsicht in allen 23 Bögen,** mit dem Gerüst der Vertragsprompts (GAME PIECE, VIEW straight top-down, POSES, flaches Grün). Schrittfolge in den Füßen, keine gezogenen Konturen (Randhelligkeit 0,79 bis 1,15), die Funktionsfarbe als dominante Fläche. Z-Image malte im einzigen Vergleichsbild eine Seitenansicht mit Bogen statt Armbrust.
- **Was bestellt werden muss:** Ausrüstung je Zelle ("In all three cells he holds ..."). Ohne diesen Satz ließ die Standpose in 2 von 2 Bögen Topf oder Fackel weg, mit ihm waren 3 von 4 vollständig. Die Armbrust als T-Form aus zwei dicken Balken: ohne Sehne in 2 von 4 Bögen, vorher in 0 von 3. Eine feste Größe mit grünem Rand hält nur teilweise.
- **Abweichungen vom Gate, gemessen:** Krea malt glatter (Feinkorn als Hochpassanteil 0,004 bis 0,019 gegen 0,018 und 0,034 beim Gate) und legt statt #00ff00 ein gleichmäßiges Mittelgrün um 76/172/80 an (Streuung 2). Ein Farbschlüssel wie `remove_chroma_key.py` des Spiels braucht dann diesen Wert. Den genauen Farbton rechnet das Spiel ohnehin nach.
- **Offen:** Vierbeiner. Der Hund kam in allen Krea-Bögen von oben. Er saß jedoch ohne seitliche Beine und hatte drei fast gleiche Posen. Gelöst am selben Abend für Hund und Wolf, siehe den Abschnitt zu den Vierbeinern.
- **Zeiten:** Krea etwa 17 s je Bogen in 1536x1024, Qwen-Edit 18 bis 30 s.
- **Workflow 18 ist `krea2_sprites`** (Graph von 10 in 1536x1024, Ablage `sprite`). Die Qwen-Edit-Fassung vom Vormittag liegt als Beleg im Scratchpad dieser Session, nicht unter `workflows/`. 35 vertragswidrige Zwischenstände und eigene Dubletten liegen im Papierkorb der Galerie, elf Bögen in vier Gruppen sind geblieben.

## Vierbeiner als Sprites, Workflow 18 mit gespiegeltem Zweitausgang (2026-09-28)

Folgeauftrag des Galerie-Koordinators: drei Posen in Draufsicht mit allen vier Beinen, gleiche Größe je Zelle, flacher Grund. Drei Tiere: Kriegshund (Funktionsfarbe #2b3350), Wolf, Maultier mit Lasten. Blätter `out/vierbeiner_28_aschekrone.png` (alle Wege) und `out/vierbeiner_28_zielgröße.png`, Galerie-Gruppen `sprite-aschekrone-kriegshund`, `-wolf` und `-maultier`.

- **Von genau oben verdeckt der Rumpf die Beine.** Seitlich aus dem Umriss bestellt ("in every cell all four legs stick out clearly beyond the outline of the body, the two front legs at the left and right of the chest and the two hind legs at the left and right of the hips, each leg one short thick shape ending in a round paw") zeigte Krea sie bei Hund und Wolf in allen zehn Bögen. Vorher saß der Hund ohne sichtbare Beine.
- **Krea malt Stand, Trab, Stand:** in allen sechs Hund- und Wolfbögen der ersten Runde wiederholte die dritte Zelle den Stand. Von oben ist ein Tier links und rechts gleich gebaut, der Trab mit dem anderen Beinpaar ist also genau das Spiegelbild der mittleren Zelle. Workflow 18 hat dafür einen zweiten Ausgang `sprite-gespiegelt` (Kernknoten ImageCrop, ImageFlip, ImageStitch, setzt 1536x1024 voraus). Nur für Figuren ohne einseitige Ausrüstung, bei Schwert oder Fackel in einer Hand wechselte sonst die Hand.
- **Qwen-2512 taugt nicht für Draufsicht-Sprites:** in Qualitätseinstellung mit demselben Gerüst zeigte keiner der fünf angesehenen Bögen eine Draufsicht, der sechste hat dieselben Konturwerte. Hunde und Wölfe standen aufrecht auf den Hinterbeinen, dazu Vorder- und Rückansichten, beim Maultier beides im selben Bogen. Dicke Konturen (Randhelligkeit 0,13 bis 0,18 des Innern), ein grüner Rahmen mit Vignette, 136 bis 172 s je Bogen.
- **Qwen-Edit mit einer Zweibeiner-Vorlage** nicht erneut getestet, am Vormittag standen 4 von 4 Hunden aufrecht.
- **Offen: das Maultier.** Die Lasten verdecken die Vorderbeine in allen vier angesehenen Bögen, auch mit dem Satz, die Last sei schmaler als die gespreizten Beine. **Gelöst am 2026-10-02:** Nichts darf seitlich herabhängen. "On top of its back sits a single small square crate centered on the spine, half as wide as the body; no saddlebags and nothing hanging down the sides" zeigte die Vorderbeine neben der Brust in 2 von 2 Bögen, die Last auf der hinteren Rückenhälfte in 1 von 2, ein langes Bündel längs der Wirbelsäule in 0 von 2 (Krea malte es quer). Gruppe `sprite-aschekrone-maultier`, Vertreter ist der gespiegelte Bogen.
- **Größe und Grün:** die Tiere füllen 78 bis 94 Prozent der Bildhöhe (Gate-Figuren 48 bis 54), berühren die Zellränder aber nicht. Der Atlas des Spiels skaliert ohnehin auf die Körperbreite. Das Grün schwankt je Bogen: bei Wolf und Maultier 9 bis 36 / 156 bis 167 / 61 bis 71, bei den Zweibeinern um 76/172/80. Den Farbschlüssel je Bogen am Rand messen.
- **Bei Zielgröße** (32 px Breite) lesen Hund und Wolf als Tier von oben. Die Beine sind kleine Höcker, die Trabphasen kaum zu unterscheiden, wie bei den Zweibeinern im Haufen.
- 23 Entwürfe liegen im Papierkorb der Galerie, darunter die beiden beinlosen Hunde vom Vormittag.

## Nahtlose Kachel aus der Aschekrone-Textur, Workflow 19 (2026-09-28)

Fünfte Art aus dem Plan Spielegrafik. Auftrag: die Hintergrundtextur (`referenz-grund.png`, im Renderer 2x2 gespiegelt) als echte nahtlose Kachel, geprüft als 3x3-Wiederholung. Blätter `out/kacheln_28_3x3_hell4.png` und `out/kacheln_28_ausschnitt_hell4.png` (1:1 aus 2x2 Kacheln mit Kreuzmitte und Kachelecke), beide vierfach aufgehellt.

- **Der Master selbst ist fast nahtlos:** der Pixelsprung über die Kachelgrenze liegt bei 1,51 und 1,70 gegen 1,13 im Innern. Vierfach aufgehellt ist die Grenze trotzdem als Linie zu sehen.
- **Das Nahtkreuz mit Z-Image neu rechnen (der geplante Weg) hinterlässt ein Gitter.** Um die halbe Kante verschoben, Kreuz maskiert (SetLatentNoiseMask), zurückgesetzt: bei denoise 0.6, 0.85 und 1.0, je ohne und mit Stylized-Textures-LoRA 0.8, war das Kreuz in allen sechs Fassungen zu sehen. Ohne LoRA wurde das Band heller und körniger (bei 1.0 Streuung 4,43 gegen 2,22), mit LoRA stimmten die Zahlen fast, die Linien blieben.
- **Die Qwen-2512 Fun ControlNet Union 2602 lädt in ComfyUI 0.36 nicht.** `ModelPatchLoader` bricht mit "cannot access local variable 'model'" ab. Die Datei trägt Schlüssel `control_blocks.*`, der Lader kennt für Qwen nur die DiffSynth-Blockwise-Fassung und die Fun-Fassung für Z-Image. Der Download vom 28.09. (3,3 GB) ist damit ohne neueres ComfyUI oder Zusatzknoten nicht nutzbar.
- **Gewonnen hat eine Rechnung ohne Modell:** verschieben und im Kreuz das unverschobene Original überblenden, das genau dort durchgehend ist. Linear (Workflow 19, Maske aus ImageShift mit Randband 80 und Unschärfe 60): nahtlos (Grenzsprung 1,16 und 1,14 gegen 1,01). Im Übergang fehlt dafür ein Fünftel des Feinkorns (1,39 gegen 1,74). Varianzerhaltend nach Heitz und Neyret 2018 (`scripts/seamless_tile.py`): nahtlos (1,31 und 1,26 gegen 1,16), Korn gleich (1,79 gegen 1,77), Helligkeit gleich. Vierfach aufgehellt ist bei beiden keine Naht und kein Kreuz zu sehen.
- **Vertragswerte der Skript-Kachel:** Mittel 17,6/15,6/13,1 (Master 17,5/15,5/13,0), hellster Wert 65 wie beim Master, Kantenhärte wie beim Master, keine Flecken ab 8 px bei 390 px. Auf der dunkleren Vorlage `vorlage-grund-dunkel.png` dasselbe Bild (Korn 0,99 gegen 1,02).
- **Neue Texturen aus Text taugen nicht ohne Nachrechnen:** Z-Image mit Stylized-Textures-LoRA 0.8 und dem Vertragsprompt lag mit 45/38/30 und 65/59/54 weit über dem Soll, eine der beiden war trotz des LoRA-Gerüsts "seamless tileable" nicht nahtlos (Grenzsprung 9 bis 12 gegen 1,3). Helligkeit rechnen statt bestellen, wie bei den Gründen am 27.09.
- **Ergebnis für das Spiel:** `out/kachel_28_aschekrone_grund.png` und `out/kachel_28_aschekrone_grund_dunkel.png` (Skript).

## Blinder Fototest Architektur, Produkt, Handwerk, Portrait (2026-09-28, Auftrag des Galerie-Koordinators)

Anlass: Z-Image ist Erste Wahl für diese vier Bereiche, belegt nur durch das A/B gegen FLUX-schnell vom 27.08. (von einem Agenten beurteilt). Gegen Krea und Qwen nie getestet, im Landschaftstest lag Z-Image hinten. Dieser Abschnitt hält nur den Aufbau fest, das Urteil fällt der Nutzer blind im Duell. **Ergebnis (Duelle bis 2026-09-29, Entscheid 2026-10-03):** Siege je Prompt Qwen-2512 in Qualitätseinstellung 7, Krea 5, Z-Image 3, CyberRealistic 1, in den blinden Paaren Qwen 10:1. Architektur Qwen 3 von 4, Produkt und Handwerk Qwen 2 von 4, Portrait Krea 4 von 4. In 25 von 48 Paaren hat der Nutzer vor der Entscheidung aufgedeckt, ganz blind blieben 5 Prompts. Entscheid des Nutzers: Architektur auf Qwen, Produkt, Handwerk und Portrait auf Krea, weil Krea über den LoRA-Stapel viel Spielraum hat. Der Stapeltest je Bereich folgt.

- **Aufbau:** 16 neue Prompts in vier Bereichen mit je vier Motiven (Architektur: Fassade, Innenraum, historisches Gebäude, Glaskonstruktion; Produkt: Keramik, Glas mit Spiegelungen, Elektronik, Textil; Handwerk: Werkbank, Hände bei der Arbeit, Schaltschrank, Holzbearbeitung; Portrait: Studio, Umgebung, älterer Mensch, zwei Personen), englisch, 108 bis 118 Wörter, Vorder-, Mittel- und Hintergrund, Licht und Brennweite, keine Qualitätsformeln, alle SFW. Je Prompt ein Seed (8201 bis 8216) und eine Größe für alle Modelle: 1344x768, die drei Einzelportraits 768x1344.
- **Modelle wie im Landschaftstest:** Z-Image (Detail 0.3), CyberRealistic Z-Image (Detail 0.3), Krea (Detail 0.5, sonst alle LoRAs 0), Qwen-2512 mit Turbo-LoRA 0.0, 30 Steps, cfg 4.0. Blockweise je Modell, jedes Bild genau einmal. Dateien `fototest_NN` mit zufälliger Nummer, ohne Gruppe. Zuordnung und Prompts: `out/fototest28_zuordnung.csv` und `out/fototest28_prompts.py`. Ob der Renderer die Kachel statt des Spiegelns nimmt, entscheidet das Spiel. In der Galerie liegen die beiden Kacheln aus Workflow 19, zehn Zwischenstände im Papierkorb.

## Zehen und Finger in Stufe 2 von JANKU (2026-09-28 bis 2026-09-30)

Anlass: Der Nutzer meldete, Stufe 2 (`janku-detail`) mache aus fünf korrekten Zehen oft sechs, dazu doppelte Körpermerkmale. Die Zählung machte der Nutzer über Markierungen in der Galerie. Meine eigene Zehenzählung an Ausschnitten taugte nicht: klein überall fünf, groß teils sechs.

- **Die Fehlerbilder stammen aus der alten Stufe 2.** 9 der 10 markierten Bilder entstanden am 24. und 25.09. mit doppelter Größe, denoise 0.5 (einmal 0.35) und karras, also 4 MP in einem Durchgang. Seit dem 25.09. rechnet `janku_t2i` nach Autorwerten 1,5-fach bei 0.4 mit simple.
- **Harmloser Test, 54 Bilder:** Stufe 1 von `janku_t2i` hatte in 3 von 6 Motiven falsche Zehen. Die heutige Stufe 2 reparierte alle drei, euler 0.4 und euler_ancestral 0.3 ebenso, euler 0.3 ließ zwei stehen. Der Galerieweg über `illustrious_t2i` mit Kacheln (2-fach, 0.25) blieb durchgehend fehlerfrei. Keine Einstellung hat einen Zeh dazuerfunden.
- **Nachgerechnet auf den 9 betroffenen NSFW-Bildern** (gleiche Stufe 1, Stufe 2 neu): heutige Einstellung euler_ancestral 0.4 in 0 von 9 mit Fehler, euler 0.4 in 1 von 9, euler_ancestral 0.3 in 3 von 9. Einschränkung: auf mehreren Bildern waren keine Füße zu sehen.
- **Folge:** `janku_t2i` bleibt wie seit dem 25.09. Weniger Stärke in Stufe 2 schadet: sie lässt Fehler aus Stufe 1 stehen und baute hier selbst welche. Das nicht-ancestrale euler brachte keinen Vorteil.

## Qwen-2512: Turbo gegen Qualitätseinstellung, blind (2026-09-30, Auftrag des Galerie-Koordinators)

Anlass: Qwen ist seit dem Foto- und dem Landschaftstest Erste Wahl für Fotorealismus und Landschaft, beide Tests liefen in der Qualitätseinstellung (rund 100 s je Bild). Offen war, ob die Turbo-Fassung der Familienvorlage (rund 13 s) mithält. Das Urteil fällte der Nutzer blind im Duell.

- **Aufbau:** 12 neue Prompts (Architektur 2, Produkt 2, Handwerk 2, Landschaft 6), keine Porträts. Je Prompt zwei Bilder mit gleichem Seed in 1344x768: L = Graph von `qwen_2512_landschaft` (Turbo-LoRA 0, 30 Steps, cfg 4), T = `qwen_2512_t2i` (Turbo-LoRA 1.0, 2 Steps, cfg 1). Dateien `qtest_NN` mit zufälliger Nummer, Paare als Handgruppen `qtest-p01` bis `qtest-p12` (gleicher Prompt mit gleichem Modell bündelt die Galerie nicht von selbst). Zuordnung `out/qtest_zuordnung.csv`.
- **Ergebnis: L gewinnt 8 von 12.** Architektur 1:1, Produkt 2:0, Handwerk 1:1, Landschaft 4:2. Alle Urteile ohne Aufdecken.
- **Renderzeit:** L im Mittel 107 s, T 15,7 s (ungestört 105 s gegen 12,5 s, Faktor 8,4).
- **Folge:** Für Foto und Landschaft bleibt die Qualitätseinstellung. Turbo nur für schnelle Entwürfe: in einem Drittel der Paare lag es vorn, ist also nicht grundsätzlich schlechter. Die ältere Aussage, 50 Steps ohne LoRA brächten keinen sichtbaren Gewinn, gilt für Foto und Landschaft nicht.

## NSFW Anime: Altersangaben im Tag-Prompt ziehen Illustrious Realism ins hohe Alter (2026-09-30)

Anlass: Vergleich JANKU gegen Illustrious Realism v4 für das Ziel NSFW Anime, nur mit Bestandsprompts, die ausdrücklich Erwachsene nennen. Für Illustrious reichte der Bestand nicht (34 Prompts nur mit „1girl“ ohne Alter), deshalb eine zweite Runde mit „25 years old woman“ direkt hinter „1girl“. Nutzerbefund nach Sichtung: alle Illustrious-Bilder schlecht, statt junger Frauen Menschen über 60. Die zweite Runde wurde nach 18 von 36 Bildern gestoppt.

- **Beobachtet (Nutzer):** Illustrious Realism v4 rendert mit „25 years old woman“ ältere Menschen über 60. Runde 1 gab Illustrious ebenfalls „22 years old woman“ und „mature female“. JANKU v5 setzte dieselben Altersangaben in seinen Originalen um.
- **Vermutung, nicht gemessen:** In Danbooru-trainierten Modellen zieht das Token „old“ aus „years old“ zum Alter, „mature female“ ist dort ein Tag für ältere Frauen.
- **Regel:** Bei Illustrious Realism keine Altersangabe mit „years old“ und kein „mature female“ in den Prompt. Was stattdessen verlässlich Erwachsene ergibt, ist nicht getestet. Die Sicherung gegen kindliche Darstellung bleibt die Negativ-Einbettung `embedding:lazyloli`, die die Galerie bei jedem expliziten SDXL-Auftrag vorn einsetzt.
- **Bestätigt (Nutzer, 30.09.):** Mit „22 years young woman“ statt „years old“ kamen Frauen im passenden Alter, es lag also am Token „old“. Ohne Altersangabe mit nur „1girl“ kamen bisher ebenfalls Frauen heraus. Die Altersangabe ist damit kein Muss, die Sicherung bleibt `embedding:lazyloli` im Negativ.
- **Der Modellvergleich ist damit nicht aussagekräftig.** Zuordnung `out/nsfwanime_zuordnung.csv`, Bilder `galerie/2026-09-30/nsfw-detail_00001` bis `00025`.
- **Dazu die zweite Stufe (Nutzerbefund):** Der Upscale an den Illustrious-Bildern machte viel kaputt. Ursache: Illustrious Realism hat nur einen UI-Workflow und keine API-Vorlage, die Galerie rechnete es deshalb über `illustrious_t2i`, die Vorlage von WAI. Das heißt WAI-Werte (40 Steps, cfg 7, euler_ancestral, normal) statt der Kartenwerte (25 Steps, cfg 6, dpmpp_2m_sde, karras, clip skip 2), und als zweite Stufe UltimateSDUpscale 2-fach mit 4x-UltraSharp bei denoise 0.25 in 1024er-Kacheln, jede Kachel mit dem ganzen Prompt. Der eigene Workflow des Modells rechnet stattdessen einen Detailpass auf etwa 1152x1664. Derselbe Fehlertyp wie bei JANKU vor dem 29.09. (fehlte in REGEN_TEMPLATES, lief ohne seine Stil-LoRAs): Ein Modell ohne eigene API-Vorlage erbt Werte und zweite Stufe eines anderen Modells seiner Familie. Vor jedem Test eines Modells prüfen, über welche Vorlage die Galerie es rechnet.

## Illustrious Realism: zweite Stufe im Blindtest (2026-09-30, Auftrag des Galerie-Koordinators)

Anlass: Nach dem Befund oben rechnete die Galerie Illustrious Realism nur noch in der Basisstufe der neuen Vorlage `illustrious_realism_t2i`. Offen war, ob eine zweite Stufe besser ist. Das Urteil fällte der Nutzer blind im Duell.

- **Aufbau:** 3 jugendfreie Bestandsprompts (Schreiner mit Hobel, Frau im Café, Zauberin mit Kugel), je gleicher Seed, 3 Varianten als eigene Graphen: A nur Basis (25 Steps, cfg 6, dpmpp_2m_sde/karras, clip skip 2, 832x1216). B Basis plus Hires-Zweig des UI-Workflows: 4x-UltraSharp statt des gelöschten 4x_NMKD-Superscale, danach 1xSkinContrast, lanczos 0,32, Vielfaches von 64 (1024x1536), KSampler 20 Steps, cfg 7, dpmpp_2m_sde/karras, denoise 0,45, Seed fest 10. C Basis plus FaceDetailer für Gesicht (face_yolov8m) und Hände (hand_yolov8s) mit Knoten-Standard (euler/simple, cfg 8, denoise 0,5). Dateien `itest_NN`, Handgruppen `itest-p01` bis `p03`, Zuordnung mit Ist-Werten `out/itest_zuordnung.csv`.
- **Ergebnis: B gewinnt 3 von 3,** jeweils gegen A und C. Bei der Zauberin stand B zusätzlich im alten Prompt-Vergleich und schlug dort auch JANKU und WAI.
- **Renderzeit (warm):** A 7 s, B 19 s, C 13 bis 25 s.
- **Folge:** `illustrious_realism_t2i` ist seit dem 30.09. zweistufig genau wie B (SAVE Basis, SAVE_DETAIL Hires), Sicherung der reinen Basisvorlage als `.bak-20260930`. FaceDetailer bringt hier keinen Vorteil, auf JANKU malte er schon am 24.09. Male ins Gesicht.


## Hand-Detailer auf JANKU-Stufe 2 (2026-10-02)

Frage: Hilft ein Hand-Detailer hinter Stufe 2 von `janku_t2i`, wie ihn die A1111-Vorlagen des Kimono-Autors als zweiten ADetailer fahren? FaceDetailer-Knoten mit `bbox/hand_yolov8s.pt`, denoise 0.4, guide_size 512, Schwelle 0.3, vier harmlose Motive mit Händen (Winken, Tasse mit beiden Händen, Victory-Zeichen, verschränkte Finger auf dem Tisch), je zwei Seeds. Ausschnitte über den Hand-Detektor, Skript `hand_blatt.py` im Scratchpad der Session 50a253bb.

- **Kaum Wirkung (Augenschein des Agenten, das Urteil des Nutzers steht aus):** bei 14 Händen sind die Fassungen mit und ohne Detailer fast gleich. Richtige Hände bleiben richtig, verschränkte Finger bleiben in beiden Fassungen ein Knäuel. Ein dritter Durchgang lohnt sich für `janku_t2i` danach nicht.
- **Nebenbefund:** Kaffeebecher bekamen ein grünes Rundlogo, das an eine bekannte Kaffeekette erinnert. Für Kundenbilder Markenlogos ins Negativ setzen.


## NSFW Anime: „oiled“ und der Stilvergleich (2026-10-03)

- **„oiled“ meiden (Nutzerbefund):** In JANKU und Illustrious Realism erzeugt „oiled“ (etwa „oiled skin“, „oiled butt“) keine glänzende Haut, sondern zähflüssige, schlecht verteilte Substanz auf der Haut. In Testprompts streichen, für Glanz eher „shiny skin“ prüfen. Die Galerie warnt seit dem 03.10. im Dialog (suggest.avoid beider Karten).
- **„open mouth“ in Illustrious Realism meiden (Nutzerbefund):** führt häufig zu unschönen, unnatürlich offenen Mündern. Die Galerie warnt seit dem 03.10. im Dialog (suggest.avoid der Karte).
- **WAI malt Text an den oberen Rand ohne Text-Negativ (Nutzerbefund):** Die Galerie rechnete WAI mit dem kurzen Negativ der Karte („bad quality, worst quality, worst detail, sketch, censor“), mehrere NSFW-Bilder trugen Text am oberen Rand. Karte und `illustrious_t2i.api.json` tragen seit dem 03.10. dasselbe Negativ wie die Vorlage plus „text“ (Sicherung `.bak-20261003`).
- **Kein Stilvergleich im Duell:** JANKU gegen Illustrious Realism ist Anime gegen halbrealistisch. Der Nutzer brach das Duell ab („unpassend“), ein Sieg sagt dort nichts über die Qualität. Für das Ziel „NSFW Anime“ treten JANKU und WAI gegeneinander an (gleicher Prompt, gleicher Seed, je Präfix der Karte), Zuordnung `out/nsfwanime3_zuordnung.csv`.

## Urteile des Nutzers vom 2026-10-03: Nachbau-Rezepte, Promptlänge, Detail, Upscaler, Sticker

Ausgelesen aus Galerie-Urteilen (Duell und S), Sternen, Mängeln und Notizen.

- **JANKU-Rezepte an Civitai-Vorlagen mit Füßen und Händen** (Gruppen `civ<id>`): Stufe 1 in 832x1216 mit der heutigen Stufe 2 (`civ-832-*`) gewann zwei Anatomie-Gruppen, das Original-Rezept stand dort gleichauf. Das Rezept vom 24.09. (`civ-2409-*`, ebenfalls 832x1216) gewann eine. Der erste Nachbau in 1024x1536 verlor jede Gruppe mit sechs oder sieben Zehen, doppelten Füßen und zwei Daumen. Das Galerie-Rezept ohne Stapel (`civ-gal-*`) war zweimal fehlerhaft. Ein Motiv (105743892) scheiterte in allen Rezepten. Folge: `janku_t2i` rechnet Stufe 1 in 832x1216.
- **FaceDetailer bleibt draußen:** der Sieger des Rezepts vom 24.09. bei 103421842 bekam einen Stern wegen Flecken auf der Wange, wie schon am 24.09. Das Original-Rezept mit TRT war dort laut Nutzer grafisch besser, nur die Hand an der Geige stimmte nicht.
- **Promptlänge** (Gruppen `prompttest-*`): ausführliche Prompts gewannen 7 von 9 Gruppen, bei Pasta und Schreiner auf allen drei Modellen. Bei Weinberg gewannen Qwen und Z-Image knapp. Die Prompt-Erweiterung durch Qwen3-VL gewann auf Krea zwei von drei Gruppen (Pasta, Weinberg) und stand beim Schreiner gleichauf. Die Masterpiece-LoRA auf Krea gewann nie, sie stand nur gleichauf. Folge: Erweiterungsschalter für Workflow 10 und 13 bauen, Masterpiece nicht in den Standard.
- **Detail-Standard** (Gruppen `mitlora-*`): auf Z-Image und CyberRealistic gewann Detail 0.6 drei von vier beurteilten Gruppen, das Original ohne LoRA eine (dort gleichauf mit 0.3), 0.3 gewann nie. Folge: `DETAIL_LORA` in 00 und 07 auf 0.6. Auf Krea gewann einmal Detail 0.5 und einmal der volle Stapel (Detail 1.0, Afterlight 0.35, Warm 0.5).
- **Anime-Upscaler** (Gruppen `upscaler-*`): `RealESRGAN_x4plus_anime_6B` gegen `RealESRGAN_x4plus` in Stufe 2 von JANKU 2:2. Es bleibt x4plus. Korrektur: die kürzere Laufzeit der 6B-Läufe kam aus dem Zwischenspeicher von ComfyUI (gleiche Stufe 1 direkt davor), nicht vom Upscaler.
- **Krea-Stapel je Bereich** (Gruppen `kreastapel-*`): erst 3 von 12 Gruppen beurteilt, zweimal gewann die Fototest-Fassung mit Detail 0.5, einmal Detail 1.0. Bei der Holzbearbeitung hatten alle vier Fassungen Logikfehler.
- **Sticker für den Druck:** die drei Gruppensieger mit `upscale.py` 2-fach bei denoise 0.15 auf 2432x1664 gerechnet, Schrift und Motiv blieben gleich. Reicht für A4 quer mit gut 200 dpi.

## Urteile des Nutzers vom 2026-10-03, Teil 2: Krea-Stapel, JANKU gegen WAI, Original-Rezepte, Pose

- **Krea-Stapel je Bereich, alle 12 Gruppen `kreastapel-*`** (Porträts und Elektronik hat der Nutzer in den Prompt-Vergleichen des Fototests beurteilt, nicht in den Handgruppen): Porträt: Standard (Detail 0.5) gewann 4 von 4, Detail 1.0 stand viermal gleichauf. Produkt: Realism +0.5 gewann 2 (Keramik, Elektronik), Detail 1.0 1 (Glas), Standard 1 (Textil). Handwerk: Detail 1.0 gewann 2 (Werkbank, Schaltschrank), Standard 1 (Hände), bei der Holzbearbeitung hatten alle Fassungen Logikfehler. Warm Light gewann nie.
- **Daraus wird noch kein Standard.** Der Nutzer will erst mehr testen: „es gibt noch deutlich mehr LoRAs, Afterlight erzeugt auch super Ergebnisse, aber situationsabhängig“. Zweiter Stapeltest mit 18 Motiven in fünf Lichtsituationen, Plan `out/_tests/stapel2/stapel2-plan.md`. Bis dahin bleiben Ziel und Karte bei Detail 0.5.
- **JANKU gegen WAI für NSFW Anime, neu gerechnet** (26 Gruppen `janku-nsfw-*`, Prompts und Seeds vom 24.09., JANKU im Rezept vom 03.10.): WAI gewann keine beurteilte Gruppe. Die JANKU-Fassung vom 24.09. gewann 10, die neue 7, 9 standen gleichauf, 10 Gruppen sind offen. JANKU bleibt für NSFW Anime. Die Bilder hat der Agent nicht angesehen.
- **Original-Rezepte der Civitai-Vorlagen mit den neu geladenen LoRAs** (`civ-orig-*`): gewannen bei 95747669 (TRT) und 98777848 (Xu Er), verloren 97612851 und 97612841 gegen den ersten Nachbau, bei 103810490 gleichauf.
- **Pose der Vorlage vor dem Nachbau prüfen:** Gewichte ab 1,5 auf Pose oder Bildausschnitt und widersprüchliche Wünsche (auf einem Bein stehen, Fußsohle zur Kamera, extreme Nahaufnahme, dazu Ganzkörper) scheitern in jedem Rezept: 105743892 brach in zehn Nachbauten mit fünf Rezepten. Die eigene Fassung des Nutzers mit sitzender Pose und Gewichten bis 1,4 wurde sehr gut, seine Notiz hatte darauf verwiesen. Notizen mit Verweis auf ein gutes Bild sofort auswerten: das Bild ins Bündel der Vorlage nehmen, als Vertreter setzen und seinen Prompt mit der Vorlage vergleichen. Das Bündel `civ105743892` trägt seit dem 03.10. Vorlage und diese Fassung, die 18 kaputten Nachbauten liegen im Galerie-Papierkorb.

## Ausformulieren-Schalter in 10 und 13, Ladezustand und Pixelgleichheit (2026-10-03)

- **Aufbau:** Nur die Oberflächen-Workflows 10 und 13 bekommen den Schalter „Ausformulieren?“ (Vorgabe aus), gebaut von `api_to_ui_workflow.py` (`erweiterung_einbauen`). Die API-Vorlagen bleiben unverändert, sie rechnen auch für die Galerie. Prompt im Textknoten „Prompt“, TextGenerate mit Qwen3-VL aus dem CLIP-Loader und dem System-Prompt der offiziellen Krea-Vorlage (`workflows/krea2_expansion_system.txt`), greedy, max_length 512. ComfySwitchNode wertet lazy aus, bei ausgeschaltetem Schalter rechnet TextGenerate nicht. Gespeichert wird weiter über SaveImage, das PNG trägt deshalb nur den Kurzprompt (Knoten „Prompt“) und den Graphen, die Galerie markiert solche Bilder als in ComfyUI ausformuliert. Den Text von TextGenerate schreibt kein Kernknoten ins PNG, SaveImage nimmt nur, was vor dem Lauf feststeht.
- **Image Saver verworfen:** comfyui-image-saver schreibt den verwendeten Prompt als A1111-Chunk `parameters` (getestet mit `download_civitai_data` aus, leerem `modelname`, ohne `easy_remix`). Seine Dateinamen heißen aber `krea.png`, dann `krea_01.png`, nicht `<name>_NNNNN_.png`, und er zählt nur Dateien mit der Bildendung. Die `.papierkorb`-Platzhalter der Galerie halten den Zähler von ComfyUI fest, damit ein neues Bild nie den Namen eines weggeworfenen erbt. Ein zweites Namensschema in denselben Ordnern war dem Galerie-Koordinator zu riskant.
- **Gemessen:** Aus 24 Wörtern wurden 106, der Lauf dauerte 33 s statt 22 s. Mit Schalter aus ist das Bild pixelgleich zur API-Vorlage mit gleichem Prompt und Seed.
- **Pixelgleich nur bei gleichem Ladezustand:** Derselbe Krea-Graph mit gleichem Seed wich nach anderen Aufträgen (andere LoRA-Stärken, TextGenerate mit dem Sprachmodell) im Mittel um 5 bis 15 von 255 ab, sichtbar in den Details. Nach `POST /free` mit `unload_models` und `free_memory` waren zwei Läufe wieder pixelgleich. Für Pixelvergleiche deshalb vor jedem Lauf `/free`. Ein Seed hält das Bild also nicht fest, wenn dazwischen andere Aufträge liefen. Das betrifft auch Neu generieren.

## Nahttest Stufe 2, Ultimate SD Upscale (2026-10-03, Auftrag des Nutzers über den Galerie-Koordinator)

Anlass: Der Nutzer sieht in Stufe-2-Bildern von Illustrious und WAI schwache gerade Streifen nahe der Mitte. Alle Vorlagen rechnen USDU mit `seam_fix_mode` None, `mask_blur` 8, `tile_padding` 32 und euler_ancestral. Plan `out/_tests/nahttest/nahttest-plan.md`, das Urteil steht aus.

- **Aufbau:** Nur Stufe 2 neu, LoadImage mit `<pfad> [output]` auf das vorhandene Basisbild, USDU sonst wie im Original. 4 Bilder (3 explizit, d sicher) je 5 Varianten: V0 Kontrolle, V1 Band Pass, V2 Half Tile + Intersections, V3 mask_blur 16, tile_padding 64, euler, V4 wie V3 mit Band Pass. `seam_fix_denoise` 0.35 statt der Knotenvorgabe 1.0, so wie im Original-Skript für A1111. Dateinummern je Bild gemischt, Gruppen `nahttest-a` bis `d`, Zuordnung `out/_tests/nahttest/nahttest_zuordnung.csv`.
- **Rechenzeit Stufe 2 (Median):** V0 47 s, V3 47 s, V4 63 s, V1 65 s, V2 87 s.
- **Messung an d** (Sprung an der Kachelgrenze geteilt durch den Median der Nachbarspalten, 1,0 unauffällig): Das Original und V0 zeigen keine messbare Naht (0,81 bis 1,02), V2 und V3 bleiben neutral. Band Pass hebt den Sprung genau an den Grenzen (V1 bis 1,35, V4 bis 1,17). Die Messung trennt schwach, weil d schon im Original keine Naht hatte.
- **Ergebnis Nutzer:** trennte nichts, jede Variante gewann ein Bild, an keinem Testbild stand eine Streifen-Notiz. Die Basisbilder waren nach Sternen gewählt, nicht nach der Streifen-Notiz des Nutzers.
- **Nahttest 2** (Plan `out/_tests/nahttest2/nahttest2-plan.md`): die drei Bilder mit der Notiz „leichte Streifen durch die Bildmitte“, Varianten V0, V2, V3 und V5 (eine Kachel so groß wie das Ausgabebild), dazu das Original als Anker (Kopie unter blindem Namen, weil zwei Originale schon in Handgruppen stecken, die das Eintragen sonst verschmölze). Eine Kachel lief auch bei 2176 × 2176 ohne VRAM-Probleme und war am schnellsten: V5 26 bis 33 s, V0 38 bis 57 s, V3 37 bis 55 s, V2 92 bis 142 s.
- **Ergebnis Nahttest 2 (Nutzer, 04.10.):** Die Streifen kamen mit den heutigen Werten wieder: V0 trug bei Bild a die Notiz „streifen“, wie das Original. Ohne Streifen-Notiz blieben V2, V3 und V5. Sieger: a V2 (schlug auch das Original), b V5, c eine Variante von V5 mit anderem Seed, die der Nutzer in der Galerie erzeugt hatte (V2 und V3 hatten dort Mängel an den Händen).
- **Folge:** `illustrious_t2i` rechnet Stufe 2 seit 04.10. in einer Kachel: `tile_width` und `tile_height` 4096, `force_uniform_tiles` aus (Sicherung `.bak-20261004`), damit auch Workflow 06. Eine feste Kachelgröße mit `force_uniform_tiles` an hätte das Bild auf Kachelgröße hochgerechnet, mit aus bleibt der Ausschnitt in Originalgröße. Gemessen am größten Galerieformat 1920 × 3328 (6,4 MP): 44 s, keine Speicherprobleme, keine messbare Naht. Größere Ausgaben sind ungetestet. `upscale.api.json` (Z-Image) bleibt bei Kacheln, dort ist nichts getestet.

## Krea-Stapeltest 2, Phase A: Afterlight wird Standard (2026-10-03, Nutzerentscheid)

Plan `out/_tests/stapel2/stapel2-plan.md`, Zuordnung mit Ist-Werten `out/_tests/stapel2/stapel2_zuordnung.csv`. 18 Foto-Motive (je 6 Produkt, Handwerk, Porträt) in fünf Lichtsituationen, je Motiv ein Seed, Graph über `create_build` der Galerie, blind im Duell beurteilt. Varianten: A1 Detail 0.5 (alter Standard), A2 Realism +0.5, A3 Detail 1.0, A4 Afterlight 0.35, A5 Afterlight 0.7, A6 Warm 0.5 (nur Abend und Fensterlicht), alle außer A3 auf Detail 0.5.

- **Sieger je Gruppe:** A4 Afterlight 0.35 neunmal, A5 Afterlight 0.7 fünfmal, A3 Detail 1.0 zweimal (Handwerk im Tages- und Kunstlicht), A2 Realism zweimal (Produkt im Abend- und Fensterlicht), A1 und A6 nie. Direkt A1 gegen A4: 9:0.
- **Nach Licht:** Tageslicht Afterlight 5 von 6, Gegenlicht 3 von 3 (alle 0.35), Abend, Fensterlicht und Studio je zwei von drei. Die frühere Regel, Afterlight bei Tageslicht niedrig zu halten, ist damit überholt.
- **Folge:** `krea2_turbo_t2i` trägt Detail 0.5 und Afterlight 0.35 (siehe models.md), damit auch Workflow 10 und alle Krea-Ziele der Galerie außer Kinobanner. Realism +0.5 bleibt Kandidat für Produkte im Abend- und Fensterlicht. Phase B mit sieben neuen Krea-LoRAs tritt gegen den neuen Standard an.

## Krea-Stapeltest 2, Phase B: neue LoRAs gegen den Standard (2026-10-04, Urteil des Nutzers)

Plan `out/_tests/stapel2b/stapel2b-plan.md`, Zuordnung `out/_tests/stapel2b/stapel2b_zuordnung.csv`. Dieselben 18 Motive und Seeds wie in Phase A, je Gruppe der Standard (Kopie von A4: Detail 0.5, Afterlight 0.35) gegen die neuen LoRAs im Knoten STYLE_LORA, Trigger vorn im Prompt.

- **Sieger je Gruppe:** PureLens 1.0 (Trigger `purelens`, zum Standard) zehnmal, UltraReal 0.7 viermal, Background Detail, Skin Detail Slider und AfterHours je einmal, der Standard selbst einmal.
- **Nach Bereich:** Produkt PureLens 4 von 6 (sonst UltraReal), Handwerk PureLens 5 von 6 (sonst Background Detail), Porträt ohne klaren Sieger (UltraReal 2, PureLens, Skin Slider, AfterHours und Standard je 1).
- **Direkte Duelle gegen den Standard** (nicht jedes Paar wurde verglichen): PureLens 4 Siege, 2 Niederlagen, 3 gleich; UltraReal 4:2; Background Detail 3:0; Skin Slider 2:0 bei 2 gleich; Skin Texture 0:1; AfterHours 1:2; God Rays einmal gleich.
- **Folge (Nutzerentscheid 05.10.):** PureLens wird Standard für Produkt und Handwerk über die eigene Vorlage `krea2_produkt` mit Trigger in `_meta.trigger`, siehe models.md. Porträt bleibt beim Standard ohne PureLens.

## Lesefehler beim Laden der Krea-Datei (2026-10-05)

- **Einmaliger Aussetzer:** Das erste Probebild mit `krea2_produkt` brach im KSampler mit „HostBuffer.read_file_slice failed“ ab. Das ComfyUI-Log zeigt den Grund: Beim Streamen der 13-GB-Datei `krea2_turbo_fp8_scaled` scheiterte ein Windows-Lesezugriff bei 11,7 GB (`GetOverlappedResult failed`, Bibliothek comfy_aimdo). Derselbe Auftrag lief direkt danach fehlerfrei. Bei diesem Fehler einmal wiederholen, erst bei Wiederholung an der Datei oder am Laufwerk suchen. `comfy_generate.py` meldet solche ComfyUI-Fehler seit dem 04.10. sofort mit Knoten und Meldung, statt bis zum Timeout zu warten.
