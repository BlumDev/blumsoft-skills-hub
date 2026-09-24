# Entscheidungen

Nicht-triviale Entscheidungen dieses Repos, append-only. Je Eintrag: Datum, Kontext,
Optionen, Entscheidung, Trade-off. Triviale Entscheidungen gehören nicht hierher.
Status und Aufgaben stehen in `backlog.md`, nicht hier.

## 2026-07-16: Skill-/Bundle-IDs per Allowlist statt Pfad-Sanitizing

**Kontext.** `sync.ps1` baute sein Löschziel mit `Join-Path` aus einem Skill-Namen, der
ungeprüft aus `registry.yaml` bzw. `bundles/*.yaml` kam, und übergab es an
`Remove-Item -Recurse -Force` (Finding `20260714-sync-remove-path-traversal`, high). Ein
Name wie `../../../victim` löschte damit ein beliebiges Verzeichnis außerhalb des
Zielordners. Vor dem Fix reproduziert: der Sync lief ohne jede Fehlermeldung durch und
meldete `[OK] ../../../victim`. Die vorhandene Prüfung `$registry.ContainsKey($skill)`
sah aus wie eine Allowlist, schützte aber nicht, weil `registry.yaml` selbst der
Injektionspunkt ist.

**Optionen.**
1. Namen sanitizen (`..` und Pfadtrenner entfernen oder ersetzen).
2. Allowlist-Regex, beim YAML-Einlesen erzwungen.
3. Nur den aufgelösten Zielpfad gegen die Zielbasis prüfen.

**Entscheidung.** Option 2 als primäre Grenze, Option 3 zusätzlich als zweite Schicht in
`Resolve-SkillTargetPath`. Sanitizing wurde verworfen: es ist eine Denylist in
Verkleidung und muss jede Kodierungsvariante kennen, während die Allowlist
`^[a-z0-9][a-z0-9-]*\z` Pfadtrenner, `..`, Laufwerksbuchstaben, Alternate Data Streams
und Wildcards strukturell ausschließt. Gegen die realen Daten geprüft: alle 82
Registry-Namen, 15 Bundle-IDs und 42 Skill-Referenzen passen, der Fix bricht also keinen
legitimen Sync.

Zwei PowerShell-Fallstricke, die eine naive Umsetzung der Fix-Spec löchrig gemacht
hätten (beide empirisch bestätigt und durch Tests abgedeckt):
- `-match` vergleicht case-insensitiv, `[a-z]` hätte `EVIL` akzeptiert. Daher `-cmatch`.
- In .NET matcht `$` auch vor einem abschließenden Newline. Daher `\z`.

**Trade-off und Restrisiken.**
- Die Pfadprüfung in `Resolve-SkillTargetPath` ist mit dieser Regex nicht erreichbar:
  was die Regex passiert, ist zwangsläufig ein direktes Kind der Basis. Sie bleibt
  bewusst als zweite Schicht, falls die Regex je gelockert wird (etwa `.` für
  `skill.v2`). Preis: Code, den kein Test rot bekommen kann.
- Skill-Namen sind damit auf Kleinbuchstaben, Ziffern und Bindestriche festgelegt. Ein
  künftiger Upstream-Skill mit `_`, `.` oder Großbuchstaben bricht den Import und muss
  bewusst umbenannt werden, oder die Regex wird bewusst erweitert.
- `path:` in `registry.yaml` bleibt unvalidiert. Er fließt nur in die Copy-Quelle, nicht
  in eine Löschung, und war nicht Teil des Findings.
- `-LiteralPath` steht dort, wo IDs in Pfadoperationen fließen, nicht global. Die
  übrigen `-Path`-Aufrufe (`$profilePath`, `$targetDir`, Workflow-Kopien) sind nicht
  ID-getrieben.
- Junctions und Symlinks im Zielverzeichnis werden nicht aufgelöst: `GetFullPath` statt
  `Resolve-Path`, weil das Ziel beim ersten Sync legitim noch nicht existiert. Wer dort
  eine Junction platzieren kann, hat ohnehin bereits Schreibrechte im Zielordner.

