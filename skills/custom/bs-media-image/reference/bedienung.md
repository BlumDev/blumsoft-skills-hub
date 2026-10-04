# gen-asset: Bedienung über die Oberfläche

Für dich zum Selbergenerieren. Der Kommandozeilen-Weg für Agenten bleibt unverändert, er steht in [usage.md](usage.md). Beide nutzen dieselben Workflows und dieselben Modelle, es ist kein zweites System.

## 1. Starten

Zwei Wege, einer reicht:

- **Aus Stability Matrix:** Packages, ComfyUI, Launch. Danach öffnet sich die Oberfläche von selbst.
- **Ohne Stability-Matrix-Fenster:** `powershell -File "C:\Users\Marcus\.claude\skills\gen-asset\scripts\ensure_comfyui.ps1"`, dann `http://127.0.0.1:8188` im Browser aufrufen. Startet nur, wenn nicht schon etwas läuft. Der Kaltstart dauert seit dem ComfyUI-Manager drei bis fünf Minuten, solange blockiert der Manager beim Laden der Registry die Oberfläche. **Updates von ComfyUI nur bei gestopptem Server** (Stability Matrix stoppt die Headless-Instanz des Skills nicht mit), sonst bleibt eine halb erneuerte Umgebung zurück, siehe learnings.md.

## 2. Die Workflows

Links in der Leiste auf **Workflows**, dort den Ordner **gen-asset** aufklappen. Zwanzig Einträge, nach Anwendungsfall nummeriert (Stand 28.09.2026). Die Nummer 08 fehlt, seit CyberRealistic Pony gestrichen wurde:

