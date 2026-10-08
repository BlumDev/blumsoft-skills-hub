#!/usr/bin/env python3
"""Wandelt einen API-Workflow (wie in workflows/*.api.json) in das UI-Format um.

ComfyUI kennt zwei Formate: den API-Graphen (was die HTTP-Schnittstelle nimmt) und
den UI-Graphen (was die Oberfläche als Knoten mit Position und Widgets zeigt).
Unsere Skript-Workflows liegen im API-Format und sind in der Oberfläche deshalb
nicht direkt anklickbar. Dieses Skript baut daraus einen UI-Graphen: Socket- und
Widget-Reihenfolge kommen aus /object_info des laufenden Servers, das Layout aus
einer Spalten-Anordnung nach Graph-Tiefe.

Aufruf:
  python api_to_ui_workflow.py --in workflows/sdxl_t2i.api.json --out ziel.json
  python api_to_ui_workflow.py --all --out-dir "<ComfyUI>/user/default/workflows/gen-asset"
"""
import argparse
import json
import os
import sys
import urllib.request

WIDGET_TYPES = {"INT", "FLOAT", "STRING", "BOOLEAN", "COMBO"}
COL_W = 400
ROW_GAP = 40
NODE_W = 330

# Sprechende Dateinamen für die Workflow-Liste in der Oberfläche. Die Liste ist dort
# alphabetisch, die Nummer sortiert sie nach Anwendungsfall statt nach Technik.
# Stand 19.09.2026: neun Workflows auf fünf Modellfamilien, nach der Konsolidierung.
UI_NAMEN = {
    "zimage_turbo_t2i": "00-foto-realistisch",
    "zimage_cutout": "01-freigestellt-png",
    "birefnet_matte": "02-vorhandenes-bild-freistellen",
    "upscale": "03-upscale-2x",
    "qwen_2512_t2i": "04-text-im-bild-und-licht",
    "qwen_edit_2511": "05-bild-bearbeiten",
    "illustrious_t2i": "06-anime",
    "zimage_nsfw_t2i": "07-nsfw-realistisch",
    "zimage_cinematic_t2i": "09-cinematic-illustration",
    "krea2_turbo_t2i": "10-krea-foto-und-stile",
    "krea2_slider_sweep": "11-regler-vergleich",
    "janku_t2i": "12-anime-janku",
    "krea2_namensposter": "13-namensposter",
    "krea2_kinobanner": "14-kinobanner",
    "zimage_kinobanner": "14b-kinobanner-zimage",
    "qwen_edit_icon_set": "15-icon-set",
    "qwen_edit_ui": "16-ui-elemente",
    "qwen_2512_landschaft": "17-landschaft",
    "krea2_sprites": "18-sprites",
    "seamless_tile": "19-kacheln",
}

# Ablage je Workflow wie bei den Agenten: Text2Img/<workflow>/<name>_00001_.png, der Ordner ist der Basisname
# des Knotens SAVE der API-Vorlage, Testreihen liegen unter _tests/<reihe>/. Kein Datum im Ordner, die
# Bildgalerie liest den Ordner als Workflow (Umzug der Bildablage, Oktober 2026).
UI_PREFIX = {
    "zimage_turbo_t2i": "foto/foto",
    "zimage_cutout": "cutout/cutout",
    "birefnet_matte": "matte/matte",
    "upscale": "upscale/upscale",
    "qwen_2512_t2i": "qwen/qwen",
    "qwen_edit_2511": "edit/edit",
    "illustrious_t2i": "anime/anime",
    "zimage_nsfw_t2i": "nsfw/real",
    "zimage_cinematic_t2i": "cinematic/cinematic",
    "krea2_turbo_t2i": "krea/krea",
    "krea2_slider_sweep": "_tests/sweep/regler",
    "janku_t2i": "janku/janku",
    "krea2_namensposter": "namensposter/name",
    "krea2_kinobanner": "banner/banner",
    "zimage_kinobanner": "banner/banner",
    "qwen_edit_icon_set": "icon/icon",
    "qwen_edit_ui": "ui/ui",
    "qwen_2512_landschaft": "landschaft/landschaft",
    "krea2_sprites": "sprite/sprite",
    "seamless_tile": "kachel/kachel",
}

# Vorbelegung der Textfelder. Die Vorlagen tragen dort "placeholder", weil die
# Skripte den Prompt beim Aufruf einsetzen. In der Oberfläche gibt es diesen Aufruf
# nicht, dort soll Run sofort ein sinnvolles Bild liefern.
UI_PROMPTS = {
    "zimage_turbo_t2i": {
        "positiv": "a small stone winery on a hillside at golden hour, rows of vines on "
                   "trellis wires, warm side light, 35mm, sharp focus, fine detail",
        "negativ": "",
    },
    "zimage_cutout": {
        "positiv": "a single glossy blue potion bottle, game icon, centered, "
                   "isolated on a flat plain light grey background, even studio light, no shadow, sharp focus",
        "negativ": "",
    },
    "upscale": {
        "positiv": "high quality photo of a wooden crate of green apples in a barn, "
                   "sharp focus, fine detail",
        "negativ": "",
    },
    "qwen_2512_t2i": {
        "positiv": "a rustic wooden sign at the entrance of a vineyard, the sign reads "
                   "\"VINEYARD OPEN DAILY\" in clean carved letters, warm afternoon light, "
                   "sharp focus, fine detail",
        "negativ": "",
    },
    "qwen_edit_2511": {
        "positiv": "Change the color of the cup to deep forest green. Keep the shape, "
                   "the background and the lighting exactly as they are.",
        "negativ": "",
    },
    "illustrious_t2i": {
        "positiv": "masterpiece, best quality, amazing quality, very aesthetic, absurdres, "
                   "newest, 1girl, silver hair, red eyes, standing in a rainy neon street, "
                   "detailed background",
        "negativ": "bad quality, worst quality, worst detail, sketch, censor, jpeg artifacts, "
                   "signature, watermark, username, blurry, bad anatomy, extra digits",
    },
    "janku_t2i": {
        "positiv": "embedding:lazypos, 1girl, solo, dutch angle, looking at viewer, cinematic lighting, volumetric "
                   "lighting, natural shadows, clouds, blue sky, blonde hair, red eyes, long hair, off-shoulder "
                   "blouse, white blouse, black skirt, red skirt, garden, flower, detailed background, smile, "
                   "leaning forward, arms behind back",
        "negativ": "embedding:lazyhand, embedding:lazyneg, embedding:lazyloli, embedding:lazynsfw, bad perspective, "
                   "poor lighting, missing limbs, photo, photorealistic, realistic, realism, signature",
    },
    "zimage_nsfw_t2i": {
        "positiv": "portrait of a woman in her 30s standing at a window, natural skin "
                   "texture with fine pores, soft side light, 85mm, sharp eyes",
        "negativ": "",
    },
    "krea2_slider_sweep": {
        "positiv": "full body photo of a woman in her 30s standing in a plain studio, neutral grey "
                   "backdrop, casual jeans and a t-shirt, soft even light, 50mm, sharp focus",
        "negativ": "",
    },
    "krea2_turbo_t2i": {
        "positiv": "a fisherman mending a net on a stone pier in the late afternoon, wooden boats "
                   "behind him, weathered hands, 50mm, sharp focus, fine detail",
        "negativ": "",
    },
    "krea2_namensposter": {
        "positiv": "a vibrant 3D name art poster, the name \"LEON\" as the large centered hero of the image, "
                   "in bold chunky 3D metal letters in blue and orange with rivets, a big monster truck jumping "
                   "high over the letters, dust clouds and sparks, a desert race track at sunset, the letters are "
                   "solid and complete, high-end 3D render with cinematic lighting and detailed textures, "
                   "saturated colours, glossy highlights, sharp focus throughout, clean composition with the "
                   "single word \"LEON\"",
        "negativ": "",
    },
    "qwen_2512_landschaft": {
        "positiv": "A landscape photograph of a high mountain lake in the early morning. In the foreground, a shore of grey "
                   "scree and flat stones leads into clear shallow water where the pebbles on the bottom are visible. In "
                   "the middle distance, the calm lake surface mirrors the surrounding peaks almost perfectly. In the "
                   "background, steep rocky mountains with a few snowfields rise against a pale blue sky, their summits "
                   "catching the first warm sunlight while the valley still lies in cool shade. The light comes from "
                   "behind the viewer on the left. Shot with a 20 mm lens at f/11 from low above the shoreline.",
        "negativ": "",
    },
    "krea2_sprites": {
        "positiv": "A sprite sheet for a 2D top-down arcade game, hand-painted matte gouache and charcoal with grainy "
                   "pigment, warm muted tones. The subject is a heavy medieval shield bearer, shown as a GAME PIECE, not "
                   "a portrait: one bold compact silhouette in one dominant colour, readable at a glance. VIEW: straight "
                   "top-down, camera directly above like looking down at a board game piece from the sky; the figure "
                   "faces the top of the image, no perspective, no horizon, no ground plane. A round kettle helmet, "
                   "broad rounded shoulder plates and a large tall shield held in front of him at the top of the figure, "
                   "painted as one thick flat slab as wide as his shoulders. The whole figure is a compact heavy block. "
                   "Shield, helmet and shoulder plates are a muted slate blue-grey (#546a86) like dull painted iron, "
                   "matte and never shiny, covering most of the figure; straps and boots dark warm brown. POSES: exactly "
                   "three poses side by side in three equal cells: left standing at rest, middle mid step with the left "
                   "foot forward and the right shoulder slightly forward, right mid step with the right foot forward and "
                   "the left shoulder slightly forward; same figure, same scale, same colours, the head centred at the "
                   "same height in every cell. Each figure is about 60 percent of the cell width and about half of the "
                   "image height, with wide empty green space above, below and beside it; nothing touches the cell "
                   "edges. Flat uniform pure green #00ff00 background, no shadow, no gradient, no grid lines, no cell "
                   "borders, no text, no face, no eyes, no drawn ink outline. Nothing thin: no strings, no straps, no "
                   "thin shafts.",
        "negativ": "",
    },
    "qwen_edit_ui": {
        "positiv": "Add one more small hollow diamond at the middle of each of the four sides, sitting on the lines, the "
                   "same size and drawn the same way as the corner diamonds. Keep the double lines, their dim warm "
                   "grey-bronze color, their thin hand-drawn charcoal quality and their position exactly the same, keep "
                   "the whole center and the background pure black, keep the frame perfectly symmetric.",
        "negativ": "",
    },
    "qwen_edit_icon_set": {
        "positiv": "Replace the red berry with a five-pointed star in a warm marigold orange-yellow (#ECA532) like egg "
                   "yolk, made of exactly the same matte material as the berry, not lemon yellow, not metallic, with "
                   "softly rounded tips, one point straight up. Keep exactly the same soft matte vinyl-toy material with "
                   "its slightly powdery surface, the same diffuse studio light from the upper left, the same single "
                   "broad low-contrast cream sheen patch, the same calm milky saturation, the same size, the same "
                   "centered position and the same plain light grey background. The five points are short, thick and "
                   "chubby like a plush star, the inner corners stay wide open. One smooth puffy surface without any "
                   "raised rim or bevel. Nothing else in the image, no outline.",
        "negativ": "",
    },
    "zimage_kinobanner": {
        "positiv": "Cinematic widescreen movie key art in 21:9, a lone knight in dark weathered armor standing on a "
                   "cliff edge, facing a colossal dragon rising out of a stormy valley, lightning flickering inside "
                   "heavy clouds, cold blue light with warm fire glow on the dragon's chest. The left half is a calm "
                   "dark stormy sky. The main subject sits in the right third of the frame. The left half of the "
                   "frame is calm open space with a soft even gradient, reserved for the movie title. Anamorphic "
                   "lens, subtle film grain, rich color grading, volumetric atmosphere, highly detailed, sharp focus.",
        "negativ": "",
    },
    "zimage_cinematic_t2i": {
        "positiv": "double exposure illustration, profile view of a young woman warrior, dark "
                   "hair in a bun with loose strands, a katana strapped across her back, ornate "
                   "dark armor, inside her silhouette a glowing fantasy castle with tall "
                   "waterfalls and lit city towers, starry night sky in her hair, plain white "
                   "background, cinematic, highly detailed, sharp focus",
        "negativ": "",
    },
}