## 2026-07-16: Pester 5 als Testframework

**Kontext.** Das Repo hatte keine automatisierten Tests. Der Traversal-Fix brauchte einen
Regressionstest. Auf der Maschine lag nur das mit Windows ausgelieferte Pester 3.4.0 von
2016, das die Operator-Syntax `Should -Be` nicht kennt.

**Optionen.** Tests in Pester-3-Syntax schreiben, oder Pester 5 installieren.

**Entscheidung.** Pester 5 (5.9.0, `-Scope CurrentUser`). Pester 3 ist zehn Jahre alt und
seine Syntax eine Sackgasse, und der Backlog plant weitere Tests
(`20260714-idea-pester-edge-tests`, `20260624-no-ci-validate-gate`). Bewusst nicht Pester
6: zu frisch für ein Repo, das gerade erst Tests einführt.

**Trade-off.** `tests/` setzt Pester 5+ voraus und schlägt unter dem systemweiten 3.4.0
fehl. Ein künftiges CI-Gate muss Pester 5 explizit installieren. Die Systeminstallation
3.4.0 bleibt unberührt.

## 2026-09-01: Skill-Austausch per Rename statt per Move-Item

**Kontext.** `sync.ps1` löschte das Zielverzeichnis und verschob erst danach die fertige Staging-Kopie an seine Stelle (Finding `20260901-sync-non-atomic-replace`). Zwischen Löschen und Verschieben lag ein Fenster, in dem ein Abbruch den Skill komplett entfernt hinterließ. Das Staging aus `2692b22` deckte nur die Kopierphase ab, nicht den Austausch.

**Optionen.**
1. Reihenfolge umdrehen: erst das Ziel wegbenennen, dann die neue Version an seine Stelle verschieben, beides mit `Move-Item`.
2. Dasselbe mit `[System.IO.Directory]::Move`.
3. Beim Austausch weiterhin löschen und nur die Fehlerbehandlung verbessern.

**Entscheidung.** Option 2, dazu ein Restore der alten Version, falls der zweite Schritt scheitert. Ausschlaggebend war eine Messung an einer gesperrten Datei im Zielverzeichnis (offener Handle ohne Freigabe): `Move-Item` verschiebt Verzeichnisse rekursiv und ließ Quelle und Ziel danach beide halb gefüllt zurück, `[System.IO.Directory]::Move` scheiterte folgenlos und ließ die Quelle vollständig stehen. Option 1 hätte das Fenster also nur verschoben statt es zu schließen. Staging- und Backup-Pfad hängen jetzt an `$dstPath`, weil die .NET-Methode relative Pfade gegen das Prozess-Arbeitsverzeichnis auflöst, das in PowerShell von `Get-Location` abweichen kann.

**Trade-off und Restrisiken.**
- Der Rename ist nur auf demselben Volume atomar. Staging, Backup und Ziel liegen im selben Ordner, damit ist das gegeben, solange niemand einzelne Skills auf ein anderes Volume verlinkt.
- Das Entsorgen der alten Version läuft mit `-ErrorAction SilentlyContinue`: ein bereits erfolgreicher Austausch darf nicht nachträglich am Aufräumen scheitern. Preis: bei gesperrten Dateien bleibt ein `.<skill>.old-<guid>`-Ordner liegen, auf den eine Warnung hinweist.
- Ein Absturz genau zwischen den beiden Renames hinterlässt das Ziel weg und das Backup da. Das ist der verbleibende Rest des Findings: jetzt ohne Datenverlust und mit einem sprechenden Ordnernamen daneben.

## 2026-09-01: Doppelte Sync-Ziele deduplizieren statt einen Alias streichen

**Kontext.** `codex` und `vscode-chatgpt` zeigen beide auf `~/.codex/skills`. Die ausgelieferten Profile führen beide in `default_targets` (Finding `20260901-sync-target-collision`), jeder Skill wurde damit zweimal in denselben Ordner kopiert und ausgetauscht.

