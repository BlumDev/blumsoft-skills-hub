---
name: bs-sap-support
description: >-
  Fehler im SAP-System vom Symptom zur Ursache zurückverfolgen, solange die
  Fundstelle noch NICHT bekannt ist: Kurzdump, abgebrochener Hintergrundjob,
  Verbuchungsabbruch, fehlende oder falsche Daten, Timeout, Sperre,
  Berechtigungsfehler, Schnittstellen- und Oberflächenfehler. Nennt je Symptom
  die richtige Anlaufstelle in der richtigen Reihenfolge und sagt konkret,
  welche Angaben aus dem System geholt werden müssen, damit eine Aussage
  belegbar wird. Laden bei: "das Programm ist abgestürzt", "Dump in ST22",
  "der Job ist abgebrochen", "die Buchung fehlt",
  "der Beleg fehlt", "der Anwender bekommt eine Fehlermeldung", "es hängt",
  "keine Berechtigung", "der IDoc steht auf Fehler", "die Fiori-App zeigt
  nichts an", "im WebClient kommt eine Meldung", "seit gestern langsam",
  "welche Transaktion brauche ich dafür"; ebenso wenn jemand einen Fehler
  ohne Fundstelle meldet. NICHT laden, wenn der
  Quelltext bereits vorliegt und beurteilt, erklärt oder erweitert werden
  soll, dafür bs-sap-abap-review.
---

# SAP-Fehleranalyse

Der Fehler ist fast nie dort, wo er auffällt. Ein Anwender meldet eine
Meldung, ein Beleg fehlt, ein Job steht auf rot: das ist die Wirkung. Die
Aufgabe ist, von dieser Wirkung aus rückwärts an die Stelle zu kommen, an der
die Ursache liegt. Über Belege statt über Vermutungen.

Der teuerste Fehler in diesem Skill ist eine plausible Ursache ohne Beleg. Sie
klingt gut, wird geglaubt, kostet einen halben Tag und ist falsch. Sag lieber,
welche Angabe fehlt.

## Arbeitsteilung, die du nicht umgehen kannst

Du hast keinen Zugriff auf das System. Marcus schaut nach, du sagst ihm wo.
Daraus folgt die wichtigste Regel dieses Skills: **frag nach genau einer
Sache, dann warte.** Eine Liste von acht Punkten führt dazu, dass drei davon
beantwortet werden und die Analyse trotzdem hängt. Nenne die Anlaufstelle, sag
was dort abzulesen ist und wozu du es brauchst.

Was fast immer als Erstes gebraucht wird und selten mitgeliefert wird:

- **Wann genau** ist es passiert, Datum und Uhrzeit auf die Minute. Ohne das
  ist kein Protokoll auffindbar.
- **Wer** hat es ausgelöst, Benutzer und Mandant.
- **Reproduzierbar oder einmalig.** Das entscheidet über den ganzen weiteren
  Weg: einmalig deutet auf Daten oder Nebenläufigkeit, reproduzierbar auf Code
  oder Customizing.
- **Seit wann.** Ein Fehler, der gestern noch nicht da war, hat fast immer
  einen Transport, ein Customizing oder einen Datenstand als Ursache, nicht
  eine Programmlogik, die seit Jahren läuft.

Diese vier Angaben sind wichtiger als jede Transaktion. Fehlen sie, sind sie
die erste Rückfrage.

## Reihenfolge

1. **Symptom trennen von Deutung.** Was wurde beobachtet, was ist bereits
   Interpretation? "Die Schnittstelle ist kaputt" ist eine Deutung. "Der Beleg
   ist im Zielsystem nicht da" ist ein Symptom.
2. **Beleg beschaffen.** Kurzdump, Joblog, Anwendungsprotokoll, Trace. Ohne
   Beleg wird nicht geraten.
3. **Ort bestimmen.** Welches Programm, welche Stelle, welcher Aufruf.
4. **Ursache belegen.** Erst hier den Quelltext holen. Ab da übernimmt
   bs-sap-abap-review.
5. **Prüfen, ob die Ursache das Symptom vollständig erklärt.** Erklärt sie nur
   einen Teil, ist sie nicht die Ursache, sondern ein zweiter Fund.

Schritt 5 wird am häufigsten übersprungen. Eine Ursache, die den Abbruch
erklärt aber nicht, warum er erst seit Dienstag auftritt, ist unvollständig.

## Symptomklassen

### Programm bricht ab, Kurzdump

Anlaufstelle **ST22**, Selektion auf Datum, Uhrzeit und Benutzer.

