---
name: bs-sap-ui5
description: >-
  Oberflächen im SAP-Umfeld bauen und beurteilen: SAPUI5, SAP Fiori, Fiori
  Elements, OData als Datenschnittstelle, Annotationen, Launchpad-Einbindung
  und die Fehlersuche im Frontend. Kern ist die erste Entscheidung zwischen
  Fiori Elements und Freestyle, weil sie den gesamten Aufwand bestimmt. Laden
  bei: "Fiori-App bauen", "UI5", "SAPUI5", "Fiori Elements", "Freestyle",
  "OData-Service anbinden", "Annotationen", "List Report", "Object Page",
  "Launchpad", "Kachel", "die App zeigt keine Daten", "Fehler im Frontend",
  "OPA-Test", "Fiori Tools", "welches Floorplan", "V2 oder V4"; ebenso wenn
  eine Anforderung eine Oberfläche braucht und die Technologie noch offen ist.
  NICHT für allgemeine Web-Frontends außerhalb von SAP (React, Vue, eigene
  Seiten), dafür die Skills bs-web-build und fable-uiux. NICHT für die
  Backend-Entwicklung dahinter, dafür bs-sap-kickoff und bs-sap-abap-review.
---

# SAPUI5 und Fiori

Der teuerste Fehler in diesem Bereich ist eine Freestyle-Anwendung für einen
Fall, den ein Standard-Floorplan abgedeckt hätte. Sie kostet das Fünffache in
der Entwicklung und das Vielfache in der Pflege, weil jede Änderung am
Datenmodell händisch nachgezogen werden muss. Der zweitteuerste ist das
Gegenteil: ein Floorplan, der um Anforderungen herumgebogen wird, für die er
nicht gemacht ist.

Diese Entscheidung fällt zuerst, vor jeder Zeile.

## 1. Fiori Elements oder Freestyle

Fiori Elements erzeugt die Oberfläche aus Metadaten. Du beschreibst am
Datenmodell, was angezeigt werden soll, das Rahmenwerk baut daraus die Seite.
Freestyle bedeutet: du schreibst die Sichten und die Steuerung selbst.

**Fiori Elements passt, wenn:**

- Der Fall einem Standardmuster entspricht: Liste mit Filter und Detailseite,
  Übersichtsseite mit Karten, Analyse mit Kennzahlen.
- Die Oberfläche im Wesentlichen Daten zeigt und ändert, statt einen
  besonderen Ablauf zu führen.
- Konsistenz mit anderen Anwendungen im Haus gewünscht ist. Das ist meist ein
  stärkeres Argument als die Optik einer Einzelanwendung.

**Freestyle passt, wenn:**

- Der Ablauf die Oberfläche bestimmt statt umgekehrt: Assistent über mehrere
  Schritte, Zeichenfläche, Planungsbild, ungewöhnliche Interaktion.
- Mehrere fachlich unabhängige Objekte auf einem Bild zusammengeführt werden,
  die kein gemeinsames Datenmodell haben.
- Die Anforderung ausdrücklich etwas verlangt, das kein Floorplan kennt.

**Die Prüfung, die den Streit beendet:** Schreib die drei bis fünf
Kernanforderungen an die Oberfläche auf und ordne jeder zu, ob ein Floorplan
sie abdeckt. Deckt er vier von fünf ab, wird die fünfte in Fiori Elements
ergänzt statt alles freihändig zu bauen: dafür gibt es Erweiterungspunkte und
Bausteine, mit denen einzelne Bereiche einer generierten Seite durch eigene
Sichten ersetzt werden. Diesen Mittelweg übersehen die meisten Entwürfe.

Ein Sonderfall, der oft falsch entschieden wird: eine schwierige Wertehilfe
oder ein Reiterband sind kein Grund für Freestyle. Beides geht in Fiori
Elements.