**Optionen.** Einen der beiden Namen aus `$targetMap` und den Profilen entfernen oder zur Laufzeit nach aufgelöstem Zielordner deduplizieren.

**Entscheidung.** Dedup. Beide Namen sind legitime Aliase: die ChatGPT-Erweiterung in VS Code liest denselben Ordner wie die Codex-CLI. Wer `-Targets vscode-chatgpt` aufruft, meint etwas Richtiges und soll keinen Fehler bekommen. Der Dedup wirkt zusätzlich auf jede künftige Alias-Konstellation und auf Profile, die ein Ziel versehentlich doppelt listen.

**Trade-off.** Welcher der beiden Namen im Log erscheint, hängt an der Reihenfolge in `default_targets`, der zweite wird als übersprungen ausgewiesen. Kommt je ein Ziel dazu, das denselben Ordner mit anderem Inhalt bespielen soll, trägt die Deduplikation nicht mehr.

## 2026-09-01: Der Lauf ohne `-Apply` bleibt ohne Nebenwirkung

**Kontext.** `setup-from-profile.ps1` rief `vendor-import.ps1` unbedingt auf, bevor es überhaupt zur `-Apply`-Weiche kam (Finding `20260901-setup-from-profile-apply-misleading`). Nur `sync.ps1` bekam `-DryRun`. Ein als Vorschau gedachter Lauf lud damit fehlende Vendor-Skills nach und schrieb `vendor-lock.json` und `UPSTREAM.md`.

**Optionen.** `vendor-import.ps1` einen eigenen Dry-Run-Modus geben oder den Import im Vorschau-Pfad auslassen.

**Entscheidung.** Auslassen und benennen. Ein Dry-Run-Modus für `vendor-import.ps1` müsste jede der drei Schreibstellen einzeln abfangen. Das Skript steht ohnehin für einen größeren Umbau an (`20260714-idea-transactional-vendor-import`). `validate.ps1` läuft weiter in beiden Pfaden: es liest nur. Die Vendor-Skills, die es prüft, liegen im Repo, der ausgelassene Import macht es also nicht rot.

**Trade-off.** Auf einer Maschine, der ein Vendor-Skill tatsächlich fehlt, meldet die Vorschau jetzt einen Validierungsfehler statt ihn stillschweigend durch einen Download zu heilen. Das ist beabsichtigt: die Vorschau soll den Zustand zeigen, nicht ändern.

## 2026-09-01: Ein Fault-Hook in sync.ps1, um das Abbruchfenster zu testen

**Kontext.** Der Verify der Session (`docs/reviews/2026-09-01-cursor-verify.md`, Finding 1) zeigte, dass das `finally` des Skill-Austauschs das Backup löschte, sobald `$backupPath` gesetzt war. Genau im Fenster zwischen den beiden Umbenennungen liegt der Skill aber nur im Backup. Ein Strg+C führt dann durch `finally` ohne `catch`: Ziel leer, beide Fassungen weg. Der Fix (Restore im `finally`, Löschen erst bei nachgewiesenem Ziel) braucht einen Test, der genau diesen Zwischenzustand herstellt. Zwischen den beiden `[System.IO.Directory]::Move`-Aufrufen steht jedoch kein Kommando, das sich per Funktion überschreiben ließe. Beide sind statische .NET-Aufrufe.

**Optionen.**
1. Timing: einen zweiten Prozess auf das Staging-Verzeichnis warten lassen und dort eine Datei sperren.
2. Den `finally`-Block als Text aus `sync.ps1` extrahieren und im Test separat ausführen.
3. Einen Fault-Hook per Umgebungsvariable in `sync.ps1`.

