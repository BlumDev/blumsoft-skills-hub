# Verify der Runde-2-Commits 2026-09-01 (cursor-grok-4.6-high)

Basis: `daef7d0..main` (8 Commits der Wartungs-Session 2026-09-01), Arbeitskopie sauber. Run-ID 20260901T120648-8b95f3 (Gate read-only). Auftrag: die Fixes der Session gegen ihre eigene Absicht prüfen, nicht neu auditieren. Ergebnis: 5 Commits sauber, 3 Findings (1 high / 1 medium / 1 low).

## Externe Ausgabe (wörtlich)

Intent der acht Commits (aus Messages + Backlog): Sync-Ziele deduplizieren und Skill-Austausch per Rename statt Löschen; `setup-from-profile` ohne `-Apply` ohne Schreib-Nebenwirkungen; `--seed` auf `SAMPLER_HIRES`; Poll-Abbruch bei ComfyUI `status=error`; eindeutige Upscale-Inputdateien; Doku/Archiv/Stil. Geprüft nur am kombinierten Diff (keine Caller außerhalb der Hunks). Hunting-Liste: Boundaries, Error-Pfade, State/Interrupt, Tests vs. Fix-Absicht.

`633c2dd scripts/skills/sync.ps1:112 - high -` `$backupPath` ist gleichzeitig Restore-Quelle und Müll. `finally` löscht das Backup immer, wenn die Variable noch gesetzt ist. Fehlerszenario: `Directory::Move($dstPath, $backupPath)` ist durch, der Skill liegt nur noch unter `.<skill>.old-<guid>`. Danach Strg+C bzw. `PipelineStoppedException` (PowerShell führt `finally` aus, `catch` oft nicht) oder das Zurückbenennen scheitert, weil `$dstPath` wieder existiert. `finally` entfernt Staging und Backup. Zielordner leer, beide Fassungen weg. Genau das Abbruchfenster, das der Fix schließen sollte; der Lock-Test trifft nur den ersten Move (Ziel bleibt liegen) und sieht Restore/`finally` nicht.

`b223786 skills/custom/gen-asset/scripts/upscale.py:109 - medium -` Jeder Lauf kopiert nach `COMFY_INPUT` unter `upscale_src_<8hex>_<basename>` und löscht die Kopie nie (Erfolg, `sys.exit` nach `execution_error`, Timeout). Vorher ein fester Name, also eine Datei zum Überschreiben. Fehlerszenario: 50 Upscales (Batch oder parallel, der Kollisionsfall des Fixes) hinterlassen 50 Dateien im geteilten Comfy-Input; die Tests prüfen nur, dass zwei `hero.png` nicht denselben Namen bekommen, nicht dass nach `download()` aufgeräumt wird.

`5335314 docs/decisions.md:106 - low -` Die drei ADRs der Session stehen zweimal hintereinander mit abweichendem Wortlaut (z.B. „statt es zu schließen“ vs. „statt geschlossen“). Fehlerszenario: ein späterer Edit aktualisiert nur die erste Kopie, die zweite bleibt die stille Zweitwahrheit.

`0d13561` sauber: `vendor-import` hängt an `$Apply`, Validate bleibt lesend, Test mit Stubs sichert den Call-Graph inkl. Gegenprobe mit `-Apply`.

`71a10e1` sauber: `SAMPLER_HIRES` bekommt denselben Seed, `--steps` bleibt auf dem Basis-Pass; Tests laden die echten Hires-JSONs und verlangen, dass das Template-Seed ≠ 4242 ist.

`69b2d61` sauber: Abbruch nur bei `status_str == "error"`, unklare Formen fallen auf den alten Timeout; Helper- und Poll-Tests prüfen Meldung, Poll-Anzahl 1 und dass Success/fehlendes Status nicht abbrechen. `images` vor Error ist dasselbe wie vorher.

`7763258` sauber: SKILL.md entspricht dem Seed/Steps-Verhalten.

`7dd3641` sauber: nur Komma vor „und“ in Kommentaren, kein Verhalten.

