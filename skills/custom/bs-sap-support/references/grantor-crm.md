# Grantor Management: Aufbau, Komponenten, Anlaufstellen

Recherchiert am 24.08.2026 aus SAP Help, dem SAP-Objektverzeichnis sapdatasheet
und der SAP Community. Quellen am Ende. Jede Angabe ist mit einem Sicherheits-
grad versehen, weil sie nicht aus einem laufenden System stammt.

**belegt** = steht so in einer der Quellen.
**abzugleichen** = plausibel aus den Quellen. Im eigenen System zu prüfen.

## Der Punkt, der alles erklärt

**belegt:** Grantor Management ist auf **zwei Systeme aufgeteilt**. Der
CRM-Teil führt den fachlichen Prozess, der ERP-Teil führt die finanzielle
Abwicklung. Beide sind über eine Prozessintegration verbunden.

Daraus folgt die wichtigste Frage bei jedem Fehler in diesem Modul: **auf
welcher Seite tritt er auf? Ist er dort entstanden oder nur angekommen?**
Ein fehlender Betrag im ERP kann drei Ursachen haben: er wurde im CRM nie
erfasst, er wurde nicht übertragen, er wurde übertragen und nicht
verbucht. Das sind drei verschiedene Anlaufstellen. Wer diese Frage
überspringt, sucht regelmäßig im falschen System.

| Seite | Was dort läuft |
|---|---|
| CRM (WebClient) | Programmdefinition, Antragsannahme, Antragsbewertung, Vereinbarung, Änderungsanträge, Case Management |
| ERP (SAP GUI) | Finanzielle Abwicklung über PSCD oder FI-AP/AR, Obligo- und Istfortschreibung, Budget über Funds Management |

**belegt:** Der bewilligte Gesamtbetrag einer Vereinbarung erzeugt im ERP eine
Obligo-Position, mit getrennten Positionen je Zahlungsart. Funds Management
(PSM-FM) ist optional und wird für den Budgetbezug genutzt.

## Anwendungskomponente und Pakete

Diese Namen sind der Schlüssel, um im eigenen System den vollständigen Bestand
aufzulisten, statt Transaktionen zu raten.

**belegt:**

- Anwendungskomponente: **PSM-GM-GTR** (Grantor Management), erstmals mit
  Release 700 ausgeliefert
- Software-Komponente: **EA-PS** (SAP Enterprise Extension Public Services)
- Superpaket: **GRANTS_MANAGEMENT**

Unterkomponenten:

| Schlüssel | Bedeutung |
|---|---|
| PSM-GM-GTR-MD | Stammdaten |
| PSM-GM-GTR-GM | Grantor Management, spezifische Buchungen |
| PSM-GM-GTR-UP | Ist- und Obligofortschreibung |
| PSM-GM-GTR-IS | Informationssystem |

Pakete:

| Paket | Inhalt |
|---|---|
| GRANTOR_MANAGEMENT | Grantor Management |
| GTR_BASIS_E | Grundobjekte |
| GTR_INTEGRATION_E | Integrationsthemen, unter anderem CRM |
| GTR_CRM_ISPS_PROXY | Prozessintegration CRM zu Grantor Management |

Diese vier Paketnamen in SE84 oder SE80 eingeben und die Objektart
Transaktionen wählen. Das ergibt in einer Minute die vollständige Liste für
den vorliegenden Releasestand. Dasselbe für Programme, Klassen und Tabellen.

## Belegte Transaktionen

Nur zwei ließen sich außerhalb eines Systems eindeutig belegen. Das ist keine
Lücke der Recherche, sondern der Grund, warum die Liste aus dem System kommen
muss.

| Transaktion | Bedeutung | Paket |
|---|---|---|
| GTRDERIVE | GTR Object Assignment, Customizing | GTR_INTEGRATION_E |
| GTRDERIVER | GTR Object Assignment, Maintenance | GTR_INTEGRATION_E |

**abzugleichen:** Weitere Transaktionen dieses Moduls beginnen erkennbar mit
`GTR`. Ein Suchmuster `GTR*` in SE93 liefert sie, ebenso der Weg über die
Pakete oben.

## CRM-Seite

**belegt:** Die Standard-Geschäftsrolle für den Einstieg heißt
**CRMGRMPRGMAN** (Grantor Program Manager). Über die Geschäftsrolle wird
gesteuert, welche Arbeitsvorräte, Navigationsleisten und Sichten ein Anwender
im WebClient sieht.

Daraus folgt für die Fehlersuche: **"Der Anwender sieht den Punkt nicht" ist
im WebClient fast immer eine Rollen- oder Konfigurationsfrage, kein Fehler.**
Die Prüfreihenfolge ist Geschäftsrolle, dann Navigationsleistenprofil, dann
die UI-Konfiguration der betroffenen Sicht, erst danach der Code.

**belegt:** Zur Bündelung aller Dokumente zu einem Antrag samt Folgevorgängen
wird Case Management verwendet. Ein "verschwundenes" Dokument ist deshalb oft
nur eines, das nicht dem erwarteten Fall zugeordnet wurde.

## Prozesskette und wo Fehler entstehen

**belegt** als Abfolge, **abzugleichen** in den Details eures Customizings:

1. Programm definieren (CRM)
2. Antrag erfassen, auch über ein Online-Formular (CRM)
3. Antrag bewerten (CRM)
4. Vereinbarung erzeugen (CRM), daraus Obligo im ERP
5. Änderungsanträge zur Vereinbarung (CRM)
6. Mittelabruf und Auszahlung (ERP, über PSCD oder FI-AP/AR)
7. Ist-Fortschreibung und Abschluss

Die beiden Übergänge zwischen den Systemen, also Schritt 4 und Schritt 6, sind
die Stellen mit den meisten Fehlern. Bei einem Fehler dort gilt die
Schnittstellen-Regel aus dem Hauptskill: beide Enden getrennt prüfen. Was das
CRM gesendet hat und was das ERP angenommen hat, sind zwei Fragen mit zwei
Protokollen.

## Was noch fehlt

Die vollständige Transaktions- und Programmliste für euren Releasestand. Der
Weg dorthin steht in `transaktionen.md` unter "Den modulspezifischen Bestand
selbst ziehen". Mit den Paketnamen aus diesem Dokument ist das jetzt ein
Fünf-Minuten-Vorgang statt einer Suche.

Ebenfalls offen und nur im System zu klären: welche der Standardobjekte bei
euch überhaupt aktiv sind, welche kundeneigenen Erweiterungen daneben stehen
und wie die Prozessintegration konkret konfiguriert ist.

## Quellen

- SAP Help Portal, Grantor Management (S/4HANA On-Premise) sowie Integration
  with Grantor Management (PSM-GM-GTR)
- sapdatasheet.org, Anwendungskomponente PSM-GM-GTR und Paket
  GRANTOR_MANAGEMENT: Unterkomponenten, Pakete, Software-Komponente
- SAP Community, Einführungsreihe zu SAP Grantor Management sowie Beiträge zur
  CRM-Geschäftsrolle CRMGRMPRGMAN
- sapbrainsonline und testingbrain zu GTRDERIVE und GTRDERIVER

Keine dieser Quellen ersetzt das eigene System. Sie liefern die Namen, mit
denen dort gesucht wird.
