---
name: project-bootstrap
description: Use to kick off a new project or take over an existing repo by creating the minimum docs, decisions, and execution plan for fast delivery.
---

# Project Bootstrap

## Goal
Turn an idea or repo into a decision-complete plan plus the minimum set of project artifacts so implementation can start immediately.

## Inputs To Ask For (if missing)
- Product goal + success metric
- Target users + top 3 use cases
- Tech constraints (stack, hosting, budget, timeline)
- Existing repo context (if any): entry points, current issues, deployment

## Deliverables (create/update as needed)
1. `PROJECT_CONTEXT.md`
2. `FEATURES/README.md` and first feature spec(s) in `FEATURES/`
3. `DECISIONS.md` (short ADR-style list)
4. An implementation plan with milestones + verification gates

## Process
1. Clarify scope: what is in/out (no gold-plating).
2. Choose the minimal viable architecture that can ship.
3. Define the first vertical slice (end-to-end).
4. Define verification: tests, checks, and a demo path.
5. Produce the files and a next-steps task list.

## Output Format
- **Decisions**: bullet list (include tradeoffs)
- **Files To Add/Update**: paths + 1 sentence each
- **Milestones**: 3-6 steps
- **Verification**: commands and smoke tests