**Entscheidung.** Option 3, `SKILLSHUB_SYNC_FAULT=between-moves` wirft zwischen den Umbenennungen. Option 1 hängt an einem Zeitfenster von Mikrosekunden und wäre im CI ein Flake-Generator. Option 2 prüft eine Textkopie statt des laufenden Skripts und bricht bei jeder Umformatierung. Der Hook ist eine Zeile, steht sichtbar im Ablauf und führt in einen Pfad, der die Installation nachweislich intakt lässt.

**Trade-off.** Produktionscode trägt einen Testschalter. Die Variable ist eindeutig benannt und sonst nirgends belegt. Wer sie setzt, bekommt einen abgebrochenen Sync mit wiederhergestelltem Skill, keinen Schaden. Der innere `try`/`catch` um den zweiten Move ist im selben Zug entfallen: er machte dasselbe wie der Restore im `finally`, zwei Kopien derselben Logik driften auseinander.

## 2026-09-02: Der Timeout-Pfad von upscale.py räumt seine Eingabe NICHT weg

**Kontext.** Seit 8071b34 entfernt `upscale.py` seine Kopie im geteilten ComfyUI-Input auf jedem Pfad, damit sich nicht pro Lauf eine Datei ansammelt. Der Befund `20260902-upscale-cleanup-removes-queued-input` aus der Lesewelle zeigt die Kehrseite: ein Timeout sagt nichts über den Job. Steht der noch in der Queue, hat ComfyUI die Datei noch gar nicht geöffnet, das Löschen gelingt also und LoadImage scheitert später. Die GPU-Arbeit ist dann verloren, obwohl der Job lief.

**Optionen.**
1. Kopie auch nach Timeout entfernen (Stand vor dem Fix).
2. Den Prompt vor dem Aufräumen per `/interrupt` bzw. `/queue`-Delete abbrechen, dann löschen.
3. Die Kopie auf dem Timeout-Pfad liegen lassen und im Fehlertext benennen.

**Entscheidung.** Option 3. Option 1 opfert einen laufenden Job für eine aufgeräumte Festplatte, das ist die falsche Richtung. Option 2 wäre sauber, braucht aber zwei zusätzliche API-Aufrufe samt Fehlerbehandlung und trifft eine Entscheidung, die dem Aufrufer gehört: ein Timeout heisst nicht zwingend, dass er den Job nicht mehr will. Option 3 kostet eine Datei je Timeout, nennt sie im Abbruchtext und lässt den Job unangetastet.

**Trade-off.** Wer häufig in den Timeout läuft, sammelt Dateien im Input-Ordner. Sie tragen den eindeutigen `upscale_src_`-Präfix aus b223786, sind also erkennbar und der Fehlertext nennt jede einzeln. Erfolg und gemeldeter Fehler räumen weiter auf, das sind die häufigen Fälle.

## 2026-09-02: upscale.py stagt über das Dateisystem, nicht über die ComfyUI-API

**Kontext.** `COMFY_INPUT` war fest auf die lokale Stability-Matrix-Installation codiert, während `--url`/`COMFYUI_URL` frei konfigurierbar blieb (Finding `20260902-upscale-comfy-input-hardcoded`). Auf eine andere Instanz gerichtet kopierte das Skript lokal, der Server suchte die Datei bei sich und der Lauf konnte nur in den 1200s-Timeout laufen.

**Optionen.**
1. Das Bild über ComfyUIs `/upload/image` hochladen, dann ist der Ordner egal.
2. Den Ordner konfigurierbar machen und einen nicht-lokalen Host ohne Angabe ablehnen.

**Entscheidung.** Option 2. Option 1 ist der saubere Weg für echte Fernnutzung, verlangt aber einen multipart/form-data-Body von Hand: die Skripte sind bewusst stdlib-only, `urllib` bringt dafür nichts mit. Der reale Anwendungsfall ist eine lokale Instanz, der Fehlerfall eine Fehlkonfiguration. Genau die fängt `--input-dir` (env `COMFYUI_INPUT`, gleiches Muster wie `--url`) ab, und ohne Angabe wird ein nicht-lokaler Host mit Begründung abgelehnt statt stumm ins Leere zu kopieren.

