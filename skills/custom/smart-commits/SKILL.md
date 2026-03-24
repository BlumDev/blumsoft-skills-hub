---
name: smart-commits
description: "Summarize current git changes into sensible commits with short commit messages and create the commits safely. Use when the user asks to group changes, suggest commit boundaries/messages, or to commit changes in a repo."
---

# Smart Commits

## Goal

Turn the current working tree into 1+ logical commits with short, meaningful messages while following repo safety rules.

## Workflow

1. Inspect git state first:
   - `git status`
   - `git diff`
   - `git diff --staged`
   - `git log -5 --oneline`
2. Propose a commit split before staging:
   - short title
   - one-sentence reason
   - files included
   - anything to exclude
3. Stage only the files for the current commit.
4. Re-check `git diff --staged` before committing.
5. Commit with a short message that matches the repo style.
6. Verify with `git status` and fast relevant checks when appropriate.

## Safety

- Never commit secrets or local-only credentials.
- Never push unless the user explicitly asks.
- Never force-push.
- Avoid amend unless the user explicitly asks and it is clearly safe.
- If hooks change files, create a follow-up commit unless amend was explicitly requested.

## Heuristics

- Separate docs from code.
- Separate frontend, backend, infra, and refactors when they are logically distinct.
- Prefer 2-4 sensible commits over one giant commit when a change spans multiple areas.
- Keep each commit buildable.
