---
name: voice
description: >-
  Erzeugt aus einem Thema (plus optionalem Quellmaterial: Datei, Vault-Pfad oder
  Text im Chat) ein TTS-optimiertes Voice-Lernskript zum Anhören unterwegs (Handy,
  Auto, beim Gehen). Reine fließende Prosa in einfacher Sprache, echte Umlaute,
  Akronyme als Einzelbuchstaben, Zahlen und Versionen ausgeschrieben, Kapitel je
  mit einem "Kurz zusammengefasst"-Recap. Liefert eine .txt (reines Hör-Skript)
  und optional eine .md mit Kapitelübersicht und Wiedergabe-Hinweisen fürs Handy.
  KEINE Meta-/Bedienhinweise, keine Versions-/Quellen-Notizen, keine
  Selbstkorrekturen im gesprochenen Text. Use when the user wants an
  audio/listening/voice learning script, something to listen to on the go, or a
  text-to-speech study script on any topic, e.g. "erzeuge ein Hör-Skript zu X",
  "mach mir ein Voice-Skript", "was zum Anhören für unterwegs", "Lernskript zum
  Hören", "TTS-Skript". Trigger: "Hör-Skript", "Voice-Skript", "Lernskript zum
  Anhören", "zum Anhören für unterwegs", "TTS-Skript", "Skript zum Vorlesen lernen".
---

# voice

Macht aus einem Thema ein Hör-Lernskript: reine, fließend gesprochene Prosa, die
eine Vorlese-Stimme sauber liest, damit Marcus unterwegs (Handy, Auto, beim Gehen)
lernen kann. Deutsche Antworten im Chat, echte Umlaute, knapp, Senior-Ton.

Das Format ist der Kern dieses Skills. Goldstandard sind zwei fertige Skripte (Ton,
Struktur, Konventionen exakt so übernehmen):
`D:\cloud.blumora.de\Apps\Obsidian\BlumOps\10 Hubs\Bewerbung Clatum (Nr 1507)\Lernmaterial\SAP-Technik Voice-Skript Clatum.txt`
(Fachwissen, Kapitel mit Recaps) und `...\Lernmaterial\Gespraechsfuehrung Voice-Skript Clatum.txt`
(Soft-Skills). Bei Unsicherheit über Ton oder Aufbau dort kurz reinschauen.

## Eingabe

Ein Thema, plus optional Quellmaterial. Quelle kann sein: ein Dateipfad, ein
Vault-Pfad, oder Text direkt im Chat.
- Quellmaterial zuerst **lesen, dann verdichten**, nie roh dumpen. Aus der Vorlage
  die Kernaussagen ziehen und in fließende Hör-Prosa umschreiben.
- Kein Quellmaterial: aus eigenem Wissen ein sauber strukturiertes Skript bauen.
- Unklar, wie tief oder wie lang: kurz fragen (grober Umfang, Zielniveau), sonst
  sinnvoll annehmen und die Annahme nennen.

## Format (harte Regeln, immer durchsetzen)

1. **Reine Prosa.** Fließend gesprochen, einfache Sätze, kurz. Kein Markdown, keine
   Bullet-Listen, keine Tabellen, keine Überschriften-Zeichen, keine Klammern, keine
   Slashes. Normale Satzzeichen (Punkt, Komma, Doppelpunkt, Semikolon) sind erwünscht,
   sie steuern die Sprechpausen.
2. **Echte deutsche Umlaute** (ä, ö, ü, ß), niemals ae/oe/ue. Datei als **UTF-8 ohne
   BOM** schreiben.
3. **TTS-freundliche Schreibung**, damit die Stimme nicht stolpert:
   - Akronyme als Einzelbuchstaben mit Leerzeichen, längere durch Komma in
     Sprech-Segmente geteilt: `BOL` wird `B O L`, `OZG` wird `O Z G`, `SEGW` wird
     `S E G W`, `CRMD-ORDERADM-H` wird `C R M D, ORDERADM, H`. (Ausnahme `ABAP`, siehe Tabelle unten.)
     Eigennamen und Akronyme, die eine deutsche Stimme falsch liest, immer nach der
     Tabelle unten korrigieren.
   - Versionen und Produktnamen ausschreiben: `S/4 HANA` wird `S vier HANA`,
     `OData V4` wird `OData V vier`, `UI5` wird `UI fünf`, `F2` wird `F zwei`.
   - Wichtige oder runde Zahlen als Wort: `95.000` wird `fünfundneunzig tausend`,
     `105.000 Euro` wird `einhundertfünf tausend Euro`, `18 Jahre` wird `achtzehn
     Jahre`. Sehr lange technische Nummern (Objektnummern, IDs) dürfen Ziffern
     bleiben, das liest die Stimme ohnehin korrekt.
   - Slashes immer ausschreiben: `und/oder` wird `und oder`.
