# IDE Agent Onboarding

## Default rule

Do not install every skill from this repo.

If an agent receives only the repo path and no further scope, install the curated default profile:

```powershell
# PowerShell, repo root
./scripts/skills/sync.ps1 -Profile freelancer-fullstack
```

## Why

- The repo contains active bundles, legacy wrappers, and archived reference skills.
- Installing everything increases trigger overlap and makes agents pull unnecessary skills.
- `freelancer-fullstack` is the default for a freelance software engineer building websites, SaaS, automation tools, and AI features.

## Default install target

Use only these bundles through the `freelancer-fullstack` profile:

- `engineering-core`
- `project-bootstrap-core`
- `web-product`
- `data-ai-systems`
- `platform-devops`
- `security-engineering`

## Add only when explicitly needed

- `business-growth` for pricing, launch, SEO, analytics, CRO, or experimentation
- legacy wrapper bundles only for backward compatibility
- archived skills never by default

## Safe prompt for IDE agents

Use a prompt like:

> This repo is a curated skills hub. Do not install all skills. Install only the `freelancer-fullstack` profile from the repo root, inspect the active bundles, and add anything else only if the task explicitly requires it.

## Useful commands

```powershell
# PowerShell, repo root
./scripts/skills/validate.ps1
./scripts/skills/sync.ps1 -Profile freelancer-fullstack -DryRun
./scripts/skills/resolve-bundle.ps1 -BundleId web-product -Summary
./scripts/skills/archive-report.ps1 -OnlyArchiveCandidates
```
