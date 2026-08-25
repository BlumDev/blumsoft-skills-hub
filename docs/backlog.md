---
status: wartung
track: infra
next_step: "Skills bei Bedarf pflegen, optional eine CI-Validierung ergänzen"
updated: 2026-08-23
---

# Backlog

Einzige Workflow-Wahrheit dieses Repos. Format/Regeln: siehe `../AGENTS.md`.
IDs `YYYYMMDD-slug`, nie renumbern. Ideen = offene Einträge mit `#idea`.

## Offen

- [ ] 20260825-zweitmeinung-audit Zweitmeinungs-Audit 2026-08-25 (cursor-grok-4.6-high): 6 neue Findings (0 high / 5 medium / 1 low), siehe docs/reviews/2026-08-25-cursor-audit.md #note

- [ ] 20260824-reconcile Reconcile 2026-08-24 (gpt-5.6-sol): 10 von 25 Review-Findings offen, 15 behoben, siehe docs/reviews/2026-08-24-reconcile.md #note

- [ ] 20260825-pester-alt-suiten-pwsh76 Alt-Testsuiten (bootstrap-project, tooling-edge) verlieren unter pwsh 7.6.5 ihre Top-Level-Variablen in It-Blöcken, 7 Tests rot unabhängig vom Code-Stand (auch auf unverändertem main), Setup nach BeforeAll/BeforeDiscovery verlagern; CI führt nur validate.ps1 aus und ist nicht betroffen #bug (Merge-Session 2026-08-25)

Aus Codex-Audit 2026-07-14 (`docs/reviews/2026-07-14-codex.md`), noch nicht validiert:

- [ ] 20260714-idea-atomic-sync Sync über temporäre Verzeichnisse, Validierung und atomaren Austausch implementieren #idea (mittel)
- [ ] 20260714-idea-real-yaml-parser Regex-YAML-Parser durch echten Parser plus Schema-Validierung ersetzen #idea (mittel)
- [ ] 20260714-idea-transactional-vendor-import Vendor-Import als transaktionale, commit-genaue Pipeline mit Staging, Inhalts-Hashes und atomarem Lock-Update #idea (gross)

Aus Code-Audit 2026-06-24 (`reviews/2026-06-24-code-audit.md`), recovered, noch nicht validiert:

- [ ] 20260624-legacy-wrapper-bundles-sunset 8 Legacy-Wrapper-Bundles (leere core_skills, delegieren nur via compose_with) verursachen dauerhaften Pflegeaufwand, Sunset-Plan sobald keine externen Referenzen mehr auf die alten IDs zeigen #idea (Quelle: reviews/2026-06-24-code-audit.md)
- [ ] 20260624-vendor-notebooklm-robustness Geerbte Vendor-Robustheitsmängel in notebooklm-Skripten (bare except fängt KeyboardInterrupt/SystemExit, unvollständiges Playwright-Cleanup), geerbt (MIT), nicht selbst fixen, ggf. Upstream-Issue/PR #bug (Quelle: reviews/2026-06-24-code-audit.md)

## Erledigt

Codex-Work-Orders Welle B, Chunks 1-4 (`ai-router/logs/tmp/wo-codex-skillshub-1..4.out.md`), 2026-07-16:

- [x] 20260714-bootstrap-splat-positional Bootstrap splattet Parameter positionell statt benannt, `-WorkspaceRoot`/Bundle-ID falsch gebunden, Kopie dann Abbruch (4b65c98, 2026-07-16)
- [x] 20260714-vendor-import-false-provenance vendor-import aktualisiert vorhandene Skills nicht, markiert sie aber mit HEAD, Provenienz falsch (73b2813, 2026-07-16)
- [x] 20260714-vendor-import-unlocked-commit vendor-import ignoriert Lock-Commit und prüft py-Exitcode nicht, unreviewter HEAD/Teilimport möglich (751d900, 2026-07-16)
- [x] 20260714-sync-default-targets-ignored sync liest `default_targets` nicht, Standardlauf synct zusätzlich nach Claude und ins aktuelle Repo (380f90a, 2026-07-16)
- [x] 20260714-bootstrap-dryrun-writes Bootstrap `-DryRun` schützt Template-Kopien nicht, Probelauf verändert das Zielprojekt (cfb2bd2, 2026-07-16)
- [x] 20260714-sync-delete-before-copy sync löscht Ziel vor erfolgreicher Kopie, Abbruch hinterlässt fehlenden/teilweisen Skill (2692b22, 2026-07-16)
- [x] 20260714-withserver-pipe-deadlock with_server konsumiert umgeleitete stdout/stderr nie, ausgabestarke Server blockieren bei vollem Pipe-Puffer (a487e5f, 2026-07-16)
- [x] 20260714-withserver-readiness-foreign with_server-Readiness akzeptiert jeden Port-Listener und prüft Prozessleben nicht, Tests gegen Fremd-Altprozess (a487e5f, 2026-07-16)
- [x] 20260714-withserver-orphan-children with_server beendet bei `shell=True` nur die Shell, Kindprozesse verwaisen und blockieren Ports (a487e5f, 2026-07-16)
- [x] 20260714-refreshlock-stale-content `-RefreshLock` aktualisiert nur den Repo-Commit ohne Inhalte/Skill-Commits, Lock fälschlich aktuell (17cfea6, 2026-07-16)
- [x] 20260714-vendor-import-hardcoded-user vendor-import hat hartkodierten Benutzerpfad `Marcus`, bricht auf anderen Maschinen ab (e6d1c00, 2026-07-16)
- [x] 20260714-github-calls-no-timeout GitHub-Aufrufe ohne Timeout/kontrollierte Fehlerbehandlung, Pipeline hängt oder bricht roh ab (56cb79f, 2026-07-16)
- [x] 20260714-duplicate-bundle-id-silent Doppelte Bundle-IDs überschreiben sich still im Hashtable, Validator erkennt Kollision nicht (728b00d, 2026-07-16)
- [x] 20260714-archive-report-unknown-profile archive-report behandelt unbekanntes Profil still als leer, plausibel falscher Archivbericht (ddfab67, 2026-07-16)
- [x] 20260714-idea-validate-profile-fields Profilfelder inkl. `default_targets` und unbekannte Properties im Validator prüfen (09928ff, 2026-07-16)
- [x] 20260714-idea-server-helper-processgroups Server-Helper mit Prozessgruppen, geerbten Log-Streams und Prozesszustandsprüfung ausstatten (a487e5f, 2026-07-16)
- [x] 20260624-withserver-custom-dup-vendor with_server.py in skills/custom/web ist byte-identische Kopie des Vendor-Skripts (DRY/Drift, Kopie liegt außerhalb vendor-lock.json), zusammen mit den withserver-*-Einträgen betrachtet; validate.ps1 erzwingt jetzt per SHA-256-Hash-Check Byte-Gleichheit zwischen beiden Kopien (b6a2e97, 2026-07-16)
- [x] 20260624-withserver-custom-shell-true with_server.py (custom) startete den Server via subprocess Popen shell=True mit ungeprüftem --server-Kommando (Command-Injection-Muster) (a487e5f, 2026-07-16)
- [x] 20260624-setcontent-utf8-bom Set-Content -Encoding UTF8 schreibt ein BOM und verletzt die No-BOM-Policy; vendor-import.ps1 (UPSTREAM.md, vendor-lock.json) auf UTF8Encoding(false)-Helfer umgestellt, der Schreibpfad in update-vendor.ps1 entfiel bereits durch die unlocked-commit-Korrektur (09b0643, 2026-07-16)
- [x] 20260624-skillmd-frontmatter-schema Kein durchgesetztes SKILL.md-Frontmatter-Schema, validate.ps1 prüft nur Existenz/BOM statt Frontmatter-Struktur, mindestens für skills/custom nicht-leere description erzwungen (61012ec, 2026-07-16)

Codex-Work-Orders Welle B, Chunk 5 (`ai-router/logs/tmp/wo-codex-skillshub-5.out.md`), 2026-07-16:

- [x] 20260624-no-ci-validate-gate Kein CI-Gate, validate.ps1 lief nur manuell, GitHub-Actions-Workflow validiert jetzt bei jedem Pull Request auf windows-latest (2793ea5, 2026-07-16)
- [x] 20260714-idea-shouldprocess-dryrun `SupportsShouldProcess`/`-WhatIf` ersetzt die Ad-hoc-DryRun-Zweige in bootstrap-project.ps1 und sync.ps1, Staging-Kopieransatz aus 2692b22 bleibt erhalten (ab07328, 2026-07-16)
- [x] 20260714-idea-bootstrap-splatting-test Pester-Regressionstest für Bootstrap-Parameter-Splatting (mehrere `-BundleId`, benannte Sync-Parameter) ergänzt (88cca11, 2026-07-16)
- [x] 20260714-idea-pester-edge-tests Pester-Edge-Case-Suite für vendor-import-Exitcode, doppelte Bundle-IDs, unsichere Skill-Namen und with_server-Portkonflikt ergänzt (68a5fe0, 2026-07-16)

Security-Session Careful-Fixes (Branch `security/careful-fixes`, gemergt 2026-08-25):

- [x] 20260714-sync-remove-path-traversal sync übergibt ungeprüfte Namen an rekursives Remove-Item, `..`/Wildcards ermöglichen Traversal/Massenlöschung (5e3d7f2, 2026-07-16)
- [x] 20260714-idea-id-allowlist-literalpath Skill-/Bundle-IDs per Allowlist validieren, `-LiteralPath` in den ID-getriebenen Pfadoperationen (5e3d7f2, 2026-07-16)
- [x] 20260825-merge-careful-fixes Branch security/careful-fixes nach main gemergt, Guard in mains Staging/ShouldProcess-Sync eingepasst, Guard-Suite 32/32 grün (a2390a3, 2026-08-25)

## Verworfen

(keine)