| Workflow | Modell | Wofür | Dauer je Bild |
|---|---|---|---|
| 00-foto-realistisch | Z-Image-Turbo + Detail-Slider 0.6 | schnellstes Foto-Modell. Seit 03.10.2026 laufen Produkt, Handwerk und Portrait besser über 10, Architektur und Landschaft über 17 | 12 bis 17 s |
| 01-freigestellt-png | Z-Image + BiRefNet | Icon, Sprite, Spiel-Asset, Produkt ohne Hintergrund, Ergebnis ist ein PNG mit echter Transparenz | etwa 20 s |
| 02-vorhandenes-bild-freistellen | BiRefNet | ein fertiges Bild nachträglich freistellen, ohne neu zu generieren | 2 bis 4 s |
| 03-upscale-2x | 4x-UltraSharp + Z-Image als Refiner | ein fertiges Bild auf die doppelte Kantenlänge bringen und Details nachrechnen | 37 s bei 1024 auf 2048 |
| 04-text-im-bild-und-licht | Qwen-Image-2512 | englische Schrift im Bild, Lichtstimmung laut Prompt | 13 bis 30 s |
| 05-bild-bearbeiten | Qwen-Image-Edit-2511 | vorhandenes Bild per Anweisung ändern, Rest bleibt stehen | 26 bis 33 s |
| 06-anime | WAI-illustrious v17 | Anime und Illustration, Danbooru-Tags, zwei Stufen mit Detail-Durchgang | etwa 55 s, ohne zweite Stufe 20 s |
| 07-nsfw-realistisch | CyberRealistic Z-Image v7 + Detail-Slider 0.6 | wie 00, unzensiert | etwa 11 s |
| 09-cinematic-illustration | Z-Image-Turbo + zwei LoRAs | Doppelbelichtung, Poster, Buchcover, Key-Art, filmischer Look statt Doku-Foto | etwa 8 s |
| 10-krea-foto-und-stile | Krea 2 Turbo + sechs LoRA-Regler, Detail 0.5 und Afterlight 0.35 | Erste Wahl für Produkt, Handwerk und Portrait (seit 03.10.2026), natürlicherer Look als 00, dazu Sticker, Charakterbogen, Pop-up-Buch und Anatomie-Querschnitt. Prompt im Knoten „Prompt“, Schalter „Ausformulieren?“ (aus) lässt Qwen3-VL einen kurzen Prompt ausschreiben | 11 bis 16 s, ausformuliert rund 30 s mehr |
| 11-regler-vergleich | Krea 2 Turbo | zeigt in einem Lauf, was ein Regler macht: fünf Stufen desselben Bildes nebeneinander | etwa 50 s |
| 12-anime-janku | JANKU v5 + vier Stil-LoRAs | Anime mit mehr Detail als 06 (Gesicht, Augen, Hintergrund), Danbooru-Tags, 832 x 1216 plus Hires 1,5-fach (seit 03.10.2026), Ganzkörper nur im Hochformat | etwa 53 s |
| 13-namensposter | Krea 2 Turbo + Typnosis 1,5 + Licht- und Detailstapel | ein Name als Hauptmotiv in einer gestalteten Szene, im Stil der Namensbilder von Ideogram. Figuren links vom ersten Buchstaben anordnen, Voxel-Schrift lieber mit 04. Prompt im Knoten „Prompt“, Schalter „Ausformulieren?“ (aus, für Namensposter ungetestet) | 11 bis 16 s |
| 14-kinobanner | Krea 2, Detail 1.0 | Key-Art im Kinoformat 21:9 (1568 x 672) mit freier Fläche für einen Titel, die Fläche im Prompt bestellen. Die Stimmung (Afterlight 0.35, Warm 0.5) ist seit 03.10.2026 an, auf 0 stellen bei Produkt, Architektur und klarem Tageslicht | etwa 12 s |
| 14b-kinobanner-zimage | Z-Image-Turbo + Luneva + Detail-Slider | dieselbe Aufgabe auf Z-Image in 1680 x 720, Alternative zu 14 | etwa 9 s |
| 15-icon-set | Qwen-Image-Edit-2511 + BiRefNet | weitere Icons im Stil eines abgenommenen Icons: das Referenz-Icon als Bild rein, im Prompt nur das neue Motiv, heraus kommt ein freigestelltes PNG | etwa 20 s |
| 16-ui-elemente | Qwen-Image-Edit-2511 | Varianten eines abgenommenen Kartenrahmens oder Kartengrunds, zweiter Ausgang exakt gespiegelt für Rahmen | etwa 20 s |
| 17-landschaft | Qwen-Image-2512, 30 Steps, cfg 4.0, ohne Turbo-LoRA | Fotolandschaft und Architektur, Erste Wahl seit den Blindtests vom 28.09.2026. Schnell geht es mit 10 im selben Format | etwa 100 s |
| 18-sprites | Krea 2, Detail 0.5 | Sprite-Bogen für ein Spiel in Draufsicht: eine Figur in drei Posen nebeneinander auf flachem Grün (1536 x 1024). Ausrüstung je Zelle bestellen | etwa 17 s |
| 19-kacheln | kein Modell | macht eine vorhandene Textur nahtlos kachelbar (um die halbe Kante verschieben, im Kreuz das Original überblenden). Nur für Texturen ohne erkennbare Formen | wenige Sekunden |

**Alle zwanzig sind fertig ausgefüllt.** Modell, Format, Steps, cfg und Sampler stehen auf den Werten, die zum jeweiligen Modell passen, Prompt und Negativ-Prompt sind vorbelegt, bei 02, 03, 05, 15, 16 und 19 auch ein Beispielbild. Ein Klick auf Run liefert also sofort ein Ergebnis, das als Nullprobe taugt. Danach nur den Motivteil des Prompts ersetzen.

**Detail ist seit 27.09.2026 standardmäßig an:** 00 und 07 mit dem Z-Image-Detail-Slider seit 03.10.2026 auf 0.6 (vorher 0.3, im Vergleich gewann 0.6), 10 mit dem Krea-Detail-Slider auf 0.5. An 16 Bildern mit drei Sternen nachgerechnet blieb die Komposition gleich, die Bilder wurden im Mittel 4 bis 8 Prozent dunkler. Wer ein Bild ganz ohne LoRA will, stellt den Knoten DETAIL_LORA auf 0.

Beim ersten Start eines Modells kommen einmalig 10 bis 60 s Ladezeit dazu, danach bleibt es im Speicher. Die Zeiten sind gemessen (27.08. bis 20.09.2026).

