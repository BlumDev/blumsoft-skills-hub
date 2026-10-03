---
name: bs-sap-estimate
description: >-
  Aufwände für SAP-Entwicklung und Beratung schätzen: zerlegen, Nebenaufwände
  vollständig erfassen, Bandbreite statt Punktzahl, jede Annahme sichtbar
  machen. Verhindert die belegten Fehlerquellen: vergessene Positionen,
  Anker durch eine vorher genannte Zielzahl, addierte Puffer. Laden, sobald
  eine Zahl für Zeit, Tage oder Geld gefragt ist: "wie lange dauert das",
  "schätz das mal", "was kostet die Anforderung", "Aufwand für den Change
  Request", "Personentage für das Angebot", "können wir das bis Ende Q3",
  "grobe Hausnummer", "der Kunde will eine Indikation"; ebenso beim Bewerten
  fremder Schätzungen ("ist das realistisch", "der Kollege sagt fünf Tage")
  und beim Nachkalkulieren nach Projektende. Auch bei bewusst grober
  Ersteinschätzung anwenden, denn gerade die wird später zitiert.
---

# Aufwandsschätzung

Eine Schätzung wird später zitiert, meistens ohne ihren Kontext. Deshalb ist
die Zahl der kleinere Teil der Arbeit. Der größere sind die Positionen, die
überhaupt erst zur Zahl führen, dazu die Annahmen, unter denen sie gilt.

## Was die Empirie sagt

Vier Befunde bestimmen das Vorgehen unten. Sie sind der Grund für Regeln, die
sonst wie Bürokratie aussehen.

**Kein Verfahren schlägt die Expertenschätzung.** Jørgensen und Shepperd haben
184 Arbeiten geprüft, die formale Schätzmodelle einführen und evaluieren.
Keines schlug erfahrene Schätzer systematisch. Function Points, COCOMO und
Planning Poker sind daher keine besseren Werkzeuge, sondern andere. Wer eine
Zahl braucht, fragt die Person, die es umsetzt.

**Die Schwachstelle ist nicht Inkompetenz, sondern Inkonsistenz und Anker.**
Dieselbe Person schätzt dieselbe Aufgabe zu verschiedenen Zeitpunkten
unterschiedlich. Und eine vorher gehörte Zahl (Kundenerwartung, Budget,
Wunschtermin) verschiebt die Schätzung um bis zu Faktor zwei, auch bei
Profis, auch wenn sie ausdrücklich als irrelevant deklariert wird. Deshalb:
erst schätzen, dann über den Preis reden.

**Puffer je Arbeitspaket darf man nicht addieren.** Die Summe der
pessimistischen Werte ist nicht der pessimistische Wert der Summe. In
Experimenten mit überwiegend Software-Profis lagen die so gebildeten
Intervalle rund 150 Prozent zu breit. Die Mehrheit der Teilnehmer addierte
trotzdem naiv. Ein Angebot, das so entsteht, ist entweder zu teuer oder wird
falsch verstanden. Puffer gehört einmal auf Projektebene.

**Prozentaufschläge schützen nicht gegen den Fall, der wehtut.** Über 5.000
untersuchte IT-Vorhaben zeigen: der Median liegt punktgenau im Budget, der
Mittelwert bei 73 Prozent darüber. Rund 18 Prozent überschreiten extrem, im
Schnitt um mehr als das Vierfache. IT ist der einzige von 23 untersuchten
Projekttypen, dessen Verteilung so schwer nach oben ausläuft, dass ein
Durchschnittsaufschlag statistisch instabil wird. Gegen dieses Risiko hilft
kein Prozentsatz, sondern Zerlegung in eigenständig nutzbare Teilergebnisse
und harte Stop-Kriterien.

**Was dagegen nachweislich hilft:** historische Ist-Daten plus eine
Schätz-Checkliste, mehrere unabhängige Schätzungen, sowie Bottom-up und
Top-down getrennt gerechnet. Genau das ist das Vorgehen unten.

## Vorgehen

1. **Verstehen und abgrenzen.** Was gehört dazu, was ausdrücklich nicht. Ohne
   Abgrenzung ist jede Zahl angreifbar.
2. **Nach der Zielzahl nicht fragen.** Wenn ein Budget oder ein Wunschtermin
   bereits im Raum steht, schätze trotzdem zuerst unabhängig und vergleiche
   danach. Das ist der billigste Hebel im ganzen Verfahren.
3. **Bottom-up zerlegen** in Positionen von höchstens zwei bis drei Tagen. Was
   du nicht zerlegen kannst, hast du nicht verstanden.
4. **Top-down gegenrechnen**, unabhängig davon: Welches abgeschlossene
   Vorhaben ist vergleichbar, was hat es gekostet? Erst danach beide Werte
   nebeneinander legen. Liegen sie mehr als etwa 30 Prozent auseinander, ist
   die Zerlegung unvollständig oder die Analogie falsch gewählt. Dann
   Information nachziehen, nicht mitteln.
