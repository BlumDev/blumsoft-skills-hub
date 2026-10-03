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
| claude | `~/.claude/skills` | global |
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

### `validate-skills.ps1`

Complements `validate.ps1`: instead of repo wiring, it checks the **content of
every `SKILL.md`** on disk (custom, vendor, and archive). Per skill it validates:

- YAML frontmatter is present and parseable
- required fields `name` and `description` are present and non-empty
- files referenced from the skill (e.g. `references/*.md`, in-skill markdown
  links) actually exist
- `name` matches the skill folder (warning)
- encoding health: broken UTF-8, mojibake, and `ae`/`oe`/`ue` used instead of
  umlauts (reported only, never changed)

Errors exit with code `1`; warnings are listed but pass. Add `-Strict` to make
warnings fail too. It only reports, it never rewrites a skill.

Run:

```powershell
./scripts/skills/validate-skills.ps1
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

### `migrate-renames.ps1`

One-time cleanup after the switch to the `bs-` prefix. `sync.ps1` only installs and
replaces, it never removes, so installed skills under their old names would sit next to
the new ones and trigger twice. Per target the script backs up each old folder to
`~/.skills-hub-backup/`, installs the skill under its new name from the repo, carries over
files that only existed in the old folder (runtime data such as `out/`), and removes the
six legacy skills. Folders whose `SKILL.md` carries a different name are left alone.

Run (dry run first, then sync as usual):

```powershell
./scripts/skills/migrate-renames.ps1 -DryRun
./scripts/skills/migrate-renames.ps1
./scripts/skills/sync.ps1 -Profile freelancer-fullstack
```

Add `-WorkspaceRoot <repo>` for project-local `.github/skills` folders synced into another repo.

## Own skills

Own skills are named `bs-<area>-<purpose>`. Vendor skills keep their upstream names, so
the prefix shows at a glance what is maintained here. Names ending in `-build` explain how
to build something, names ending in `-audit` or `-review` produce a report.

| Area | Skill | Purpose |
|---|---|---|
| dev | `bs-dev-workflow` | plan, implement, debug, verify, land a branch |
| dev | `bs-dev-kickoff` | start a project or take over a repo |
| dev | `bs-dev-commits` | cut changes into clean commits |
| dev | `bs-dev-audit` | audit existing code by dimension, report or `--fix` |
| dev | `bs-dev-repo-review` | keep/refactor/rewrite decision per module |
| dev | `bs-dev-security` | write secure code, design auth and APIs |
| web | `bs-web-build` | pages, components, UI/UX, browser checks |
| web | `bs-web-audit` | measured website quality report |
| ai | `bs-ai-build` | prompts, MCP, RAG, agents |
| ai | `bs-ai-harden` | harden LLM/agent code against attacks |
| ops | `bs-ops-infra` | backend, deploy, containers, observability, IaC |
| ops | `bs-ops-deploy-blumsoft` | release flow of the BlumSoft platform |
| text | `bs-text-natural` | visible text that does not read as generated |
| text | `bs-text-audio` | listening scripts for text-to-speech |
| media | `bs-media-image` | local image assets via ComfyUI |
| business | `bs-business-growth` | pricing, launch, analytics, experiments |

The mapping from the old names is recorded in [docs/decisions.md](docs/decisions.md)
(2026-10-03) and in `scripts/skills/migrate-renames.ps1`.

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
