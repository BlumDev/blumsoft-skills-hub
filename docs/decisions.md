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

## 2026-09-01: Skill-Austausch per Rename statt per Move-Item

**Kontext.** `sync.ps1` löschte das Zielverzeichnis und verschob erst danach die fertige Staging-Kopie an seine Stelle (Finding `20260901-sync-non-atomic-replace`). Zwischen Löschen und Verschieben lag ein Fenster, in dem ein Abbruch den Skill komplett entfernt hinterließ. Das Staging aus `2692b22` deckte nur die Kopierphase ab, nicht den Austausch.

**Optionen.**
1. Reihenfolge umdrehen: erst das Ziel wegbenennen, dann die neue Version an seine Stelle verschieben, beides mit `Move-Item`.
2. Dasselbe, aber mit `[System.IO.Directory]::Move`.
3. Beim Austausch weiterhin löschen und nur die Fehlerbehandlung verbessern.

**Entscheidung.** Option 2, plus Restore der alten Version, falls der zweite Schritt scheitert. Ausschlaggebend war eine Messung an einer gesperrten Datei im Zielverzeichnis (offener Handle ohne Freigabe): `Move-Item` verschiebt Verzeichnisse rekursiv und ließ Quelle und Ziel danach beide halb gefüllt zurück, `[System.IO.Directory]::Move` scheiterte folgenlos und ließ die Quelle vollständig stehen. Option 1 hätte das Fenster also nur verschoben statt geschlossen. Staging- und Backup-Pfad hängen jetzt an `$dstPath`, weil die .NET-Methode relative Pfade gegen das Prozess-Arbeitsverzeichnis auflöst, das in PowerShell von `Get-Location` abweichen kann.

**Trade-off und Restrisiken.**
- Der Rename ist nur auf demselben Volume atomar. Staging, Backup und Ziel liegen im selben Ordner, damit ist das gegeben, solange niemand einzelne Skills auf ein anderes Volume verlinkt.
- Das Entsorgen der alten Version läuft mit `-ErrorAction SilentlyContinue`: ein bereits erfolgreicher Austausch darf nicht nachträglich am Aufräumen scheitern. Preis: bei gesperrten Dateien bleibt ein `.<skill>.old-<guid>`-Ordner liegen, auf den eine Warnung hinweist.
- Ein Absturz genau zwischen den beiden Renames hinterlässt das Ziel weg und das Backup da. Das ist der verbleibende Rest des Findings, jetzt aber ohne Datenverlust und mit einem sprechenden Ordnernamen daneben.

## 2026-09-01: Doppelte Sync-Ziele deduplizieren statt einen Alias streichen

**Kontext.** `codex` und `vscode-chatgpt` zeigen beide auf `~/.codex/skills`, und die ausgelieferten Profile führen beide in `default_targets` (Finding `20260901-sync-target-collision`). Jeder Skill wurde damit zweimal in denselben Ordner kopiert und ausgetauscht.

**Optionen.** Einen der beiden Namen aus `$targetMap` und den Profilen entfernen, oder zur Laufzeit nach aufgelöstem Zielordner deduplizieren.

**Entscheidung.** Dedup. Beide Namen sind legitime Aliase: die ChatGPT-Erweiterung in VS Code liest denselben Ordner wie die Codex-CLI. Wer `-Targets vscode-chatgpt` aufruft, meint etwas Richtiges und soll keinen Fehler bekommen. Der Dedup wirkt zusätzlich auf jede künftige Alias-Konstellation und auf Profile, die ein Ziel versehentlich doppelt listen.

**Trade-off.** Welcher der beiden Namen im Log erscheint, hängt an der Reihenfolge in `default_targets`, der zweite wird als übersprungen ausgewiesen. Kommt je ein Ziel dazu, das denselben Ordner mit anderem Inhalt bespielen soll, trägt die Deduplikation nicht mehr.

## 2026-09-01: Der Lauf ohne `-Apply` bleibt ohne Nebenwirkung

**Kontext.** `setup-from-profile.ps1` rief `vendor-import.ps1` unbedingt auf, bevor es überhaupt zur `-Apply`-Weiche kam (Finding `20260901-setup-from-profile-apply-misleading`). Nur `sync.ps1` bekam `-DryRun`. Ein als Vorschau gedachter Lauf lud damit fehlende Vendor-Skills nach und schrieb `vendor-lock.json` und `UPSTREAM.md`.

**Optionen.** `vendor-import.ps1` einen eigenen Dry-Run-Modus geben, oder den Import im Vorschau-Pfad auslassen.

**Entscheidung.** Auslassen und benennen. Ein Dry-Run-Modus für `vendor-import.ps1` müsste jede der drei Schreibstellen einzeln abfangen, und das Skript steht ohnehin für einen größeren Umbau an (`20260714-idea-transactional-vendor-import`). `validate.ps1` läuft weiter in beiden Pfaden: es liest nur, und die Vendor-Skills, die es prüft, liegen im Repo, der ausgelassene Import macht es also nicht rot.

**Trade-off.** Auf einer Maschine, der ein Vendor-Skill tatsächlich fehlt, meldet die Vorschau jetzt einen Validierungsfehler statt ihn stillschweigend durch einen Download zu heilen. Das ist beabsichtigt: die Vorschau soll den Zustand zeigen, nicht ändern.