## Triage am Code (Claude, 2026-09-01)

Alle drei Findings bestätigt, keines widerlegt. Kein Rework an den fünf als sauber gemeldeten Commits.

### 1. sync.ps1 finally löscht das Backup bedingungslos (high, BESTÄTIGT, behoben)

Beleg am Stand `7dd3641`: `sync.ps1:109` prüfte im `finally` nur `if ($backupPath -and (Test-Path -LiteralPath $backupPath))` und löschte danach. Die Variable ist ab `sync.ps1:94` gesetzt, also bereits vor dem ersten `Directory::Move`. Zwischen den beiden Renames ist der Zustand "Ziel weg, Backup da": ein Abbruch dort führte durch dasselbe `finally`, das Staging und Backup entfernte. Der innere `catch` deckte nur die Ausnahme des zweiten `Move` ab, nicht `PipelineStoppedException`, und `finally` lief in beiden Fällen.

Fix: das `finally` prüft zuerst `Test-Path -LiteralPath $dstPath`. Fehlt das Ziel und existiert das Backup, wird der Restore versucht, bevor irgendetwas gelöscht wird. Das Backup fällt nur, wenn das Ziel nachweislich vorliegt. Der innere `try`/`catch` um den zweiten `Move` ist entfallen: er tat nichts anderes als der Restore im `finally` und wäre eine zweite, leicht abdriftende Kopie derselben Logik.

Test: `tests/skills/sync-targets.Tests.ps1`, Describe "sync.ps1 interrupted between the two renames". Der Zwischenzustand entsteht über einen dokumentierten Fault-Hook (`SKILLSHUB_SYNC_FAULT=between-moves`), weil zwischen den beiden `Directory::Move`-Aufrufen kein Kommando steht, das sich von außen ersetzen ließe. Die Quelle wird vor dem Fehllauf verändert, damit der Test die alte Fassung am Ziel nachweist statt nur irgendeine.

Mutationsprobe: `finally` wieder auf bedingungsloses Löschen gestellt, Test rot (Ziel leer). Zurückgestellt, Test grün.

### 2. upscale.py lässt die Kopie im geteilten Input liegen (medium, BESTÄTIGT, behoben)

Beleg am Stand `7dd3641`: `upscale.py:112` kopierte nach `COMFY_INPUT` und `main()` kannte keinen Aufräumpfad, weder nach `download()` noch vor den drei `sys.exit`-Ausgängen. Die Eindeutigkeit aus `b223786` verschärft das: der feste Name überschrieb sich selbst, der eindeutige sammelt sich an.

Fix: der Rumpf von `main()` ab dem Kopieren liegt in `try`/`finally`, das `finally` entfernt die Kopie per `os.remove` und fängt `OSError` (ein noch lesender ComfyUI-Prozess hält die Datei unter Windows offen; ein gescheitertes Aufräumen darf ein fertiges Upscale nicht zum Fehler machen).

Test: `tests/test_gen_asset.py`, `UpscaleInputCleanupTests` deckt Erfolgspfad und Fehlerpfad ab. Die Kollisionsprüfung aus `b223786` misst jetzt zum Zeitpunkt von `/prompt` statt nach dem Lauf, sonst hätte das Aufräumen ihre Aussage aufgefressen.

### 3. Drei ADRs doppelt in decisions.md (low, BESTÄTIGT, behoben)

Beleg: `git show --stat 5335314 -- docs/decisions.md` weist 72 eingefügte Zeilen aus, also beide Kopien aus demselben Commit derselben Session. Die Abweichungen sind rein sprachlich (`Dasselbe mit` vs. `Dasselbe, aber mit`, `statt es zu schließen` vs. `statt geschlossen`), inhaltlich decken sich Kontext, Optionen, Entscheidung und Trade-offs Punkt für Punkt. Damit ist es Rauschen und keine Historie.

Fix: die zweite Kopie der drei Einträge entfernt, an der ersten kein Wort geändert. Bewusste Ausnahme von der Append-only-Regel der `AGENTS.md`, begründet im Commit.
