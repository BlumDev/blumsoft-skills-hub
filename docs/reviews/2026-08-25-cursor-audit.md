# Zweitmeinungs-Audit 2026-08-25 (blumsoft-skills-hub)

- Basis: Branch `main`, Commit `3b07c8c`.
- Modell: cursor-grok-4.6-high, read-only via ai-router Gate (`scripts/gate.py`), decision_id 20260825T211500-33b95d.
- Auftrag: neue Findings finden, die die bisherigen Reviews unter `docs/reviews/` nicht kennen (Schwerpunkte Datenverlust, Robustheit, Security, Vereinfachung).
- Ergebnis: 6 neue Findings (0 high / 5 medium / 1 low), unten byte-verbatim.
- Validierung: Stichprobe der Welle: blumsoft-crawler saveChain-Poison am Code-Muster plausibilisiert (AtomicJsonStore hat den .catch, die CLI-Kette nicht); dieses Repo im Detail unvalidiert übernommen

## Gate-Output (byte-verbatim)

# Audit blumsoft-skills-hub (main, 3b07c8c)

## New findings

`scripts/skills/sync.ps1:38` - severity(medium) - `codex` and `vscode-chatgpt` both resolve to `$HOME/.codex/skills`, and `profiles/freelancer-fullstack.json` (the documented default) lists both in `default_targets`. A normal `sync.ps1 -Profile freelancer-fullstack` therefore delete-and-replace every Codex skill twice; an interrupt or failed `Move-Item` on the second pass removes the tree the first pass just installed.

`scripts/skills/vendor-import.ps1:52` - severity(medium) - Presence is snapshotted before install (`$preExistingSkills`, line 28) and any skill whose dest folder already exists is skipped (line 52). If the installer writes a directory and then throws (line 59), a retry treats those folders as complete: they are not re-fetched, `UPSTREAM.md` is not written (line 66), and `vendor-lock.json` still gets a fresh `generated_at` (lines 84–86). A partial vendor tree stays partial with no provenance.

`skills/custom/gen-asset/scripts/ensure_comfyui.ps1:20` - severity(medium) - `Start-Process -RedirectStandardOutput/-RedirectStandardError` always targets the same `%TEMP%\comfyui_server.log` / `.err` names and does not pass `-Force`. After the first start those files exist; the next start while ComfyUI is down (reboot, crash) fails on the existing logs, then the script still polls for 240s and exits 1. The skill documents this helper as the autonomous, idempotent engine start.

`scripts/skills/setup-from-profile.ps1:11` - severity(medium) - `-Apply` only gates `sync.ps1`. Every invocation, including the no-flag “preview” path (line 17), runs `vendor-import.ps1` first, which downloads skills and rewrites `vendor-lock.json`. The switch name implies a dry run; it is not.

`scripts/skills/vendor-import.ps1:80` - severity(medium) - New lock entries are never inserted (`if ($skillProp) { $skillProp.Value.commit = $commit }`), and `Install-RepoSkills` only knows `guanyang/antigravity-skills` and `sickn33/antigravity-awesome-skills` (line 16). `skills/registry.yaml:305` registers `brand-review` as `vendor-anthropic` (`path: skills/vendor/anthropic/brand-review`); it is in `bundles/business-growth.yaml` but absent from `vendor-lock.json`, has no `UPSTREAM.md`, and cannot be re-imported or pinned by this pipeline. `validate.ps1` never compares registry vendor skills to the lock.

`.github/workflows/validate.yml:17` - severity(low) - CI runs only `./scripts/skills/validate.ps1`. `tests/skills/tooling-edge.Tests.ps1`, `tests/test_with_server.py`, `tests/project/bootstrap-project.Tests.ps1`, and `scripts/skills/validate-skills.ps1` never run on a PR, so the regression tests added for the 2026-07-16 tooling fixes cannot fail the gate.

## Not new but worth repeating

`scripts/skills/sync.ps1:72` — still logged as medium, but it is installed-skill data loss; the default profile now triggers that replace twice on `~/.codex/skills`.
`scripts/skills/sync.ps1:59` — path-traversal `Remove-Item -Path` is still open while `20260714-idea-pester-edge-tests` is marked done; those tests are not in CI.
`scripts/skills/validate.ps1:158` — the with_server duplication is no longer just drift risk: CI now requires the two copies to stay byte-identical.

## Summary

6 new findings (0 high / 5 medium / 1 low). The one that matters most: default sync maps `codex` and `vscode-chatgpt` to the same directory and replace-cycles it twice.
