---
name: bs-doc-html
description: >-
  Erzeugt eigenständige HTML-Dokumente in einem festen, markenfreien Format:
  entweder als Arbeitsdokument zum Lesen (Analyse, Konzept, Antrag,
  Vorbereitung) oder als Referenzkarte zum Nachschlagen unter Belastung
  (Cheatsheet, Spickzettel, Übersicht). Beide offline lauffähig, druckbar, mit
  Hell- und Dunkelmodus. Diagramme entstehen als Inline-SVG statt Textwüste:
  Ablaufketten, Verzweigungen wie im Programmablaufplan, Systemgrenzen,
  Objektbeziehungen, Stufenleitern. Laden bei: "mach mir ein Cheatsheet",
  "Spickzettel", "Referenzkarte", "Übersicht als HTML", "fass das als Dokument
  zusammen", "bereite das auf", "stell das grafisch dar", "zeichne den
  Ablauf", "Flowchart", "PAP", "Diagramm dazu", "wie hängen die Objekte
  zusammen", "zum Nachschlagen", "zum Ausdrucken"; ebenso wenn
  ein vorhandenes Arbeitsdokument dieser Reihe erweitert wird. NICHT für
  Präsentationen im BlumSoft-Design mit Folien und Marke, dafür den Befehl
  /html. NICHT für Architekturdiagramme eines Repos gegen den laufenden Stand,
  dafür gen-diagram.
---

# Wissensdokument

Zweck ist, dass dasselbe Format nicht jedes Mal neu erfunden wird. Vor diesem
Skill existierten fünf Dokumente derselben Art in drei verschiedenen Layouts,
drei davon ohne Dunkelmodus. Das Gerüst liegt als Datei vor. Du lieferst den
Inhalt, nicht das CSS.

## Zwei Modi, eine Entscheidung

Die Frage lautet: **Wird das gelesen oder wird darin nachgeschlagen?**

| | Arbeitsdokument | Referenzkarte |
|---|---|---|
| Leser | liest von oben nach unten, einmal | sucht eine Stelle, unter Zeitdruck |
| Aufbau | Abschnitte, Absätze, Argumentation | Karten und Tabellen, kaum Fließtext |
| Länge | so lang wie nötig | passt gedruckt auf ein bis zwei Seiten |
| Auszeichnung | `<body>` ohne Klasse | `<body class="dense">` |
| Typischer Fall | Analyse, Konzept, Antrag, Vorbereitung | Transaktionen, Fehlerklassen, Prozessschritte, Kürzel |

Im Zweifel fragen. Ein Cheatsheet, das wie ein Aufsatz aussieht, ist unter
Belastung wertlos. Ein Konzept in Karten zerfällt in Stichpunkte ohne
Begründung.

## Ablauf

1. **Modus bestimmen** (siehe oben). Bei Erweiterung eines vorhandenen
   Dokuments dessen Modus übernehmen.
2. **`references/bausteine.html` lesen.** Dort stehen alle verfügbaren Blöcke
   mit ihrem Zweck. Keine eigenen Klassen erfinden.
3. **Diagramme entscheiden**, bevor der Text steht. Siehe unten.
4. **Inhalt schreiben**, nur den Teil zwischen den Markierungen. Layout, CSS
   und Umschalter kommen aus `references/geruest.html`.
5. **Zusammensetzen**: Gerüst lesen, `<!-- INHALT -->` durch den eigenen
   Inhalt ersetzen, `<title>` setzen, als eigene Datei schreiben.
6. **Ansehen**, siehe Selbstprüfung. Ohne Screenshot ist es nicht fertig.

Für Schritt 5 reicht ein kurzes Python- oder PowerShell-Einzeiler, kein
Bauskript. Datei immer als UTF-8 ohne BOM schreiben.

## Wann ein Diagramm hingehört

