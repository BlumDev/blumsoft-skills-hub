---
name: bs-sap-abap-review
description: >-
  ABAP-Code prüfen und verbessern: Korrektheit, Performance, Berechtigungen,
  Testbarkeit. Findet die Fehlerklassen, die im Produktivbetrieb wirklich
  wehtun. Unterdrückt Stil-Nits. Laden, sobald ABAP-Quelltext im Spiel ist und
  beurteilt, erklärt, aufgeräumt oder erweitert werden soll: "schau dir den
  Report an", "review", "warum ist das langsam", "prüf mal die Logik",
  "Code-Review für den Kollegen", "kannst du das erklären", "was macht dieser
  FORM", "ist das so sauber", "vor dem Transport drübergucken";
  ebenso bei Performance-Beschwerden, sobald die betroffene Stelle bekannt ist
  ("dieser Report läuft ewig", "die Schleife hier ist langsam"); ebenso wenn
  vorhandener Code um eine Funktion erweitert werden soll. Gilt für Reports,
  Klassen, Funktionsbausteine, Methoden, Enhancements, BAdIs, CDS-Views und
  AMDP. Nicht für reine Syntaxfragen ohne Code. NICHT laden, solange die
  Fundstelle erst gesucht wird (Kurzdump, abgebrochener Job, verschwundene
  Buchung, Fehlermeldung ohne bekannten Ort), dafür bs-sap-support.
---

# ABAP-Review

Ein Review ist nur so viel wert wie sein schlechtester Befund. Zwanzig
Stilhinweise mit einem echten Fehler dazwischen sind schlechter als drei
belegte Befunde, weil der Leser aufhört zu lesen. Priorisiere hart und lass
weg, was du nicht belegen kannst.

## Reihenfolge

Arbeite in dieser Folge, weil ein Korrektheitsfehler jede Performance-Aussage
wertlos macht und Stil erst zählt, wenn der Rest sitzt.

1. **Verstehen.** Was soll der Code fachlich tun? Steht das irgendwo oder
   leitest du es aus dem Code ab? Sag es dazu, wenn du es ableitest.
2. **Korrektheit und Daten**
3. **Performance**
4. **Berechtigungen und Sicherheit**
5. **Testbarkeit und Wartbarkeit**
6. **Stil**, nur wenn er die Lesbarkeit ernsthaft behindert

## Was wirklich zählt

### Korrektheit und Daten

- `SELECT SINGLE` ohne vollständigen Schlüssel. Liefert einen beliebigen Satz,
  fällt jahrelang nicht auf und dann im falschen Moment.
- Fehlende `sy-subrc`-Prüfung nach `SELECT`, `READ TABLE`, `CALL FUNCTION`,
  `AUTHORITY-CHECK`. Besonders bei `READ TABLE`, weil die Arbeitsstruktur dann
  den alten Inhalt behält statt leer zu sein.
- Annahme über Reihenfolge ohne `ORDER BY` oder `SORT`. Die Datenbank darf jede
  Reihenfolge liefern. Sie ändert sie beim Wechsel des Ausführungsplans.
- Währungs- und Mengenfelder: Betrag ohne zugehörige Währung verarbeitet oder
  Dezimalverschiebung nach `TCURX` nicht berücksichtigt. Der Fehler taucht nur
  bei Währungen ohne zwei Nachkommastellen auf, also spät.
- Datum und Zeit: Systemzeit statt Anwenderzeitzone, Monatsarithmetik von Hand
  statt über Funktionsbaustein.
- Typkonvertierung und Längenüberlauf bei `MOVE` zwischen unterschiedlichen
  Typen, gekürzte Schlüssel bei `CONCATENATE`.
- Änderungen an internen Tabellen innerhalb einer Schleife über dieselbe
  Tabelle.

### Performance

Die Reihenfolge hier ist nach tatsächlichem Schaden sortiert.

- **`FOR ALL ENTRIES` ohne Prüfung, ob die Treibertabelle gefüllt ist.** Ist sie
  leer, entfällt die gesamte `WHERE`-Bedingung und der Zugriff liest die Tabelle
  vollständig. Das ist der häufigste Grund für einen Kurzdump im Produktivsystem
  bei Code, der im Test lief.
- `SELECT` innerhalb einer Schleife. Ersetzen durch Join, `FOR ALL ENTRIES` oder
  vorgelagertes Lesen in eine sortierte Tabelle.
- `FOR ALL ENTRIES` ohne vorheriges Entfernen von Duplikaten in der
  Treibertabelle.
- `WHERE`-Bedingung, die keinen Index bedient: führende Schlüsselfelder fehlen
  oder es wird mit `LIKE '%...'` gesucht. Nenne den Index, den du erwartest.
- `SELECT *` statt Feldliste, besonders bei breiten Tabellen wie BSEG oder VBAP.
- `READ TABLE ... WITH KEY` auf einer Standardtabelle innerhalb einer Schleife.
  Linearer Zugriff mal Schleifenlänge. Sortierte oder Hash-Tabelle verwenden.