4. **Kapitelstruktur.** Jedes Kapitel startet mit `Kapitel eins. Kurzer Titel.`
   (Zahl als Wort), dann der Inhalt, am Ende **genau ein** Recap-Absatz, der mit
   `Kurz zusammengefasst:` beginnt und die Kernpunkte des Kapitels bündelt.
5. **Optionaler Überblick** ganz am Anfang (vor Kapitel eins): ein kurzer,
   **sachlicher** Absatz, der die Hauptbereiche des Themas benennt. Sachlich
   einordnen, nicht bewerten. Weglassen, wenn das Thema klein ist.
6. **Du-Ansprache** an den Lernenden ist ok, aber sachlich. Kein bewertendes
   "das ist deine Lücke" / "das kannst du schon", außer der Nutzer wünscht es.

## Aussprache- und Schreibkonventionen für TTS

Die Vorlese-Stimme (meist Google Deutsch in @Voice Aloud Reader auf Android) liest
manches falsch. Diese Regeln vermeiden das. Sie gelten zusätzlich zu Regel 3 oben.

1. **Abkürzungen immer ausschreiben** im gesprochenen Text:
   - Wochentage: `Mo`/`Di`/`Mi`/`Do`/`Fr`/`Sa`/`So` wird `Montag`/`Dienstag`/
     `Mittwoch`/`Donnerstag`/`Freitag`/`Samstag`/`Sonntag`.
   - Monate ausschreiben (`Jan.` wird `Januar` usw.), Uhrzeiten als Wort
     (`8:30 Uhr` wird `acht Uhr dreißig`).
   - Gängige Kürzel: `z.B.` wird `zum Beispiel`, `usw.` wird `und so weiter`,
     `etc.` wird `und so weiter`, `ca.` wird `circa`, `Nr.` wird `Nummer`,
     `Std.` wird `Stunden`, `inkl.` wird `inklusive`.
2. **Vollständige Sätze.** Keine angedeuteten oder unvollständigen Satzenden.
   Besonders Abschluss- und Schlusssätze müssen voll ausformuliert sein, nicht als
   Stichwort oder Verweis. Nicht `und dann der Urlaubshinweis`, sondern den
   Urlaubssatz wirklich ausschreiben.
3. **Eigennamen und Akronyme korrigieren**, die eine deutsche Stimme falsch liest.
   Erweiterbare Tabelle, Begriff zu TTS-Schreibung:

   | Begriff | TTS-Schreibung | Warum |
   |---|---|---|
   | `ABAP` | `Abapp` | sonst englisch als "ebep" gesprochen; phonetisch geschrieben liest die Stimme es korrekt als "Ah-bap" |
   | `SAP SE` | `SAP S E` | sonst wird `SE` als englisches Wort "south east" gelesen; einzeln klingt es "Es Eh" |

   Konvention für ABAP: phonetisch als `Abapp` geschrieben, weil die Vorlese-Stimme das
   als "Ah-bap" liest, die gewohnte Aussprache. Buchstabiert (`A B A P`) wäre die
   Alternative, klingt aber "Ah-Beh-Ah-Peh". Neue Problemfälle einfach als Zeile ergänzen.

## Streng verboten (der eigentliche Kern, häufigster Fehler)

Nichts davon darf im gesprochenen Text vorkommen:
- **Keine Meta- oder Bedienhinweise:** kein "Willkommen", kein "hör dir das mehrmals
  an", kein "beim Spazieren / im Auto", kein "Merke dir das", kein "Viel Erfolg".
- **Keine Versions-, Stand- oder Quellen-Notizen:** kein "Stand nach...", kein
  "aktualisiert", kein "dieses Skript", kein Verweis auf die Vorlage.
- **Keine Selbstkorrekturen oder Verweise auf frühere Annahmen:** kein "das war
  falsch", kein "nicht X sondern Y", kein "wie letzte Woche", kein "das alte
  Skript". Der Text klingt, als wäre er von Anfang an richtig gewesen.
- **Keine Struktur-Meta:** kein "Kapitel neun, das letzte", kein "bis hierher
  hattest du...", kein "im nächsten Kapitel".
- **Kein Vorgeplänkel:** direkt im Stoff (oder im sachlichen Überblick) starten,
  keine Begrüßung, kein "in diesem Skript geht es um...".

## Ausgabe

1. **Eine `.txt`** mit dem reinen Hör-Skript nach obigen Regeln. Dateiname:
   `<Thema> Voice-Skript.txt` (bei thematischem Bezug Suffix wie in der Vorlage, z.B.
   `... Clatum`). Mit dem Write-Tool schreiben (UTF-8 ohne BOM). Falls per PowerShell
   geschrieben wird: `WriteAllText` mit `UTF8Encoding($false)`.