**Ein Regler in 01 und 02, den man kennen sollte:** im Knoten BiRefNet Ultra V2 steht `process_detail` auf false. Bei Motiven mit vielen kleinen Strukturen (Haar, Fell, Flaum) auf true stellen und `detail_method` auf `GuidedFilter` setzen, `detail_erode` 4 und `detail_dilate` 2 bleiben stehen: der Haarsaum wird sichtbar besser. Bei klaren Linien und harten Kanten (Produkt, Icon, Blatt) ausgelassen lassen, dort weicht die Verfeinerung die Kante zu einem Glimmen auf. Über die Kommandozeile macht das der Schalter `--matte-detail`. Die acht Einzelurteile dazu stehen in `learnings.md` im Abschnitt vom 22.09.2026.

## 3. Ablauf

Links neben jedem Graphen liegt ein oranger Notizzettel **Kurzanleitung**: wofür der Workflow taugt, was du ändern sollst, das passende Format, Beispiel-Prompts zum Kopieren, die Ablage und die jeweilige Stolperfalle. Der Zettel ist ein reiner Oberflächen-Knoten, er wird beim Lauf nicht mitgeschickt.

1. Workflow anklicken, er ersetzt den Graphen auf der Fläche.
2. Direkt **Run** drücken, wenn du erst sehen willst, was der Workflow kann: das Beispiel ist eingetragen. Sonst im Knoten **POSITIVE_PROMPT** deinen englischen Prompt eintippen, das ist das einzige Feld, das du zwingend anfassen musst. Bei 06 die Qualitäts-Tags am Anfang stehen lassen.
3. Optional: **LATENT** für das Format, dabei im Rahmen bleiben, den die Kurzanleitung nennt. **NEGATIVE_PROMPT** gibt es nur noch bei 06, die Z-Image- und Qwen-Workflows haben keinen (cfg 1.0), dort gehört alles in den positiven Prompt.
4. Oben auf **Run**. Der Fortschritt steht im Tab-Titel und am Knoten.
5. Das Bild erscheint im Knoten **SAVE** und liegt gleichzeitig auf der Platte.

Der Seed steht auf **randomize**, jeder Lauf gibt also ein neues Bild. Willst du ein Ergebnis exakt wiederholen, den Seed am Knoten SAMPLER auf **fixed** stellen, bevor du erneut auf Run drückst.

Prompt-Kurzregeln: englisch, konkret, Motiv plus Setting plus Licht plus Optik ("35mm, golden hour"). `sharp focus, fine detail` für Schärfe. Bei 06 Danbooru-Tags statt Sätze. Ausführlicher: [learnings.md](learnings.md).

## Bewerten statt löschen

Platz ist kein Argument: 1395 Bilder belegen 2,3 GB, frei sind 382 GB. Und jedes PNG trägt seinen kompletten Workflow mit Prompt und Seed, ein misslungenes Bild dokumentiert also, was nicht funktioniert. Deshalb wird hier nichts weggeworfen, nur einsortiert.

**Nichts verschwindet von allein.** Auch Agentenläufe bleiben liegen, solange du sie nicht selbst wegräumst.

### Die drei Stufen

Fünf Stufen waren zu viel. Die Mitte trug keine Entscheidung: zwischen "gut" und "sehr gut" zu unterscheiden kostet Überlegung und ändert hinterher nichts. Es gibt beim Durchsehen genau drei Fragen, und darauf ist die Skala jetzt zugeschnitten.

| Sterne | Frage, die du dir stellst | Bedeutung |
|---|---|---|
| **3** | Würde ich das herzeigen? | Herzeigbar, kommt auf die Modellseite. |
| **2** | Würde ich das nochmal gebrauchen? | Nochmal brauchbar oder als Vorlage. |
| **1** | Zeigt das etwas, das ich behalten will? | Fehlschlag mit Erkenntniswert, nur mit Notiz. |

**Unbewertet ist der Normalfall** und kein Urteil. Es heißt: gesehen und für gut befunden reicht nicht, oder gar nicht angesehen. Der Großteil deiner Bilder bleibt so.

