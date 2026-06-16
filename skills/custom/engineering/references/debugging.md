# Systematic debugging

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to use

Use for ANY technical issue: test failures, production bugs, unexpected behavior, performance problems, build failures, integration issues.

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes, or the previous fix didn't work
- You don't fully understand the issue

Don't skip because the issue "seems simple" (simple bugs have root causes too) or because someone wants it fixed NOW (systematic is faster than thrashing).

## The four phases

Complete each phase before proceeding to the next.

### Phase 1: Root cause investigation

BEFORE attempting ANY fix:

1. **Read error messages carefully.** Don't skip errors or warnings; they often contain the exact solution. Read stack traces completely. Note line numbers, file paths, error codes.
2. **Reproduce consistently.** Can you trigger it reliably? What are the exact steps? If not reproducible, gather more data, don't guess.
3. **Check recent changes.** Git diff, recent commits, new dependencies, config changes, environmental differences.
4. **Gather evidence in multi-component systems.** When a system has multiple components (CI → build → signing, API → service → database), add diagnostic instrumentation BEFORE proposing fixes. For each component boundary: log data entering and exiting, verify environment/config propagation, check state at each layer. Run once to reveal WHERE it breaks, then investigate that specific component.

   Example, instrumenting each layer to find where signing breaks:
   ```bash
   # Layer 1: Workflow, are secrets available?
   echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"
   # Layer 2: Build script, did the env var propagate?
   env | grep IDENTITY || echo "IDENTITY not in environment"
   # Layer 3: Signing script, keychain state
   security find-identity -v
   # Layer 4: Actual signing
   codesign --sign "$IDENTITY" --verbose=4 "$APP"
   ```
   This reveals which boundary fails (e.g. secrets → workflow OK, workflow → build broken).
5. **Trace data flow.** When the error is deep in the call stack: where does the bad value originate? What called this with the bad value? Keep tracing up to the source. Fix at the source, not the symptom. See `root-cause-tracing.md` for the full backward-tracing technique.

### Phase 2: Pattern analysis

1. **Find working examples.** Locate similar working code in the same codebase. What works that resembles what's broken?
2. **Compare against references.** If implementing a pattern, read the reference implementation COMPLETELY, every line, before applying it.
3. **Identify differences.** List every difference between working and broken, however small. Don't assume "that can't matter."
4. **Understand dependencies.** What other components, settings, config, environment does this need? What assumptions does it make?

### Phase 3: Hypothesis and testing

1. **Form a single hypothesis.** State it clearly: "I think X is the root cause because Y." Be specific, not vague.
2. **Test minimally.** Make the SMALLEST change to test the hypothesis. One variable at a time. Don't fix multiple things at once.
3. **Verify before continuing.** Worked? Go to Phase 4. Didn't work? Form a NEW hypothesis; don't stack more fixes on top.
4. **When you don't know,** say "I don't understand X." Don't pretend. Ask for help or research more.

### Phase 4: Implementation

Fix the root cause, not the symptom.

1. **Create a failing test case.** Simplest possible reproduction, automated if possible (a one-off script if there's no framework). MUST have it before fixing.
2. **Implement a single fix.** Address the identified root cause. ONE change. No "while I'm here" improvements, no bundled refactoring.
3. **Verify the fix.** Test passes now? No other tests broken? Issue actually resolved?
4. **If the fix doesn't work, STOP.** Count your attempts. If < 3, return to Phase 1 and re-analyze with the new information. If ≥ 3, question the architecture (next step). Don't attempt fix #4 without architectural discussion.
5. **If 3+ fixes failed, question the architecture.** Warning signs: each fix reveals new shared state/coupling elsewhere, fixes require "massive refactoring," each fix creates new symptoms. Ask: is this pattern fundamentally sound, or are we continuing through sheer inertia? This is not a failed hypothesis, it's a wrong architecture. Discuss with your human partner before more fixes.

## Red flags - STOP and follow the process

If you catch yourself thinking any of these, return to Phase 1:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)
- Each fix reveals a new problem in a different place

## Signals from your human partner that you're doing it wrong

- "Is that not happening?", you assumed without verifying
- "Will it show us...?", you should have added evidence gathering
- "Stop guessing", you're proposing fixes without understanding
- "Ultrathink this", question fundamentals, not just symptoms
- "We're stuck?" (frustrated), your approach isn't working

When you see these: STOP, return to Phase 1.

## Common rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | The first fix sets the pattern. Do it right from the start. |
| "I'll write the test after confirming the fix" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern. |

## When the process reveals "no root cause"

If investigation shows the issue is truly environmental, timing-dependent, or external: you've completed the process, so document what you investigated, implement appropriate handling (retry, timeout, error message), and add monitoring/logging. But 95% of "no root cause" cases are incomplete investigation.

## Supporting techniques

- `root-cause-tracing.md`, trace bugs backward through the call stack to the original trigger
- `defense-in-depth.md`, add validation at multiple layers after finding root cause
- `condition-based-waiting.md`, replace arbitrary timeouts with condition polling
- `find-polluter.sh`, bisect a flaky / order-dependent test suite to find the test that pollutes shared state (adapt the test command for the project; the script assumes `npm test`)