5. **Nebenaufwände ergänzen** anhand der Liste unten. Einzeln benennen statt
   prozentual aufschlagen, sonst fällt der Aufschlag in der ersten Verhandlung
   als Erstes weg.
6. **Risiken benennen** mit Wirkung auf die Zahl.
7. **Bandbreite ausweisen** statt einer Einzelzahl. Den Puffer einmal auf das
   Ganze setzen.

## Positionen, die regelmäßig fehlen

Diese Liste ist der wirksamste Teil des Verfahrens, weil Checklisten zu den
wenigen belegten Mitteln gegen Unterschätzung gehören. Geh sie einzeln durch.
Was nicht anfällt, ausdrücklich mit null ausweisen statt weglassen, denn eine
sichtbare Null zeigt dem Leser, dass daran gedacht wurde.

- **Fachliche Klärung** vor und während der Umsetzung. Rückfragen,
  Abstimmungen, Warten auf Entscheidungen. Bei Workflows und Formularen liegt
  hier erfahrungsgemäß der größere Teil, nicht im Bau.
- **Technisches Feinkonzept** und Abstimmung mit der Architektur.
- **Entwicklung** selbst.
- **Unit-Tests**, bei ABAP Unit einschließlich der Testdoppel für
  Datenbankzugriffe.
- **Code-Review und Qualitätssicherung**, einschließlich der Nacharbeit aus dem
  Review. In den Schätzvorlagen der Praxis steht das als eigene Position, in
  Schätzungen aus dem Bauch fehlt es fast immer.
- **Testfälle erstellen** und Testdaten beschaffen. Testdaten sind in
  gewachsenen Systemen regelmäßig der teuerste Einzelposten.
- **Testdurchführung** und Fehlerbehebung in mehreren Runden.
- **Transportwesen**: Anlegen, Freigeben, Nachziehen über die Systemlinie,
  Reihenfolgeabhängigkeiten.
- **Dokumentation** für Betrieb und Wartung.
- **Abnahmebegleitung** und Nacharbeit nach der Abnahme.
- **Übergabe und Schulung** von Key Usern oder Betrieb.
- **Projektbegleitung**: Statustermine, Berichte, Koordination.
- **Puffer für Wartezeiten**, die nicht in deiner Hand liegen: Freigaben,
  Systemverfügbarkeit, Zulieferung durch Dritte.

### Zur Frage, wie groß der Nicht-Entwicklungsanteil ist

Trenne hier zwei Ebenen, sonst vergleichst du Unvergleichbares.

**Auf Objektebene kursiert ein Multiplikator von rund 2,2 auf die reine
Bauzeit.** Der Bauanteil wird in den auffindbaren Quellen mit 40 bis 45 Prozent
angesetzt: in zwei SAP-Schätzwerkzeugen, bei COCOMO II über den gesamten
Entwicklungszyklus (42 bis 48 Prozent), bei ISBSG für neue Entwicklungen (41
Prozent). Als Erwartungshaltung ist das brauchbar: wer drei Tage Programmierung
sieht und drei Tage anbietet, liegt sicher falsch.

**Nutz diesen Faktor aber nicht als Gegenprobe.** In beiden offengelegten
Werkzeugen ist er keine Messung, sondern eine Konfigurationskonstante: über der
Tabelle steht die Faktorenliste, aus der er entsteht. Praktisch jede Zeile ist
schlicht die Bauzeit mal festen Anteilen. Wer seine Schätzung mit einer
Annahme prüft, die dieselbe Annahme ist, bestätigt sich immer selbst. Auch die
Übereinstimmung der Quellen untereinander beweist wenig, weil eine
herumgereichte Branchenkonvention genauso aussieht wie ein unabhängiger Befund.
Genau daran ist die 40-20-40-Regel gescheitert.

Die echte Gegenprobe ist die unabhängige Zweitschätzung oder der Vergleich mit
einem abgerechneten eigenen Projekt. Der eigentliche Ertrag dieser Werkzeuge
ist nicht ihr Faktor, sondern ihre Positionsliste.

**Auf Projektebene taugt keine Faustregel.** Dort messen die verbreiteten
Zahlen Verschiedenes: Codieren allein liegt in den Quellen bei 14 bis 20
Prozent, mit Detail-Design und Unit-Test (so rechnet COCOMO) bei 40 bis 58
Prozent, mit Anforderungsklärung und Design bei rund 40 bis 50 Prozent. Die
verbreitete Aussage "Entwicklung ist die Hälfte" benutzt meist den dritten
Schnitt und wird im ersten Sinn verstanden. So gelesen unterschätzt sie den
Nebenaufwand erheblich. Hinzu kommt: die größte Prüfung dieser Faustregeln an
rund 1.500 Projekten fand, dass nur sehr wenige Projekte überhaupt nahe an
einer solchen Regel liegen. Auf Projektebene kommen Steuerung, Architektur,
Migration und Abnahme dazu, die auf Objektebene gar nicht anfallen. Nimm dort
keine Prozentregel als Anker, sondern die Positionsliste.

## Risiken, die den Aufwand treiben

