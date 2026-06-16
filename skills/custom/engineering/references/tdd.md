# Test-driven development

Write the test first. Watch it fail. Write minimal code to pass.

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing. Violating the letter of the rules is violating the spirit.

## When to use

Always: new features, bug fixes, refactoring, behavior changes.

Exceptions (ask first): throwaway prototypes, generated code, config files.

Thinking "skip TDD just this once"? That's rationalization.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Wrote code before the test? Delete it. Don't keep it as "reference", don't "adapt" it while writing tests, don't look at it. Delete means delete. Implement fresh from tests.

## Red-Green-Refactor

### RED - write failing test

One minimal test showing what should happen: one behavior, clear name, real code (no mocks unless unavoidable).

<Good>
```typescript
test('retries failed operations 3 times', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```
Clear name, tests real behavior, one thing.
</Good>

<Bad>
```typescript
test('retry works', async () => {
  const mock = jest.fn()
    .mockRejectedValueOnce(new Error())
    .mockRejectedValueOnce(new Error())
    .mockResolvedValueOnce('success');
  await retryOperation(mock);
  expect(mock).toHaveBeenCalledTimes(3);
});
```
Vague name, tests mock not code.
</Bad>

### Verify RED - watch it fail

**MANDATORY. Never skip.** Run the test. Confirm: it fails (not errors), the failure message is expected, it fails because the feature is missing (not a typo).

- Test passes? You're testing existing behavior. Fix the test.
- Test errors? Fix the error, re-run until it fails correctly.

### GREEN - minimal code

Simplest code to pass the test. Don't add features, refactor other code, or "improve" beyond the test.

<Good>
```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error('unreachable');
}
```
Just enough to pass.
</Good>

<Bad>
```typescript
async function retryOperation<T>(
  fn: () => Promise<T>,
  options?: { maxRetries?: number; backoff?: 'linear' | 'exponential'; onRetry?: (attempt: number) => void; }
): Promise<T> { /* YAGNI */ }
```
Over-engineered.
</Bad>

### Verify GREEN - watch it pass

**MANDATORY.** Run the test. Confirm: it passes, other tests still pass, output is pristine (no errors, warnings).

- Test fails? Fix the code, not the test.
- Other tests fail? Fix now.

### REFACTOR - clean up

After green only: remove duplication, improve names, extract helpers. Keep tests green. Don't add behavior.

### Repeat

Next failing test for the next feature.

## Good tests

| Quality | Good | Bad |
|---------|------|-----|
| **Minimal** | One thing. "and" in name? Split it. | `test('validates email and domain and whitespace')` |
| **Clear** | Name describes behavior | `test('test1')` |
| **Shows intent** | Demonstrates desired API | Obscures what code should do |

## Why order matters

Tests written after code pass immediately, which proves nothing: might test the wrong thing, might test implementation rather than behavior, might miss edge cases you forgot, and you never saw it catch a bug. Test-first forces you to see the test fail.

Tests-after answer "What does this do?" Tests-first answer "What should this do?" Tests-after are biased by your implementation: you test what you built, not what's required, and verify remembered edge cases rather than discovered ones.

## Common rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Already manually tested" | Ad-hoc != systematic. No record, can't re-run. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is technical debt. |
| "Keep as reference, write tests first" | You'll adapt it. That's testing after. Delete means delete. |
| "Need to explore first" | Fine. Throw away the exploration, start with TDD. |
| "Test hard = design unclear" | Listen to the test. Hard to test = hard to use. |
| "TDD will slow me down" | TDD is faster than debugging. Pragmatic = test-first. |
| "Existing code has no tests" | You're improving it. Add tests for existing code. |

## Red flags - STOP and start over

Code before test. Test after implementation. Test passes immediately. Can't explain why the test failed. Tests added "later". Rationalizing "just this once" / "I already manually tested it" / "it's about spirit not ritual" / "keep as reference" / "deleting is wasteful" / "TDD is dogmatic, I'm being pragmatic" / "this is different because...".

All of these mean: delete the code, start over with TDD.

## Verification checklist

Before marking work complete:

- [ ] Every new function/method has a test
- [ ] Watched each test fail before implementing
- [ ] Each test failed for the expected reason (feature missing, not typo)
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass
- [ ] Output pristine (no errors, warnings)
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Edge cases and errors covered

Can't check all boxes? You skipped TDD. Start over.

## When stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write the wished-for API and the assertion first. Ask. |
| Test too complicated | Design too complicated. Simplify the interface. |
| Must mock everything | Code too coupled. Use dependency injection. |
| Test setup huge | Extract helpers. Still complex? Simplify the design. |

## Debugging

Bug found? Write a failing test reproducing it, then follow the TDD cycle. The test proves the fix and prevents regression. Never fix bugs without a test.

## Final rule

```
Production code -> test exists and failed first
Otherwise       -> not TDD
```

No exceptions without permission.
