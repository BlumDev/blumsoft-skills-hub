# Reconcile 2026-09-02 (cursor-grok-4.6-high)

Basis: main, Kurz-SHA 08347c5. Run-ID 20260902T115757-4b16a9.

## Tabelle (wörtlich aus dem Lauf)

1. Bestand: 5 Berichte bis 2026-08-25 (`2026-06-24-code-audit.md`, `2026-07-14-codex.md`, `2026-08-18-reconcile.md`, `2026-08-24-reconcile.md`, `2026-08-25-cursor-audit.md`). Die beiden Reconciles vom 18. und 24.08. benennen denselben Ursprungsbestand (10 + 15); gezählt wird jedes Finding einmal unter dem Ursprungsbericht, plus die 6 Neuen vom 25.08. Ideen aus Abschnitt 2 des Codex-Berichts und die 08-18-Backlog-Ideen sind keine eigenen Audit-Findings.

| Bericht | Finding-Kurzname | Urteil | Beleg |
|---|---|---|---|
| 2026-06-24-code-audit.md | H1 with_server-Duplikat Custom/Vendor | OPEN | `scripts/skills/validate.ps1:152-160` erzwingt weiter zwei byte-identische Kopien (`skills/custom/web/scripts/with_server.py` und `skills/vendor/guanyang/webapp-testing/scripts/with_server.py`) |
| 2026-06-24-code-audit.md | H2 shell=True mit CLI-Kommando | OPEN | `skills/custom/web/scripts/with_server.py:35-39,133-136` — `--server` ist shell-frei, `--shell-server` übergibt weiter ein CLI-Kommando an `Popen(..., shell=True)` |
| 2026-06-24-code-audit.md | M1 Set-Content UTF8-BOM | FIXED | `scripts/skills/vendor-import.ps1:79,86` schreibt über `Write-FileUtf8NoBom`; `scripts/skills/update-vendor.ps1` schreibt die Lock-Datei nicht mehr; kein `Set-Content` unter `scripts/` |
| 2026-06-24-code-audit.md | M2 heterogenes SKILL.md-Frontmatter | OPEN | `scripts/skills/validate.ps1:129-140` prüft nicht-leere `description` nur für `skills/custom`, nicht für Vendor/Archiv |
| 2026-06-24-code-audit.md | M3 Regex-YAML-Parser | OPEN | `scripts/skills/lib.ps1:108-130` (Bundles), `191-207` (Registry), `230-244` (Archivplan) parsen weiter zeilenweise per Regex |
| 2026-06-24-code-audit.md | M4 GitHub-API ohne Timeout/Auth | FIXED | `scripts/skills/lib.ps1:250-263` — `-TimeoutSec 30`, optionales `GITHUB_TOKEN`, kontrollierte Fehlermeldung |
| 2026-06-24-code-audit.md | M5 keine CI | FIXED | `.github/workflows/validate.yml:3-17` — PR-Workflow auf `windows-latest` führt `validate.ps1` aus |
| 2026-06-24-code-audit.md | L1 hartkodierter User-Pfad | FIXED | `scripts/skills/vendor-import.ps1:22-25` löst über `$HOME` / `USERPROFILE` / `CODEX_HOME` auf |
| 2026-06-24-code-audit.md | L2 Legacy-Wrapper-Bundles | OPEN | `bundles/index.yaml:23-46` listet die acht Wrapper weiter; `templates/project/.github/copilot-instructions.md:7,10` verweist auf `essentials` und `project-kickoff` |
| 2026-06-24-code-audit.md | L3 notebooklm bare except / Cleanup | OPEN | `skills/vendor/guanyang/notebooklm/scripts/ask_question.py:96,132,153,180,186`; `browser_utils.py:75`; `browser_session.py:223-231` schließt nur die Page |
| 2026-07-14-codex.md | bootstrap splat positional | FIXED | `scripts/project/bootstrap-project.ps1:43-61` splattet ein benanntes Hashtable in `sync.ps1` |
| 2026-07-14-codex.md | vendor-import falsche Provenienz | FIXED | `scripts/skills/vendor-import.ps1:28-32,65-66` überspringt vorab vorhandene Skills bei `UPSTREAM.md` und Lock-Commit |
| 2026-07-14-codex.md | vendor-import ohne Lock-Commit / Exitcode | FIXED | `scripts/skills/vendor-import.ps1:16-20,58-59` — `--ref $Commit` und Throw bei `$LASTEXITCODE -ne 0` |
| 2026-07-14-codex.md | sync Remove-Item-Path-Traversal | FIXED | `scripts/skills/lib.ps1:15-55` (`Assert-SkillId`, `Resolve-SkillTargetPath`); `scripts/skills/sync.ps1:70,118,122` nur noch `-LiteralPath` |
| 2026-07-14-codex.md | sync default_targets ignoriert | FIXED | `scripts/skills/sync.ps1:29` übernimmt `default_targets` aus dem Profil, wenn `-Targets` ungebunden ist |
| 2026-07-14-codex.md | bootstrap DryRun ohne Schutz | FIXED | `scripts/project/bootstrap-project.ps1:1,13,28` — `SupportsShouldProcess`, `-DryRun` setzt `WhatIfPreference` |
| 2026-07-14-codex.md | sync Delete-vor-Copy | FIXED | `scripts/skills/sync.ps1:88-117` — zwei `Directory::Move` mit Restore im `finally`, kein Löschen des Ziels vor dem Austausch |
| 2026-07-14-codex.md | with_server Pipe-Deadlock | FIXED | `skills/custom/web/scripts/with_server.py:132-137` erbt stdout/stderr, leitet nicht mehr in ungelesene Pipes um |
| 2026-07-14-codex.md | with_server Readiness fremder Listener | OPEN | `skills/custom/web/scripts/with_server.py:42-57` — Prozess lebendig plus Port belegt, kein Nachweis dass das Kind den Listener besitzt |
| 2026-07-14-codex.md | with_server verwaiste Kindprozesse | OPEN | `skills/custom/web/scripts/with_server.py:67-83` — lebender Leader: `taskkill /T`; bereits beendeter Leader (Zeile 78) killt überlebende Nachkommen nicht |
| 2026-07-14-codex.md | RefreshLock stale Lock | FIXED | `scripts/skills/update-vendor.ps1:7-8` wirft bei `-RefreshLock` und ändert `vendor-lock.json` nicht |
| 2026-07-14-codex.md | vendor-import hartkodierter User | FIXED | `scripts/skills/vendor-import.ps1:22-25` (kein `C:\Users\Marcus`) |
| 2026-07-14-codex.md | GitHub-Aufrufe ohne Timeout | FIXED | `scripts/skills/lib.ps1:250-263` |
| 2026-07-14-codex.md | doppelte Bundle-ID still | FIXED | `scripts/skills/lib.ps1:144` wirft bei doppelter Bundle-ID |
| 2026-07-14-codex.md | archive-report unbekanntes Profil | FIXED | `scripts/skills/archive-report.ps1:16` wirft, wenn die Profildatei fehlt |
| 2026-08-25-cursor-audit.md | sync doppeltes Codex-Ziel | FIXED | `scripts/skills/sync.ps1:50-63` überspringt Targets mit demselben aufgelösten Ordner (`codex` / `vscode-chatgpt`) |
| 2026-08-25-cursor-audit.md | vendor-import Partial-Retry | OPEN | `scripts/skills/vendor-import.ps1:28-32,51-53,56-59` — Snapshot vor Install, Skip wenn Dest existiert; Teilbaum nach Throw gilt beim Retry als fertig, `generated_at` wird trotzdem geschrieben (`84-86`) |
| 2026-08-25-cursor-audit.md | ensure_comfyui Log-Dateien ohne -Force | OPEN | `skills/custom/gen-asset/scripts/ensure_comfyui.ps1:20-25` — feste `%TEMP%\comfyui_server.log`/`.err`, kein `-Force`; danach 240s-Poll (`27-31`) |
| 2026-08-25-cursor-audit.md | setup-from-profile Preview schreibt Import | FIXED | `scripts/skills/setup-from-profile.ps1:12-19` — `vendor-import.ps1` nur mit `-Apply` |
| 2026-08-25-cursor-audit.md | brand-review ohne Lock / keine neuen Lock-Einträge | OPEN | `scripts/skills/vendor-import.ps1:16,80-81` kennt nur zwei Repos und aktualisiert nur vorhandene Lock-Einträge; `skills/registry.yaml:305-308` `vendor-anthropic`/`brand-review` fehlt in `vendor-lock.json`, kein `UPSTREAM.md`; `validate.ps1` vergleicht die Lock-Datei nicht |
| 2026-08-25-cursor-audit.md | CI nur validate.ps1 | OPEN | `.github/workflows/validate.yml:15-17` — `tests/skills/tooling-edge.Tests.ps1`, `tests/test_with_server.py`, `tests/project/bootstrap-project.Tests.ps1`, `scripts/skills/validate-skills.ps1` laufen nicht in CI |