2. **MP3s erzeugen (Standard, immer anbieten):** eine MP3 pro Kapitel über das
   Skill-Tool `scripts/voice_mp3.py` (edge-tts, Microsoft-Neural-Stimmen,
   Default `de-DE-ConradNeural`, Marcus' Wahl). Aufruf (PowerShell):
   `python "C:\Users\Marcus\.claude\skills\voice\scripts\voice_mp3.py" "<pfad>\<Thema> Voice-Skript.txt" [--voice de-DE-KatjaNeural]`
   Ausgabe: Ordner `<Thema> Voice-Skript MP3` neben der `.txt`, Dateien
   `NN <Kurztitel>.mp3`, Vorspann als `00 Überblick`. Liegt die `.txt` unter
   `D:\cloud.blumora.de\...`, synct Nextcloud die MP3s automatisch aufs Handy.
   **Cloud-Hinweis:** edge-tts schickt den Text an einen Microsoft-Endpunkt.
   Keine Kundendaten und nichts Hochsensibles; in dem Fall nur `.txt` liefern
   (Offline-Weg) und das kurz sagen.
3. **Optional eine begleitende `.md`** mit Kapitelübersicht und Wiedergabe-Hinweisen
   fürs Handy. Vorlage:
   `...\Lernmaterial\SAP-Technik Voice-Skript Clatum.md`. Anbieten, nicht ungefragt
   immer erzeugen. Inhalt: kurze Kapitelliste plus dieser Wiedergabe-Block (an Thema
   und Ablageort anpassen):
   - **MP3s (bevorzugt):** Nextcloud-App, MP3-Ordner "Offline verfügbar" machen,
     abspielen mit einem Hörbuch-Player (z.B. "Voice" von Paul Woitaschek,
     open source): Pause, Springen zwischen Kapiteln, Tempo, merkt die Position.
   - **Fallback `.txt` per TTS:** App @Voice Aloud Reader (kostenlos): die `.txt`
     öffnen, oder in Nextcloud lang drücken, Teilen, @Voice, Play. Deutsche Stimme:
     Android, Einstellungen, System, Sprachausgabe, Google Sprachausgabe, Deutsch.
   - **Ohne App:** Obsidian mobile (Lesemodus) plus Android "Auswählen zum Vorlesen",
     oder die Datei in Chrome, Menü, "Vorlesen".

   Wird die `.md` in den BlumOps-Vault gelegt, Frontmatter nach
   `99 System/Frontmatter Schema.md` setzen und mit `[[...]]` auf die `.txt`
   verlinken; außerhalb des Vaults reicht minimale oder keine Frontmatter.

## Ablage

Standardmäßig dorthin, wo das Quellmaterial liegt. Sonst nach kurzer Rückfrage. Bei
BlumOps-/Vault-Themen passend in den Vault
(`D:\cloud.blumora.de\Apps\Obsidian\BlumOps`), bei Bezug zu einem Hub in dessen
`Lernmaterial`-Ordner (wie die Clatum-Skripte). Den erzeugten Pfad im Chat ausgeben.

## Ablauf

1. Thema und (optional) Quellmaterial klären. Quelle lesen und verdichten.
2. Inhalt in Kapitel gliedern; bei größeren Themen einen sachlichen Überblick voran.
3. Skript schreiben: fließende Hör-Prosa, TTS-Schreibung anwenden, jedes Kapitel mit
   `Kurz zusammengefasst:` schließen.
4. **Selbstprüfung (Pflicht) vor dem Speichern:** den Entwurf gegen "Streng verboten"
   prüfen und alle Treffer entfernen. Zusätzlich: keine ae/oe/ue, keine Slashes,
   keine Klammern, keine Listen/Markdown, Akronyme gespaced, wichtige Zahlen und
   Versionen ausgeschrieben, jeder Kapitel-Recap vorhanden und genau einer.
5. `.txt` (UTF-8 ohne BOM) am Ablageort schreiben. MP3s per `scripts/voice_mp3.py`
   erzeugen (bzw. anbieten, Cloud-Hinweis beachten). Begleit-`.md` anbieten oder,
   wenn gewünscht, mit erzeugen.
6. Knapp melden: Ablageort(e), Kapitelanzahl, ob MP3s erzeugt wurden.

## Mini-Beispiel (ein Kapitel, als Maßstab)

> Kapitel eins. Die drei Schichten.
>
> Die Architektur hat drei Schichten. Ganz oben die Oberfläche, der WebClient.
> Darunter die B O L, der Business Object Layer, sie hält die Objekte im Speicher.
> Unten die GenIL, sie ruft die Funktionsbausteine im System. Du arbeitest immer
> oben über die B O L, niemals direkt auf den Tabellen.
>
> Kurz zusammengefasst: Drei Schichten, WebClient oben, B O L in der Mitte, GenIL
> unten. Gearbeitet wird über die B O L, nie direkt auf den Daten.