UI_PROMPTS["krea2_kinobanner"] = UI_PROMPTS["zimage_kinobanner"]  # dasselbe Beispielmotiv auf beiden Motoren

# Beispielbilder für die Workflows, die ein Bild brauchen statt es zu erzeugen.
# Liegen unter ComfyUI\input\, damit Run auch dort ohne Vorbereitung funktioniert.
UI_BILD = {
    "birefnet_matte": "beispiel-freistellen.png",
    "upscale": "beispiel-upscale.png",
    "qwen_edit_2511": "beispiel-bearbeiten.png",
    "qwen_edit_icon_set": "beispiel-icon-referenz.png",
    "qwen_edit_ui": "beispiel-ui-rahmen.png",
    "seamless_tile": "beispiel-kachel-grund.png",
}

# Kurzanleitung, die als MarkdownNote links neben dem Graphen liegt.
NOTIZEN = {
    "seamless_tile": """## 19 Kachel nahtlos machen (ohne Modell)

Macht aus einer vorhandenen Textur eine echte nahtlose Kachel, die sich lückenlos wiederholen lässt. Kein Modell, kein Sampler, in wenigen Sekunden fertig. Seit 28.09.2026, erster Testsatz für Aschekrone (der abgenommene Grund und die dunklere Vorlage).

**So geht es:** VERSATZ_HALB verschiebt das Bild um die halbe Kante. Die alten Außenkanten liegen dann als Kreuz in der Mitte und die neuen Außenkanten passen bauartbedingt aneinander. ÜBERBLENDUNG legt im Kreuz das unverschobene Original darüber, das genau dort durchgehend ist. Die weiche Maske kommt aus VERSATZ_HALB (Randband 80, Unschärfe 60).

**Was du änderst:** nur INPUT_IMAGE. Quadratisch 1024 px, sonst in VERSATZ_HALB shift_x und shift_y auf die halbe Kantenlänge setzen.

**Nur für Texturen ohne erkennbare Formen** (Pigment, Nebel, Stoff, Erde). Steine, Fugen oder Muster schienen im Kreuz doppelt durch.

**Feinkorn im Kreuz:** die lineare Überblendung verliert im Übergang rund ein Fünftel des Feinkorns (Aschekrone-Grund: 1,39 gegen 1,74). Die varianzerhaltende Fassung liegt als Skript bei (`scripts/seamless_tile.py`, gleiches Verfahren, Korn unverändert).

**Prüfen:** das Ergebnis 3 x 3 nebeneinanderlegen und vierfach aufgehellt ansehen, Nähte fallen dort zuerst auf.

**Nicht bewährt:** das Kreuz mit Z-Image maskiert neu rechnen (sichtbares Gitter, auch mit der Stylized-Textures-LoRA) und die Qwen-2512 Fun ControlNet Union 2602 (lädt in ComfyUI 0.36 nicht).

Ablage: `output/spiel-kacheln/<datum>/kachel_00001_.png`""",
    "krea2_sprites": """## 18 Sprites (Krea 2, eine Figur in drei Posen)

Ein Sprite-Bogen für ein Spiel in Draufsicht: dieselbe Figur in drei Zellen nebeneinander (Stand, Schritt links, Schritt rechts) auf flachem Grün, 1536 x 1024. Seit 28.09.2026, erster Testsatz für Aschekrone (vier Gegner im Stil der Gate-Figuren).

**Was du änderst:** nur POSITIVE_PROMPT (englisch). Das Gerüst im Beispiel stammt aus den Vertragsprompts des Spiels: GAME PIECE statt Porträt, VIEW straight top-down mit Blick zum oberen Bildrand, POSES mit den drei Zellen, feste Größe mit grünem Rand, flaches Grün. Motiv, Ausrüstung und Farbe tauschen.

**Was im Test hielt:** echte Draufsicht in allen Bögen, Schrittfolge in den Füßen, die Funktionsfarbe als dominante Fläche, keine gezogenen Konturen. Den genauen Farbton rechnet das Spiel nach, wie bei den Gate-Figuren. **Was bestellt werden muss:** Ausrüstung je Zelle ("In all three cells he holds ..."), sonst fehlt sie in der Standpose. Eine Armbrust als T-Form aus zwei dicken Balken, sonst kommt eine dünne Sehne. Die feste Größe, sonst füllt die Figur die Zelle bis an den Rand.

**Zwei Ausgänge:** `sprite_*` ist der Bogen wie gerechnet. `sprite-gespiegelt_*` behält Stand und Schritt und setzt als dritte Zelle das Spiegelbild der mittleren. Krea malte Vierbeiner stets als Stand, Trab, Stand, von oben ist ein Tier aber links und rechts gleich gebaut, der zweite Trabschritt ist also genau das Spiegelbild. Für Tiere und Figuren ohne einseitige Ausrüstung den gespiegelten nehmen, bei Schwert oder Fackel in einer Hand den rohen, sonst wechselt die Hand.

**Vierbeiner:** die Beine ausdrücklich seitlich aus dem Umriss bestellen ("in every cell all four legs stick out clearly beyond the outline of the body"), von genau oben verdeckt der Rumpf sie sonst. Hielt bei Hund und Wolf, beim Maultier verdecken die Satteltaschen die Vorderbeine.

**Der Grund ist kein reines #00ff00,** sondern ein gleichmäßiges Grün, dessen Ton je Bogen schwankt (Zweibeiner um 76/172/80, Tiere bis 9/156/61). Beim Freistellen per Farbschlüssel den Wert am Rand des Bogens messen oder über 02 freistellen.

**Varianten eines abgenommenen Bogens:** über 05 mit dem Bogen als Eingang und SAMPLER denoise 0.8. Stil, Haltung und Draufsicht bleiben, Farben und kleine Teile ändern sich. Bei 4 Schritten rechnet denoise 0.9 genau wie 1.0. Ganz neue Figuren aus einer Vorlage dreht Qwen-Edit zu Vorder-, Seiten- und Rückansicht, dafür dieser Workflow.

Etwa 17 s je Bogen. Ablage: `output/spiel-sprites/<datum>/sprite_00001_.png`""",
    "qwen_2512_landschaft": """## 17 Landschaft (Qwen-Image-2512, Qualitätseinstellung)

Erste Wahl für Fotolandschaften seit dem Blindtest vom 28.09.2026: 16 Landschaftsprompts, je vier Modelle mit gleichem Seed, vom Nutzer blind beurteilt. Qwen gewann 8 der 16 Prompts, Krea 5, CyberRealistic 2, Z-Image 1.

**Einstellungen, die gewonnen haben:** Turbo-LoRA auf 0.0, 30 Steps, cfg 4.0, 1344 x 768. Der Knoten TURBO_LORA bleibt im Graphen, auf 1.0 mit 2 Steps und cfg 1.0 wird daraus eine schnelle Vorschau, die aber deutlich weniger Feinstruktur hat.

**Was du änderst:** nur POSITIVE_PROMPT (englisch). Im Test hat sich dieses Gerüst bewährt: Vordergrund, Mittelgrund und Hintergrund je in einem Satz, dazu Lichtrichtung und Brennweite (`Shot with a 35 mm lens at f/8`). Qualitätsformeln wie 8K oder masterpiece braucht es nicht.

**Schnelle Alternative:** Krea 2 über Workflow 10 im selben Format, etwa 11 s statt 100 s. Krea gewann im Test Mosel-Steilhang, Sturm an der Küste, Steinbrücke, Wintertal und Raureif.

Etwa 100 s je Bild. Ablage: `output/landschaft/<datum>/landschaft_00001_.png`""",
    "qwen_edit_ui": """## 16 UI-Element nach Referenz (Qwen-Edit, mit Spiegelung)

Varianten eines abgenommenen UI-Flächen-Assets, etwa eines Kartenrahmens oder eines Kartengrunds. Qwen-Image-Edit-2511 ändert nur das, was der Prompt nennt, Strich, Farbe und Aufbau der Vorlage bleiben. Seit 27.09.2026, erster Testsatz für Aschekrone (Stil gouache-dunkel).

**Zwei Ausgänge:** `ui_*` ist das Ergebnis wie gerechnet. `ui-symmetrisch_*` spiegelt das linke obere Viertel waagerecht und senkrecht, das ergibt exakte Vierfach-Symmetrie. So ist der abgenommene Aschekrone-Rahmen gebaut, erzeugte Rahmen weichen sonst leicht ab. Für Rahmen den symmetrischen nehmen, für Gründe und Texturen den rohen (gespiegelt entsteht dort ein sichtbares Muster).

**Was du änderst:** INPUT_IMAGE (das abgenommene Asset, quadratisch 1024 px, sonst stimmt das Viertel nicht) und POSITIVE_PROMPT: was sich ändern soll, dann `Keep ... exactly the same`. Im Beispiel liegt der Aschekrone-Rahmen.

**Was im Test hielt:** zusätzliche Akzente auf den Linien, eine ruhigere Fassung des Grunds ohne Glutpunkte. **Was nicht hielt:** "slightly cooler" machte den warmen Grund blau, Farbwechsel lieber rechnen als bestellen. Ersetzen von Eckformen gelang nur teilweise, Qwen setzte die neuen Formen oft zusätzlich nach innen.

**Die Striche kommen heller als in der Vorlage** (Mittel etwa 90 bis 120 gegen 78 im abgenommenen Rahmen). Vor dem Einbau die Helligkeit an die Vorlage angleichen.

**Rahmen ganz ohne Vorlage:** Krea (Workflow 10) traf den Aschekrone-Rahmen aus Text in Palette und Aufbau, Qwen-2512 wurde zu hell und zu dick.

Etwa 17 bis 23 s je Bild. Ablage: `output/spiel-ui/<datum>/ui_00001_.png` und `ui-symmetrisch_00001_.png`""",
    "qwen_edit_icon_set": """## 15 Icon-Serie nach Referenz (Qwen-Edit + BiRefNet)

Weitere Icons im Stil eines schon abgenommenen Icons. Qwen-Image-Edit-2511 tauscht in der Vorlage nur das Motiv aus, Material, Licht, Größe und Position bleiben stehen. Danach stellt BiRefNet frei wie in 01, heraus kommt ein PNG mit echtem Alpha-Kanal. Seit 27.09.2026, erster Testsatz für Blumilie (Vinyl-Stil).

**Was du änderst:** INPUT_IMAGE ist das abgenommene Referenz-Icon auf flachem hellgrauem Grund (ein Transparenz-PNG vorher auf Grau legen, das Beispiel ist die Blumilie-Beere). Im POSITIVE_PROMPT nur das neue Motiv mit Farbe und die Formauflage für kleine Größen tauschen.

**Gerüst:** `Replace the <Motiv der Vorlage> with <neues Motiv, Farbe>. Keep exactly the same <Material>, the same <Licht>, the same size, the same centered position and the same plain light grey background. <Formauflage>. Nothing else in the image, no outline.`

**Farben als matten Stoff beschreiben, nicht als Farbnamen allein:** "warm gold" ergab metallisches Gold mit abgesetzter Kante, "sunflower yellow" ein kaltes Zitronengelb. Getroffen hat "a warm marigold orange-yellow (#ECA532) like egg yolk, made of exactly the same matte material as the berry, not lemon yellow, not metallic".

**Glanz ausdrücklich weich bestellen,** sonst malt Qwen einen harten Glanzstreif: "the only light on it is one broad soft blurry cream sheen on the upper left".

**Prüfen bei Zielgröße:** das Icon auf die kleinste Anzeigegröße verkleinern (bei Blumilie 24 px) und auf allen App-Hintergründen nebeneinander ansehen. Alpha-Zwischenwerte lagen im Test bei 0,4 bis 0,8 Prozent.

Etwa 20 s je Icon, beim ersten Lauf kommt das Laden von Qwen-Edit und BiRefNet dazu. Ablage: `output/spiel-icons/<datum>/icon_00001_.png`""",
    "krea2_kinobanner": """## 14 Kinobanner 21:9 (Krea 2, Detail 1.0, Stimmung an)

Key-Art im Kinoformat mit freier Fläche für einen Titel, 1568 x 672 (Kreas eigenes 21:9-Format). Erste Wahl seit dem Nutzerurteil vom 27. und 28.09.2026: Krea gewann alle sechs Testmotive gegen Z-Image, Detail 1.0 ist gesetzt.

**Stimmung:** STIMMUNG_AFTERLIGHT (0.35) und STIMMUNG_WARM (0.5) sind seit 03.10.2026 Standard, im Blindtest verlor die Fassung mit Stimmung nie. Sie geben mehr Kontrast und Tiefe, dazu Unschärfe im hinteren und äußeren Bereich. Auf 0 stellen bei Produkt, Architektur, klarem Tageslicht und überall, wo Ränder scharf bleiben sollen.

**Was du änderst:** POSITIVE_PROMPT (englisch), bei Bedarf die beiden Stimmungsknoten. Die Titelfläche musst du bestellen, von allein bleibt sie nicht frei.

**Gerüst:** `Cinematic widescreen movie key art in 21:9, <Szene>. The left half is <ruhige Fläche, etwa a calm dark stormy sky>. The main subject sits in the right third of the frame. The left half of the frame is calm open space with a soft even gradient, reserved for the movie title. Anamorphic lens, subtle film grain, rich color grading, volumetric atmosphere, highly detailed, sharp focus.`

**Kein Schild im Bild bestellen:** "neon sign" schreibt Fantasietext ins Bild, "a single bare horizontal pink neon tube" ergab Licht ohne Schrift.

**Andere Motoren:** 14b ist dieselbe Aufgabe auf Z-Image (1680 x 720), schwächer bei weiten Szenen. Qwen-2512 kann kein 21:9.

Etwa 11 bis 12 s je Bild. Ablage: `output/banner/<datum>/banner_00001_.png`""",
    "zimage_kinobanner": """## 14b Kinobanner 21:9, Z-Image-Fassung (Z-Image + zwei LoRAs)

Alternative zu 14 (Krea, Erste Wahl seit 28.09.2026). Key-Art im Kinoformat mit freier Fläche für einen Titel. Derselbe Motor wie 09 (Z-Image mit Luneva Cinematic 0.5 und Detail Slider 1.0), nur im Format 1680 x 720. Das ist eines der Formate, auf die Z-Image trainiert ist (Aussage des Z-Image-Teams), 2016 x 864 geht ebenso. Seit 27.09.2026.

**Was du änderst:** nur POSITIVE_PROMPT (englisch). Die Titelfläche musst du bestellen, von allein bleibt sie nicht frei.

**Gerüst:** `Cinematic widescreen movie key art in 21:9, <Szene>. The left half is <ruhige Fläche, etwa a calm dark stormy sky>. The main subject sits in the right third of the frame. The left half of the frame is calm open space with a soft even gradient, reserved for the movie title. Anamorphic lens, subtle film grain, rich color grading, volumetric atmosphere, highly detailed, sharp focus.`

**Ausführlich beschreiben lohnt sich:** Z-Image setzt lange Prompts deutlich treuer um als knappe (Test vom 27.09.2026).

**Titelfläche hält nicht immer:** im Test sechs Motive, Z-Image ließ sie bei einem erst frei, als der Prompt sagte, was links steht ("The left half is filled with soft hazy jungle mist"). Krea hielt sie in sechs von sechs.

**Kein Schild im Bild bestellen:** "neon sign" und selbst "neon light above a doorway" schrieben Fantasietext ins Bild. "a single bare horizontal pink neon tube" ergab Licht ohne Schrift.

**Mit Krea:** Workflow 14. **Qwen-2512 kann kein 21:9**, dort 16:9 rechnen und zuschneiden.

**Größer:** das fertige Bild durch 03 schicken, ergibt 3360 x 1440.

Etwa 9 s je Bild. Ablage: `output/banner/<datum>/banner_00001_.png`""",
    "krea2_namensposter": """## 13 Namensposter (Krea 2 mit Typnosis)

Ein Name als Hauptmotiv in einer gestalteten Szene, im Stil der Namensbilder von Ideogram. Krea 2 Turbo mit der Typografie-LoRA Typnosis auf 1,5, dazu der gemessene Licht- und Detailstapel. Standard seit 26.09.2026.

**Was du änderst:** nur den Text im Knoten „Prompt“ (unten links, englisch). Den Namen immer in Anführungszeichen und in Großbuchstaben schreiben, am Anfang und am Ende des Prompts.

**Ausformulieren?** (standardmäßig aus) lässt Qwen3-VL einen kurzen Prompt ausführlich ausschreiben, Text in Anführungszeichen bleibt dabei wörtlich. Für Namensposter ungetestet: das Gerüst unten ist schon ausführlich, dafür bleibt der Schalter aus. Den verwendeten Text zeigt „Verwendeter Prompt“, im PNG steht nur der Kurzprompt.

**Gerüst:** `a vibrant 3D name art poster, the name "LEON" as the large centered hero of the image, in <Material> 3D letters, <Figuren und Szene>, the letters are solid and complete, high-end 3D render with cinematic lighting and detailed textures, saturated colours, glossy highlights, sharp focus throughout, clean composition with the single word "LEON"`

**Ein Negativ-Prompt existiert hier nicht** (cfg 1.0). Verbote wie "no text" gehören auch nicht in den Positiv-Prompt, sie ziehen das Verbotene eher ins Bild. Beschreib stattdessen, was du willst.

**Figuren und Fahrzeuge links anordnen:** "to the left of the first letter" hält. "to the right of the last letter" landet vor dem letzten Buchstaben und verdeckt ihn.

**Kein "soft blurred background":** das erzeugt verschwommene Doppelgänger von Figuren und Buchstaben im Hintergrund. Nenn einen konkreten Hintergrund.

**Klötzchen-Schrift im Voxel-Stil kann Krea nicht**, dafür 04 nehmen.

| Knoten | Wert | Wofür |
|---|---|---|
| STYLE_LORA | Typnosis 1.5 | Typografie, 1.0 bis 2.0 brauchbar, ab 3.0 kippt die Schrift |
| DETAIL_LORA | 1.0 | mehr Feinstruktur, verdunkelt leicht |
| AFTERLIGHT_LORA | 0.35 | Glanzlichter und Tiefe, höher frisst Details |
| WARM_LORA | 0.5 | gleicht die Verdunkelung durch DETAIL aus |

**Bei Pastell und Glitzer** macht der Stapel das Bild gemessen 6 bis 9 Prozent dunkler und kontrastreicher. Soll es zart bleiben, AFTERLIGHT_LORA auf 0.
""",
    "janku_t2i": """## 12 Anime mit JANKU (JANKU v5 und vier Stil-LoRAs)

Anime mit mehr Detail als 06. JANKU v5 (Illustrious-Basis) trägt Gesicht, Augen und Haar, dazu kommt der Stil-Stapel des Civitai-Autors akizukirei608. Im Vergleich vom 24.09.2026 gewann der volle Stapel alle sechs Paare gegen einen gekürzten, und die JANKU-Bilder schlugen WAI im Direktvergleich.

**Prompt-Sprache:** Danbooru-Tags wie bei 06, vorne `embedding:lazypos, `, dann Figur, Details, Hintergrund. Lange Qualitäts-Tags braucht es nicht. Künstlerstile mit `by <name>`. Landschaft ohne Figuren: `scenery, no humans` in den Prompt, sonst stellt JANKU kleine Figuren hinein.

**Negativ-Prompt ist vorbelegt:** `embedding:lazyneg`, `embedding:lazyhand` und `embedding:lazyloli` (laut Autor für v5 wichtig, damit Figuren erwachsen wirken, immer drin lassen). `photo, realistic, realism` schieben bewusst weg vom Fotolook: JANKU ist ein Anime-Modell, für realistische Bilder sind 00, 07 und 10 da.

**NSFW:** `embedding:lazynsfw` im Negativ hält NSFW heraus. Für NSFW-Motive dort streichen, das Modell kann es. `embedding:lazywet` dazunehmen, wenn Haut zu nass glänzt.

**Format:** Ganzkörper immer im Hochformat. Im Quadrat brach die Anatomie in zwei von zwei NSFW-Versuchen, im Hochformat nicht (25.09.2026). Der Autor nennt 768 x 1344, 832 x 1216, 768 x 1280, 704 x 1408 und 1024 x 1536.

**Die vier LoRAs** (Knoten STIL_LORA): USNR 0.5 (dünner Farbauftrag, Textur), WSSKX 0.3 (Gegenlicht, Glühen, Lens Flare), Smooth Booster 0.65 und Stabilizer 0.25. Einzeln wegschalten mit Strg+B (Bypass).

**Settings:** 30 Steps, cfg 5, `euler_ancestral` mit simple, seit 03.10.2026 in 832 x 1216. Danach Hires 1,5-fach bei Denoise 0.4, Ergebnis 1248 x 1824. In 1024 x 1536 kamen bei Füßen und Händen sechs Zehen und doppelte Füße, in 832 x 1216 mit derselben zweiten Stufe nicht. Die zweite Stufe 2-fach bei 0.5 (altes Rezept) erfindet Zehen dazu.

**Keine Gesichtskorrektur, mit Absicht:** FaceDetailer malte auf JANKU Male und Farbflecken ins Gesicht, die Hires-Stufe war sauber.

**Schwäche:** abstrakte Konzepte. Bei `fractal art` kam statt Fraktalkunst ein weißhaariges Mädchen, dort ist 06 besser. Charakter-Tokens aus fremden Prompts (etwa `kaela20`) nur zusammen mit ihrer LoRA übernehmen.

Etwa 53 s je Bild. Ablage: `output/anime/<datum>/janku_00001_.png`, fertig als `janku-detail_00001_.png`""",
    "zimage_turbo_t2i": """## 00 Foto realistisch (Z-Image-Turbo)

Das schnellste Foto-Modell, etwa 8 s je Bild. Bis 03.10.2026 Erste Wahl für Architektur, Handwerk, Produkt und Portraits. Im blinden Fototest vom 28.09.2026 lag es dort nur bei 3 von 16 Prompts vorn, seither gilt: **Produkt, Handwerk und Portrait mit 10 (Krea), Architektur und Landschaft mit 17 (Qwen).** Diesen Workflow nehmen, wenn es schnell gehen muss.

**Was du änderst:** POSITIVE_PROMPT (englisch), bei Bedarf LATENT für das Format.

**Ein Negativ-Prompt existiert hier nicht.** Der Graph nullt das Negativ über ConditioningZeroOut, cfg steht auf 1.0. Alles, was du willst, gehört in den positiven Prompt.

**Format:** voreingestellt 1024 x 1024. Querformat 1344 x 768, Hochformat 896 x 1152, alle im A/B geprüft.

**Schwäche:** dramatisches Licht. Z-Image bleibt neutral, also Lichtrichtung und Stimmung ausdrücklich prompten (`low sun behind the subject, long shadows, warm rim light`). Steht die Lichtstimmung im Mittelpunkt, ist 04 die bessere Wahl, Qwen trifft "golden hour" deutlich sicherer.

**Knoten DETAIL_LORA steht auf 0.6, Standard seit 03.10.2026** (im Vergleich mit 0.3 und ohne gewann 0.6 drei von vier Motiven). Im Mittel 14 Prozent dunkler, Komposition gleich, bei 0.3 waren es 5 Prozent. Der Regler ist bipolar, für helle Motive auf 0 stellen.

12 bis 17 s je Bild. Ablage: `output/foto/<datum>/foto_00001_.png`""",
    "zimage_cutout": """## 01 Freigestellt als PNG (Z-Image + BiRefNet)

Icon, Sprite, Spiel-Asset, Produkt ohne Hintergrund. Z-Image erzeugt das Motiv, BiRefNet schneidet es im selben Lauf frei. Heraus kommt ein PNG mit echtem Alpha-Kanal. Seit 19.09.2026 auf Z-Image statt FLUX, im Vergleichslauf gleiche Kantenqualität (84,7 % transparent, 0,3 % Halbtransparenz) und bessere Prompt-Treue: Z-Image hält sich an "no shadow".

**Was du änderst:** nur POSITIVE_PROMPT. Ein einzelnes Motiv, mittig, ohne Szene drumherum.

**Format:** 1024 x 1024 lassen. Ein freigestelltes Einzelmotiv braucht kein Panorama, und die Kante wird im Quadrat am saubersten.

**Im Prompt stehen lassen:** `isolated on a flat plain light grey background, even studio light, no shadow`. Der flache Grund gibt die saubere Kante, entfernt wird er trotzdem. Hellgrau statt Grün seit dem 26.08.2026: Grün färbt halbtransparente Ränder oliv, am Haarsaum 58,7 Prozent grünstichige Randpixel gegen 0,0 bei Grau.

**Im Feld steht schon ein Beispiel** (blaue Trankflasche), Run genügt. Weitere Ideen:

- `a wooden treasure chest, closed, game icon, isolated on a flat plain light grey background, even studio light, no shadow`
- `a single red apple, product cutout, isolated on a flat plain light grey background, even studio light, no shadow`
- `a stylized silver key, game icon, centered, isolated on a flat plain light grey background, even studio light, no shadow`

**Nicht erschrecken:** In der Windows-Fotoanzeige sieht die Datei hellgrau aus. Die Farbwerte behalten den Grund, durchsichtig ist nur der Alpha-Kanal. Im Browser, in Figma oder in GIMP stimmt es.

Etwa 20 s je Bild. Ablage: `output/freigestellt/<datum>/cutout_00001_.png`""",
    "birefnet_matte": """## 02 Vorhandenes Bild freistellen (BiRefNet)

Erzeugt nichts, schneidet nur frei. Für Bilder, die schon da sind: eigene Fotos, ältere Generierungen, zugeliefertes Material. Soll das Motiv erst entstehen, nimm 01.

**Ein Beispielbild ist voreingestellt** (`beispiel-freistellen.png`, die rote Tasse), Run genügt. Für ein eigenes Bild im Knoten INPUT_IMAGE auf `choose file to upload`. 2 bis 4 s je Bild.

**Gemessene Grenzen** (aus der Katalog-Umstellung vom 15.08.2026):
- Offene Linienzeichnungen füllt BiRefNet mit dem Hintergrund, die Zwischenräume werden zugemalt.
- Weißen Papiergrund hält es für Motiv und lässt ihn stehen.
- Spiegelnde Ränder behalten die Farbe des Hintergrunds.

In diesen drei Fällen ist der alte Chroma-Key (`tools/keyout.py` im bildstil-lab) das bessere Werkzeug.

Ablage: `output/freigestellt/<datum>/matte_00001_.png`""",
    "upscale": """## 03 Upscale 2x (UltimateSDUpscale mit 4x-UltraSharp)

Hebt ein fertiges Bild auf die doppelte Kantenlänge und rechnet dabei Details nach, gekachelt, damit auch große Bilder in den Speicher passen. Als Refiner rechnet seit dem 22.09.2026 **Z-Image-Turbo** (vorher CyberRealistic Pony, davor Juggernaut XL).

**Warum Z-Image:** im Refiner-Vergleich vom 22.09.2026 an einem neutralen Testbild wirkte es am natürlichsten. Krea 2 rechnet zwar am meisten nach und gewinnt jede Detail-Messung, übertreibt dabei aber sichtbar, vor allem im Haar. Das ist die Nutzerabnahme, nicht die Zahl: eine Kantenmessung belohnt jede zusätzliche Struktur und kann Überschärfung nicht von echtem Detail unterscheiden. Pony und Illustrious Realism glätten beide zu stark.

**Beispielbild und passender Prompt sind voreingestellt** (`beispiel-upscale.png`, die Apfelkiste), Run genügt. Für ein eigenes Bild im Knoten INPUT_IMAGE auf `choose file to upload`.

**Der POSITIVE_PROMPT beschreibt, WAS auf dem Bild zu sehen ist.** Er steuert die nachgerechneten Details, deshalb gehört dort ein Satz zum Motiv statt nur `high quality`. Wechselst du das Bild, wechsle auch diesen Satz. Die alten `score_`-Tags aus der Pony-Zeit brauchst du nicht mehr, sie schaden nur.

**Einen Negativ-Prompt gibt es nicht mehr.** Krea 2 rechnet mit cfg 1.0 und genulltem Negativ, wie die anderen modernen Modelle auch.

**upscale_by** steht auf 2.0, das ist die Kantenlänge. Aus 1024 x 1024 werden 2048 x 2048. Für 4-fach den Wert auf 4.0 setzen, dann dauert es entsprechend länger.

**denoise am Knoten UPSCALE** steht auf 0.2. Darunter wird nur geschärft, über 0.35 erfindet das Modell neue Inhalte.

Gemessen 50 s für 768 x 1024 auf das Doppelte. Ablage: `output/upscale/<datum>/upscale_00001_.png`""",
    "qwen_2512_t2i": """## 04 Text im Bild und Lichtstimmung (Qwen-Image-2512, 2 Steps)

Für Motive mit lesbarer Schrift (Schilder, Etiketten, Verpackung) und für Szenen, deren Lichtstimmung im Prompt steht ("golden hour" trifft Qwen sicherer als 00). Läuft über die Turbo-LoRA mit 2 Schritten.

**Was du änderst:** POSITIVE_PROMPT (englisch), bei Bedarf LATENT für das Format. Den gewünschten Text in Anführungszeichen in den Prompt schreiben: `the sign reads "OPEN DAILY"`.

**Englischer Text sitzt, deutscher nicht.** Getestet am 28.08.2026: "VINEYARD OPEN DAILY" fehlerfrei, "Weingut" wurde in vier von vier Versuchen zu "Weengut" oder "Weegrut", auch in Großbuchstaben und über mehrere Seeds, und 05 konnte es hinterher auch nicht korrigieren. Deutsche Schrift also immer nachsehen, für Kundenmaterial die Typografie im Layout setzen und hier nur den Hintergrund erzeugen.

**Ein Negativ-Prompt existiert nicht** (ConditioningZeroOut, cfg 1.0), alles Gewünschte gehört in den positiven Prompt.

**Format:** nativ 1328 x 1328. Getestet und gut: 1216 x 832 und 896 x 1152.

13 bis 30 s je Bild. Ablage: `output/text-und-licht/<datum>/qwen_00001_.png`""",
    "qwen_edit_2511": """## 05 Bild bearbeiten (Qwen-Image-Edit-2511, 4 Steps)

Ändert ein vorhandenes Bild per Anweisung, statt ein neues zu würfeln: Farbe tauschen, Objekt entfernen, Hintergrund ersetzen, englische Schrift ersetzen. Der Rest des Bildes bleibt stehen. Geprüft am 28.08.2026: Tasse umgefärbt bei unveränderter Form, Schatten und Reflexion, Schildtext zu "GREEN VALLEY" getauscht bei unveränderter Maserung. Deutsche Schrift konnte es nicht korrigieren.

**Was du änderst:** das Bild im Knoten INPUT_IMAGE und die Anweisung im POSITIVE_PROMPT. Die Anweisung ist ein Befehl, keine Bildbeschreibung: `Change the color of the cup to deep forest green. Keep everything else identical.`

**Format kommt aus dem Eingangsbild**, es gibt keinen LATENT-Knoten. Der Knoten SCALE_INPUT rechnet die Größe selbst auf ein für das Modell passendes Raster.

**Im Feld steht schon ein Beispiel** (die graue Tasse aus dem Modellvergleich), Run genügt. Weitere Ideen:

- `Replace the background with a bright studio wall, keep the object untouched.`
- `Remove the person in the background, fill the gap naturally.`
- `Make it look like an overcast day instead of sunshine.`

26 bis 33 s je Bild. Ablage: `output/bearbeiten/<datum>/edit_00001_.png`""",
    "illustrious_t2i": """## 06 Anime (WAI-illustrious-SDXL v17)

Anime und Illustration auf Illustrious-Basis. Die VAE steckt im Checkpoint, es braucht keine Zusatzdatei. Modell ist installiert.

**Prompt-Sprache ist anders:** Illustrious erwartet Danbooru-Tags, keine Sätze. Also `1girl, silver hair, red eyes, rain, neon lights` statt "a girl with silver hair standing in the rain". Die Qualitäts-Tags am Anfang (`masterpiece, best quality, amazing quality, very aesthetic, absurdres, newest`) gehören dazu, der Negativ-Prompt ist mit dem üblichen Gegenstück vorbelegt. Die Embeddings `lazyneg`, `lazypos` und `lazyhand` liegen im Embeddings-Ordner, in ComfyUI heißen sie im Prompt `embedding:lazyneg` und so weiter, das blanke Wort allein tut nichts.

**Settings, hier voreingestellt:** 40 Steps, cfg 7.0, `euler_ancestral`, normal. Das sind die Werte aus einem Referenzbild vom 28.08.2026, das dem Nutzer gefiel. Die Modellseite selbst nennt 15 bis 30 Steps und cfg 5 bis 7 als Rahmen, also ruhig nach unten probieren, das spart Zeit.

**Format:** voreingestellt 960 x 1664, das sind 1,6 Megapixel. Illustrious ist anders als das nackte SDXL auf hohe Auflösungen trainiert, die 1,5-Megapixel-Warnung von 08 gilt hier NICHT. Unter 1024 Kantenlänge wird es dagegen schlechter.

**Komposition per Text ist die Schwäche.** Bei Küstenstadt-Motiven rutscht das Modell fast immer in die Vogelperspektive, egal was im Negativ steht. Wer eine bestimmte Komposition will, gibt sie besser als Bild vor (img2img), so sind auch die meisten Civitai-Vorzeigebilder entstanden.

Etwa 20 s je Bild bei 40 Steps. Ablage: `output/anime/<datum>/anime_00001_.png`

**Knoten DETAIL_LORA, steht auf 0.0 und ist damit aus.** Gemessen am 22.09.2026: der Slider greift, hebt aber fast nur den Hintergrund, und bei diesem Modell ist der Effekt kaum sichtbar (Detailwert 42,9 auf 43,9, also zwei Prozent). Sinnvoller Bereich 0.5 bis 1.0, negative Werte sind laut Autor unzuverlässig.

**Wenn dir Details fehlen, ist der Upscale der richtige Weg, nicht dieser Regler.** Dasselbe Bild durch Workflow 03 geschickt, mit diesem Checkpoint als Refiner und denoise 0.25, bringt fünfzehn Prozent mehr Feinstruktur, und das sieht man: feinere Haarsträhnen, schärfere Augen, lesbarere Schrift im Hintergrund. Kostet 55 s.

**Achtung, 0.0 ist hier nicht dasselbe wie aus.** Bei den SDXL-Modellen verschiebt schon der eingehängte Knoten das Ergebnis leicht, auch auf Stärke 0.0: gemessen weichen rund zehn Prozent der Pixel sichtbar ab, im Testbild änderte sich der Schnitt der Jacke. Willst du exakt das Bild von vorher, klick den Knoten an und drück Strg+B (Bypass), dann reicht er das Modell unverändert durch. Bei Krea 2 in Workflow 10 gibt es das Problem nicht, dort ist 0.0 pixelgenau neutral.

## Zwei Stufen in einem Lauf

Seit dem 22.09.2026 macht dieser Workflow zwei Durchgänge und speichert beide Bilder. Grund: bei Illustrious kommt Detail nicht aus einer LoRA, sondern aus dem zweiten Durchgang. Gemessen am selben Motiv steigt die Feinstruktur von 42,9 auf 50,9, und das sieht man: einzelne Haarsträhnen, scharfe Iris mit Lichtern, Regentropfen im Haar, lesbarere Neonschrift.

- **Stufe 1** liefert wie bisher `anime_00001_.png` in 960 x 1664, etwa 20 s.
- **Stufe 2** schickt dieses Bild durch UltimateSDUpscale mit demselben Checkpoint als Refiner und speichert `anime-detail_00001_.png` in 1920 x 3328, etwa 45 s zusätzlich. Seit dem 04.10.2026 in einer einzigen Kachel (Kachel 4096, force_uniform_tiles aus): mit 1024er-Kacheln zeigten sich leichte Streifen durch die Bildmitte, im Nahttest gewann die Fassung mit einer Kachel zwei von drei Bildern.

Zusammen etwa 55 s. **Willst du nur schnell Varianten durchprobieren**, klick den Knoten UPSCALE an und drück Strg+B (Bypass), dann bist du wieder bei 20 s und bekommst nur Stufe 1. Zum Schluss den Bypass wieder lösen und die Favoriten noch einmal laufen lassen.

Der Regler `denoise` am Knoten UPSCALE steht auf 0.25. Darunter wird nur geschärft, über 0.35 erfindet das Modell neue Inhalte im Bild.""",
    "zimage_nsfw_t2i": """## 07 NSFW realistisch (CyberRealistic Z-Image v7.0)

Derselbe Graph wie 00, nur mit einem unzensierten Z-Image-Finetune im Knoten CHECKPOINT. Tempo und Bedienung bleiben gleich. Installiert ist `cyberrealisticZImage_v70_bf16.safetensors` (12,3 GB), Nullprobe am 19.09.2026 sauber in 11 s.

**Settings:** die Basiswerte von Z-Image, 8 Steps, cfg 1.0, `res_multistep`, simple. **INT8-Fassungen** scheiterten auf ComfyUI 0.25.1 (`KeyError: int8_tensorwise`), seit dem Update auf 0.36.0 kennt ComfyUI das Format, getestet ist es hier nicht. BF16 bleibt der sichere Weg.

**Alternative, nicht installiert:** PerfecZion 4.0 (`perfeczionZImageTurbo_40BF16FP8.safetensors`, BF16 12,0 GB oder FP8 6,0 GB), laut Modellseite 12 Steps, cfg 1.0, `dpmpp_3m_sde`, simple. Stärker auf Ästhetik gezogen, weniger dokumentarisch.

**Kein Negativ-Prompt** (cfg 1.0, ConditioningZeroOut). Wer ein echtes Negativ braucht, nimmt 08.

**Knoten DETAIL_LORA steht auf 0.6, Standard seit 03.10.2026** (im Vergleich gewann 0.6). Auf diesem Checkpoint dunkelt der Slider stärker ab als auf 00 (bei 0.6 um 21 Prozent, bei 0.3 um 8 Prozent). Bei hellen Motiven auf 0 stellen.

**Format:** wie 00, voreingestellt 1024 x 1024, Hochformat 896 x 1152.

Was sich in der Praxis bewährt, gehört in reference/learnings.md. Ablage: `output/nsfw/<datum>/real_00001_.png`""",
    "krea2_slider_sweep": """## 11 Regler-Vergleich (Krea 2)

Zeigt in einem einzigen Lauf, was ein Regler macht. Derselbe Prompt und derselbe Seed werden fünfmal gerechnet, mit den Stärken **-2, -1, 0, +1, +2**, und die fünf Bilder landen nebeneinander in einer Datei. Links die stärkste negative Stufe, rechts die stärkste positive, in der Mitte das unveränderte Bild.

**Was du änderst:** POSITIVE_PROMPT, bei Bedarf LATENT für das Format.

**Anderen Regler prüfen:** in allen fünf Knoten STUFE_1 bis STUFE_5 dieselbe LoRA-Datei wählen. Die Stärken bleiben stehen, nur die Datei wechselt. Voreingestellt ist der Weight Slider.

Die Regler, die sich lohnen (alle ohne Trigger-Wort):
- `WeightSlider-KREA2_v2.safetensors`, Körperfülle
- `RealismSlider-v1.safetensors`, Illustration gegen Foto
- `WarmLightSlider-KREA2_v1.safetensors`, Helligkeit und Wärme
- `Detailer-KREA2.safetensors`, Feinstruktur
- `Afterlight_v1.safetensors`, goldenes Gegenlicht

**Andere Stufen fahren:** `strength_model` an den fünf Knoten STUFE_1 bis STUFE_5 setzen, etwa -1, -0.5, 0, +0.5, +1 für eine feinere Auflösung nahe der Mitte.

**Der Seed muss gleich bleiben**, sonst vergleichst du fünf verschiedene Bilder statt fünf Stufen desselben. Alle fünf Sampler tragen denselben Wert, ändere ihn nur an allen fünf gleichzeitig oder gar nicht.

Etwa 50 s je Lauf, also fünfmal die Zeit eines Einzelbildes. Ablage: `output/vergleich/<datum>/regler_00001_.png`""",
    "krea2_turbo_t2i": """## 10 Krea 2: Foto und Stile

Krea 2 Turbo, das zweite Foto-Modell neben 00. Im A/B vom 20.09.2026 auf elf Motiven stand es 5:2 vor Z-Image bei vier Unentschieden: natürlicherer Fotolook, bessere Lichtführung, breitere Stilspanne. Z-Image bleibt vorn bei feinsten Strukturen wie Fell und Chrom und bei der Prompt-Treue in vollen Szenen.

**Was du änderst:** den Text im Knoten „Prompt“ (unten links, englisch), bei Bedarf LATENT für das Format.

**Ein Negativ-Prompt existiert hier nicht.** Der Graph nullt das Negativ über ConditioningZeroOut, cfg steht auf 1.0.

**Format:** voreingestellt 1024 x 1024. Krea rechnet bis 2048 nativ, Querformat 1216 x 832, Hochformat 832 x 1216.

**Ausformulieren?** (standardmäßig aus) schreibt aus einem kurzen Prompt einen ausführlichen, wie die offizielle Krea-Vorlage: Qwen3-VL, der Text-Encoder selbst, ergänzt Licht, Kamera, Material und Komposition. Im Test vom 27.09.2026 gewann der ausformulierte Prompt auf Krea zwei von drei Motiven gegen den kurzen. Kostet rund 30 Sekunden mehr, die Bilder werden oft dunkler und stimmungsvoller. Den verwendeten Text zeigt „Verwendeter Prompt“. Im PNG steht nur der Kurzprompt, der ausformulierte Text nicht: zum Wiederverwenden dort kopieren. Die Galerie markiert solche Bilder als in ComfyUI ausformuliert. Wer schon ausführlich schreibt (rund 100 Wörter), lässt den Schalter aus.

## Die sechs LoRA-Knoten

**DETAIL_LORA 0.5 und AFTERLIGHT_LORA 0.35 sind der Standard** (Detail seit 27.09.2026, Afterlight seit 03.10.2026). Im blinden Stapeltest vom 03.10. (18 Foto-Motive in Produkt, Handwerk und Porträt, fünf Lichtsituationen) gewann Afterlight 14 von 18 Gruppen, 0.35 neunmal und 0.7 fünfmal, Detail 0.5 allein keine. Auch bei Tageslicht lag Afterlight vorn (5 von 6). Für ein Bild ganz ohne LoRA beide auf 0.0 stellen. Bei den Stilen unten (Sticker, Charakterbogen, Pop-up, Anatomie) AFTERLIGHT_LORA auf 0.0, dort ist es ungetestet.

Die übrigen stehen auf 0.0 und sind damit aus. Das ist nachgemessen neutral: mit und ohne die Knoten kommt bei gleichem Seed das byte-identische Bild heraus, und die Laufzeit bleibt bei 11 s. Du kannst sie also stehen lassen und nur bei Bedarf hochdrehen.

| Knoten | Wofür | Sinnvoller Bereich |
|---|---|---|
| WARM_LORA | Bild heller und wärmer machen | +0.5 bis +1.5 (kalt und dunkel: -0.5 bis -1.5) |
| DETAIL_LORA | mehr Feinstruktur | 0.5 (Standard) bis +2.0 |
| AFTERLIGHT_LORA | goldenes Gegenlicht, Dunst, Bokeh | 0.35 (Standard) bis 1.0 |
| REALISM_LORA | negativ Richtung Illustration, positiv Richtung Foto | -1.0 bis +1.0 |
| WEIGHT_LORA | Körperfülle der dargestellten Person | -2.0 bis +2.0, ganzer Bereich brauchbar |
| STYLE_LORA | einen der vier Stile zuschalten | 0.8 bis 1.0, Trigger-Wort nicht vergessen |

**Zu dunkel? Nimm WARM_LORA, nicht den Prompt.** Gemessen an einem Hafenmotiv hebt er die Helligkeit von 103 auf 144, ohne dass die Feinstruktur leidet (33,3 gegen 32,2). Das kann sonst nichts: der Detail-Slider und die Hell-Wörter im Prompt kosten beide Struktur.

**Achtung, die Modellseite auf Civitai nennt -6 bis +3 als Bereich, das ist zu weit.** Gemessen ist +3 komplett orange und ausgefressen, -3 fast schwarz. Bleib zwischen -1.5 und +1.5.

**REALISM_LORA hat einen engeren Bereich, als die Modellseite nahelegt.** Bei -1.0 kommt eine saubere flache Comic-Zeichnung heraus, bei -2.0 zerfällt das Bild in abstrakte Farbflächen. Bei +1.0 wird es fotografisch und dunkel, bei +2.0 matschig. Bleib zwischen -1.0 und +1.0.

**WEIGHT_LORA trägt über den ganzen Bereich von -2.0 bis +2.0**, sauber und ohne Nebenwirkungen: Pose, Kleidung, Hintergrund und Licht bleiben stehen, nur die Figur ändert sich. Willst du die Stufen nebeneinander sehen, nimm Workflow 11.

**AFTERLIGHT_LORA ist kein Aufheller, sondern ein Look.** Es macht das Bild dunkler (bei 1.0 gemessen 103 auf 77), bringt aber die stärkste Feinstruktur von allen, dazu Gegenlicht und Glitzer auf Wasser. Bei Produkten im Abend- und Fensterlicht gewann im Stapeltest zweimal REALISM_LORA +0.5, das wird noch gegen den neuen Standard getestet.

## Die vier Stile im Knoten STYLE_LORA

Datei im Knoten wählen, Stärke auf 0.8 bis 1.0, und das Trigger-Wort in den Prompt schreiben, sonst passiert nichts:

- `Sticker_KREA2_V1.safetensors`, Trigger `sticker`
- `CharacterDesign-KREA2_v1.safetensors`, Trigger `Character design` (Charakterbogen mit Vorder-, Seiten- und Rückansicht, Mimikstudien, Farbpalette)
- `Pop-up_book_KREA2.safetensors`, Trigger `pop-up book`
- `Anatomy-Reveal-KREA2.safetensors`, Trigger `Anatomy-reveal` (Querschnitt mit Knochen und Organen, funktioniert auch auf Gebäuden und Fahrzeugen)

**Diese LoRAs laufen nur auf Krea 2.** Die Z-Image-LoRAs aus Workflow 09 passen hier nicht und umgekehrt. Steckst du die falsche ein, meldet ComfyUI nichts, das Bild kommt einfach unverändert heraus.

11 bis 16 s je Bild. Ablage: `output/krea/<datum>/krea_00001_.png`""",
    "zimage_cinematic_t2i": """## 09 Cinematic und Illustration (Z-Image + zwei LoRAs)

Derselbe Motor wie 00, aber mit zwei aufgesteckten LoRAs: **Midjourney Luneva Cinematic** (Stärke 0.5) bringt den filmischen Look und die Bildkomposition, **[ZIT] Detail Slider** (Stärke 1.0) legt Feindetails nach. Für Doppelbelichtung, Buchcover, Poster, Key-Art und alles, was mehr Stimmung als Dokumentation sein soll. Für ein sachliches Foto bleibt 00 richtig.

**Was du änderst:** POSITIVE_PROMPT (englisch), bei Bedarf LATENT für das Format.

**Ein Negativ-Prompt existiert hier nicht.** Der Graph nullt das Negativ über ConditioningZeroOut, cfg steht auf 1.0. Alles, was du willst, gehört in den positiven Prompt.

**Die zwei Regler, die etwas bewirken:**
- `strength_model` am Knoten CINEMATIC_LORA: 0.5 ist die Voreinstellung und die Empfehlung des Autors. Bei sehr langen Prompts auf 0.6 bis 1.0 erhöhen, sonst hängt sich das Modell zu stark am Prompt fest und der Stil verschwindet.
- `strength_model` am Knoten DETAIL_LORA: 1.0 ist die Voreinstellung. Der Regler ist bipolar und trägt von -2 bis +2, negativ heißt weniger Detail und mehr Helligkeit.

**Beide LoRAs verdunkeln, das ist gemessen.** Am selben Bergmotiv (mittlere Helligkeit, 0 ist schwarz und 255 weiß): ohne LoRA 132, nur Detail Slider 107, nur Luneva 115, beide zusammen 87.

**Willst du ein helles, sonniges Bild, nimm den Prompt und nicht den Regler.** Gemessen an einer Blumenwiese: Hell-Wörter im Prompt heben die Helligkeit von 104 auf 152 und kosten dabei nur 3 Prozent Feinstruktur. Der Slider auf -1.0 hebt sie auf 172, kostet aber 34 Prozent Feinstruktur, die Wiese verliert Blüten und wird dunstig. Bei -2.0 ist ein Drittel des Bildes ausgefressen.

Diese Wortliste hat gewirkt, einfach hinten an den Prompt hängen:

`high key lighting, bright and airy, luminous, sun-drenched, glowing white highlights, light pastel palette, cheerful and joyful mood`

Reicht das nicht, danach den Detail Slider in Schritten von 0.5 senken. Beides gleichzeitig auf voller Stärke überzieht: Slider -1.0 plus Hell-Wörter ergibt ein ausgewaschenes Bild. Für dunkle Motive (Nacht, Neon, Key-Art, Doppelbelichtung) bleibt die Voreinstellung 0.5 und 1.0 richtig.

Auf CyberRealistic Z-Image wirkt die Wortliste noch stärker: dort hob sie ein Nachtporträt von 30 auf 99 und steigerte die sichtbare Textur gleich mit, weil die LoRAs `high key lighting` als Gegenlicht umsetzen. Zwei Dinge dabei wissen: die Wörter löschen die Nacht nicht, die Neon-Lichter bleiben stehen (wer Tageslicht will, muss `at night` aus dem Prompt nehmen), und eigene Umschreibungen wie `lifted shadows` wirken deutlich schwächer als genau diese gängigen Begriffe. Der Prompt verschiebt außerdem Pose und Ausdruck, ein bestehendes Bild hellt er nicht auf, dafür ist 03 da.

**Kein Trigger-Wort.** Beide LoRAs wirken ohne Schlüsselbegriff im Prompt.

**Ecken prüfen.** Die Luneva-LoRA backt selten ein kleines Wasserzeichen in eine Bildecke. Über 15 Bilder und alle vier Ecken trat es genau einmal auf, und zwar bei einem bestimmten Seed, unabhängig von Motiv und LoRA-Stärke. Fällt eines auf: Seed um eins weiterdrehen, dann ist es weg. Über den Negativ-Prompt geht es nicht, den gibt es hier nicht.

**Zwei Leuchtfarben im selben Bild** (etwa blau glühende Augen und roter Feueratem) hält der Workflow sauber auseinander, wenn jede Farbe ausdrücklich ihrem Objekt zugewiesen wird und die Lichtrichtung mitgenannt ist: `cold blue rim light along the horns` gegen `red firelight reflecting on the chest scales`.

**Format:** voreingestellt 832 x 1216 (Hochformat, passt zu Figur und Poster). Quadratisch 1024 x 1024, Querformat 1216 x 832.

**Rezept für Doppelbelichtung:** `double exposure illustration` voranstellen, dann die Figur im Profil beschreiben, dann mit `inside her silhouette` die zweite Szene, zum Schluss `plain white background`.

**Lizenz:** Bilder aus der Luneva-LoRA dürfen kommerziell verwendet werden, der Autor verlangt aber Namensnennung. Die LoRA selbst darf nicht weitergegeben oder in ein Modell gemerged werden.

8 s je Bild, die LoRAs kosten kein Tempo. Ablage: `output/cinematic/<datum>/cinematic_00001_.png`""",
}