**Trade-off.** Eine ComfyUI-Instanz auf einer anderen Maschine bleibt nur nutzbar, wenn ihr Input-Ordner hier als Pfad erreichbar ist (Netzlaufwerk, Mount). Ein reiner HTTP-Tunnel reicht nicht. Das ist ehrlicher als vorher: der Lauf scheitert jetzt sofort mit dem Grund statt nach zwanzig Minuten mit einem Timeout.

## 2026-09-02: website-audit behält Port und Pfade fest und erzwingt stattdessen Exklusivität

**Kontext.** Der Skill startet Edge auf Debug-Port 9222 mit Profil `$env:TEMP\edge-lh` und schreibt den Lighthouse-Report nach `$env:TEMP\lh-report`. Alle drei Namen sind hart codiert und die Warteschleife akzeptierte jeden Prozess, der auf 9222 antwortet (Finding `20260902-website-audit-debug-port-collision`). Ein abgestürzter Vorlauf oder ein Parallellauf liess Lighthouse damit die falsche Session messen bzw. den Report überschreiben.

**Optionen.**
1. Freien Port und eindeutige Profil- und Report-Pfade je Lauf erzeugen.
2. Die festen Namen behalten und im ersten Schritt sicherstellen, dass kein zweiter Lauf aktiv ist.

**Entscheidung.** Option 2. Option 1 scheitert an der Ablaufform des Skills: jeder Block ist ein eigener Tool-Call und der Shell-State überlebt den Call nicht (der Skill sagt das in Schritt b2 selbst). Ein zufälliger Port müsste also über eine Datei weitergereicht werden, deren Name wieder fest wäre. Statt die Kollision aufzulösen macht Schritt a die Voraussetzung explizit: antwortet auf 9222 schon jemand, bricht der Lauf ab, Profil-Reste eines Absturzes werden beendet und ein alter Report wird gelöscht, bevor gemessen wird.

**Trade-off.** Zwei Audits gleichzeitig auf derselben Maschine sind nicht mehr möglich, sie waren es faktisch vorher auch nicht, nur ohne Warnung. Ein fremder Chrome- oder Edge-Debug-Port auf 9222 blockiert den Audit ebenfalls, was richtig ist: den hätte der Lauf sonst vermessen.

## 2026-09-02: Der Antigravity-Test nagelt den Apply-Pfad fest, nicht den Dry-Run

**Kontext.** Aus dem Cursor-Lauf `20260902T154440-9e966d` kam ein Test mit der Behauptung, er falle aus, wenn der Workflow-Block in `sync.ps1:130-145` sein `Copy-Item -Force` außerhalb von `ShouldProcess` ausführt. Die Mutationsprobe widerlegt das: der Test bleibt grün. Unter `-DryRun` schützen zwei Schichten unabhängig voneinander. `sync.ps1:15` setzt `$WhatIfPreference = $true`. Diese Preference hält `Copy-Item` und `New-Item` schon von sich aus an, weil beide selbst `ShouldProcess` unterstützen. Das Auflösen des `if ($PSCmdlet.ShouldProcess(...))`-Blocks ändert deshalb nichts, `Copy-Item -WhatIf:$false` ebenso wenig (die zweite Probe lief nur deshalb grün, weil die erste Schicht noch stand). Rot wird ein Dry-Run-Test auf diesem Block allein durch das Streichen von `sync.ps1:15`. Das fängt bereits der Test über den Skill-Austausch.

**Optionen.**
1. Den Test unverändert übernehmen: er ist grün, er beschreibt eine wahre Aussage über das Verhalten.
2. Den Test verwerfen, weil seine benannte Mutation nicht greift.
3. Den Test auf den Apply-Pfad umstellen: die Vorlage aus dem Repo überschreibt eine lokal geänderte Workflow-Datei.

