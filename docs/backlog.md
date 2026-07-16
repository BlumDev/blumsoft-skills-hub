# Backlog

Einzige Workflow-Wahrheit dieses Repos. Format/Regeln: siehe `../AGENTS.md`.
IDs `YYYYMMDD-slug`, nie renumbern. Ideen = offene Einträge mit `#idea`.

## Offen

Aus Codex-Audit 2026-07-14 (`docs/reviews/2026-07-14-codex.md`), noch nicht validiert:

- [ ] 20260714-bootstrap-splat-positional Bootstrap splattet Parameter positionell statt benannt, `-WorkspaceRoot`/Bundle-ID falsch gebunden, Kopie dann Abbruch #bug (codex-audit high)
- [ ] 20260714-vendor-import-false-provenance vendor-import aktualisiert vorhandene Skills nicht, markiert sie aber mit HEAD, Provenienz falsch #bug (high)
- [ ] 20260714-vendor-import-unlocked-commit vendor-import ignoriert Lock-Commit und prüft py-Exitcode nicht, unreviewter HEAD/Teilimport möglich #bug (high)
- [ ] 20260714-sync-default-targets-ignored sync liest `default_targets` nicht, Standardlauf synct zusätzlich nach Claude und ins aktuelle Repo #bug (med)
- [ ] 20260714-bootstrap-dryrun-writes Bootstrap `-DryRun` schützt Template-Kopien nicht, Probelauf verändert das Zielprojekt #bug (med)
- [ ] 20260714-sync-delete-before-copy sync löscht Ziel vor erfolgreicher Kopie, Abbruch hinterlässt fehlenden/teilweisen Skill #bug (med)
- [ ] 20260714-withserver-pipe-deadlock with_server konsumiert umgeleitete stdout/stderr nie, ausgabestarke Server blockieren bei vollem Pipe-Puffer #bug (med)
- [ ] 20260714-withserver-readiness-foreign with_server-Readiness akzeptiert jeden Port-Listener und prüft Prozessleben nicht, Tests gegen Fremd-Altprozess #bug (med)
- [ ] 20260714-withserver-orphan-children with_server beendet bei `shell=True` nur die Shell, Kindprozesse verwaisen und blockieren Ports #bug (med)
- [ ] 20260714-refreshlock-stale-content `-RefreshLock` aktualisiert nur den Repo-Commit ohne Inhalte/Skill-Commits, Lock fälschlich aktuell #bug (med)
- [ ] 20260714-vendor-import-hardcoded-user vendor-import hat hartkodierten Benutzerpfad `Marcus`, bricht auf anderen Maschinen ab #bug (med)
- [ ] 20260714-github-calls-no-timeout GitHub-Aufrufe ohne Timeout/kontrollierte Fehlerbehandlung, Pipeline hängt oder bricht roh ab #bug (med)
- [ ] 20260714-duplicate-bundle-id-silent Doppelte Bundle-IDs überschreiben sich still im Hashtable, Validator erkennt Kollision nicht #bug (med)
- [ ] 20260714-archive-report-unknown-profile archive-report behandelt unbekanntes Profil still als leer, plausibel falscher Archivbericht #bug (low)
- [ ] 20260714-idea-bootstrap-splatting-test Bootstrap-Parameter per Hashtable-Splatting übergeben und Multi-Bundle-Test ergänzen #idea (quick-win)
- [ ] 20260714-idea-shouldprocess-dryrun `SupportsShouldProcess`/`-WhatIf` und vollständig nebenwirkungsfreien Dry-Run einführen #idea (quick-win)
- [ ] 20260714-idea-validate-profile-fields Profilfelder inkl. `default_targets` und unbekannte Properties im Validator prüfen #idea (quick-win)
- [ ] 20260714-idea-atomic-sync Sync über temporäre Verzeichnisse, Validierung und atomaren Austausch implementieren #idea (mittel)
- [ ] 20260714-idea-pester-edge-tests Pester-Tests für Argumentbindung, Native-Command-Fehler, Portkonflikte, doppelte IDs und böse Pfade #idea (mittel)
- [ ] 20260714-idea-real-yaml-parser Regex-YAML-Parser durch echten Parser plus Schema-Validierung ersetzen #idea (mittel)
- [ ] 20260714-idea-server-helper-processgroups Server-Helper mit Prozessgruppen, geerbten Log-Streams und Prozesszustandsprüfung ausstatten #idea (mittel)
- [ ] 20260714-idea-transactional-vendor-import Vendor-Import als transaktionale, commit-genaue Pipeline mit Staging, Inhalts-Hashes und atomarem Lock-Update #idea (gross)