# Prompt ausformulieren wie die offizielle ComfyUI-Vorlage für Krea 2 Turbo: Qwen3-VL-4B, der Text-Encoder selbst, schreibt
# aus einem kurzen Prompt einen ausführlichen (System-Prompt der Vorlage in workflows/krea2_expansion_system.txt). Nur in der
# Oberfläche von 10 und 13 und standardmäßig aus, die API-Vorlagen bleiben unverändert: sie rechnen auch für die Galerie.
# Greedy (sampling_mode off) wie im Promptlängen-Test vom 27.09.2026, dort gewann die Erweiterung auf Krea zwei von drei.
ERWEITERUNG = {"krea2_turbo_t2i", "krea2_namensposter"}
ERWEITERUNG_SYSTEM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "workflows", "krea2_expansion_system.txt")


def erweiterung_einbauen(ui):
    """Schalter „Ausformulieren?“ vor POSITIVE_PROMPT: der Prompt steht in einem Textknoten, ComfySwitchNode nimmt ihn oder
    den Text von TextGenerate (lazy, der andere Zweig rechnet nicht), PreviewAny zeigt den verwendeten Text und gibt ihn an
    CLIPTextEncode. Knotenformat wie in der offiziellen Vorlage, damit die Oberfläche die Widgets richtig zuordnet. Gespeichert
    wird weiter über SaveImage: der Image Saver schriebe den Text mit, bricht aber das Namensschema <name>_NNNNN_.png und
    zählt die .papierkorb-Platzhalter nicht mit (03.10.2026, Entscheid des Galerie-Koordinators)."""
    with open(ERWEITERUNG_SYSTEM, encoding="utf-8") as fh:
        system = fh.read()
    ziel = next(n for n in ui["nodes"] if n.get("title") == "POSITIVE_PROMPT")
    clip = next(n for n in ui["nodes"] if n["type"] == "CLIPLoader")
    ids = iter(range(ui["last_node_id"] + 1, ui["last_node_id"] + 8))

    def knoten(typ, pos, size, widgets, inputs=(), outputs=(), titel=None, eingeklappt=False):
        node = {"id": next(ids), "type": typ, "pos": pos, "size": size, "flags": {"collapsed": True} if eingeklappt else {},
                "order": len(ui["nodes"]), "mode": 0,
                "inputs": [{"name": name, "type": typ_, "link": None, **extra} for name, typ_, extra in inputs],
                "outputs": [{"name": name, "type": typ_, "links": [], "slot_index": i} for i, (name, typ_) in enumerate(outputs)],
                "properties": {"Node name for S&R": typ}, "widgets_values": widgets}
        if titel:
            node["title"] = titel
        ui["nodes"].append(node)
        return node

    def verbinde(quelle, slot_q, senke, name):
        ui["last_link_id"] += 1
        lid = ui["last_link_id"]
        slot_s = next(i for i, e in enumerate(senke["inputs"]) if e["name"] == name)
        typ = quelle["outputs"][slot_q]["type"]
        ui["links"].append([lid, quelle["id"], slot_q, senke["id"], slot_s, typ])
        quelle["outputs"][slot_q]["links"].append(lid)
        senke["inputs"][slot_s]["link"] = lid

    widget = lambda name: {"widget": {"name": name}}
    optional = {"shape": 7}
    prompt = knoten("PrimitiveStringMultiline", [60, 740], [730, 240], [ziel["widgets_values"][0]],
                    outputs=[("STRING", "STRING")], titel="Prompt")
    schalter = knoten("PrimitiveBoolean", [60, 1030], [330, 58], [False], outputs=[("BOOLEAN", "BOOLEAN")],
                      titel="Ausformulieren?")
    system_knoten = knoten("PrimitiveStringMultiline", [460, 1030], [330, 120], [system], outputs=[("STRING", "STRING")],
                           titel="System-Prompt Ausformulieren", eingeklappt=True)
    verketten = knoten("StringConcatenate", [860, 1030], [330, 140], ["", "", ""],
                       inputs=[("string_a", "STRING", widget("string_a")), ("string_b", "STRING", widget("string_b"))],
                       outputs=[("STRING", "STRING")], eingeklappt=True)
    erzeugen = knoten("TextGenerate", [1260, 1030], [330, 270], ["", 512, "off", False, True],
                      inputs=[("clip", "CLIP", {}), ("image", "IMAGE", optional), ("video", "IMAGE", optional),
                              ("audio", "AUDIO", optional), ("prompt", "STRING", widget("prompt"))],
                      outputs=[("generated_text", "STRING")])
    weiche = knoten("ComfySwitchNode", [860, 740], [330, 100], [False],
                    inputs=[("on_false", "STRING", {}), ("on_true", "STRING", {}), ("switch", "BOOLEAN", widget("switch"))],
                    outputs=[("output", "STRING")])
    anzeige = knoten("PreviewAny", [1260, 740], [730, 240], [], inputs=[("source", "*", {})], outputs=[("STRING", "STRING")],
                     titel="Verwendeter Prompt")
    ziel["inputs"].append({"name": "text", "type": "STRING", "widget": {"name": "text"}, "link": None})
    verbinde(system_knoten, 0, verketten, "string_a")
    verbinde(prompt, 0, verketten, "string_b")
    verbinde(clip, 0, erzeugen, "clip")
    verbinde(verketten, 0, erzeugen, "prompt")
    verbinde(prompt, 0, weiche, "on_false")
    verbinde(erzeugen, 0, weiche, "on_true")
    verbinde(schalter, 0, weiche, "switch")
    verbinde(weiche, 0, anzeige, "source")
    verbinde(anzeige, 0, ziel, "text")
    ui["last_node_id"] += 7
    ui["groups"].append({"title": "Prompt, Ausformulieren optional", "bounding": [40, 690, 1970, 630], "color": "#3f789e",
                         "font_size": 24, "flags": {}})
    return ui