**Die dritte Möglichkeit, die selten geprüft wird:** für interne Werkzeuge und
kleine Anwendungen lässt sich eine UI5-Oberfläche auch vollständig in ABAP
schreiben (abap2UI5). Das spart Frontend-Server, Node-Werkzeugkette und eine
getrennte Auslieferung. Wenn die Anwendung ohnehin nur im eigenen Haus läuft
und der Aufwand für eine reguläre Fiori-Auslieferung in keinem Verhältnis
steht, ist das die schnellere Antwort. Für Anwendungen beim Kunden oder mit
Anspruch auf Fiori-Konformität nicht.

## 2. OData V2 oder V4

Die Version ist keine Geschmacksfrage, sie ergibt sich aus dem Backend.

- **RAP im Backend:** OData V4. Das ist der Weg für neue Entwicklungen auf
  S/4HANA.
- **Bestehender V2-Service:** dabei bleiben. Eine Umstellung ist ein eigenes
  Projekt, kein Nebenprodukt.
- **Fiori Elements:** funktioniert mit beiden, die Vorlagen und der
  Funktionsumfang unterscheiden sich aber je Version. Vor der Zusage an den
  Kunden prüfen, ob das gewünschte Merkmal in der vorliegenden Version
  vorhanden ist, statt es aus der anderen Version zu erinnern.

Mischbetrieb in einer Anwendung wird nicht gemacht.

## 3. Wo die Annotationen leben

Annotationen sind die eigentliche Arbeit bei Fiori Elements. Ihr Ort
entscheidet über die Wartbarkeit.

- **Im CDS-View im Backend:** der Regelfall. Die Beschreibung liegt dort, wo
  das Datenmodell liegt. Sie gilt für jeden Verbraucher.
- **In einer lokalen Annotationsdatei im Frontend:** nur für Anpassungen, die
  wirklich nur diese eine Anwendung betreffen.
- **Verteilt auf beides ohne Regel:** der Normalzustand nach zwei Jahren
  Wartung und der Grund, warum niemand mehr weiß, woher eine Spalte kommt.
  Leg die Regel am Anfang fest und schreib sie auf.

Beim Beurteilen einer bestehenden Anwendung ist die erste Frage deshalb nicht
"wie sieht sie aus", sondern "wo stehen die Annotationen".

## 4. Aufsetzen und Werkzeuge

- **SAP Fiori Tools** als Erweiterung für Visual Studio Code sind der
  vorgesehene Weg zum Anlegen einer Anwendung, inklusive Vorlagengenerator und
  Anwendungsmodellierer.
- **ui5-tooling** für den lokalen Lauf, Bau und die Anbindung an ein Backend
  über einen Proxy. Dazu der UI5-Linter für die statische Prüfung, vor allem
  vor einem Versionswechsel.
- Für die Arbeit mit einem Coding-Agenten existieren offizielle MCP-Server von
  SAP für UI5, für Fiori-Anwendungsgenerierung und für die UI5 Web Components,
  dazu UI5-Plugins für Coding-Agenten. Sie liefern dem Agenten die
  Framework-Kenntnis, die er sonst aus veraltetem Trainingswissen zieht. Das
  ist bei UI5 besonders wirksam, weil sich die Steuerelement-API zwischen
  Versionen ändert.
- Eine Anwendung, die nur im Launchpad des Entwicklungssystems läuft und
  lokal nicht startet, ist schwer zu testen. Den lokalen Lauf gleich am Anfang
  einrichten, nicht wenn der erste Fehler auftritt.

Für das Launchpad gehören drei Dinge zusammen und werden einzeln vergessen:
die Anwendungsbeschreibung (Manifest), die Zielzuordnung (Semantic Object und
Aktion) sowie die Kachel und ihre Rollenzuordnung. Eine Anwendung ohne
Rollenzuordnung ist für den Anwender nicht vorhanden, obwohl sie technisch
läuft.

## 5. Wenn nichts angezeigt wird

