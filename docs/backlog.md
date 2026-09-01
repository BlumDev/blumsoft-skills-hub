---
status: wartung
track: infra
next_step: "Skills bei Bedarf pflegen, optional eine CI-Validierung ergänzen"
updated: 2026-09-01
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

Ältere Einträge liegen in `archive/backlog-archive.md` (Archiv-Regel der AGENTS.md).

Security-Session Careful-Fixes (Branch `security/careful-fixes`, gemergt 2026-08-25):

- [x] 20260714-sync-remove-path-traversal sync übergibt ungeprüfte Namen an rekursives Remove-Item, `..`/Wildcards ermöglichen Traversal/Massenlöschung (5e3d7f2, 2026-07-16)
- [x] 20260714-idea-id-allowlist-literalpath Skill-/Bundle-IDs per Allowlist validieren, `-LiteralPath` in den ID-getriebenen Pfadoperationen (5e3d7f2, 2026-07-16)
- [x] 20260825-merge-careful-fixes Branch security/careful-fixes nach main gemergt, Guard in mains Staging/ShouldProcess-Sync eingepasst, Guard-Suite 32/32 grün (a2390a3, 2026-08-25)

Wartungs-Session 2026-09-01 (Findings aus den Reviews 2026-08-24, 2026-08-25 und 2026-08-31; jeder Fix mit Regressionstest, jeder Test gegen daef7d0 gegengeprüft):

- [x] 20260901-sync-target-collision sync.ps1 synchronisierte jeden Skill zweimal in denselben Ordner, weil `codex` und `vscode-chatgpt` beide auf `~/.codex/skills` zeigen und die Profile beide in default_targets führen; Ziele werden jetzt nach aufgelöstem Ordner dedupliziert (633c2dd, 2026-09-01)
- [x] 20260901-sync-non-atomic-replace sync.ps1 löschte das Ziel vor dem finalen Move, ein Abbruch dazwischen hinterließ den Skill komplett entfernt; Austausch jetzt über zwei Renames mit Restore, `Move-Item` durch `[System.IO.Directory]::Move` ersetzt, weil Move-Item Verzeichnisse rekursiv verschiebt und bei Fehlern beide Seiten halb gefüllt zurücklässt (633c2dd, 2026-09-01)
- [x] 20260901-setup-from-profile-apply-misleading setup-from-profile.ps1 rief vendor-import.ps1 auch ohne `-Apply` und schrieb dabei vendor-lock.json und UPSTREAM.md; der Vorschau-Lauf lässt den Import jetzt aus und benennt ihn, validate.ps1 läuft weiter in beiden Pfaden (0d13561, 2026-09-01)
- [x] 20260901-comfy-generate-seed-hires-mismatch `--seed` erreichte den zweiten Sampler der Hires-Workflows nicht, der Hires-Pass blieb auf dem eingebackenen Seed 12345; SAMPLER_HIRES bekommt jetzt denselben Seed, `--steps` bleibt bewusst auf dem Basis-Pass (71a10e1 plus Skill-Doku 7763258, 2026-09-01)
- [x] 20260901-comfy-generate-poll-ignores-error Poll-Schleifen in comfy_generate.py und upscale.py lasen nur `outputs.images` und warteten bei `status=error` den vollen Timeout ab statt den Fehler zu melden; beide prüfen jetzt `status.status_str`, unklare History-Formen warten weiter (69b2d61, 2026-09-01)
- [x] 20260901-upscale-input-filename-collision upscale.py kopierte die Eingabe unter festem Namen in ComfyUIs geteilten Input-Ordner, gleicher Basename oder paralleler Lauf überschrieb die fremde Eingabe (b223786, 2026-09-01)
- [x] 20260831-cursor-audit Zweitmeinungs-Audit 2026-08-31 (cursor-grok-4.6-high): alle 3 Findings behoben, siehe die drei 20260901-Einträge zum gen-asset-Tooling (b223786, 2026-09-01)

## Verworfen

(keine)
