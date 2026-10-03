---
name: bs-doc-meeting
description: >-
  Rohnotizen aus einem Termin in Entscheidungen, Aufgaben und offene Punkte
  zerlegen, mit Verantwortlichem und Termin, dazu die Lücken benennen statt
  sie zu füllen. Trennt sauber, was beschlossen wurde, von dem was jemand nur
  gesagt hat. Laden bei: "hier meine Notizen vom Termin", "fass das Meeting
  zusammen", "mach ein Protokoll draus", "was wurde eigentlich entschieden",
  "was ist daraus offen", "Nachbereitung", "Jour fixe", "Abstimmung mit dem
  Kunden", "Gesprächsnotiz", "was muss ich nachhalten", "wer macht was bis
  wann"; ebenso bei einem fremden Protokoll, das auf Lücken geprüft werden
  soll. NICHT für die Ablage von Fachwissen (dafür der Befehl /note), NICHT
  für die Pflege des Aufgabenboards (dafür /task), NICHT für Fachkonzepte und
  Anforderungen (dafür bs-sap-spec).
---

# Termin-Nachbereitung

Der Wert liegt nicht in der Zusammenfassung. Er liegt in der Trennung von
vier Dingen, die in Rohnotizen ununterscheidbar durcheinanderstehen:

1. **Entschieden** wurde etwas, wenn jemand Entscheidungsbefugter es gesagt hat
   und niemand widersprochen hat.
2. **Zugesagt** hat jemand etwas, wenn eine Person und eine Handlung erkennbar
   sind.
3. **Gesagt** hat jemand etwas, was weder das eine noch das andere ist:
   Meinungen, Einschätzungen, Absichtserklärungen.
4. **Offen** ist, was gefragt wurde und keine Antwort bekommen hat.

Der teuerste Fehler ist, Kategorie 3 als Kategorie 1 zu protokollieren. "Wir
sollten das mal angehen" ist keine Entscheidung. Wer es als eine aufschreibt,
erzeugt vier Wochen später einen Streit darüber, was vereinbart war.

## Vorgehen

1. **Alles einmal durchgehen** und jeder Aussage eine der vier Kategorien
   zuordnen. Was in keine passt, fliegt raus.
2. **Bei jeder Aufgabe drei Felder prüfen**: wer, was, bis wann. Fehlt eines,
   wird es als Lücke markiert, nicht ergänzt.
3. **Bei jeder Entscheidung prüfen**, ob erkennbar ist, wer sie getroffen hat.
   Eine Entscheidung ohne Urheber ist eine Kategorie-3-Aussage.
4. **Offene Punkte mit dem Adressaten versehen.** Ein offener Punkt ohne
   jemanden, der ihn beantworten kann, ist nur eine Notiz.
5. **Ausgabe erzeugen** und die Lücken oben nennen, nicht unten.

## Die Regel gegen das Auffüllen

Rohnotizen sind lückenhaft. Die Versuchung ist, aus dem Zusammenhang zu
schließen, wer gemeint war oder bis wann etwas fällig ist. Genau das macht ein
Protokoll unbrauchbar, denn der Leser kann Ergänztes nicht von Notiertem
unterscheiden.

Deshalb: **keine Namen ergänzen, keine Termine schätzen, keine Beschlüsse
formulieren, die so nicht gefallen sind.** Wo etwas fehlt, steht `offen` mit
der Frage, die es klärt. Drei ehrliche Lücken sind besser als ein
vollständiges Protokoll, das an drei Stellen erfunden ist.

Ausnahme sind reine Formulierungsglättungen: aus "MB macht Doku bis Fr" wird
"Marcus Blum erstellt die Dokumentation bis Freitag", sofern die Kürzel im
selben Termin eingeführt wurden.

## Was nicht ins Protokoll gehört

- **Eigene Bewertungen.** Ob eine Entscheidung klug war, steht nicht im
  Protokoll. Wenn es gesagt werden muss, dann in einem getrennten Teil, der
  ausdrücklich als Einschätzung gekennzeichnet ist.
- **Vermutungen über Motive.** "Der Kunde will damit vermutlich Zeit
  gewinnen" ist eine Unterstellung, sobald sie geschrieben ist.
- **Stimmungen und Zwischentöne**, außer sie ändern eine Handlung. "Ablehnend"
  gehört rein, wenn der nächste Schritt davon abhängt.
- **Alles, was nur der Vollständigkeit dient.** Ein Protokoll wird unter
  Zeitdruck gelesen. Jede Zeile, die keine Handlung ändert, verdrängt eine,
  die es tut.

## Ausgabe

```
Termin:     wann, mit wem, Anlass
Entschieden
  - <Beschluss>. Entschieden von <wer>.
Zugesagt
  - <wer> <was> bis <wann>.
  - <wer> <was> bis offen  ← Termin fehlt
Offen
  - <Frage>. Zu klären mit <wer>.
Erwartet, nicht besprochen
  - <Punkt aus der Agenda ohne Ergebnis>
```

Der letzte Abschnitt fällt weg, wenn es keine Agenda gab. Er ist der
wertvollste, wenn es eine gab, denn übergangene Punkte fallen sonst niemandem
auf.

Danach in einem Satz: was als Nächstes passieren muss. Dazu, von wem es abhängt.

## Weitergabe und Vertraulichkeit

Vor dem Versenden zwei Fragen:

- **Geht das an Teilnehmer oder nach außen?** Ein internes Protokoll enthält
  Dinge, die in einer Kundenmail nichts verloren haben. Im Zweifel zwei
  Fassungen, deutlich getrennt.
- **Stehen Personendaten drin, die nicht hineinmüssen?** Namen von
  Teilnehmern gehören dazu. Alles Weitere über Personen fast nie.

Solange kein Firmenzugang mit Auftragsverarbeitungsvertrag besteht, gehören
Rohnotizen mit Kunden- oder Firmenbezug überhaupt nicht in ein KI-Werkzeug.
Das ist keine Vorsichtsmaßnahme, sondern die Vertragslage. Wenn Notizen dieser
Art auftauchen, weise darauf hin, bevor du sie verarbeitest.

## Wenn ein fremdes Protokoll geprüft wird

Dieselbe Zerlegung. Die Ausgabe ist dann eine Mängelliste:

- Welche Aufgaben haben keinen Verantwortlichen oder keinen Termin?
- Welche Beschlüsse sind so formuliert, dass zwei Leser sie verschieden
  verstehen können?
- Welcher Agendapunkt hat kein Ergebnis?
- Wo steht eine Meinung als Beschluss?

Das ist die häufigste Fundklasse und lohnt fast immer den kurzen Blick, bevor
ein Protokoll bestätigt wird.
