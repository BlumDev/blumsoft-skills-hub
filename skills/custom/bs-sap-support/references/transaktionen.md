# Transaktionen nach Symptom

Nur belegte Standardtransaktionen. Modulspezifisches (Grantor, CRM, PSM) steht
bewusst nicht drin, sondern wird nach der Anleitung im unteren Teil aus dem
eigenen System gezogen.

## Abbruch und Protokoll

| Transaktion | Wofür | Was dort abzulesen ist |
|---|---|---|
| ST22 | Kurzdumps (Laufzeitfehler) | Fehlerklasse, auslösende Zeile, Aufrufstapel, Benutzer, Zeitpunkt |
| SM21 | Systemprotokoll | Systemnahe Ereignisse im Zeitfenster: Datenbank, Speicher, Abbrüche |
| SM37 | Hintergrundjobs | Status, Laufzeit, Joblog mit dem tatsächlichen Grund |
| SM13 | Verbuchungsabbrüche | Gescheiterte Verbuchungen samt Verbuchungsfunktion und Dump-Bezug |
| SLG1 | Anwendungsprotokoll | Fachliche Meldungen, die der Anwender nie sieht |
| SM35 | Batch-Input-Mappen | Fehlgeschlagene Sätze bei Mappenverarbeitung |

## Laufzeit

| Transaktion | Wofür | Wann sie die richtige ist |
|---|---|---|
| ST05 | Trace für Datenbank, Sperren, Fernaufrufe | Verdacht auf Datenbank oder unklare Lage. Zeigt vor allem Wiederholungen |
| SAT | Laufzeitanalyse ABAP | Wenn die Datenbankzeit klein ist und die Zeit im Coding liegt |
| ST12 | Einzeltransaktionsanalyse | Schnellster Einstieg, wenn ein Lauf gezielt vermessen werden kann |
| ST03N | Statistik im Nachhinein | Vorfall ist vorbei und nicht reproduzierbar |
| STAD | Einzelsatzstatistik | Ein konkreter Vorgang eines Benutzers in einem Zeitfenster |
| SM50 | Arbeitsprozesse | Läuft gerade etwas fest und woran |
| DB02 | Datenbankwachstum, Indizes | Verdacht auf fehlenden Index oder Tabellenwachstum |
| SQLM | SQL-Monitor im Produktivbetrieb | Welche Anweisung im echten Lastfall wie oft läuft |

## Berechtigungen

| Transaktion | Wofür | Einschränkung |
|---|---|---|
| SU53 | Letzte fehlgeschlagene Prüfung | Gilt für den eigenen Benutzer im eigenen Modus, direkt nach dem Fehler |
| STAUTHTRACE | Berechtigungstrace | Der saubere Weg bei fremdem Benutzer oder sporadischem Fall |
| SUIM | Auswertungen über Benutzer und Rollen | Wer hat welches Objekt, welche Rolle enthält was |

## Sperren

| Transaktion | Wofür |
|---|---|
| SM12 | Sperreinträge, wer hält was seit wann |
| SM13 | Verbuchung im Stau, häufige Ursache scheinbarer Sperren |
| DB01 | Datenbankseitige Wartesituationen |

## Schnittstellen

| Transaktion | Kanal | Was dort abzulesen ist |
|---|---|---|
| SM58 | tRFC | Abgebrochene transaktionale Aufrufe mit Fehlertext |
| SM59 | RFC-Verbindungen | Verbindungstest und Berechtigungstest, beide getrennt ausführen |
| SMQ1 | qRFC ausgehend | Blockierte Warteschlangen, die alles dahinter aufstauen |
| SMQ2 | qRFC eingehend | Dasselbe auf der Empfängerseite |
| WE02, WE05 | IDoc | Status und Inhalt. Der Statuscode zuerst, dann der Inhalt |
| WE19 | IDoc | Nachstellen eines Belegs zum Debuggen |
| BD87 | IDoc | Erneutes Verarbeiten nach Korrektur |
| /IWFND/ERROR_LOG | OData Frontend | Fehler auf dem Gateway-Server |
| /IWBEP/ERROR_LOG | OData Backend | Fehler im Backend-Anteil. Nicht mit dem Frontend-Protokoll verwechseln |
| /IWFND/TRACES | OData | Aufzeichnung von Aufruf und Nutzlast |
| /IWFND/MAINT_SERVICES | OData Frontend | Dienst aktivieren, Systemzuordnung prüfen, Metadaten neu laden |
| /IWFND/GW_CLIENT | OData Frontend | Den Dienst direkt aufrufen, ohne Oberfläche dazwischen |
| /IWFND/CACHE_CLEANUP | OData Frontend | Zwischenspeicher leeren, wenn geänderte Metadaten nicht ankommen |
| /IWBEP/CACHE_CLEANUP | OData Backend | Dasselbe im Backend, nötig nach geänderten CDS-Annotationen |
| SXMB_MONI | Prozessintegration | Nachrichtenverfolgung, wenn PI oder PO im Spiel ist |