Ein Diagramm ist teuer in der Herstellung und wertlos, wenn es dasselbe sagt
wie der Text daneben. Es lohnt genau dann, wenn der Leser sonst eine Reihenfolge,
eine Verzweigung oder eine Zuordnung im Kopf konstruieren müsste.

**Nimm ein Diagramm**, wenn eine dieser Fragen im Raum steht:

- In welcher Reihenfolge passiert was? Wo wechselt die Zuständigkeit?
- Wovon hängt ab, wie es weitergeht?
- Was läuft in welchem System? Was wird dabei übergeben?
- Was hängt womit zusammen, in welcher Vielfachheit?
- Was ist besser, was ist letzte Wahl?

**Lass es weg**, wenn der Sachverhalt eine Liste ist, wenn er aus zwei
Elementen besteht. Ebenso wenn derselbe Inhalt darunter nochmal in Prosa steht.
Eine Tabelle schlägt ein schlechtes Diagramm immer.

Die fünf Muster samt fertigem SVG stehen in `references/diagramme.md`. Sie
werden kopiert und beschriftet, nicht neu erfunden. Farben ausschließlich über
die `d-*`-Klassen, sonst verschwindet das Diagramm im Dunkelmodus.

## Aufbauregeln

**Beide Modi:**

- Der Titel benennt den Gegenstand, nicht die Gattung. "Fehleranalyse im
  Hintergrundbetrieb" statt "Übersicht".
- Kein Beiwerk vor dem Inhalt. Was der Leser sucht, steht ohne Scrollen da.
- Interne und zeigbare Teile werden mit `tag-int` und `tag-ext` markiert,
  sobald ein Dokument beides enthält, dazu ein Warnkasten ganz oben.
- Jede Zahl, jeder Transaktionscode, jeder Paketname trägt entweder einen Beleg
  oder eine Kennzeichnung als ungesichert. Erfundene Details in einem
  Nachschlagewerk sind schlimmer als eine Lücke.

**Nur Referenzkarte:**

- `<body class="dense">` setzen.
- Karten in `.cards` statt Abschnitte. Drei bis fünf Wörter je Zeile, keine
  Sätze mit Nebensatz.
- Was der Leser am häufigsten sucht, steht oben links.
- Tastenkürzel und Codes in `.kbd`, Zustände in `.pill`.
- Am Ende prüfen, ob es gedruckt auf ein bis zwei Seiten passt. Wenn nicht,
  ist zu viel drin. Dann fliegt der seltenste Block raus.

## Selbstprüfung, vor "fertig"

```
node ~/.claude/scripts/shot.js "<datei>" -o pruef.png --full
```

Dann das Bild ansehen und diese fünf Dinge prüfen:

1. **Diagramme**: keine überlappende oder abgeschnittene Beschriftung, alle
   Pfeilspitzen sichtbar, jede Linie endet an einem Kasten und nicht im Leeren.
2. **Dunkelmodus**: Taste T, erneut ansehen. Hartkodierte Farben fallen hier auf.
3. **Schmal**: `--viewport 420x900`. Nichts darf seitlich überlaufen.
4. **Erste Bildschirmseite**: steht dort der Inhalt oder nur Vorspann?
5. **Sprache**: echte Umlaute, kein Komma vor "und", "oder", "aber", keine
   Gedankenstriche.

Ein Prüfskript ersetzt den Blick nicht. Beim letzten Durchlauf meldete die
Tag-Zählung ein sauberes Dokument, während im Diagramm eine Beschriftung über
einem Kasten lag und zwei Pfeilspitzen fehlten.

## Ablage

Neben die Quelle, aus der der Inhalt stammt. Sonst in den Ordner, den der Nutzer
nennt. Dateiname sprechend und mit echten Umlauten. Den erzeugten Pfad immer
im Chat ausgeben.

Enthält das Dokument Kunden- oder Personendaten, gehört es nicht in einen
Ordner, der geteilt wird. Der Warnkasten oben sagt das dann ausdrücklich.