**Entscheidung.** Option 3. Option 1 hätte einen Test in die Suite gelegt, der eine doppelt abgesicherte Stelle ein drittes Mal bestätigt und dafür einen zusätzlichen Kind-pwsh startet: er kann nur noch mit dem Test brechen, den er dupliziert. Option 2 hätte auch das Apply-Verhalten weggeworfen, das tatsächlich ungetestet war. Die Probe "Copy-Item im Workflow-Block entfernt" macht den umgestellten Test rot, damit hängt er an einer eigenen Mutation.

**Trade-off.** Die Zusage "`-DryRun` fasst die Workflows nicht an" steht jetzt nirgends als Test. Sie hängt an `sync.ps1:15`, das der Test `leaves the installed skill untouched with -DryRun` abdeckt. Fällt diese Zeile, wird dieser eine Test rot und der Grund ist im Kommentar des Antigravity-Tests notiert, damit niemand den Dry-Run-Fall aus Versehen ein zweites Mal baut.

## 2026-09-06: Ein dauerhaft fehlschlagender Poll bricht nicht ab, er wird in der Timeout-Meldung benannt

**Kontext.** Der Verify-Lauf `20260904T072157-6da303` hat an `upscale.py:172` und `comfy_generate.py:200` zwei Seiten desselben `except OSError` beanstandet. Die eine ist ein Fehler: `api()` endet in `json.loads(...)`, ein neustartendes ComfyUI oder ein Proxy davor antwortet mit leerem Body oder HTML, und die daraus entstehende `JSONDecodeError` ist kein `OSError`. Genau der Neustart, für den die Wiederholung gebaut wurde, beendete den Lauf also sofort. Die andere ist eine Frage der Auslegung: `urllib.error.HTTPError` erbt von `OSError`, ein Server, der jeden Poll mit 500 beantwortet, wird deshalb bis zum Budget wiederholt (gemessen: 39 Polls bei `--timeout 60`) und der Lauf meldet am Ende einen Timeout, nicht den Statuscode.

**Optionen.**
1. Beim ersten `HTTPError` abbrechen, `ValueError` weiter wiederholen.
2. Nach N Fehlversuchen in Folge abbrechen.
3. Weiter wiederholen, den letzten Poll-Fehler aber merken und in der Timeout-Meldung nennen.

**Entscheidung.** Option 3, dazu `except (OSError, ValueError)` für den eigentlichen Fehler. Option 1 macht die Wiederholung an der Stelle wertlos, an der sie gebraucht wird: ein Neustart liefert typischerweise erst 502/503 vom Proxy und danach wieder 200, ein Abbruch beim ersten 5xx tötet also gesunde Läufe. Option 2 braucht eine zweite Zahl neben `--timeout`, die niemand kennt und die den Lauf trotzdem hart beendet. Option 3 lässt die Semantik, wie sie ist (`--timeout` ist die einzige Grenze) und behebt den Teil, der wirklich fehlte: die Ursache steht jetzt in der Abschlussmeldung statt nur in einer stderr-Zeile, die in einem langen Lauf untergeht.

**Trade-off.** Ein Server, der dauerhaft 500 liefert, kostet weiter das volle Budget, bevor der Lauf endet. Das ist bewusst: die Alternative ist ein Abbruch, der zwischen "kaputt" und "startet gerade neu" nicht unterscheiden kann.

## 2026-09-06: Der Tunnel auf 127.0.0.1 bleibt ungeprüft, statt ihn per HTTP zu erraten

**Kontext.** Der `LOCAL_HOSTS`-Guard aus `a0fa1f8` lehnt einen nicht-lokalen Host ohne `--input-dir` ab. Der Verify-Lauf hält dagegen, dass genau der im Kommentar genannte Tunnel durchrutscht: zeigt `--url` auf `127.0.0.1` und liegt ComfyUI woanders, landet die Kopie im lokalen Input-Ordner, der Server sieht sie nie und der Lauf endet nach 1200s im Timeout (bestätigt, siehe `docs/reviews/2026-09-04-cursor-verify.md`). Der Hostname trägt diese Information nicht, keine Prüfung an der URL kann den Fall erkennen.

