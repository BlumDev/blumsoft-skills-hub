---
status: wartung
track: infra
next_step: "Skills bei Bedarf pflegen, optional eine CI-Validierung ergänzen"
updated: 2026-09-02
---

# Backlog

Einzige Workflow-Wahrheit dieses Repos. Format/Regeln: siehe `../AGENTS.md`.
IDs `YYYYMMDD-slug`, nie renumbern. Ideen = offene Einträge mit `#idea`.

## Offen

- [ ] 20260825-zweitmeinung-audit Zweitmeinungs-Audit 2026-08-25 (cursor-grok-4.6-high): 6 neue Findings (0 high / 5 medium / 1 low), siehe docs/reviews/2026-08-25-cursor-audit.md #note

- [ ] 20260824-reconcile Reconcile 2026-08-24 (gpt-5.6-sol): 10 von 25 Review-Findings offen, 15 behoben, siehe docs/reviews/2026-08-24-reconcile.md #note

- [ ] 20260825-pester-alt-suiten-pwsh76 Alt-Testsuiten (bootstrap-project, tooling-edge) verlieren unter pwsh 7.6.5 ihre Top-Level-Variablen in It-Blöcken, 7 Tests rot unabhängig vom Code-Stand (auch auf unverändertem main), Setup nach BeforeAll/BeforeDiscovery verlagern; CI führt nur validate.ps1 aus und ist nicht betroffen #bug (Merge-Session 2026-08-25)

Aus Codex-Audit 2026-07-14 (`docs/reviews/2026-07-14-codex.md`), am 2026-08-18 gegen den Code validiert (`docs/reviews/2026-08-18-reconcile.md`, Basis 4dcd9fd). Zwei der fünf damals bestätigt offenen Punkte sind inzwischen erledigt (siehe `## Erledigt`), diese drei bleiben offen, Belege am Merge-Stand 2026-09-02 nachgezogen:

- [ ] 20260714-idea-atomic-sync Sync über temporäre Verzeichnisse, Validierung und atomaren Austausch implementieren #idea (mittel, Rest bestätigt 2026-09-02: Staging und atomarer Austausch sind da (`sync.ps1:78-101`, zwei Umbenennungen statt Löschen plus Verschieben, 633c2dd und fb163c6), offen bleibt allein die Validierung des Stagings, `sync.ps1:82-86` normalisiert nur die Kodierung der `SKILL.md`)
- [ ] 20260714-idea-real-yaml-parser Regex-YAML-Parser durch echten Parser plus Schema-Validierung ersetzen #idea (mittel, bestätigt 2026-09-02: `lib.ps1:96-133` (Bundles), `lib.ps1:185-210` (Registry) und `lib.ps1:222-248` (Archivplan) parsen weiter zeilenweise)
- [ ] 20260714-idea-transactional-vendor-import Vendor-Import als transaktionale, commit-genaue Pipeline mit Staging, Inhalts-Hashes und atomarem Lock-Update #idea (gross, Rest bestätigt 2026-09-02: gesperrter Commit und Exitcode-Prüfung sind da, es fehlen Staging, Inhalts-Hashes und der atomare Lock-Schreibvorgang in `vendor-import.ps1:56-58,84-86`)

Aus Code-Audit 2026-06-24 (`reviews/2026-06-24-code-audit.md`), recovered, am 2026-08-18 gegen den Code validiert (`docs/reviews/2026-08-18-reconcile.md`), beide bestätigt offen:

- [ ] 20260624-legacy-wrapper-bundles-sunset 8 Legacy-Wrapper-Bundles (`bundles/index.yaml:23-46`) delegieren via compose_with und verursachen Pflegeaufwand, Sunset-Plan sobald keine externen Referenzen mehr auf die alten IDs zeigen #idea (Quelle: reviews/2026-06-24-code-audit.md, korrigiert 2026-08-18: die core_skills sind nicht mehr leer, jeder Wrapper trägt genau einen Skill; die Sunset-Bedingung ist nicht erfüllt, `templates/project/.github/copilot-instructions.md:7,10` verweist noch auf `essentials` und `project-kickoff`)
- [ ] 20260624-vendor-notebooklm-robustness Geerbte Vendor-Robustheitsmängel in notebooklm-Skripten (bare except fängt KeyboardInterrupt/SystemExit, unvollständiges Playwright-Cleanup), geerbt (MIT), nicht selbst fixen, ggf. Upstream-Issue/PR #bug (Quelle: reviews/2026-06-24-code-audit.md, bestätigt 2026-08-18: `ask_question.py:96,132,153,180,186`, `browser_utils.py:75`, Cleanup nur der Page in `browser_session.py:77-80,224-231`)

## Erledigt

Ältere Einträge liegen in `archive/backlog-archive.md` (Archiv-Regel der AGENTS.md). Der Reconcile vom 2026-08-18 hat die damals hier stehenden Einträge stichprobenartig gegen den Code gehalten, alle geprüften sind tatsächlich umgesetzt (Belege in `docs/reviews/2026-08-18-reconcile.md`); inzwischen sind sie ins Archiv gewandert.

Security-Session Careful-Fixes (Branch `security/careful-fixes`, gemergt 2026-08-25). Der Reconcile vom 2026-08-18 führte diese beiden Punkte noch als offen, richtig für seine Basis 4dcd9fd: der Fix lag zu dem Zeitpunkt erst auf dem Branch, main erreichte er über a2390a3:

