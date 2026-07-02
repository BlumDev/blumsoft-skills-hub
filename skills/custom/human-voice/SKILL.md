---
name: human-voice
description: >
  Schreibregeln für authentisch menschlich klingenden Fließtext auf Deutsch und Englisch.
  Nutze diesen Skill, wenn nutzerseitig sichtbarer Prosatext erzeugt oder umgeschrieben wird:
  Website- und UI-Texte, Landingpage- und Marketing-Copy, E-Mail- und Nachrichtenantworten,
  Blog, LinkedIn, Angebote. Trigger-Phrasen: "klingt zu KI-mäßig", "zu glatt", "humanisieren",
  "menschlicher machen", "kein AI slop", "natürlicher klingen", "rewrite",
  "E-Mail klingt generiert", "sounds like ChatGPT", "make it human", "less corporate",
  "weniger roboterhaft". NICHT verwenden für Code-Kommentare, Commit-Messages, Log-Ausgaben,
  technische Bezeichner oder reine Code- und Konfig-Dokumentation: dort wäre es Overkill.
---

# Human Voice Skill

Ziel: Text erzeugen oder transformieren, der wie ein konkreter Mensch schreibt,
nicht wie ein statistisches Sprachmodell. Das bedeutet: spezifisch statt generisch,
direkt statt performativ höflich, ungleichmäßig statt metronomisch.

Drei Modi:

- **Write-Modus**: Neuen Text mit diesen Regeln verfassen
- **Rewrite-Modus**: Fertigen Text umschreiben (AI-Text oder zu steifer Mensch-Text)
- **Check-Modus**: Text beurteilen, ob er gut genug ist oder wirklich Änderungen braucht

---

## Kernregeln (immer anwenden)

### 1. Verbotene Wörter und Phrasen

Niemals verwenden (auf Englisch und Deutsch):

**Lexik / Buzzwords**
delve, tapestry, multifaceted, leverage, harness, utilize, streamline, robust,
seamless, innovative, cutting-edge, pivotal, groundbreaking, revolutionize,
transformative, nuanced, landscape, realm, testament, underpinnings, synergy,
unlock, game-changer, elevate, empower, disruptive, comprehensive, holistic,
paradigm, ecosystem, stakeholder, deep dive, shed light on, it's worth noting,
it is important to note, needless to say

**Deutsche Entsprechungen**
tiefgreifend, wegweisend, Ökosystem (im abstrakten Sinn), Mehrwert (als leere
Floskel), ganzheitlich, optimieren (als leere Floskel), maßgeschneidert,
zukunftsweisend, innovativ (außer als direktes Adjektiv mit Beleg),
"In der heutigen Zeit", "Es ist wichtig zu betonen"

**Übergangswörter, die AI verraten**
Furthermore, Moreover, Additionally, Consequently, In conclusion, In summary,
Notably, Importantly, Undoubtedly, Certainly, It goes without saying,
Darüber hinaus (als leere Brücke), Zusammenfassend lässt sich sagen,
Abschließend möchte ich betonen

### 2. Verbotene Satzzeichen und Formatierung

- **Niemals em dashes (—) oder en dashes (–) in Fließtext**
- Keine Semikolons in informellen Texten
- Keine Markdown-Fettung mitten im Fließtext
- Keine Hashtags außer explizit für Social Media erbeten
- Kein "**Punkt**: Erklärung" als Standard-Listenformat

### 3. Satzrhythmus (burstiness)

Menschliches Schreiben ist ungleichmäßig. KI schreibt in gleichförmigen
Mittelmaß-Sätzen (immer 15-25 Wörter, immer 3-4 Zeilen pro Absatz).

Regel: Wechsle bewusst zwischen kurz und lang. Ein kurzer Satz kann einen
langen Absatz abschließen. Oder eröffnen. Dann kommt wieder eine ausholendere
Konstruktion, die Kontext gibt und den Leser mitnimmt, bevor es wieder knallt.
Kurz.

Ziel: mindestens 30% der Sätze unter 10 Wörter, mindestens 10% über 30 Wörter.

### 4. Übergänge ohne Ankündigungen

Schlechte Übergänge kündigen den Themenwechsel an:
> "Furthermore, we should also consider..."

Gute Übergänge nutzen die Logik des vorherigen Satzes:
> "The features are impressive. The price tag isn't."

Regel: Übergangswörter löschen oder durch direkte inhaltliche Verbindung ersetzen.
Wenn man "außerdem" schreibt, prüfen ob der Satz nicht einfach der vorherige
Gedanke ist, weitergeführt.

### 5. Konkret statt generisch

KI generalisiert: "This is an important topic in today's world."
Menschen sind spezifisch: "Drei Handwerksbetriebe in Grünstadt haben das letztes
Jahr selbst erlebt."

Regel: Wo immer möglich, konkrete Zahlen, Orte, Namen, Zeitpunkte einsetzen.
Wenn keine vorliegen: konkrete Beispiele erfinden die plausibel sind, oder
den Nutzer fragen. Nicht mit leeren Generalisierungen auffüllen.

### 6. Haltung zeigen

KI ist neutral und performativ ausgewogen. Menschen haben Meinungen.

Regel: Eine klare Haltung einnehmen, auch bei sachlichen Texten. Nicht jede
Aussage durch ein "however" absichern. Nicht jede Empfehlung in "it may be
worth considering" einwickeln.

Schlecht: "There are both advantages and disadvantages to this approach."
Gut: "Das funktioniert. Aber nur wenn X stimmt, sonst nicht."

### 7. Kein performativer Einstieg

Niemals starten mit:
- "In today's fast-paced world..."
- "In einer Zeit, in der..."
- "I hope this message finds you well."
- "Es freut mich, Ihnen mitteilen zu können..."
- Einem Kompliment an den Leser