## Nachschlagen und Umfeld

| Transaktion | Wofür |
|---|---|
| SE93 | Was steckt hinter einem Transaktionscode: Programm, Bildnummer, Berechtigungsobjekt |
| SE84 | Repository-Infosystem. Objekte nach Paket oder Anwendungskomponente auflisten, auch Transaktionen |
| SE81 | Anwendungshierarchie. Der Weg vom Fachgebiet zur Komponente und zu deren Paketen |
| SE16N | Tabelleninhalte ansehen |
| SE11 | Struktur einer Tabelle, Indizes, Fremdschlüssel |
| SE95 | Modifikationsabgleich, wer hat im Standard geändert |
| SCU3 | Auswertung von Tabellenänderungen (Customizing) |
| STMS | Transportwesen. Was wurde wann eingespielt, wichtig bei "seit gestern" |

## Den modulspezifischen Bestand selbst ziehen

Transaktionscodes für Nischenmodule dürfen nicht aus dem Modellwissen kommen,
dort entstehen erfundene Codes. Der eigene Bestand ist genauer und deckt den
tatsächlichen Releasestand ab.

### Weg 1: über die Oberfläche, ohne Export

**SE81** öffnen, die Anwendungshierarchie bis zum gesuchten Fachgebiet
aufklappen (Public Sector Management, Grantor Management, CRM je nach Fall),
den Knoten markieren und ins Infosystem abspringen. Dort unter Programmierung
die Objektart Transaktionen wählen. Ergebnis ist die vollständige Liste der
Transaktionen dieser Komponente mit Texten.

Alternativ direkt **SE84**, Zweig Programmierung, dann Transaktionen, mit Paket
oder Anwendungskomponente als Einschränkung.

Die Komponente vorher heraussuchen statt sie zu vermuten. Der Kürzelbaum in
SE81 ist die Quelle, nicht das Gedächtnis.

### Weg 2: als Datei, für die Referenzdatei dieses Skills

Über **SE16N** je Tabelle, Ergebnis als Tabellenkalkulation sichern:

- `TSTC`: Feld `TCODE` und `PGMNA`. Alle Transaktionscodes mit dem Programm
  dahinter.
- `TSTCT`: Felder `SPRSL`, `TCODE`, `TTEXT`. Die Texte, Sprache auf DE oder EN
  einschränken.
- `TADIR`: `PGMID` gleich `R3TR`, `OBJECT` gleich `TRAN`, dazu `OBJ_NAME` und
  `DEVCLASS`. Ordnet jeder Transaktion ihr Paket zu.
- `TDEVC`: `DEVCLASS` und `COMPONENT`. Ordnet jedem Paket seine
  Anwendungskomponente zu.

Über diese vier Tabellen entsteht durch Verknüpfung die Liste "Transaktion,
Text, Paket, Komponente" für genau die Bereiche, die gebraucht werden. Das
Ergebnis kommt als weitere Referenzdatei in diesen Skill.

### Wo das gemacht wird

Im **Clatum-eigenen S/4-System**, nicht auf einem Kundensystem. Transaktions-
und Paketverzeichnisse sind SAP-Standardinhalte ohne Geschäftsdaten. Ein
Export aus einem Kundensystem bleibt trotzdem eine Datenmitnahme aus fremder
Umgebung. Das ist die Vertragsfrage, nicht die technische.

Solange die Liste nicht existiert, gilt: eine unsichere Transaktion wird nicht
genannt. Stattdessen der Weg über SE81 oder SE84, den Marcus in einer Minute
selbst geht.