Zu lesen sind vier Dinge, in dieser Reihenfolge: die Fehlerklasse in der
Kopfzeile, der Text unter "Was ist passiert", die auslösende Quelltextzeile
und der Aufrufstapel. Der Aufrufstapel ist der wertvollste Teil und wird am
häufigsten ignoriert: er sagt, wer das abgestürzte Programm gerufen hat.

Häufige Fehlerklassen und was sie bedeuten:

- `CX_SY_OPEN_SQL_DB` und Nachfolger: Datenbankfehler, oft Sperre oder
  Feldüberlauf.
- `CX_SY_CONVERSION_NO_NUMBER`, `CX_SY_CONVERSION_OVERFLOW`: Daten passen
  nicht ins Zielfeld. Fast immer ein Datenfall, nicht ein Programmfehler.
- `MESSAGE_TYPE_X`: das Programm hat sich selbst abgebrochen. Die eigentliche
  Meldung steht im Dump, Nachricht und Nummer nachschlagen.
- `TIME_OUT`: Laufzeitbegrenzung im Dialog. Kein Fehler an sich, sondern ein
  Mengenproblem. Weiter bei "Zu langsam".
- `TSV_TNEW_PAGE_ALLOC_FAILED`: Speicher erschöpft, meist unbegrenzt wachsende
  interne Tabelle.
- `DBIF_RSQL_INVALID_CURSOR`, `SAPSQL_ARRAY_INSERT_DUPREC`: Doppelter
  Schlüssel oder abgebrochener Cursor, oft Nebenläufigkeit.

Falle: Der Dump zeigt die Stelle des Abbruchs, nicht die Stelle des Fehlers.
Ein Konvertierungsfehler kann von einer Datenzeile stammen, die drei
Programme vorher entstanden ist.

### Hintergrundjob abgebrochen oder nicht gelaufen

Anlaufstelle **SM37**, Selektion großzügig setzen: Benutzer auf Stern, Status
alle, Zeitraum weit. Ein Job, der "nicht gelaufen ist", steht oft auf geplant
oder freigegeben statt auf abgebrochen.

Reihenfolge: Joblog lesen, nicht den Status. Der Status sagt nur ob, das
Joblog sagt warum. Bricht der Job mit Dump ab, steht die Dump-Referenz im
Joblog und führt zurück nach ST22.

Typische Ursachen, die nicht im Programm liegen: Job läuft unter einem
Benutzer ohne die nötigen Rechte, Variante zeigt auf einen Zeitraum der
verstrichen ist, Vorgängerjob in der Kette ist ausgefallen, kein freier
Hintergrundprozess.

### Buchung ist verschwunden

Der Anwender hat gespeichert, das System hat es bestätigt, die Daten sind
trotzdem nicht da. Anlaufstelle **SM13**, Verbuchungsabbrüche für Benutzer und
Datum.

Das ist die am häufigsten übersehene Fehlerklasse: der Dialogteil war
erfolgreich, die Verbuchung im Hintergrund ist gescheitert. Der Anwender sieht
keinen Fehler. In SM13 steht die Verbuchungsfunktion und meist ein Kurzdump
dahinter.

### Falsche oder fehlende Daten ohne jeden Abbruch

Der schwerste Fall, weil es keinen Beleg gibt, den man aufschlagen könnte.

Reihenfolge: Zuerst das **Anwendungsprotokoll SLG1** prüfen, viele
Anwendungen schreiben dort ihre fachlichen Meldungen weg, ohne dass der
Anwender sie sieht. Dann klären, ob der Datensatz gar nicht entstanden ist
oder ob er entstanden und wieder verändert wurde: Änderungsbelege über CDHDR
und CDPOS, dazu die Änderungszeitstempel des Datensatzes selbst.

Erst wenn beides nichts hergibt, gezielt debuggen. Ein Debugger ohne
Hypothese ist Zeitverschwendung: vorher aufschreiben, welchen Wert du an
welcher Stelle erwartest.

### Welche Art von Debugger

Die Standardeinstellung erreicht mehrere der häufigsten Fälle nicht. Wer das
nicht weiß, sucht an einem Haltepunkt, der nie erreicht wird. Der Schluss
daraus ist dann eine falsche Ursache.

- **Verbuchung:** Code in der Verbuchung läuft in einem eigenen Prozess. Ohne
  eingeschaltetes Verbuchungs-Debugging läuft der Debugger am Fehler vorbei.
  Das ist der Standardfall bei allem, was aus SM13 kommt.