Aus Code-Audit 2026-06-24 (`reviews/2026-06-24-code-audit.md`), recovered, noch nicht validiert:

- [ ] 20260624-withserver-custom-dup-vendor with_server.py in skills/custom/web ist byte-identische Kopie des Vendor-Skripts (DRY/Drift, Kopie liegt ausserhalb vendor-lock.json), zusammen mit den withserver-*-Eintraegen betrachten (dieselbe evtl. loeschbare Datei) #bug (Quelle: reviews/2026-06-24-code-audit.md)
- [ ] 20260624-withserver-custom-shell-true with_server.py (custom) startet den Server via subprocess Popen shell=True mit ungeprüftem --server-Kommando (Command-Injection-Muster), zusammen mit den withserver-*-Eintraegen betrachten (dieselbe evtl. loeschbare Datei) #bug (Quelle: reviews/2026-06-24-code-audit.md)
- [ ] 20260624-setcontent-utf8-bom Set-Content -Encoding UTF8 schreibt ein BOM und verletzt die No-BOM-Policy an 3 Stellen (vendor-import.ps1:54 UPSTREAM.md, :67 vendor-lock.json, update-vendor.ps1:26 vendor-lock.json), auf UTF8Encoding(false)-Helfer umstellen #bug (Quelle: reviews/2026-06-24-code-audit.md)
- [ ] 20260624-skillmd-frontmatter-schema Kein durchgesetztes SKILL.md-Frontmatter-Schema, validate.ps1 prüft nur Existenz/BOM statt Frontmatter-Struktur, mindestens für skills/custom nicht-leere description erzwingen #idea (Quelle: reviews/2026-06-24-code-audit.md)
- [ ] 20260624-no-ci-validate-gate Kein CI-Gate, validate.ps1 läuft nur manuell, GitHub-Actions-Workflow ergänzen der bei PR validate.ps1 ausführt #idea (Quelle: reviews/2026-06-24-code-audit.md)
- [ ] 20260624-legacy-wrapper-bundles-sunset 8 Legacy-Wrapper-Bundles (leere core_skills, delegieren nur via compose_with) verursachen dauerhaften Pflegeaufwand, Sunset-Plan sobald keine externen Referenzen mehr auf die alten IDs zeigen #idea (Quelle: reviews/2026-06-24-code-audit.md)
- [ ] 20260624-vendor-notebooklm-robustness Geerbte Vendor-Robustheitsmängel in notebooklm-Skripten (bare except fängt KeyboardInterrupt/SystemExit, unvollständiges Playwright-Cleanup), geerbt (MIT), nicht selbst fixen, ggf. Upstream-Issue/PR #bug (Quelle: reviews/2026-06-24-code-audit.md)

## Erledigt

- [x] 20260714-sync-remove-path-traversal sync übergibt ungeprüfte Namen an rekursives Remove-Item, `..`/Wildcards ermöglichen Traversal/Massenlöschung (5e3d7f2, 2026-07-16)
- [x] 20260714-idea-id-allowlist-literalpath Skill-/Bundle-IDs per Allowlist validieren, `-LiteralPath` in den ID-getriebenen Pfadoperationen (5e3d7f2, 2026-07-16)

## Verworfen

(keine)
