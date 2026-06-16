# Verification before completion

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always. Violating the letter of this rule violates its spirit.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

Before claiming any status or expressing satisfaction:

1. **IDENTIFY** the command that proves the claim.
2. **RUN** it fresh and in full.
3. **READ** the full output, check the exit code, count failures.
4. **VERIFY** the output confirms the claim. If not, state the actual status with evidence.
5. **ONLY THEN** make the claim, with evidence.

Skipping any step is lying, not verifying.

## Common Failures

| Claim | Requires | Not sufficient |
|-------|----------|----------------|
| Tests pass | Test output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build: exit 0 | Linter passing, logs look good |
| Bug fixed | Original symptom retested: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to".
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!").
- About to commit/push/PR without verification.
- Trusting agent success reports or partial verification.
- Thinking "just this once" or wanting the work over.
- Any wording implying success without having run verification.

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence is not evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter is not a compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion is not an excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words" | Spirit over letter |

## Key Patterns

**Tests:** Run the test command, see `34/34 pass`, then claim "All tests pass". Not "Should pass now".

**Regression tests (TDD red-green):** Write, run (pass), revert fix, run (MUST FAIL), restore, run (pass). Not "I've written a regression test" without the red-green cycle.

**Build:** Run build, see exit 0, then claim "Build passes". A passing linter does not check compilation.

**Requirements:** Re-read the plan, build a checklist, verify each item, report gaps or completion. Not "Tests pass, phase complete".

**Agent delegation:** Agent reports success, then check the VCS diff and verify the changes before reporting actual state.

## When To Apply

Always before any success/completion claim, any expression of satisfaction, any positive statement about work state, committing, PR creation, task completion, moving to the next task, or delegating to agents.

The rule applies to exact phrases, paraphrases, synonyms, and any communication implying completion or correctness.

## The Bottom Line

Run the command. Read the output. THEN claim the result. Non-negotiable.
