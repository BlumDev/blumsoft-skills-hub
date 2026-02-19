# BlumSoft Skills Hub

![Automation](https://img.shields.io/badge/Automation-PowerShell-5391FE?logo=powershell&logoColor=white)
![Workflow](https://img.shields.io/badge/Workflow-Bundle--First-1F6FEB)
![Targets](https://img.shields.io/badge/Targets-Codex%20%7C%20Cursor%20%7C%20Antigravity%20%7C%20VS%20Code-2DA44E)

Bundle-first skills hub for Codex, Cursor, Antigravity, and VS Code (Copilot).
Goal: maintain skills/bundles once, sync consistently to all targets.

## Quick links

- [Supported targets](#supported-targets)
- [Concepts](#concepts)
- [Quickstart](#quickstart)
- [Daily usage](#daily-usage)
- [License and third-party](#license-and-third-party)

## Supported targets

| Target | Sync path | Scope |
|---|---|---|
| `codex` | `~/.codex/skills` | global |
| `cursor` | `~/.cursor/skills` | global |
| `antigravity` | `~/.gemini/antigravity/skills` | global |
| `vscode-copilot` | `<repo>/.github/skills` | project-local |
| `antigravity workflows` | `~/.gemini/antigravity/global_workflows` | optional |

## Concepts

- `Skill`: a folder containing `SKILL.md`
- `Bundle`: curated stack of `core_skills` plus optional `extended_skills`
- `Profile`: predefined bundle selection (e.g. `fullstack-founder`)
- `global_workflows`: Antigravity session starter markdown files (not skills)

## Quickstart

```powershell
# PowerShell (repo root)
./scripts/skills/validate.ps1
./scripts/skills/sync.ps1 -Profile fullstack-founder -SyncAntigravityWorkflows
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Daily usage

```powershell
# Inspect bundle
./scripts/skills/resolve-bundle.ps1 -BundleId web-wizard
./scripts/skills/resolve-bundle.ps1 -BundleId web-wizard -IncludeExtended
./scripts/skills/resolve-bundle.ps1 -BundleId web-wizard -Summary
```

```powershell
# Sync selected bundles/targets
./scripts/skills/sync.ps1 -BundleId web-wizard,security-engineer -Targets codex,cursor,antigravity
```

## License and third-party

See `LICENSE.md` and `THIRD_PARTY_NOTICES.md`.