Die Spalte Bedeutung steht wortgleich im Tooltip an der Sternzeile der Galerie (`RATING_SCALE` in `static/index.html`). Wer eine der beiden Stellen ändert, ändert die andere mit, sonst behauptet die Anleitung etwas anderes als das Werkzeug.

Daneben gibt es weiter die zwei Tasten, die etwas anderes tun als bewerten: **F** merkt ein Bild als Favorit, damit du es schnell wiederfindest, **B** erklärt es zum Beispielbild eines Modells. Drei Sterne zählen für die Modellseite übrigens genauso viel wie ein B, du musst also nicht beides drücken.

**Kaputte Bilder bekommen keinen Stern, sondern die Entf-Taste.** Sie wandern in den Papierkorb und sind damit aus dem Weg, ohne verloren zu sein.

**So arbeitest du die Bilder durch.** Links in der Filterleiste unter Workflow steht die Gruppe **Bewertung** mit drei Einträgen samt Zähler: Unbewertet, Bewertet, Nur 3 Sterne. Nochmal klicken hebt den Filter wieder auf.

- **Unbewertet** ist dein Arbeitsstapel, wenn du Sterne vergeben willst.
- **Nur 3 Sterne** zeigt deine Referenzen, also das, was auf den Modellseiten landet.
- **Bewertet** zeigt alles, was du schon angefasst hast.

Die Bewertungen wirken außerdem im Render-Dialog: ab zwei Sternen gilt ein Bild dort als gutes Beispiel, ein Stern als schlechtes.

### Wenn es unübersichtlich wird

Nicht löschen, sondern filtern. Die Galerie blendet mit einem Klick aus, was gerade stört: Quelle auf UI stellt alle Skript-Läufe beiseite, der Dubletten-Filter zeigt Mehrfachkopien, und über die Sortierung nach bester Bewertung stehen die guten oben.

## 4. Wo die Bilder landen und wie sie heißen

