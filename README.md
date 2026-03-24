# BlumSoft Skills Hub

![Automation](https://img.shields.io/badge/Automation-PowerShell-5391FE?logo=powershell&logoColor=white)
![Workflow](https://img.shields.io/badge/Workflow-Bundle--First-1F6FEB)
![Targets](https://img.shields.io/badge/Targets-Codex%20%7C%20Cursor%20%7C%20Antigravity%20%7C%20VS%20Code-2DA44E)

Bundle-first skills hub for Codex, Cursor, Antigravity, and VS Code / Copilot.

The goal is simple: maintain skills once in this repository, then sync only the right curated set to each target.

## What this repo contains

- `skills/`: the canonical skill folders plus registry and archive plan
- `bundles/`: curated groups of skills
- `profiles/`: default bundle selections for common use cases
- `scripts/skills/`: validation, resolve, sync, import, and archive-report tooling
- `docs/`: governance, onboarding, and consolidation notes

## Default recommendation

Do not install every skill from this repo.

For the default setup, use the curated profile `freelancer-fullstack`. It is intended for a freelance software engineer building websites, SaaS, automation tools, and AI features.

## Supported targets

| Target | Sync path | Scope |
|---|---|---|
| codex | `~/.codex/skills` | global |
| cursor | `~/.cursor/skills` | global |
| antigravity | `~/.gemini/antigravity/skills` | global |
| vscode-copilot | `<repo>/.github/skills` | project-local |
| antigravity workflows | `~/.gemini/antigravity/global_workflows` | optional |

## Quickstart

Run these commands in **PowerShell from the repo root**:

```powershell
./scripts/skills/validate.ps1
./scripts/skills/sync.ps1 -Profile freelancer-fullstack -SyncAntigravityWorkflows
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## What the scripts do

### `validate.ps1`

Checks whether the repo is internally consistent. It validates:

- bundle definitions
- bundle index references
- registry entries
- profile resolution
- archive plan consistency
- skill paths and `SKILL.md` files
- UTF-8 without BOM for checked skill files

Run:

```powershell
./scripts/skills/validate.ps1
```

### `sync.ps1`

Resolves a profile or bundle selection and copies only those skills to the target locations for Codex, Cursor, Antigravity, or VS Code / Copilot.

Run:

```powershell
./scripts/skills/sync.ps1 -Profile freelancer-fullstack
```

Dry run:

```powershell
./scripts/skills/sync.ps1 -Profile freelancer-fullstack -DryRun
```

## IDE agent onboarding

If you hand this repo path to an IDE agent, do not ask it to install everything.

Tell it to:

1. Read `AGENTS.md`
2. Validate the repo
3. Sync only `freelancer-fullstack`

Recommended command sequence:

```powershell
./scripts/skills/validate.ps1
./scripts/skills/sync.ps1 -Profile freelancer-fullstack
```

More details:

- [AGENTS.md](AGENTS.md)
- [docs/ide-agent-onboarding.md](docs/ide-agent-onboarding.md)

## Active bundles

The active bundle family is:

- `engineering-core`
- `project-bootstrap-core`
- `web-product`
- `data-ai-systems`
- `platform-devops`
- `security-engineering`
- `business-growth`

Legacy wrapper bundle IDs still exist for backward compatibility, but new work should use the active bundle family.

## Useful commands

All commands below are for **PowerShell in the repo root**:

```powershell
./scripts/skills/resolve-bundle.ps1 -BundleId web-product -Summary
./scripts/skills/resolve-bundle.ps1 -BundleId engineering-core -IncludeExtended
./scripts/skills/archive-report.ps1
./scripts/skills/archive-report.ps1 -OnlyArchiveCandidates
./scripts/skills/sync.ps1 -BundleId web-product,security-engineering -Targets codex,cursor,antigravity
```

## Governance and docs

- [docs/skills-governance.md](docs/skills-governance.md)
- [docs/skills-consolidation-archive-matrix.md](docs/skills-consolidation-archive-matrix.md)
- [bundles/README.md](bundles/README.md)

## License and third-party

See [LICENSE.md](LICENSE.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