def object_info(url):
    with urllib.request.urlopen(url.rstrip("/") + "/object_info", timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def input_specs(info):
    """required- und optional-Eingänge in Deklarationsreihenfolge."""
    out = []
    for section in ("required", "optional"):
        for name, spec in (info.get("input", {}).get(section) or {}).items():
            typ = spec[0] if isinstance(spec, list) and spec else spec
            opts = spec[1] if isinstance(spec, list) and len(spec) > 1 else {}
            out.append((name, typ, opts if isinstance(opts, dict) else {}))
    return out


def is_widget(typ, opts, hat_wert):
    """Widget oder Eingangs-Socket?

    hat_wert = der API-Graph liefert für diesen Eingang einen festen Wert statt
    einer Verlinkung. Das ist das verlässlichste Signal, weil eigene Node-Pakete
    Widget-Typen erfinden (LoadImage: `upload` vom Typ IMAGEUPLOAD), die in keiner
    festen Liste stehen.
    """
    if isinstance(typ, list):  # Auswahlliste
        return True
    if opts.get("forceInput"):
        return False
    return typ in WIDGET_TYPES or hat_wert


def steuer_widget(name, typ, opts):
    """Hängt die Oberfläche hinter diesen Eingang ein control_after_generate-Widget?

    Die Oberfläche tut das, wenn object_info es meldet, UND aus Altlast-Gründen bei
    jedem INT namens seed/noise_seed. Fremde Nodes (UltimateSDUpscale) melden das
    Flag nicht, bekommen das Widget aber trotzdem: fehlt es hier, verrutschen ALLE
    folgenden Widget-Werte des Knotens um eine Position.
    """
    return bool(opts.get("control_after_generate")) or (
        typ == "INT" and name in ("seed", "noise_seed")
    )


def default_for(typ, opts):
    if "default" in opts:
        return opts["default"]
    if isinstance(typ, list):
        return typ[0] if typ else ""
    return {"INT": 0, "FLOAT": 0.0, "STRING": "", "BOOLEAN": False}.get(typ, None)


def convert(api, oi, seed_control="randomize", notiz=None, prefix=None,
            prompts=None, bild=None):
    fehlend = sorted({n["class_type"] for n in api.values() if n["class_type"] not in oi})
    if fehlend:
        sys.exit(f"Unbekannte Node-Typen (läuft der richtige ComfyUI?): {fehlend}")

    if prefix or prompts or bild:
        api = json.loads(json.dumps(api))  # Vorlage des Aufrufers nicht anfassen
        for node in api.values():
            titel = node.get("_meta", {}).get("title", "")
            if prefix and node["class_type"] == "SaveImage":
                # Mehrstufige Workflows speichern zweimal. Damit die Stufen
                # auseinanderzuhalten sind, bekommt die zweite ein Suffix: SAVE_DETAIL wird
                # "-detail", jeder andere Zusatz im Titel (SAVE_SYMMETRISCH) wird zum Suffix.
                if titel.startswith("SAVE_DETAIL"):
                    node["inputs"]["filename_prefix"] = prefix + "-detail"
                elif titel.startswith("SAVE_"):
                    node["inputs"]["filename_prefix"] = prefix + "-" + titel[5:].lower()
                else:
                    node["inputs"]["filename_prefix"] = prefix
            # Qwen-Edit-Knoten nennen das Feld "prompt", CLIPTextEncode "text" (wie inject() in comfy_generate.py).
            # Vorher landete der Text in einem Feld, das der Knoten nicht hat, und 05 zeigte "placeholder".
            if prompts and titel == "POSITIVE_PROMPT":
                node["inputs"]["prompt" if "prompt" in node["inputs"] else "text"] = prompts["positiv"]
            if prompts and titel == "NEGATIVE_PROMPT":
                node["inputs"]["prompt" if "prompt" in node["inputs"] else "text"] = prompts["negativ"]
            if bild and node["class_type"] == "LoadImage":
                node["inputs"]["image"] = bild

    tiefe = {}

    def berechne(nid, pfad=()):
        if nid in tiefe:
            return tiefe[nid]
        if nid in pfad:  # Zyklus, sollte es nicht geben
            return 0
        quellen = [v[0] for v in api[nid]["inputs"].values()
                   if isinstance(v, list) and len(v) == 2 and str(v[0]) in api]
        d = 0 if not quellen else 1 + max(berechne(str(q), pfad + (nid,)) for q in quellen)
        tiefe[nid] = d
        return d

    for nid in api:
        berechne(nid)

    reihenfolge = sorted(api, key=lambda n: (tiefe[n], int(n) if n.isdigit() else 0))
    spalten_y = {}
    links = []
    link_id = 0
    knoten = {}

    for nid in reihenfolge:
        node = api[nid]
        info = oi[node["class_type"]]
        eingaenge, widgets = [], []
        for name, typ, opts in input_specs(info):
            wert = node["inputs"].get(name, "__fehlt__")
            verlinkt = isinstance(wert, list) and len(wert) == 2 and str(wert[0]) in api
            if verlinkt or not is_widget(typ, opts, wert != "__fehlt__"):
                eingaenge.append({
                    "name": name,
                    "type": "COMBO" if isinstance(typ, list) else typ,
                    "link": None,
                    "_quelle": (str(wert[0]), wert[1]) if verlinkt else None,
                })
            else:
                widgets.append(default_for(typ, opts) if wert == "__fehlt__" else wert)
                if steuer_widget(name, typ, opts):
                    widgets.append(seed_control)
        d = tiefe[nid]
        y = spalten_y.get(d, 60)
        hoehe = 60 + 26 * len(widgets) + 22 * len(eingaenge)
        spalten_y[d] = y + hoehe + ROW_GAP
        knoten[nid] = {
            "id": int(nid),
            "type": node["class_type"],
            "pos": [60 + d * COL_W, y],
            "size": [NODE_W, hoehe],
            "flags": {},
            "order": reihenfolge.index(nid),
            "mode": 0,
            "inputs": eingaenge,
            "outputs": [
                {"name": on, "type": ot, "links": [], "slot_index": i}
                for i, (on, ot) in enumerate(zip(info.get("output_name") or info.get("output", []),
                                                 info.get("output", [])))
            ],
            "properties": {"Node name for S&R": node["class_type"]},
            "widgets_values": widgets,
        }
        if node.get("_meta", {}).get("title"):
            knoten[nid]["title"] = node["_meta"]["title"]

    for nid in reihenfolge:
        for slot, eingang in enumerate(knoten[nid]["inputs"]):
            quelle = eingang.pop("_quelle", None)
            if not quelle:
                continue
            src_id, src_slot = quelle
            link_id += 1
            typ = eingang["type"]
            links.append([link_id, int(src_id), int(src_slot), int(nid), slot, typ])
            eingang["link"] = link_id
            ziel = knoten[src_id]["outputs"]
            while len(ziel) <= src_slot:
                ziel.append({"name": "OUT", "type": typ, "links": [], "slot_index": len(ziel)})
            ziel[src_slot]["links"].append(link_id)

    liste = [knoten[n] for n in reihenfolge]
    letzte_id = max(int(n) for n in api)
    if notiz:
        # MarkdownNote ist ein reiner Oberflächen-Knoten (isVirtualNode), er landet
        # nicht im API-Graphen und stört die Ausführung deshalb nicht.
        letzte_id += 1
        liste.insert(0, {
            "id": letzte_id,
            "type": "MarkdownNote",
            "pos": [-500, 60],
            "size": [420, 700],
            "flags": {},
            "order": 0,
            "mode": 0,
            "inputs": [],
            "outputs": [],
            "properties": {},
            "widgets_values": [notiz],
            "color": "#432",
            "bgcolor": "#653",
            "title": "Kurzanleitung",
        })

    return {
        "last_node_id": letzte_id,
        "last_link_id": link_id,
        "nodes": liste,
        "links": links,
        "groups": [],
        "config": {},
        "extra": {},
        "version": 0.4,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="quelle")
    p.add_argument("--out")
    p.add_argument("--all", action="store_true", help="alle workflows/*.api.json umwandeln")
    p.add_argument("--out-dir")
    p.add_argument("--url", default=os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188"))
    p.add_argument(
        "--seed-control",
        default="randomize",
        choices=["randomize", "fixed", "increment", "decrement"],
        help="Was der Seed nach jedem Lauf tut. randomize ist für Handbetrieb richtig, "
        "fixed für Reproduktion.",
    )
    p.add_argument(
        "--roh-namen",
        action="store_true",
        help="Dateinamen der Vorlage behalten statt der sprechenden aus UI_NAMEN",
    )
    a = p.parse_args()

    try:
        oi = object_info(a.url)
    except Exception as exc:  # noqa: BLE001 - eine freundliche Meldung für jeden Fehler
        sys.exit(f"ComfyUI nicht erreichbar unter {a.url}: {exc}")

    hier = os.path.dirname(os.path.abspath(__file__))
    if a.all:
        if not a.out_dir:
            sys.exit("--all braucht --out-dir")
        os.makedirs(a.out_dir, exist_ok=True)
        wf_dir = os.path.join(hier, "..", "workflows")
        for name in sorted(os.listdir(wf_dir)):
            if not name.endswith(".api.json"):
                continue
            with open(os.path.join(wf_dir, name), "r", encoding="utf-8") as fh:
                api = json.load(fh)
            schluessel = name.replace(".api.json", "")
            basis = schluessel if a.roh_namen else UI_NAMEN.get(schluessel, schluessel)
            ziel = os.path.join(a.out_dir, basis + ".json")
            ui = convert(api, oi, a.seed_control, NOTIZEN.get(schluessel), UI_PREFIX.get(schluessel),
                         UI_PROMPTS.get(schluessel), UI_BILD.get(schluessel))
            if schluessel in ERWEITERUNG:
                erweiterung_einbauen(ui)
            with open(ziel, "w", encoding="utf-8") as fh:
                json.dump(ui, fh, indent=1)
            print(ziel)
    else:
        if not a.quelle or not a.out:
            sys.exit("Fehlt: --in und --out (oder --all --out-dir)")
        with open(a.quelle, "r", encoding="utf-8") as fh:
            api = json.load(fh)
        # Auch ein einzelner Workflow bekommt Notiz, Ablage und Beispiel-Prompt, sonst müsste man für einen neuen
        # Eintrag --all fahren und damit jede in der Oberfläche angepasste Datei überschreiben
        schluessel = os.path.basename(a.quelle).replace(".api.json", "")
        ui = convert(api, oi, a.seed_control, NOTIZEN.get(schluessel), UI_PREFIX.get(schluessel),
                     UI_PROMPTS.get(schluessel), UI_BILD.get(schluessel))
        if schluessel in ERWEITERUNG:
            erweiterung_einbauen(ui)
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(ui, fh, indent=1)
        print(a.out)


if __name__ == "__main__":
    main()