**Optionen.**
1. Nach dem Kopieren prüfen, ob der Server die Datei sieht (`/object_info/LoadImage` listet den Inhalt seines Input-Ordners), und sonst mit dem Hinweis auf `--input-dir` abbrechen.
2. Das Bild über ComfyUIs Upload-Endpunkt schicken statt es zu kopieren, dann entfällt der geteilte Ordner ganz.
3. Nichts tun und die Lücke benennen.

**Entscheidung.** Vorerst Option 3, gebucht als offener Backlog-Eintrag `20260904-upscale-tunnel-input-dir`. Option 1 hängt an einer Antwortform, die ComfyUI zwischen Versionen ändern kann, und ist ohne laufende Instanz nicht prüfbar, also nicht in einer Triage-Session zu belegen. Option 2 ist der saubere Weg, verlangt aber einen multipart/form-data-Body von Hand (die Skripte sind stdlib-only, das ist bereits am 2026-09-02 entschieden worden) und ändert das Aufräumen mit.

**Trade-off.** Die Fehlkonfiguration "Tunnel auf einen fremden Rechner" kostet weiter ein volles Timeout und hinterlässt seit `ddb3ad4` zusätzlich die Staging-Kopie, die der Lauf bewusst liegen lässt. Der reale Anwendungsfall bleibt die lokale Instanz, der Guard fängt weiter jeden Fall, den er ohne Rateschritt erkennen kann.


## 2026-09-07: Die Staging-Kopie gehört dem Job ab dem Absenden, nicht ab der Antwort

**Kontext.** `ddb3ad4` übergab die Kopie in ComfyUIs Input-Ordner an den Job, sobald `/prompt` mit einer `prompt_id` geantwortet hatte. Der Verify-Lauf `20260907T074020-639054` hält dagegen, dass ComfyUI den Prompt schon während des offenen POST in die Queue stellt: Strg+C zwischen Absenden und Antwort lief mit `keep_staged` False ins `finally` und löschte die Eingabe eines Jobs, der bereits eingereiht war (bestätigt, Probe im Commit-Text von `1be5ecc`). Der Punkt ist nicht, wo das Flag steht, sondern welche Ausgänge als Beweis gelten, dass kein Job existiert.

**Optionen.**
1. Flag erst nach der Antwort setzen (Status vor diesem Fix), Fenster bleibt offen.
2. Flag vor dem Absenden setzen und bei jedem Fehler des POST wieder fallen lassen.
3. Flag vor dem Absenden setzen und nur dort fallen lassen, wo die Antwort selbst beweist, dass nichts eingereiht wurde: ein HTTP-Fehler (der Server hat geantwortet und abgelehnt) oder ein Body ohne `prompt_id`.

**Entscheidung.** Option 3. Option 2 sieht symmetrisch aus, wirft aber genau den Fall weg, um den es geht: eine mitten im POST sterbende Verbindung sagt nichts darüber, ob der Server den Prompt vorher angenommen hat, und behandelt ihn wie eine Ablehnung. Die beiden Fehler kosten unterschiedlich viel: eine überflüssige Kopie ist eine Datei im geteilten Ordner, eine fehlende Kopie ist ein Job, der später in LoadImage stirbt, samt der GPU-Arbeit davor. Bei Unklarheit wird deshalb behalten. Die Vorprüfung über `/system_stats` liegt vor dem Kopieren, ein schlicht nicht laufendes ComfyUI erreicht diesen Pfad also gar nicht.

**Trade-off.** Ein Abbruch, der die Verbindung mitten im POST reißt, hinterlässt jetzt eine Datei, obwohl vielleicht nichts eingereiht wurde. Der Ordner ist geteilt, aus einer Leiche wird über viele Läufe ein Haufen; dagegen steht der eindeutige Dateiname je Lauf und die Tatsache, dass der häufige Fehlerfall (abgelehnter Workflow, vertippter `--checkpoint`) über den HTTP-Fehler weiter aufräumt und mit einem eigenen Test festgehalten ist.