Basis ist `D:\Apps\Stability Matrix\Data\Images\Text2Img\`, das ist derselbe Ordner wie `Packages\ComfyUI\output\` (ComfyUI schreibt direkt in die Bildbibliothek von Stability Matrix). Seit dem Umzug vom 03.10.2026 gilt: ein Ordner je Workflow, kein Datumsordner mehr darunter, Testreihen unter `_tests\`:

```text
Text2Img\foto\foto_00001_.png                  (00)
Text2Img\cutout\cutout_00001_.png              (01)
Text2Img\matte\matte_00001_.png                (02)
Text2Img\upscale\upscale_00001_.png            (03)
Text2Img\qwen\qwen_00001_.png                  (04)
Text2Img\edit\edit_00001_.png                  (05)
Text2Img\anime\anime_00001_.png                (06)
Text2Img\anime\anime-detail_00001_.png         (06, zweite Stufe)
Text2Img\nsfw\real_00001_.png                  (07)
Text2Img\cinematic\cinematic_00001_.png        (09)
Text2Img\krea\krea_00001_.png                  (10)
Text2Img\_tests\sweep\regler_00001_.png        (11)
Text2Img\janku\janku_00001_.png                (12, Hires janku-detail)
Text2Img\namensposter\name_00001_.png          (13)
Text2Img\banner\banner_00001_.png              (14, 14b)
Text2Img\icon\icon_00001_.png                  (15)
Text2Img\ui\ui_00001_.png                      (16)
Text2Img\landschaft\landschaft_00001_.png      (17)
Text2Img\sprite\sprite_00001_.png              (18)
Text2Img\kachel\kachel_00001_.png              (19)
Text2Img\_tests\<reihe>\<reihe>_01_00001_.png  (Testreihen)
```

Die fünfstellige Nummer zählt je Basisname hoch, ComfyUI legt den Ordner selbst an. Steuern kannst du das im Knoten **SAVE**, Feld `filename_prefix`: alles vor dem letzten Schrägstrich ist Ordner, der Rest ist Dateiname. Bilder von vor dem Umzug tragen ihr Datum im Namen (`foto_2026-09-20_00001_.png`), damit die Nummern nicht kollidieren. Kein `%date%` mehr in neue Prefixe setzen.

Läufe über die Kommandozeile (Agent) landen im selben Workflow-Ordner wie die UI-Läufe: `comfy_generate.py`, `upscale.py` und `comfy_matte.py` biegen jeden Prefix über `scripts\ablage.py` dorthin um (auch einen alten wie `agent/%date:yyyy-MM-dd%/foto`), Testreihen wie `qtest_01` nach `_tests\qtest\`. Die Skripte geben den Pfad aus und legen keine zweite Kopie an (`--out` optional: Hardlink innerhalb der Bibliothek, sonst Kopie, nach `out\` abgelehnt). Archiv liegt unter `Images\_archiv\` (`bis-2026-09-19`, `old-gpu`, `bildstil-lab`), Aussortiertes unter `Images\_papierkorb\` beziehungsweise `out\_papierkorb\`.

**Testmaterial aus dem Blickfeld.** Die Bildgalerie hat einen Filter Quelle mit den Werten Agent, UI und unbekannt. Ein Klick auf UI blendet alles aus, was aus Skript-Läufen stammt, und die Auswahl bleibt gemerkt. Die Quelle steht seit dem Umzug nicht mehr im Pfad: die Skripte schreiben sie als PNG-Chunk `gallery_source` (`agent`) ins Bild, ein Bild mit eingebettetem Workflow ohne diesen Chunk gilt als UI.

Aufräumen: `python scripts\cleanup.py` zeigt, was wegkäme, `--apply` verschiebt es wirklich nach `Images\_papierkorb\`. Voreingestellt sind 30 Tage, `--days 60` ändert das. Verschont bleibt automatisch jede Datei, die im Ledger steht, in einer Datei unter `reference\` namentlich zitiert wird, oder in der Galerie einen Favoriten, eine Bewertung oder eine Notiz trägt. Gelöscht wird nie, nur verschoben.

Jedes PNG trägt seinen kompletten Workflow in den Metadaten: ziehst du es später per Drag-and-drop auf die ComfyUI-Fläche, ist der Graph mit Prompt und Seed wieder da. Das ist das Archiv, aus dem am 15.08. die 29 Katalog-Motive neu freigestellt wurden, ohne ein einziges Bild neu zu erzeugen.

Behaltenswertes gehört als Hardlink nach `D:\Apps\Stability Matrix\Data\Images\library\<vertical>\` (`New-Item -ItemType HardLink -Path <library-Ziel> -Target <Bildpfad>`), dann findet es der Ledger-Recall wieder und die Bibliothek hält jede Datei nur einmal.

## 5. Fallen, die Zeit kosten

- **Das freigestellte PNG sieht grün aus.** Workflow 01 und 02 behalten die Hintergrundfarbe in den RGB-Werten und setzen nur den Alpha-Kanal auf durchsichtig. Windows-Fotoanzeige und viele Editoren zeigen dann Grün. Die Transparenz ist trotzdem da, geprüft am Beispiel: Rand-Alpha 0, Motiv-Alpha 255. Zum Prüfen ein Programm nehmen, das Alpha kann (Browser, GIMP, Krita, Figma).
- **Deutsche Schrift im Bild wird falsch.** Qwen setzt englischen Text fehlerfrei, deutsche Wörter kippen in einzelnen Buchstaben ("Weengut"), und 05 kann das nicht reparieren. Für Kundenmaterial die Typografie im Layout setzen.
- **Zu dunkel oder zu kalt?** In 10 gibt es dafür einen eigenen Regler. WARM_LORA zwischen +0.5 und +1.5 macht das Bild heller und wärmer, ohne Feinstruktur zu kosten, gemessen 103 auf 144. Das kann sonst nichts: in 09 kostet der Detail-Slider Struktur, und Hell-Wörter im Prompt verschieben die Bildkomposition mit. Achtung, die Civitai-Seite nennt -6 bis +3, das ist zu weit gegriffen, bei +3 ist alles orange.

**Format ist kein freies Feld.** SD-Modelle haben eine Auflösung, auf die sie trainiert sind. Illustrious (06) unter 1024 wird matschig, Qwen (04) rechnet nativ auf 1328. Die Kurzanleitung nennt je Workflow die sicheren Werte, größer wird über 03.
- **Negativ-Prompt bei Z-Image und Qwen gibt es nicht.** Diese Workflows (00, 01, 04, 05, 07) laufen mit cfg 1.0, ein Negativ-Feld würde nicht wirken und ist deshalb gar nicht im Graphen.
- **Nur ein Bildprogramm gleichzeitig.** Die Karte hat 16 GB, Z-Image und die Qwen-Modelle belegen jeweils den größten Teil. ComfyUI, SwarmUI und Forge starten eigene Backends, parallel laufen sie sich gegenseitig aus dem Speicher.
- **INT8-Modelle von Civitai:** auf ComfyUI 0.25.1 brachen sie mit `KeyError: int8_tensorwise` ab, seit 0.36.0 ist das ungetestet. BF16 oder FP8 ist der sichere Griff.
- **Beim ersten Öffnen zeigt ComfyUI seinen eigenen Beispiel-Workflow**, der ein Modell verlangt, das hier nicht liegt, und deshalb rot meckert. Einfach ignorieren und einen gen-asset-Workflow laden.
- **Kein Modell wechseln, ohne den Rest anzupassen.** Ein Danbooru-Prompt an Z-Image oder ein Z-Image-Modell im SDXL-Graphen liefert Matsch. Welches Modell wofür taugt und was lizenzrechtlich gilt, steht in [models.md](models.md).

## 6. Eigene Workflows behalten

Änderst du einen Graphen und willst ihn behalten: **Workflow, Save As**, unter eigenem Namen. Speichere nicht über die gen-asset-Dateien, die werden aus den Vorlagen neu erzeugt und dabei überschrieben:

```powershell
& "D:\SDKs\Python311\python.exe" "C:\Users\Marcus\.claude\skills\gen-asset\scripts\api_to_ui_workflow.py" --all --out-dir "D:\Apps\Stability Matrix\Data\Packages\ComfyUI\user\default\workflows\gen-asset"
```

Der Befehl baut die neun Oberflächen-Workflows aus den API-Vorlagen in `workflows\*.api.json` neu. Nötig ist er nur, wenn eine Vorlage sich ändert oder ein Node-Paket dazukommt. ComfyUI muss dabei laufen, der Konverter holt die Knoten-Definitionen vom Server.

## 7. Was heute fehlt

- **ControlNet und IPAdapter sind nicht installiert.** Damit lässt sich weder eine Pose oder Silhouette vorgeben noch ein Referenzbild als Stilvorlage anhängen. Für eine Serie mit konsistenter Figur ist das die entscheidende Lücke. Teilersatz: 05 bearbeitet ein vorhandenes Bild gezielt.
- **Kein img2img-Workflow für Illustrious.** Komposition lässt sich dort per Text kaum steuern, die guten Civitai-Beispiele sind fast alle aus einer Bildvorlage entstanden.
- **LoRAs:** installiert sind nur die Turbo- und Lightning-LoRAs der Qwen-Modelle. Weitere lassen sich mit dem Civitai-Token direkt laden (Liste in models.md), eingehängt wird über einen LoRA-Knoten, den es in den Vorlagen noch nicht gibt.
- **Kein Inpainting- und kein Gesichts-Nachschärf-Workflow**, obwohl das Impact Pack dafür installiert ist.
- **Kein Video.**

## 8. Andere Oberflächen

Stability Matrix hat neben ComfyUI noch **SwarmUI**, **Forge Neo** und **InvokeAI** installiert. SwarmUI ist die bequemste davon (ein Eingabefeld statt Knotengraph) und greift laut seiner Konfiguration auf dieselben Modellordner zu, gestartet und geprüft wurde es bisher nicht. Es fährt beim Start eine eigene ComfyUI-Instanz hoch, also vorher die andere beenden (Punkt 5).
