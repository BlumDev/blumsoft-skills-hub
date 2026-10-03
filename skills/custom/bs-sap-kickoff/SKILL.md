---
name: bs-sap-kickoff
description: >-
  Eine neue SAP-Entwicklung sauber aufsetzen, bevor die erste Zeile entsteht:
  Muss überhaupt entwickelt werden, welche Erweiterungstechnik ist die
  richtige, wo landet das Objekt (Paket, Namensraum, Transport), klassisches
  ABAP oder ABAP Cloud, wie wird es geschnitten damit es testbar bleibt. Laden
  bei: "ich soll etwas Neues bauen", "wie fange ich das an", "neuer Report",
  "neue Klasse anlegen", "brauche einen Z-Baustein", "wie erweitere ich das",
  "gibt es dafür ein BAdI", "welches Paket", "Namensraum", "RAP oder
  klassisch", "Clean Core", "darf ich den Standard ändern", "Customer Exit",
  "Enhancement", "neues Template bauen"; ebenso beim Bewerten eines fremden
  Entwurfs ("der Kollege will das so bauen") und wenn eine Anforderung
  vorliegt und der technische Weg noch offen ist. NICHT laden für vorhandenen
  Quelltext (dafür bs-sap-abap-review), nicht für Fehlersuche (dafür
  bs-sap-support), nicht für die fachliche Spezifikation (dafür
  bs-sap-spec).
---

# SAP-Projektstart

Die teuersten Entscheidungen fallen in der ersten halben Stunde und werden
nie wieder angefasst: die Erweiterungstechnik, der Ort und der Schnitt. Ein
Programmierfehler kostet einen Tag. Ein Objekt an der falschen Stelle mit der
falschen Technik kostet es bei jedem Release erneut.

## Die Reihenfolge der Fragen

1. **Muss überhaupt entwickelt werden?**
2. **Wenn ja, mit welcher Technik greift es in den Standard ein?**
3. **Wo landet es?**
4. **Wie wird es geschnitten?**
5. **Woran erkennt man, dass es funktioniert?**

Die erste Frage wird am häufigsten übersprungen und spart am meisten.

## 1. Muss überhaupt entwickelt werden

Jede Eigenentwicklung ist eine Verbindlichkeit: sie muss gepflegt, getestet
und bei jedem Upgrade geprüft werden. Bevor eine entsteht, drei Prüfungen in
dieser Reihenfolge:

- **Customizing.** Deckt der Standard den Fall über Einstellungen ab? Diese
  Frage gehört an den Fachbereich oder an den Modulberater, nicht an die
  Entwicklung.
- **Standardfunktion, die niemand kennt.** Gerade in großen Modulen existieren
  Funktionen, die im Haus nie eingeführt wurden. Der Weg dorthin läuft über
  die Anwendungshierarchie und die Modulberatung, nicht über die Suche im
  Quelltext.
- **Bestehende Eigenentwicklung.** Gibt es schon etwas Ähnliches im
  Kundennamensraum? Eine Erweiterung des Vorhandenen ist fast immer besser als
  ein zweites Programm daneben.

Fällt die Entwicklung trotzdem an, halte den Grund schriftlich fest. Er wird
beim nächsten Upgrade gebraucht.

## 2. Wie in den Standard eingegriffen wird

Die Leiter, von oben nach unten. Nimm immer die höchste Stufe, die den Fall
löst:

1. **Customizing und Konfiguration.** Keine Entwicklung, keine
   Upgradebelastung.
2. **Freigegebene Schnittstellen (Released APIs).** SAP sichert die Stabilität
   dieser Objekte über Releases hinweg zu. Wenn eine passende existiert, ist
   sie die richtige Wahl, auch wenn ein direkter Tabellenzugriff kürzer wäre.
   Den Freigabestatus nachschlagen statt annehmen: im ADT wird er am Objekt
   angezeigt, außerhalb liefert ihn das SAP Cloudification Repository, das
   zusätzlich die empfohlene Alternative für nicht freigegebene Objekte nennt.
   Behaupte nie, ein Objekt sei freigegeben, ohne das geprüft zu haben.
3. **BAdI oder Enhancement Spot.** Von SAP vorgesehene Einhängepunkte. Prüfen,
   ob der Punkt an der Stelle liegt, an der die Daten schon vollständig sind.
4. **Implizite Erweiterung.** Funktioniert, ist aber schwach dokumentiert und
   beim Upgrade fragil. Nur wenn 1 bis 3 nichts hergeben. Dann mit
   Kommentar warum.
5. **Modifikation des Standards.** Praktisch nie. Sie erzeugt beim Upgrade
   Abgleichaufwand für immer und wird nur mit ausdrücklicher Entscheidung des
   Kunden gemacht, nicht aus Bequemlichkeit.

Eine Kopie eines SAP-Programms in den Kundennamensraum ist keine Stufe dieser
Leiter, sondern eine Modifikation mit zusätzlicher Tarnung: sie friert den
Stand des Kopiertages ein und bekommt keine Korrekturen mehr.

## 3. Klassisches ABAP oder ABAP Cloud

Auf S/4HANA gilt das Clean-Core-Ziel: Erweiterungen sollen ohne Modifikation
auskommen und ausschließlich über freigegebene Schnittstellen auf den Kern
zugreifen, damit Upgrades ohne Nacharbeit durchlaufen.

SAP hat das zunächst als Drei-Stufen-Modell beschrieben (ABAP Cloud auf dem
Stack, Übergangslösungen für fehlende freigegebene Schnittstellen, klassisches
ABAP als unterste Stufe) und inzwischen zu einem Stufenkonzept
weiterentwickelt. Prüfe den aktuellen Extensibility Guide, bevor du die
Einstufung eines Objekts gegenüber einem Kunden behauptest. Das Prinzip ist
stabil, die Bezeichnungen ändern sich.