Direkt anfangen. Mit dem Punkt.

### 8. Kein Abschluss-Reflex

Niemals enden mit:
- "In conclusion / Zusammenfassend..."
- "I hope this helps!"
- "Feel free to reach out if you have any questions."
- "Ich stehe Ihnen für Rückfragen gerne zur Verfügung."
- Einer Aufzählung der gerade genannten Punkte

Enden wenn der letzte Gedanke gesagt ist. Fertig.

---

## Kontext-Sensitivität

### Formalitätsstufen

Nicht jeder Text soll locker klingen. Die Regeln gelten immer, aber der
Ton wird dem Kontext angepasst:

| Kontext | Ton | Besonderheiten |
|---|---|---|
| E-Mail, Blog, Social, Angebot | Direkt, ggf. umgangssprachlich | Volle Blacklist aktiv |
| Geschäftsbericht, Präsentation | Sachlich-direkt, kein Kauderwelsch | Blacklist aktiv, Formalität erlaubt |
| Juristische / DSGVO-Texte | Formal, präzise | Übergangswörter mit Bedacht erlaubt wenn rechtlich notwendig; keine Buzzwords trotzdem |
| Technische Dokumentation | Neutral, sachlich | Listen und Struktur ausdrücklich erlaubt; Slop-Wörter trotzdem raus |

Wenn der Kontext formell ist: die Struktur darf straff sein, aber die
Blacklist-Wörter und der performative Stil bleiben verboten. "Utilize" ist
auch in einem Rechtsdokument nur ein schlechteres "use".

---

### Listen

KI-Listen: immer "**Header:** Erklärungssatz"
Menschliche Listen: gemischt, unregelmäßig, oder gar nicht.

Wenn eine Liste 3 Punkte hat, die alle kurz sind: als Satz schreiben.
"Dafür brauchst du Zeit, Budget und einen klaren Ansprechpartner."

Listen nur dann wenn die Punkte wirklich parallel und nicht als Fließtext
lesbar sind.

### Absatzlänge

Kein uniformes 4-Zeilen-Raster. Varianz ist Pflicht.
Ein Absatz kann ein Satz sein.

Kann auch mal länger werden, wenn der Gedanke es verlangt und nicht
künstlich gestoppt werden sollte, weil die KI denkt, vier Zeilen sei die
richtige Länge für einen Absatz. Das ist sie nicht.

---

## Sprach-spezifisches

### Deutsch

- Aktiv bevorzugen: "Wir liefern" statt "Es wird geliefert"
- Keine Schachtelsätze mit mehr als zwei Einschüben
- Umgangssprache erlaubt wenn kontextuell passend: "Das klappt" statt
  "Dies lässt sich realisieren"
- Kontraktionen wo natürlich: "Das ist kein Problem" statt "Dies stellt
  kein Problem dar"

### Englisch

- Contractions verwenden: "it's", "you'll", "we've" (außer bei formellen
  Dokumenten explizit ohne)
- Aktiv und direkt: "We ship Tuesday" nicht "Shipment will be facilitated
  by Tuesday"
- Umgangssprache nach Kontext dosieren

---

## Check-Modus: Erst beurteilen, dann entscheiden

Wenn fertiger Text zur Überprüfung kommt, ZUERST einschätzen ob ein Rewrite
überhaupt nötig ist.

**Kein Rewrite nötig wenn:**
- Kein Blacklist-Wort vorkommt
- Satzrhythmus variiert
- Kein reflexartiger Einstieg/Abschluss
- Konkrete Aussagen statt Generalisierungen
- Übergänge inhaltlich funktionieren

In diesem Fall: kurz bestätigen was gut ist, ggf. 1-2 Kleinigkeiten benennen
die man noch schärfen könnte (optional), aber KEINEN kompletten Rewrite liefern.
"Der Text klingt bereits menschlich. Einzige kleine Sache: [X]. Willst du das
geändert haben?"

**Teilrewrite wenn:**
- Nur einzelne Probleme (2-3 Stellen) im Text
- Nur die Problemstellen korrigieren, Rest unverändert lassen

**Vollrewrite wenn:**
- Mehrere Blacklist-Wörter, gleichförmiger Rhythmus, und/oder performative
  Einstiege/Abschlüsse gleichzeitig

---

## Rewrite-Modus: Vorgehen

Wenn fertiger Text humanisiert werden soll:

1. Text auf Blacklist-Wörter prüfen, alle ersetzen oder Satz neu bauen
2. Alle em/en dashes ersetzen (Komma, Klammer, Punkt je nach Kontext)
3. Übergangswörter streichen oder durch inhaltliche Brücke ersetzen
4. Gleichförmige Sätze identifizieren, Rhythmus brechen
5. Einleitung und Schluss prüfen, reflexartige Phrasen streichen
6. Generische Aussagen identifizieren, durch Konkretes ersetzen oder
   markieren als [KONKRETISIEREN: was genau?]
7. Haltung prüfen: wo weicht der Text neutralem Absichern aus? Direkter
   formulieren.

---

## Qualitäts-Check vor Ausgabe

Vor dem Ausgeben eines jeden Textes intern prüfen:

- [ ] Kein Wort aus der Blacklist?
- [ ] Kein em/en dash in Fließtext?
- [ ] Satzlängen variieren?
- [ ] Kein reflexartiger Einstieg / Abschluss?
- [ ] Mindestens eine konkrete Aussage statt Generalisierung?
- [ ] Übergänge inhaltlich statt deklarativ?

Wenn eine Prüfung fehlschlägt: Stelle vor Ausgabe korrigieren, nicht trotzdem
rausgeben und am Ende "Hinweis: ..." schreiben.
