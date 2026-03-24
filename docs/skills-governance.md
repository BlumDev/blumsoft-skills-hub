# Skills Governance

1. `skills/custom/*` for project-specific workflows.
2. `skills/vendor/guanyang/*` is canonical for overlapping names.
3. `skills/vendor/sickn33/*` is gap-fill only.

## Rules
- Bundles are starter sets, not automatic orchestration.
- Start with core skills; add extended skills only on demand.
- Never sync the full registry by default; prefer a curated profile.
- Every vendored skill must have `UPSTREAM.md`.
- Run `scripts/skills/validate.ps1` after bundle/registry changes.

## Active default stack

- Prefer `engineering-core`, `web-product`, `data-ai-systems`, `platform-devops`, `security-engineering`, and `project-bootstrap-core`.
- Prefer profile `freelancer-fullstack` for a freelance software engineer building websites, SaaS, automation tools, and AI features.
- Add `business-growth` only when the project scope includes pricing, launch, SEO, analytics, or experimentation.

## Legacy wrappers

- `essentials`, `web-wizard`, `security-engineer`, `startup-growth`, `data-ai`, `devops-cloud`, `workflow-ops`, and `project-kickoff` remain available as compatibility wrappers.
- Do not expand legacy wrappers with new content.
- Put new bundle design work only into the active bundle family.

## Archive policy

- Do not delete or move old skill folders until their content has been absorbed into active core skills or references.
- Treat the mapping in [skills-consolidation-archive-matrix.md](/D:/Repos/blumsoft-skills-hub/docs/skills-consolidation-archive-matrix.md) as the source of truth for archive readiness.
- Archived or archive-candidate skills should stay out of default profiles and only appear in active bundles when there is a strong scope reason.
- Physical archive location is `skills/archive/<owner>/<skill-name>`, with `skills/registry.yaml` as the canonical source of truth for the moved path.