Praktische Entscheidungshilfe:

- **Neues Objekt in einem S/4-System, freigegebene Schnittstellen vorhanden:**
  ABAP Cloud, mit Sprachversion ABAP for Cloud Development.
- **Neues Objekt ohne freigegebene Schnittstelle für den nötigen Zugriff:** den
  Übergangsweg dokumentieren statt ihn zu verstecken. Ein bewusst
  eingestufter Kompromiss ist etwas anderes als ein unbemerkter.
- **Erweiterung eines bestehenden klassischen Objekts:** klassisch bleiben.
  Zwei Sprachversionen in einem Objekt sind kein Fortschritt.
- **System ist kein S/4:** die Frage stellt sich nicht.

## 4. Wo es landet

- **Paket.** Fachlich schneiden, nicht nach Objektart. Ein Paket "ZFI" mit
  allem drin ist genauso falsch wie ein Paket je Report. Existiert im Haus
  eine Paketstruktur, wird sie übernommen, auch wenn sie nicht ideal ist.
- **Namensraum.** Kundennamensraum `Z` oder `Y`. Vorrang hat ein registrierter
  Namensraum falls vorhanden. Beim Kunden gilt dessen Konvention, immer, auch
  wenn sie von der eigenen abweicht.
- **Namenskonvention.** Vor dem ersten Objekt klären, ob es eine gibt. Fehlt
  sie, eine vorschlagen und aufschreiben, statt implizit eine eigene zu
  etablieren. Der spätere Leser sucht nach Muster, nicht nach Kreativität.
- **Transport.** Ein Auftrag je fachlicher Änderung, nicht je Arbeitstag.
  Abhängigkeiten zwischen Aufträgen sind der häufigste Grund für gescheiterte
  Importe.
- **Versionierung.** Der Transportauftrag ist kein Versionsstand. Existiert im
  Haus eine Git-Anbindung für ABAP, gehört das Objekt hinein. Fehlt sie, ist
  das eine offene Frage an die Organisation, keine Eigenschaft von ABAP:
  abapGit macht ABAP-Objekte versionierbar. Ohne Versionierung ist jede Arbeit
  an Templates schwer wiederverwendbar. Ein Coding-Agent kann dann nur im
  System arbeiten statt auf einem Repository.

Beim Kunden zusätzlich: klären, wer freigibt und importiert. Dazu, ob es
Zeitfenster gibt. Ein fertiger Transport, der drei Wochen liegt, ist nicht
fertig.

## 5. Wie geschnitten wird

Der Schnitt entscheidet, ob das Objekt jemals testbar ist. Drei Teile, immer
getrennt:

- **Datenbeschaffung.** Selektion, Lesen, Aufbereiten der Rohdaten.
- **Fachliche Logik.** Rechnen, Prüfen, Entscheiden. Kein Datenbankzugriff,
  keine Ausgabe.
- **Ausgabe oder Verbuchung.** Liste, Datei, Schnittstelle, Buchung.

Liegt die Logik in derselben Routine wie der Datenbankzugriff, ist ein
Unit-Test nur mit echten Daten möglich. Damit wird er nicht geschrieben.
Nachgerüstet wird er danach nie. Dieser eine Punkt ist der Unterschied
zwischen wartbarem und nicht wartbarem Code, wichtiger als jede
Namenskonvention.

Weiter:

- Ausnahmen bewusst wählen: klassenbasiert, mit einer Ausnahmeklasse je
  fachlichem Fehlerfall. Keine Rückgabecodes als Ersatz.
- Nachrichten in den Nachrichtenklassen ablegen, nicht als Literale im Code.
  Sonst gibt es keine Übersetzung und keine Auffindbarkeit.
- Mengengerüst vor der ersten Zeile klären. Eine Lösung für tausend Sätze
  sieht anders aus als eine für zehn Millionen.

## 6. Woran man erkennt, dass es funktioniert

- **ABAP Unit von Anfang an**, nicht nachträglich. Mindestens für die
  fachliche Logik aus dem mittleren Teil des Schnitts. Datenbeschaffung wird
  über Testdoubles ersetzt, nicht über Testmandanten.
- **ATC-Prüfung** laufen lassen, bevor der Transport freigegeben wird. Im ADT
  direkt am Objekt.
- **Abnahmekriterien** stehen im Fachkonzept, nicht im Kopf. Sind sie nicht
  prüfbar formuliert, gehört das zurück (siehe bs-sap-spec).

## Was in den ersten Stunden entstehen sollte

Nicht Code, sondern vier Zeilen, die später jede Diskussion abkürzen:

```
Warum entwickelt: was der Standard nicht kann, kurz belegt
Eingriffstechnik: welche Stufe der Leiter und warum nicht die höhere
Ort:              Paket, Namensraum, Transportschicht
Schnitt:          welche drei Teile, welche Grenze dazwischen
```

Das gehört in die Objektdokumentation oder in eine Datei neben den Code, nicht
in eine Mail.

## Wenn ein fremder Entwurf beurteilt wird

Prüf ihn gegen dieselbe Leiter. Sag dabei nicht "das ist falsch", sondern zeig
die höhere Stufe. Der häufigste echte Befund ist nicht schlechter Code,
sondern eine Eigenentwicklung, die eine Standardfunktion nachbaut. Der
zweithäufigste ist eine Modifikation, die als Erweiterung ausgegeben wird.

Halte dich zurück bei Namens- und Stilfragen im fremden System. Dort gilt die
Konvention des Hauses, nicht die eigene.
