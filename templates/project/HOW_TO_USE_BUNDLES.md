# How To Use Bundles

## Default Rule

Do not install every skill from the hub. Start with the curated default profile or bundle core skills only. Add extended skills only when complexity demands it.

## Default Install

Use `freelancer-fullstack` unless the project scope clearly requires something else.

```powershell
# PowerShell, repo root
./scripts/skills/sync.ps1 -Profile freelancer-fullstack
```

## Quick Picks

- `project-bootstrap-core`: new project or taking over an unfamiliar repo
- `web-product`: UI, UX, frontend quality, browser testing
- `security-engineering`: audits and hardening before release
- `data-ai-systems`: prompt, MCP, RAG, agent systems
- `platform-devops`: backend, deployment, observability
- `business-growth`: only for pricing, launch, SEO, analytics, CRO

## Best Practice Prompts

- \"Use `freelancer-fullstack` or `<bundle-id>` core only. List assumptions, then propose a plan, then execute.\"
- \"Do not install all skills from the repo. Start with the curated default profile and add more only when the task explicitly needs them.\"

