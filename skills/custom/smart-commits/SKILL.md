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
   - short title, preferably 72 characters or fewer
   - one-sentence reason
   - files included
   - anything to exclude
3. If the user only asked for a summary or proposal, stop before staging.
4. Stage only the files for the current commit with non-interactive commands. Do not stage unrelated changes.
5. Re-check `git diff --staged` and confirm it matches the proposed commit.
6. Commit with a short message that matches the repo style. Use a body only when it adds useful context, and avoid shell-specific message syntax.
7. Verify with `git status` and fast relevant checks when appropriate. If automated checks are unavailable, state what was verified manually.

## Safety

- Never commit secrets or local-only credentials. Inspect suspicious files such as `.env`, private keys, tokens, and credential exports; stop and warn before staging them.
- Never push unless the user explicitly asks.
- Never force-push.
- Amend only when the user explicitly asks and the target is an unpushed commit created during the current task.
- If hooks change files, create a follow-up commit unless amend was explicitly requested.

## Heuristics

- Separate docs from code.
- Separate frontend, backend, infra, and refactors when they are logically distinct.
- Prefer 2-4 sensible commits over one giant commit when a change spans multiple areas.
- Keep each commit buildable.