- [x] 20260714-sync-remove-path-traversal sync übergibt ungeprüfte Namen an rekursives Remove-Item, `..`/Wildcards ermöglichen Traversal/Massenlöschung (5e3d7f2, 2026-07-16; verifiziert 2026-09-02: `Test-SkillId`/`Assert-SkillId`/`Resolve-SkillTargetPath` in `lib.ps1:15-55`, `sync.ps1` arbeitet durchgehend mit `-LiteralPath`)
- [x] 20260714-idea-id-allowlist-literalpath Skill-/Bundle-IDs per Allowlist validieren, `-LiteralPath` in den ID-getriebenen Pfadoperationen (5e3d7f2, 2026-07-16; verifiziert 2026-09-02: Allowlist `^[a-z0-9][a-z0-9-]*\z` mit `-cmatch` in `lib.ps1:15-19`, beim YAML-Einlesen erzwungen)
- [x] 20260825-merge-careful-fixes Branch security/careful-fixes nach main gemergt, Guard in mains Staging/ShouldProcess-Sync eingepasst, Guard-Suite 32/32 grün (a2390a3, 2026-08-25)

Wartungs-Session 2026-09-01 (Findings aus den Reviews 2026-08-24, 2026-08-25 und 2026-08-31; jeder Fix mit Regressionstest, jeder Test gegen daef7d0 gegengeprüft):

- [x] 20260901-sync-target-collision sync.ps1 synchronisierte jeden Skill zweimal in denselben Ordner, weil `codex` und `vscode-chatgpt` beide auf `~/.codex/skills` zeigen und die Profile beide in default_targets führen; Ziele werden jetzt nach aufgelöstem Ordner dedupliziert (633c2dd, 2026-09-01)
- [x] 20260901-sync-non-atomic-replace sync.ps1 löschte das Ziel vor dem finalen Move, ein Abbruch dazwischen hinterließ den Skill komplett entfernt; Austausch jetzt über zwei Renames mit Restore, `Move-Item` durch `[System.IO.Directory]::Move` ersetzt, weil Move-Item Verzeichnisse rekursiv verschiebt und bei Fehlern beide Seiten halb gefüllt zurücklässt (633c2dd, 2026-09-01)
- [x] 20260901-setup-from-profile-apply-misleading setup-from-profile.ps1 rief vendor-import.ps1 auch ohne `-Apply` und schrieb dabei vendor-lock.json und UPSTREAM.md; der Vorschau-Lauf lässt den Import jetzt aus und benennt ihn, validate.ps1 läuft weiter in beiden Pfaden (0d13561, 2026-09-01)
- [x] 20260901-comfy-generate-seed-hires-mismatch `--seed` erreichte den zweiten Sampler der Hires-Workflows nicht, der Hires-Pass blieb auf dem eingebackenen Seed 12345; SAMPLER_HIRES bekommt jetzt denselben Seed, `--steps` bleibt bewusst auf dem Basis-Pass (71a10e1 plus Skill-Doku 7763258, 2026-09-01)
- [x] 20260901-comfy-generate-poll-ignores-error Poll-Schleifen in comfy_generate.py und upscale.py lasen nur `outputs.images` und warteten bei `status=error` den vollen Timeout ab statt den Fehler zu melden; beide prüfen jetzt `status.status_str`, unklare History-Formen warten weiter (69b2d61, 2026-09-01)
- [x] 20260901-upscale-input-filename-collision upscale.py kopierte die Eingabe unter festem Namen in ComfyUIs geteilten Input-Ordner, gleicher Basename oder paralleler Lauf überschrieb die fremde Eingabe (b223786, 2026-09-01)
- [x] 20260831-cursor-audit Zweitmeinungs-Audit 2026-08-31 (cursor-grok-4.6-high): alle 3 Findings behoben, siehe die drei 20260901-Einträge zum gen-asset-Tooling (b223786, 2026-09-01)

Verify der Runde-2-Commits (`docs/reviews/2026-09-01-cursor-verify.md`, cursor-grok-4.6-high, Basis daef7d0..main): 5 Commits sauber, 3 Findings, alle drei am Code bestätigt und mit Mutationsprobe belegt:

- [x] 20260901-sync-backup-deleted-in-finally Das `finally` des Skill-Austauschs löschte das Backup, sobald `$backupPath` gesetzt war; ein Abbruch zwischen den beiden Umbenennungen (Strg+C läuft durch finally ohne catch) nahm Staging und Backup mit und ließ das Ziel leer zurück. Restore jetzt im finally, Löschen erst bei nachgewiesenem Ziel, Testzugang über den Fault-Hook `SKILLSHUB_SYNC_FAULT` (fb163c6, 2026-09-01)
- [x] 20260901-upscale-input-not-cleaned-up upscale.py entfernte seine Kopie im geteilten ComfyUI-Input auf keinem Pfad, mit den eindeutigen Namen aus b223786 sammelt sich eine Datei je Lauf an; main() räumt jetzt im finally auf, OSError gefangen (8071b34, 2026-09-01)
- [x] 20260901-decisions-duplicate-adrs Die drei ADRs der Wartungs-Session standen doppelt in decisions.md, beide Kopien aus 5335314; zweite Kopie entfernt, erste unverändert, bewusste Ausnahme von append-only im Commit begründet (4010295, 2026-09-01)
- [x] 20260901-cursor-verify Verify-Lauf 20260901T120648-8b95f3 selbst: Report angelegt, Triage am Code, kein Rework an den fünf sauberen Commits (21a12a0, 2026-09-01)

## Verworfen

(keine)