Benenne die zutreffenden ausdrücklich mit ihrer Wirkung, denn sie sind der
Grund für die obere Grenze der Bandbreite.

- Gewachsener Altcode ohne Dokumentation im betroffenen Bereich
- Modifikationen am Standard oder viele vorhandene Erweiterungen
- Schnittstellen zu Fremdsystemen, besonders mit fremder Zuständigkeit
- Migration oder Umsetzung von Altdaten
- Unklares Berechtigungskonzept
- Mehrere Entscheider oder ein Entscheider, der nicht greifbar ist
- Fehlende Testumgebung oder produktionsnahe Testdaten
- Der Kunde hat einen vergleichbaren Vorgang noch nie durchgeführt
- Fachliche Regeln, die erst im Verlauf entstehen

Geänderte Anforderungen sind über Jahrzehnte hinweg die meistgenannte Ursache
für Fehlschätzungen. Das ist kein Schätzproblem, sondern ein Vertragsproblem:
Scope-Änderung gehört als Änderung geregelt, nicht als Auslegungsfrage.

## Bandbreite

Nenne drei Werte in der Summe: optimistisch, wahrscheinlich, pessimistisch.
Der wahrscheinliche Wert ist nicht der Mittelwert, sondern der, den du bei
üblichem Verlauf erwartest.

Zwei Regeln dazu:

- **Nicht je Position puffern und aufaddieren.** Schätze je Position den
  erwarteten Wert und setze die Unsicherheit einmal auf das Ganze. Sonst
  entsteht eine Spanne, die viel zu breit ist und im Angebot unglaubwürdig
  wirkt.
- **Unsicherheit anders formulieren.** Die Frage "was ist das Minimum und was
  das Maximum" erzeugt nachweislich zu enge Intervalle. Frag stattdessen: "Wie
  wahrscheinlich ist es, dass es mehr als X wird?" Diese Formulierung eignet
  sich auch gegenüber dem Kunden besser als eine Min-Max-Angabe.

Die Spanne selbst ist die Information: Acht bis vierundzwanzig Tage sagt dem
Kunden, dass etwas geklärt werden muss, bevor er belastbar planen kann. Genau
das soll sie sagen. Runde nicht auf eine glatte Zahl, die vertrauenswürdig
wirkt. Wenn aus der Zerlegung siebzehn Tage kommen, dann sind es siebzehn.

**Die Spanne verengt sich nicht von selbst.** Das verbreitete Bild vom Trichter,
der mit Projektfortschritt schmaler wird, geht auf eine gezeichnete Annahme
zurück, nicht auf eine Messung. Die einzige veröffentlichte Nachmessung an
echten Projektdaten fand ein über den Verlauf nahezu konstantes
Unsicherheitsband. Verenge eine Bandbreite deshalb nur, wenn du benennen
kannst, welche Frage inzwischen beantwortet ist. Bloßer Fortschritt ist kein
Grund. Ein Risikoaufschlag, der nach Zeitplan sinkt, ist eine Gewohnheit ohne
Grundlage.

## Ausgabe

Eine Tabelle mit den Positionen, danach die Summenzeile mit der Bandbreite.
Darunter drei kurze Abschnitte:

- **Annahmen.** Nummeriert, jede so formuliert, dass sie widerlegbar ist. Diese
  Liste ist der eigentliche Schutz, wenn später jemand die Zahl zitiert.
- **Nicht enthalten.** Die Abgrenzung.
- **Was die Spanne verkleinert.** Welche Klärung welchen Teil der Unsicherheit
  auflöst. Das gibt dem Kunden eine Handlung statt nur einer Zahl.

## Fremde Schätzungen bewerten

Frag zuerst nach der Zerlegung. Gibt es keine, ist die Bewertung fertig: eine
Zahl ohne Zerlegung lässt sich nicht beurteilen, nur glauben. Gibt es eine,
prüf sie gegen die Positionsliste oben. Der Befund lautet fast immer, dass
Test, Abstimmung und Nacharbeit fehlen, nicht dass die Entwicklung falsch
geschätzt wurde.

Zweite Frage: Kannte die schätzende Person das Budget oder den Wunschtermin?
Wenn ja, ist die Zahl mit hoher Wahrscheinlichkeit daran gezogen.

## Kalibrierung

Der unbequemste Befund der Forschung: Mehr Berufserfahrung führte in den
Studien **nicht** zu besseren Schätzungen, weil in den meisten Organisationen
die Rückkopplung fehlt. Erfahrung ohne Soll-Ist-Vergleich verbessert nichts.

Trag deshalb nach jedem abgeschlossenen Vorgang den Ist-Aufwand gegen den
geschätzten in `references/kalibrierung.md` ein. Lies die Datei, bevor du
schätzt, sofern sie Einträge enthält. Nach wenigen Einträgen zeigt sich der
eigene systematische Fehler. Der ist wertvoller als jede Faustregel aus der
Literatur, weil er für die eigene Arbeit und die eigenen Kunden gilt.

Belege und Quellenlage zu den Befunden oben: BlumOps-Vault, Note zur
Aufwandsschätzung in der SAP-Entwicklung.
