# Reconcile 2026-08-24 (blumsoft-skills-hub)

- Basis: Branch `main`, Commit `a87267c`, Arbeitskopie sauber.
- Modell: gpt-5.6-sol, read-only via ai-router Gate (`scripts/gate.py`), decision_id 20260824T213428-f1604e.
- Auftrag: alle Findings aus `docs/reviews/` gegen den heutigen Code geprüft (behoben / offen / obsolet / nicht nachweisbar).
- Ergebnis: 25 Findings gesamt, 15 behoben, 10 offen, 0 obsolet, 0 nicht nachweisbar.
- Validierung: Stichproben der Welle: MergeMadnessSolver (FIXED-Beleg) und papierkram-belege (OPEN-Beleg) am Code bestätigt; dieses Repo im Detail unvalidiert übernommen

## Gate-Output (byte-verbatim)

# Reconcile blumsoft-skills-hub (main, a87267c)

## Verdicts

### docs/reviews/2026-07-14-codex.md

`scripts/project/bootstrap-project.ps1:55 high` | FIXED | `scripts/project/bootstrap-project.ps1:43,61` | The script constructs a named hashtable and splats it into `sync.ps1`, so workspace, profile, and bundle arguments bind correctly.

`scripts/skills/vendor-import.ps1:44 high` | FIXED | `scripts/skills/vendor-import.ps1:65` | Pre-existing skills are skipped when writing `UPSTREAM.md` and skill commit metadata, preventing unchanged content from being labeled as newly imported.

`scripts/skills/vendor-import.ps1:34 high` | FIXED | `scripts/skills/vendor-import.ps1:58` | The installer receives the locked commit through `--ref $Commit`, and line 59 throws for a nonzero native exit code.

`scripts/skills/sync.ps1:66 high` | OPEN | `scripts/skills/sync.ps1:59,72` | Registry names still reach `Join-Path` without an allowlist, and the resulting destination is deleted through wildcard-aware `Remove-Item -Path`.

`scripts/skills/sync.ps1:25 medium` | FIXED | `scripts/skills/sync.ps1:29` | When callers do not bind `-Targets`, the script now loads the profile's `default_targets`.

`scripts/project/bootstrap-project.ps1:30 medium` | FIXED | `scripts/project/bootstrap-project.ps1:13,28` | `-DryRun` enables `WhatIfPreference`, and template creation proceeds only after `ShouldProcess` approves it.

`scripts/skills/sync.ps1:66 medium` | OPEN | `scripts/skills/sync.ps1:72` | Copying now uses staging, but the installed skill is still deleted before the staging directory is moved into place, so a failed move can leave no installation.

`skills/custom/web/scripts/with_server.py:72 medium` | FIXED | `skills/custom/web/scripts/with_server.py:132` | Server output is inherited instead of redirected to unread pipes, so verbose servers cannot block on a full pipe buffer.

`skills/custom/web/scripts/with_server.py:79 medium` | OPEN | `skills/custom/web/scripts/with_server.py:46` | Process liveness is now checked, but any listener on the requested port is still accepted while the launched process remains alive.

`skills/custom/web/scripts/with_server.py:96 medium` | OPEN | `skills/custom/web/scripts/with_server.py:69` | Running Windows process trees are terminated with `taskkill /T`, but the already-exited leader branch at line 78 cannot terminate surviving descendants.

`scripts/skills/update-vendor.ps1:21 medium` | FIXED | `scripts/skills/update-vendor.ps1:7` | `-RefreshLock` now aborts explicitly without changing `vendor-lock.json`.

`scripts/skills/vendor-import.ps1:12 medium` | FIXED | `scripts/skills/vendor-import.ps1:22` | The installer path is derived from `CODEX_HOME`, the current user's home directory, or `USERPROFILE`, with no fixed username.

`scripts/skills/lib.ps1:192 medium` | FIXED | `scripts/skills/lib.ps1:203` | GitHub requests now use a 30-second timeout, optional token authentication, and controlled exception handling.

`scripts/skills/lib.ps1:87 medium` | FIXED | `scripts/skills/lib.ps1:93` | `Get-AllBundles` now throws immediately when a bundle ID already exists in the map.

`scripts/skills/archive-report.ps1:17 low` | FIXED | `scripts/skills/archive-report.ps1:16` | The report now throws when the requested profile file does not exist.

### docs/reviews/2026-06-24-code-audit.md

`H1 high skills/custom/web/scripts/with_server.py vs skills/vendor/guanyang/webapp-testing/scripts/with_server.py` | OPEN | `scripts/skills/validate.ps1:158` | The two scripts remain byte-identical copies, and validation now explicitly requires that duplication to remain synchronized.

`H2 high skills/custom/web/scripts/with_server.py shell=True` | OPEN | `skills/custom/web/scripts/with_server.py:98,135` | Ordinary `--server` commands are shell-free, but `--shell-server` still passes an arbitrary CLI-supplied command to `Popen` with shell execution enabled.

`M1 medium Set-Content -Encoding UTF8` | FIXED | `scripts/skills/vendor-import.ps1:79,86` | Both generated files are written through `Write-FileUtf8NoBom`, while `update-vendor.ps1` no longer writes the lock file.

`M2 medium heterogeneous SKILL.md frontmatter` | OPEN | `scripts/skills/validate.ps1:129` | Validation enforces only a nonempty description for maintainer-owned skills, leaving vendor and archive frontmatter without a common schema.

`M3 medium scripts/skills/lib.ps1 YAML parsing` | OPEN | `scripts/skills/lib.ps1:60` | Bundle, registry, and archive YAML are still parsed line by line with regular expressions rather than a YAML parser.

`M4 medium scripts/skills/lib.ps1:190-196` | FIXED | `scripts/skills/lib.ps1:199` | GitHub access now supports `GITHUB_TOKEN`, applies 30-second timeouts, and converts request failures into a controlled error.

`M5 medium missing CI` | FIXED | `.github/workflows/validate.yml:3` | A pull-request workflow on Windows now runs `./scripts/skills/validate.ps1`.

`L1 low scripts/skills/vendor-import.ps1:12` | FIXED | `scripts/skills/vendor-import.ps1:22` | The installer location is resolved from environment-specific home paths instead of `C:\Users\Marcus`.

`L2 low bundles/index.yaml legacy wrappers` | OPEN | `bundles/index.yaml:23` | All eight legacy wrapper IDs remain registered through line 46 and therefore continue expanding the maintained configuration surface.

`L3 low skills/vendor/guanyang/notebooklm/scripts/*` | OPEN | `skills/vendor/guanyang/notebooklm/scripts/ask_question.py:96` | Multiple bare `except:` handlers remain, and `BrowserSession.close` at `browser_session.py:223` still closes only its page.

## Summary

Counts: 25 total / 15 fixed / 10 open / 0 obsolete / 0 not-verifiable.

`scripts/skills/sync.ps1:59,72` | Unvalidated registry names still influence a recursive wildcard-aware deletion target.

`scripts/skills/sync.ps1:72` | Replacement is staged but not atomic because the working installation is removed before the final move.

`skills/custom/web/scripts/with_server.py:46` | Readiness still proves only that the child is alive and the port is occupied, not that the child owns the listener.