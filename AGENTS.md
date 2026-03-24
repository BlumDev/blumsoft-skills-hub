# Agent Instructions

## Skill Installation

This repository is a curated skills hub. Do not install every skill from the repo by default.

When the task is to install skills from this repo, use **PowerShell in the repo root** and install only the curated default profile:

```powershell
./scripts/skills/validate.ps1
./scripts/skills/sync.ps1 -Profile freelancer-fullstack
```

## Default behavior

- Prefer profile `freelancer-fullstack`.
- Do not sync the full registry.
- Do not add legacy wrapper bundles unless explicitly requested.
- Do not add archived skills unless explicitly requested.
- Add `business-growth` only when the task explicitly includes pricing, launch, SEO, analytics, CRO, or experimentation.

## If unsure

- Read `README.md`
- Read `docs/ide-agent-onboarding.md`
- Inspect `profiles/freelancer-fullstack.json`