- **Hintergrundprozess:** ein laufender Job wird über SM50 gefangen, nicht
  über einen Haltepunkt im Quelltext.
- **WebClient, Fiori, RFC:** der Code läuft in einer anderen Sitzung. Dafür
  ist externes Debugging nötig, gebunden an Benutzer oder Terminal-ID.
- **Fremde Schichten überspringen:** kommt der Abbruch tief aus Standardcode,
  spart schichtbewusstes Debugging (SLAD) das Durchsteigen durch
  Rahmenwerksebenen.
- **Watchpoint statt Haltepunkt**, sobald die Frage lautet "wer ändert diesen
  Wert". Ein Haltepunkt beantwortet das nicht, ein Watchpoint schon.

### Zu langsam oder Timeout

Erst messen, dann deuten. Die Frage ist immer dieselbe: liegt die Zeit in der
Datenbank oder im ABAP?

- **ST05** zeichnet Datenbankzugriffe, Sperren und Fernaufrufe auf. Nutzen,
  wenn der Verdacht auf Datenbank liegt oder unklar ist. Der wichtigste Blick
  ist "gleiche Anweisung sehr oft" statt "eine Anweisung sehr langsam".
- **SAT** ist die Laufzeitanalyse für den ABAP-Anteil. Nutzen, wenn ST05 wenig
  Datenbankzeit zeigt.
- **ST12** kombiniert beides für einen Lauf und ist meist der schnellste
  Einstieg, wenn du eine Transaktion oder einen Report gezielt vermessen
  kannst.
- **ST03N** und **STAD** liefern die Statistik im Nachhinein, wenn der Vorfall
  vorbei ist und nicht reproduzierbar.

Falle: Eine Aussage über Performance ohne Mengengerüst ist wertlos. Frage
immer, wie viele Sätze im Spiel sind. Ein Zugriff in einer Schleife über zehn
Sätze ist harmlos, derselbe über zwei Millionen legt das System lahm.

Zweite Falle: "Seit gestern langsam" ist selten ein Codeproblem. Prüfe zuerst
Datenwachstum, fehlenden Index nach einer Migration, geänderte Variante oder
einen Transport.

### Berechtigungsfehler

**SU53** direkt nach dem Fehler, im selben Modus des betroffenen Benutzers.
Das ist die Einschränkung, die den Wert meist zerstört: SU53 zeigt die letzte
fehlgeschlagene Prüfung dieses Benutzers, nicht die des Anwenders drei
Schreibtische weiter.

Sauberer und bei sporadischen Fällen der einzige Weg: **STAUTHTRACE**, Trace
für den betroffenen Benutzer einschalten, Fall nachstellen lassen, Trace
auswerten. Zeigt alle geprüften Objekte, auch die erfolgreichen.

Falle: Ein fehlendes Berechtigungsobjekt ist ein Befund, keine Lösung. Die
Frage, ob der Benutzer das Recht haben SOLL, ist fachlich und gehört nicht in
die technische Analyse.

### Es hängt

**SM12** für Sperren, **SM50** für die Arbeitsprozesse im laufenden System.
Ein Prozess, der lange auf "Sequential Read" derselben Tabelle steht, sagt
mehr als jede Vermutung.

Sperre erkennen heißt noch nicht Ursache kennen: Frage ist immer, wer die
Sperre hält und warum er sie nicht loslässt. Ein hängender Dialogbenutzer, ein
abgebrochener Job und eine Verbuchung im Stau sehen im Ergebnis gleich aus.

### Schnittstellen

Nach Kanal getrennt, weil jeder sein eigenes Protokoll hat:

- **RFC:** SM58 für abgebrochene transaktionale Aufrufe, SM59 zum Prüfen der
  Verbindung selbst. Bei SM59 den Verbindungstest UND den Berechtigungstest
  laufen lassen, sie prüfen Verschiedenes.
- **IDoc:** WE02 oder WE05 für Status und Inhalt, WE19 zum Nachstellen. Der
  Statuscode ist die erste Information, nicht der Inhalt.
- **qRFC-Warteschlangen:** SMQ1 ausgehend, SMQ2 eingehend. Eine blockierte
  Warteschlange staut alles dahinter, das Symptom erscheint dann bei fachlich
  unbeteiligten Vorgängen.
- **OData und Fiori:** /IWFND/ERROR_LOG im Frontend-Server, /IWBEP/ERROR_LOG
  im Backend. Die beiden zu verwechseln kostet regelmäßig eine halbe Stunde.

