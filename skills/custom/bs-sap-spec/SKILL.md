---
name: bs-sap-spec
description: >-
  Fachkonzepte, Feinkonzepte, Anforderungs- und Änderungsdokumente im
  SAP-Umfeld schreiben oder prüfen. Der Kern ist das Finden von Lücken:
  fehlende Fehlerfälle, fehlende Abgrenzung, nicht prüfbare
  Abnahmekriterien, Widersprüche zwischen Abschnitten. Laden, sobald ein
  fachliches Dokument entsteht oder beurteilt wird: "schreib ein
  Fachkonzept", "prüf das Konzept", "ist die Spezifikation vollständig",
  "der Kunde hat eine Anforderung geschickt", "kannst du daraus ein
  Konzept machen", "was fehlt hier noch", "Feinkonzept für die
  Entwicklung", "Change Request bewerten", "Anforderung aufnehmen",
  "User Story ausformulieren"; ebenso wenn aus Gesprächsnotizen oder
  einem Protokoll eine belastbare Vorgabe werden soll. Nicht für reine
  Angebots- oder Vergabetexte.
---

# Fachkonzept schreiben und prüfen

Ein Fachkonzept hat genau eine Aufgabe: dass Entwicklung und Test daraus
dasselbe verstehen wie der Fachbereich. Alles andere ist Beiwerk.

Daraus folgt die wichtigste Regel für beide Modi: **Eine plausibel
zugetextete Lücke ist schlimmer als eine sichtbare.** Wo etwas fehlt, wird
nachgefragt. Wo etwas Plausibles steht, wird gebaut. Erfinde deshalb nie
eine fachliche Regel, eine Zahl oder einen Sonderfall, um einen Abschnitt
zu füllen. Markiere die Stelle stattdessen als offen und nenne die Frage,
die zu klären ist.

## Modus erkennen

**Prüfen** ist der häufigere Fall. Es liegt ein Dokument vor. Gefragt ist
nicht eine Zusammenfassung, sondern was fehlt, was mehrdeutig ist, was
sich widerspricht. Fass nicht zusammen, was ohnehin dasteht.

**Schreiben** heißt: aus Notizen, Protokoll, Mailverlauf oder Zuruf ein
Dokument bauen. Trenne dabei sichtbar, was aus der Quelle stammt, von
dem, was du ergänzt hast.

## Aufbau

Für ein Änderungs- oder Entwicklungskonzept. Kürze, was nicht zutrifft. Sag
dazu, dass du gekürzt hast. Streich keinen Abschnitt stillschweigend,
denn genau die weggelassenen sind die, die später fehlen.

1. **Anlass und Ziel.** Warum das gemacht wird, woran der Erfolg gemessen wird.
2. **Ist-Situation.** Wie es heute läuft, einschließlich der Umgehungslösungen.
3. **Soll-Prozess.** Ablauf mit Auslöser, Schritten, Ergebnis, Beteiligten.
4. **Fachliche Regeln.** Die eigentliche Substanz: Bedingungen, Berechnungen,
   Prüfungen, Statusübergänge. Jede Regel prüfbar formuliert.
5. **Betroffene Objekte.** Belegarten, Geschäftsobjekte, Felder, Tabellen,
   Customizing-Einstellungen.
6. **Schnittstellen.** Richtung, Auslöser, Format, Fehlerbehandlung, wer bei
   einer Störung was tut.
7. **Berechtigungen.** Wer darf auslösen, sehen, ändern, freigeben.
8. **Altdaten.** Was passiert mit vorhandenen Sätzen. Wird migriert, umgesetzt
   oder bewusst nichts getan.
9. **Mengengerüst.** Sätze je Lauf, Spitzen, erwartete Laufzeit. Ohne das ist
   keine Aussage über Performance oder Aufwand möglich.
10. **Abgrenzung.** Was ausdrücklich nicht Teil ist. Der meistvergessene und
    im Streitfall wertvollste Abschnitt.
11. **Annahmen und offene Punkte.** Mit Zuständigkeit und Frist.
12. **Abnahmekriterien.** So formuliert, dass ein Tester sie ohne Rückfrage
    prüfen kann.

## Lückenkatalog

Diese Punkte fehlen in der Praxis am häufigsten. Geh sie beim Prüfen einzeln
durch statt frei zu lesen, denn beim freien Lesen übersieht man genau das,
was gar nicht dasteht.

**Fehlerfälle.** Beschrieben ist der Happy Path. Was passiert bei fehlenden
Pflichtfeldern, gesperrten Sätzen, abgelehnter Prüfung, Abbruch mitten im
Lauf, doppeltem Aufruf? Ist ein zweiter Lauf ungefährlich?

**Sonderfälle der Daten.** Storno und Rücknahme, Teilmengen, Nullwerte,
negative Beträge, Fremdwährung, mehrere Sprachen, mehrere Buchungskreise
oder Mandanten, Sätze mit historischem Stand.

**Zeitliche Aspekte.** Stichtage, Fristen, Rückwirkung, was bei einer Änderung
mit bereits laufenden Vorgängen geschieht.

**Zuständigkeit.** Zu jedem manuellen Schritt gehört eine Rolle. "Es wird
geprüft" ist keine Vorgabe.

**Nicht prüfbare Kriterien.** "Soll performant sein", "benutzerfreundlich",
"zeitnah". Frag nach der Zahl. Ohne Zahl ist es kein Abnahmekriterium.

**Widersprüche.** Vergleiche Abschnitte gegeneinander, besonders Soll-Prozess
gegen fachliche Regeln gegen Abnahmekriterien. Widersprüche entstehen fast
immer beim Überarbeiten eines älteren Dokuments.

**Begriffe.** Wird dasselbe durchgehend gleich benannt? Uneinheitliche
Begriffe sind kein Stilproblem, sie führen dazu, dass zwei Leser
unterschiedliche Dinge bauen.

**Im öffentlichen Sektor zusätzlich:** Rechtsgrundlage der Regel, Fristen und
ihre Berechnung, Bescheiderstellung, Widerspruch und Rücknahme, Rückforderung,
Aufbewahrung, Nachweispflichten.

## Ausgabe beim Prüfen

Nach Wirkung sortiert, nicht nach Reihenfolge im Dokument.

```
[Schwere] Was fehlt oder widersprüchlich ist
Stelle:   Abschnitt oder Zitat
Folge:    was in Entwicklung oder Test daraus entsteht
Frage:    die konkrete Frage an den Fachbereich
```

Schweregrade: **blockierend** (so nicht entwickelbar, es würde geraten),
**hoch** (führt absehbar zu Nacharbeit), **mittel** (Klärung vor Abnahme),
**niedrig** (Verständlichkeit).

Am Ende eine Liste der Fragen in der Form, in der man sie ohne Umbau in eine
Mail an den Fachbereich übernehmen kann. Das ist der Teil, der tatsächlich
weiterverwendet wird.

## Ausgabe beim Schreiben

Das Dokument selbst, in der obigen Struktur. Danach getrennt:

- **Übernommen aus der Quelle:** stichwortartig, damit nachvollziehbar bleibt,
  was belegt ist.
- **Von mir ergänzt:** jede Ergänzung mit Begründung. Das sind die Stellen, an
  denen der Fachbereich widersprechen muss.
- **Offen:** was nicht ergänzt werden konnte, mit der zugehörigen Frage.

Nutz im Dokument selbst eine erkennbare Markierung für offene Stellen, etwa
`[OFFEN: ...]`. Sie muss beim Überfliegen ins Auge fallen, sonst wandert sie
ungeklärt in die Entwicklung.