Die häufigste Meldung aus dem Fachbereich. Fast nie ein UI-Fehler. Vorgehen
in dieser Reihenfolge:

1. **Netzwerkanalyse im Browser.** Den Aufruf des Dienstes ansehen. Statuscode
   und Antwort.
2. **Statuscode deuten:** 200 mit leerem Ergebnis heißt, der Dienst hat
   geantwortet und nichts gefunden. Das ist ein Selektions- oder
   Berechtigungsthema, kein Fehler. 401 und 403 sind Anmeldung und
   Berechtigung. 500 kommt aus dem Backend.
3. **Backend-Protokolle**, wenn es 500 war oder wenn der Aufruf gar nicht
   ankam. Ab hier übernimmt bs-sap-support mit den Gateway-Protokollen.
4. **Erst danach** die Anwendung selbst verdächtigen.

Zwei Fallen: Ein Zwischenspeicher im Browser oder im Launchpad zeigt oft einen
alten Stand, deshalb vor jeder Fehlersuche einmal ohne Zwischenspeicher laden.
Und die Metadaten des Dienstes werden serverseitig zwischengespeichert:
geänderte Annotationen wirken erst nach dem Leeren dieses Speichers, was
regelmäßig als "die Annotation funktioniert nicht" fehlgedeutet wird. Dafür
gibt es zwei getrennte Transaktionen. Meist braucht man beide:
`/IWFND/CACHE_CLEANUP` im Frontend, `/IWBEP/CACHE_CLEANUP` im Backend. Die
Backend-Variante ist die, an die niemand denkt, obwohl geänderte
CDS-Annotationen genau dort hängen bleiben.

Zwei weitere Anlaufstellen, bevor die Anwendung verdächtigt wird:
`/IWFND/MAINT_SERVICES` zeigt, ob der Dienst überhaupt aktiv und dem richtigen
System zugeordnet ist. `/IWFND/GW_CLIENT` ruft ihn direkt auf, ohne Oberfläche
dazwischen. Antwortet er dort richtig, liegt der Fehler im Frontend. Antwortet
er dort falsch, hat die Anwendung nie eine Chance gehabt.

## 6. Prüfen

- **QUnit** für einzelne Bausteine und Formatierer.
- **OPA5** für den Ablauf durch die Oberfläche.
- Bei Fiori Elements ist der Anteil eigener Tests klein, weil das Rahmenwerk
  geprüft ist. Getestet wird das Eigene: Erweiterungen, Formatierer, eigene
  Prüfungen.
- Barrierefreiheit und Tastaturbedienung sind im öffentlichen Sektor kein
  Zusatzwunsch, sondern Anforderung. Bei Fiori Elements weitgehend geschenkt,
  bei Freestyle ein eigener Aufwandsposten, der in die Schätzung gehört (siehe
  bs-sap-estimate).

## 7. Beim Kunden

Prüf vor jeder Zusage die Versionslage: die UI5-Version im Kundensystem
bestimmt, welche Steuerelemente und welche Fiori-Elements-Merkmale zur
Verfügung stehen. Eine Anwendung gegen die neueste Fassung zu entwerfen und
danach auf einem älteren Stand auszuliefern, ist der Klassiker unter den
Fehlschätzungen.

Ebenso klären: eigener Frontend-Server oder eingebettet, wer betreut das
Launchpad, gibt es einen Freigabeprozess für neue Kacheln.

## Abgrenzung: CRM WebClient UI

Der WebClient in älteren CRM-Systemen ist keine UI5-Anwendung, sondern beruht
auf BSP mit eigenem Komponentenmodell und eigener Datenschicht. Nichts aus
diesem Skill gilt dort. Anlaufstellen sind stattdessen die Component
Workbench und die UI-Konfiguration. Der häufigste Fehler ist eine
Konfiguration, die für die falsche Rolle oder den falschen Objekttyp greift.
Für Fehler dort siehe bs-sap-support.
