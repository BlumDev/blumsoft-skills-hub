# Skills Governance

1. `skills/custom/*` for project-specific workflows.
2. `skills/vendor/guanyang/*` is canonical for overlapping names.
3. `skills/vendor/sickn33/*` is gap-fill only.

## Rules
- Bundles are starter sets, not automatic orchestration.
- Start with core skills; add extended skills only on demand.
- Every vendored skill must have `UPSTREAM.md`.
- Run `scripts/skills/validate.ps1` after bundle/registry changes.