## 2026-09-07: Die Poll-Schleife fängt drei benannte Ausnahmeklassen, nicht `Exception`

**Kontext.** Zum dritten Mal steht dieselbe `except`-Klammer zur Debatte. `f938366` hat `ValueError` ergänzt (der Body, an dem `json.loads` scheitert), dieser Lauf `http.client.HTTPException` (das Drahtformat, an dem `resp.read()` scheitert: `IncompleteRead` bei zu kurzem Body, `BadStatusLine` bei kaputter Statuszeile). Die naheliegende Frage ist, ob die Aufzählung nicht besser `except Exception` heißen sollte, damit die vierte Klasse nicht auch noch einzeln nachgereicht werden muss.

**Optionen.**
1. `except Exception`, jeder Poll-Fehler wird wiederholt.
2. Die drei Klassen benennen und die Liste bei Bedarf erweitern.

**Entscheidung.** Option 2. `except Exception` würde auch eigene Programmierfehler in der Schleife (Tippfehler auf einem Attribut, falscher Typ in `min(30.0, remaining)`) in stille Wiederholungen verwandeln: der Lauf liefe bis zum Timeout und meldete am Ende einen Poll-Fehler, statt sofort mit dem Traceback zu sterben. Die drei benannten Klassen decken alles ab, was zwischen Prozess und Server schiefgehen kann, und jede weitere Erweiterung braucht dieselbe Begründung wie diese hier.

**Trade-off.** Kommt eine vierte Fremdklasse dazu, stirbt der Lauf beim ersten Poll, statt sie zu überstehen. Der Preis ist ein Fehlschlag mit Traceback, der die Klasse benennt, statt eines stillen Timeouts, der sie verschluckt.

## 2026-09-24: Modernisierungs-Review als Entscheidungsschicht über code-audit, kein eigener Umsetzungs-Skill

**Kontext.** Ziel: ältere Repos regelmäßig mit neueren Modellen prüfen und modernisieren. Ein Brainstorming-Prompt schlug 16 Phasen und zwei Skills vor (`repository-audit` für die Analyse, `repository-modernization` für die Umsetzung). Vorhanden waren `code-audit` (Befunde je Zeile, schließt Architektur ausdrücklich aus), `gen-diagram` (IST gegen den laufenden Stand) und dünne Plugin-Raster (`engineering:tech-debt`, `engineering:architecture`). Keiner davon entscheidet je Modul oder bewertet einen Rewrite.

**Optionen.**
1. Kein neuer Skill, die vorhandenen nur kombinieren.
2. Ein vollständiger Skill mit allen 16 Phasen, unabhängig von `code-audit`.
3. Ein schlanker Skill als Entscheidungsschicht, der die Prüftiefe an `code-audit` delegiert, dazu kein eigener Umsetzungs-Skill.

**Entscheidung.** Option 3 (`repo-modernization-review`). Option 1 lässt genau die Lücke offen, um die es geht: KEEP/REFACTOR/REWRITE/DELETE je Modul, SOLL mit Delta und die Rewrite-Bewertung. Option 2 pflegt dieselben Prüfregeln an zwei Stellen. Die Umsetzung decken `engineering` und `code-audit --fix` bereits ab; die Trennung von Analyse und Umsetzung hält der Skill selbst, weil er nur berichtet. Pilot am 2026-09-24 auf `blumsoft-platform` (Deep) und `sound-studio` (Standard) mit Opus 5.5, die Rückmeldungen beider Läufe sind eingearbeitet.

**Trade-off.** Die Qualität hängt an `code-audit`: ändert sich dessen Referenzstruktur, muss Step 2 nachgezogen werden. Ein Lauf kostete im Pilot rund 400.000 Tokens und 25 bis 30 Minuten; Tier-C-Repos laufen deshalb nur als Triage.