**Summe:** 31 gesamt, 19 fixed, 12 open, 0 obsolete, 0 not-verifiable.

## Stichproben (hart am Code nachvollzogen)

1. **M1 Set-Content UTF8-BOM — FIXED, bestätigt.** `scripts/skills/vendor-import.ps1` schreibt `UPSTREAM.md` (Zeile 79) und `vendor-lock.json` (Zeile 86) beide über `Write-FileUtf8NoBom`. `scripts/skills/update-vendor.ps1` liest die Lock-Datei nur noch (`Get-Content ... ConvertFrom-Json`) und schreibt sie nicht mehr; bei `-RefreshLock` wirft es sofort (Zeile 7-8), bevor irgendetwas geschrieben würde. `grep -rn "Set-Content" scripts/` liefert keinen Treffer.

2. **sync default_targets ignoriert — FIXED, bestätigt.** `scripts/skills/sync.ps1:27-30`: Wenn kein `-BundleId` gebunden ist und `profiles/<Profile>.json` existiert, übernimmt der Block `$Targets` aus `$p.default_targets`, sofern `-Targets` nicht explizit per `$PSBoundParameters.ContainsKey('Targets')` gesetzt wurde. Der Parameter-Default (`@('claude','codex','cursor',...)`) wird dabei korrekt vom Profilwert überschrieben.

