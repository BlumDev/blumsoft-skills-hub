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
