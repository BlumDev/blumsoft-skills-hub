---
name: engineering
description: >-
  The disciplined software-delivery workflow: how to plan, implement, debug,
  verify, review, and land changes well. Loads focused references on demand,
  ideation & plan-writing, systematic debugging, test-driven development,
  verification-before-completion, code-review etiquette (requesting & receiving),
  and git worktrees & finishing a branch. Use whenever the user is working
  through delivery work and wants a disciplined approach rather than ad-hoc
  steps, e.g. "how should I approach this", "write a plan for X before I code",
  "this bug makes no sense, help me debug it properly", "how do I do TDD here",
  "is this actually done", "get this ready for review", "respond to this review",
  "set up a worktree", "land/finish this branch". For auditing existing code for
  quality, security, or robustness use the code-audit skill; for commit messages
  and commit hygiene use the smart-commits skill.
---

# Engineering Workflow

The disciplined path for delivery work: ideate, plan, implement, debug, verify,
review, land. Each phase has a focused reference. Load only the one(s) the task
needs rather than reading all of them.

## References

| When | Read |
|---|---|
| Scoping an idea, writing a plan before coding | `references/planning.md` |
| A bug whose cause isn't obvious | `references/debugging.md` |
| Implementing with tests first | `references/tdd.md` |
| About to claim something is done | `references/verification.md` |
| Preparing a change for review, or responding to one | `references/code-review.md` |
| Isolating work in a worktree, or landing a branch | `references/git-workflow.md` |

## Typical flow

ideate / plan → implement (TDD where it fits) → debug when stuck → verify before
claiming done → request review → finish the branch. You rarely need every phase;
pick up at the relevant one.

## Boundaries

- Auditing existing code for quality, security, or robustness → **code-audit**
  skill (don't duplicate it here).
- Commit messages and commit hygiene → **smart-commits** skill.
- This skill is the methodology layer; those two are sharp single-purpose tools
  that sit alongside it.