3. **vendor-import Partial-Retry — OPEN, bestätigt.** `Install-RepoSkills` (`vendor-import.ps1:34-59`) überspringt einen Skill allein anhand `Test-Path (Join-Path $DestPath $s)` (Zeile 51) — ein durch einen vorherigen Fehlschlag angelegter, unvollständiger Ordner (Installer bricht nach `New-Item -ItemType Directory` für Skill B ab, während Skill A schon fertig ist) gilt beim nächsten Lauf als bereits vorhanden und wird nicht erneut installiert. Am Ende des Skripts wird `$lock.generated_at` (Zeile 84) und die komplette Lock-Datei (Zeile 85-86) unbedingt geschrieben, unabhängig davon, ob im Lauf ein Skill übersprungen oder erst teilweise installiert wurde — kein Erfolgsnachweis vor dem Schreiben.

## Backlog-Abgleich

Kein Eintrag in `docs/backlog.md` unter `## Offen` beschreibt einen der beiden hier als FIXED bestätigten Punkte (M1 Set-Content, sync default_targets) — beide waren dort nie als offener Eintrag geführt, es gibt also nichts, das auf Erledigt zu verschieben wäre. Die bereits im Backlog laufenden `20260714-idea-*`-Einträge (atomarer Sync, YAML-Parser, transaktionaler Vendor-Import) decken sich mit den hier als OPEN bestätigten Punkten und bleiben unverändert offen.