- Verschachtelte Schleifen über große Mengen ohne Schlüsselzugriff.
- Datenbankzugriff in PBO, in einer Schleife über Bildschirmelemente oder in
  einer Konvertierungsroutine.
- Mengengerüst prüfen: bei fünfzig Sätzen ist vieles egal, bei fünf Millionen
  nichts. Frag danach, wenn es nicht dabei steht.

### Berechtigungen und Sicherheit

- Fehlender `AUTHORITY-CHECK` vor Anzeige oder Änderung geschützter Daten.
  Ebenso einer, dessen `sy-subrc` niemand auswertet.
- Dynamisches SQL oder dynamische `WHERE`-Bedingung aus Benutzereingabe.
- Datei- und Verzeichniszugriffe ohne Prüfung des übergebenen Pfads.
- Hart kodierte Benutzer, Mandanten, Systemnamen oder Kennwörter.
- `CLIENT SPECIFIED` ohne erkennbaren Grund.

### Testbarkeit und Wartbarkeit

- Datenbeschaffung und fachliche Logik in derselben Routine. Ohne Trennung ist
  kein ABAP-Unit-Test möglich, ohne echte Daten anzulegen.
- Nicht abgefangene Ausnahmen. Ebenso leere `CATCH`-Blöcke, die einen Fehler
  verschlucken.
- Wiederholter identischer Block an mehreren Stellen. Nur melden, wenn es
  wirklich derselbe Fall ist, nicht bei zufälliger Ähnlichkeit.
- Namen, die etwas anderes sagen als der Code tut. Das ist ein echter Befund,
  weil daran später jemand scheitert.

## Falschmeldungen vermeiden

Bevor ein Befund in die Ausgabe geht, prüf ihn gegen dich selbst: Kannst du
einen konkreten Ablauf beschreiben, bei dem er zu falschem Ergebnis, Abbruch
oder spürbarer Laufzeit führt? Wenn nicht, ist es kein Befund sondern eine
Beobachtung. Die gehört allenfalls in eine Randnotiz.

Häufige Fehlurteile, die es zu vermeiden gilt:

- Etwas als fehlend melden, was in einer aufgerufenen Routine passiert, die du
  nicht gesehen hast. Sag stattdessen, dass du sie nicht kennst.
- Modernisierung um ihrer selbst willen vorschlagen (`FORM` zu Methode, interne
  Tabelle mit Kopfzeile, `MOVE` zu `=`). Nur melden, wenn es an dieser Stelle
  einen konkreten Nutzen hat.
- Performance-Aussagen ohne Mengenannahme.
- Kundeneigene Namenskonventionen als falsch bewerten, ohne sie zu kennen.

## Ausgabe

Sortiert nach Schwere, keine Nummerierung von Kleinkram. Je Befund vier Zeilen:

```
[Schwere] Kurzer Titel
Fundstelle: Zeile oder Routine
Wirkung:    was konkret passiert, mit dem auslösenden Fall
Vorschlag:  die Änderung, wenn möglich als Codeausschnitt
```

Schweregrade: **kritisch** (falsches Ergebnis, Abbruch, Datenverlust,
Sicherheitslücke), **hoch** (Laufzeit oder Sperren im Produktivbetrieb),
**mittel** (Wartbarkeit, Testbarkeit), **niedrig** (Randnotiz).

Danach ein Absatz mit dem, was gut ist, sofern es zutrifft. Nicht als
Höflichkeit, sondern damit klar wird, was beim Umbau erhalten bleiben soll.

Zum Schluss offene Fragen, die du nicht selbst beantworten konntest: fehlendes
Mengengerüst, unbekannte aufgerufene Routinen, unklare fachliche Absicht.

## Werkzeuge, die vor dem manuellen Review laufen sollten

Was eine Maschine findet, gehört nicht in ein Review von Hand. Erst
automatisch prüfen, dann die Zeit auf das verwenden, was nur ein Mensch sieht.

- **ATC** ist der Standard und läuft im ADT direkt am Objekt.
- **code pal for ABAP** von SAP erweitert ATC um konfigurierbare Prüfungen zu
  Clean Code, etwa Methodenlänge, Verschachtelungstiefe und Testabdeckung.
- **abapOpenChecks** ist die verbreitete Sammlung zusätzlicher Prüfungen für
  Code Inspector und ATC aus der Community.
- **Clean ABAP** aus dem SAP-Styleguide ist die Referenz, auf die sich
  Diskussionen über Stil zurückführen lassen. Ein Verweis darauf beendet
  Geschmacksdebatten schneller als eine eigene Begründung.

Läuft im Haus keines davon, ist das selbst ein Befund. Allerdings ein
organisatorischer. Er gehört in die Randnotizen, nicht in die Befundliste zum
geprüften Objekt.

## Wenn Code erweitert statt geprüft wird

Erst den vorhandenen Stil erfassen und ihn übernehmen, auch wenn er nicht dem
entspricht, was du selbst schreiben würdest. Ein Report in einheitlich altem
Stil ist wartbarer als einer mit zwei Handschriften. Nenne den Stilbruch als
Randnotiz, statt ihn ungefragt zu beheben.
