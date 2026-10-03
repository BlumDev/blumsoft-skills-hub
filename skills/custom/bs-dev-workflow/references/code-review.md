# Code review (requesting & receiving)

Core principle: review early, review often. When receiving feedback, verify before implementing, ask before assuming. Technical correctness over social comfort.

## Requesting a review

### When to request

Mandatory:
- After each task in subagent-driven development
- After completing a major feature
- Before merging to main

Optional but valuable:
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing a complex bug

### How to request

1. Get git SHAs:
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

2. Dispatch the code-reviewer subagent with:
- `{WHAT_WAS_IMPLEMENTED}` - what you just built
- `{PLAN_OR_REQUIREMENTS}` - what it should do
- `{BASE_SHA}` / `{HEAD_SHA}` - starting and ending commits
- `{DESCRIPTION}` - brief summary

3. Act on feedback:
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if the reviewer is wrong (with reasoning)

### Cadence by workflow

- Subagent-driven development: review after each task, before moving on.
- Executing plans: review after each batch (~3 tasks).
- Ad-hoc development: review before merge, or when stuck.

### Never

- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

If the reviewer is wrong: push back with technical reasoning, show code/tests that prove it works, request clarification.

## Receiving a review

Code review requires technical evaluation, not emotional performance.

### Response pattern

1. READ: complete feedback without reacting
2. UNDERSTAND: restate the requirement in your own words (or ask)
3. VERIFY: check against codebase reality
4. EVALUATE: technically sound for THIS codebase?
5. RESPOND: technical acknowledgment or reasoned pushback
6. IMPLEMENT: one item at a time, test each

### Forbidden responses

Never:
- "You're absolutely right!"
- "Great point!" / "Excellent feedback!" (performative)
- "Let me implement that now" (before verification)
- Any gratitude expression ("Thanks for catching that!"). If you catch yourself writing "Thanks", delete it and state the fix.

Instead: restate the requirement, ask clarifying questions, push back with reasoning if wrong, or just start working (actions > words).

### Unclear feedback

If any item is unclear, STOP. Do not implement anything yet. Ask for clarification on the unclear items first. Items may be related, and partial understanding leads to wrong implementation.

Example: feedback is "Fix 1-6", you understand 1,2,3,6 but not 4,5.
- Wrong: implement 1,2,3,6 now, ask about 4,5 later.
- Right: "I understand items 1,2,3,6. Need clarification on 4 and 5 before proceeding."

### Source-specific handling

From your human partner:
- Trusted. Implement after understanding.
- Still ask if scope is unclear. No performative agreement. Skip to action or technical acknowledgment.

From external reviewers (be skeptical, but check carefully). Before implementing, check:
1. Technically correct for THIS codebase?
2. Breaks existing functionality?
3. Reason for the current implementation?
4. Works on all platforms/versions?
5. Does the reviewer understand full context?

- If the suggestion seems wrong: push back with technical reasoning.
- If you can't easily verify: say so. "I can't verify this without [X]. Should I investigate/ask/proceed?"
- If it conflicts with your human partner's prior decisions: stop and discuss first.

### YAGNI check for "professional" features

If a reviewer suggests "implementing properly", grep the codebase for actual usage.
- If unused: "This endpoint isn't called. Remove it (YAGNI)?"
- If used: implement properly.

### Implementation order

For multi-item feedback:
1. Clarify anything unclear first.
2. Implement in order: blocking issues (breaks, security) → simple fixes (typos, imports) → complex fixes (refactoring, logic).
3. Test each fix individually.
4. Verify no regressions.

### When to push back

- Suggestion breaks existing functionality
- Reviewer lacks full context
- Violates YAGNI (unused feature)
- Technically incorrect for this stack
- Legacy/compatibility reasons exist
- Conflicts with your human partner's architectural decisions

How: use technical reasoning, not defensiveness. Ask specific questions, reference working tests/code, involve your human partner if the issue is architectural.

### Acknowledging correct feedback

- "Fixed. [Brief description of what changed]"
- "Good catch - [specific issue]. Fixed in [location]."
- Just fix it and show it in the code.

### Correcting your own pushback

If you pushed back and were wrong, state the correction factually and move on:
- "You were right - I checked [X] and it does [Y]. Implementing now."
- "Verified, you're correct. My initial understanding was wrong because [reason]. Fixing."

Avoid long apologies, defending why you pushed back, or over-explaining.

### Common mistakes

| Mistake | Fix |
|---------|-----|
| Performative agreement | State requirement or just act |
| Blind implementation | Verify against codebase first |
| Batch without testing | One at a time, test each |
| Assuming reviewer is right | Check if it breaks things |
| Avoiding pushback | Technical correctness > comfort |
| Partial implementation | Clarify all items first |
| Can't verify, proceed anyway | State limitation, ask for direction |

### GitHub thread replies

When replying to inline review comments on GitHub, reply in the comment thread (`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), not as a top-level PR comment.

## Bottom line

External feedback = suggestions to evaluate, not orders to follow. Verify. Question. Then implement. No performative agreement, technical rigor always.