Regel für jede Schnittstelle: beide Enden ansehen. Was das eine System
gesendet hat und was das andere angenommen hat, sind zwei getrennte Fragen mit
zwei getrennten Protokollen.

### Oberfläche

**Fiori:** Erst im Browser die Netzwerkanalyse öffnen und den fehlgeschlagenen
Aufruf ansehen, Statuscode und Antwortkörper. Eine leere Liste ohne
Fehlermeldung ist meist ein erfolgreicher Aufruf mit leerem Ergebnis, also ein
Berechtigungs- oder Selektionsproblem, kein Fehler. Danach
/IWFND/ERROR_LOG.

**CRM WebClient UI:** Meldung im Fenster notieren, dann prüfen, ob sie aus der
Anwendung oder aus dem Rahmenwerk kommt. Anwendungsmeldungen führen über den
Nachrichtenkatalog zur auslösenden Stelle. Rahmenwerksfehler zeigen sich in
der Component Workbench (BSP_WD_CMPWB) und hängen oft an der
UI-Konfiguration, nicht am Code.

## Falschmeldungen vermeiden

Bevor eine Ursache genannt wird, prüf sie gegen dich selbst:

- Erklärt sie das Symptom **vollständig**, einschließlich des Zeitpunkts, ab
  dem es auftritt?
- Würde sie bei jedem Auftreten dieselbe Wirkung erzeugen? Wenn der Fehler
  sporadisch ist, die Ursache aber deterministisch, passt es nicht zusammen.
- Beruht sie auf einem Beleg aus dem System oder auf Modellwissen über SAP?
  Modellwissen ist ein Ausgangspunkt, kein Befund.

Häufige Fehlurteile:

- Aus einem Dump auf einen Programmfehler schließen, obwohl die Fehlerklasse
  auf einen Datenfall zeigt.
- Eine Transaktion nennen, ohne zu sagen, was dort abzulesen ist. Das
  verschiebt die Arbeit nur.
- Customizing als Ursache ausschließen, weil der Code plausibel aussieht.
- Bei Nischenmodulen wie Grantor Management Transaktionscodes aus dem
  Gedächtnis nennen. Wenn du eine Transaktion nicht sicher belegen kannst, sag
  das und nutze den Weg über die Referenzdatei dieses Skills.

## Ausgabe

Kurz, in dieser Form:

```
Symptom:     was beobachtet wurde, ohne Deutung
Nächster Schritt: eine Anlaufstelle, was dort abzulesen ist, wofür
Hypothesen: höchstens zwei, jede mit dem Beleg, der sie bestätigen oder
            widerlegen würde
Fehlt mir:  die Angabe, ohne die es nicht weitergeht
```

Sobald der Beleg da ist, wird die Hypothesenliste kürzer statt länger. Wächst
sie, ist der Beleg nicht ausgewertet worden.

## Im ADT statt im GUI

Marcus arbeitet heute im SAP GUI und wird später parallel mit Eclipse und ADT
sowie VS Code arbeiten. Die Entsprechungen, damit die Analyse nicht an der
Oberfläche hängt:

- Kurzdumps stehen im **Feed Reader** unter "ABAP Runtime Errors", das ist die
  ST22 in Eclipse. Für die ABAP-Umgebung in der Cloud ist es sogar der einzige
  Weg.
- Der Debugger in ADT kann mehr als der klassische, vor allem bei
  Bedingungen und dynamischen Haltepunkten.
- ATC-Prüfungen laufen dort direkt am Objekt, statisch und ohne Ausführung.
- Was es in ADT nicht gibt, bleibt im GUI: Verbuchung, Sperren,
  Arbeitsprozesse, Warteschlangen, die Basis-Protokolle.

Nenne im Zweifel beide Wege, GUI zuerst, solange kein Eclipse eingerichtet
ist.

## Transaktionen nachschlagen

`references/transaktionen.md` enthält die belegten Standardtransaktionen nach
Symptom sortiert, dazu die Anleitung, wie der modulspezifische Bestand aus dem
eigenen System gezogen wird, statt ihn zu raten.

`references/grantor-crm.md` enthält den Aufbau von Grantor Management: die
Aufteilung auf CRM und ERP, die Anwendungskomponente PSM-GM-GTR mit ihren
Paketnamen, die belegten Transaktionen und die Prozesskette mit den beiden
Übergabestellen, an denen die meisten Fehler entstehen. Bei jedem
Grantor-Thema zuerst dort nachsehen, vor allem wegen der einen Frage, die
über das halbe Suchen entscheidet: liegt der Fehler auf der CRM-Seite oder auf
der ERP-Seite.
