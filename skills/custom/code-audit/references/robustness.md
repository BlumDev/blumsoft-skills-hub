# Dimension: robustness

Does the code hold up when reality misbehaves — bad input, a failing dependency,
an empty collection, a race? Like security, **hardening changes behavior on the
bad path on purpose**, so it is not a pure refactoring: report by default, apply
with approval, keep the happy path identical.

Look for:

- **Swallowed errors.** A bare `except:`/`catch (e) {}` that hides failure; an
  error logged and then ignored so execution continues in a broken state; a return
  value that signals failure but is never checked. Fix: handle meaningfully, or let
  it propagate — do not silently continue.
- **Over-broad catches.** Catching `Exception`/`Throwable` where only one specific
  failure is expected, masking unrelated bugs (including the ones you would want to
  crash on). Fix: catch the narrowest type that you can actually handle.
- **Unvalidated input at the boundary.** Trusting external data's shape, type,
  range, or presence (`config["key"]` that may be absent, an index assumed in
  range, a parse assumed to succeed). Fix: validate at the edge, fail with a clear
  message, keep the core assuming clean data.
- **Missing edge cases.** Empty collection, single element, zero/negative numbers,
  null/None, max values, duplicate keys, off-by-one at boundaries, empty string,
  Unicode. Walk the obvious ones for the logic at hand.
- **Leaked resources.** A file/socket/lock/connection opened without guaranteed
  release on the error path. Fix: `with`/`using`/`defer`/try-finally so cleanup
  always runs.
- **Unsafe external assumptions.** Assuming a network call succeeds, returns the
  expected schema, or returns quickly — no timeout, no retry/backoff where it
  matters, no handling of a partial/malformed response. Fix: timeouts, bounded
  retries for idempotent calls, validate the response.
- **Concurrency hazards.** Shared mutable state without synchronization; a
  check-then-act race (TOCTOU); assuming ordering across threads/tasks; a deadlock-
  prone lock order. Fix: confine state, use the right primitive, make the operation
  atomic. These are subtle — flag clearly and prefer reporting over auto-fixing.
- **Silent precision/encoding traps.** Float for money; naive timezone handling;
  assuming an encoding on byte input. Fix: appropriate type/explicit handling.

Why it matters: robustness bugs hide until the worst moment (the failing
dependency, the malformed input, the production race) and then fail in ways that
are hard to diagnose. Closing them is cheap now and expensive later.

For each finding: the trigger condition (what input/timing/failure exposes it),
the consequence (crash, corruption, hang, silent wrong result), and the fix. A fix
that adds a check changes behavior for the bad case by design — call that out, and
confirm the existing tests for the good path still pass unchanged.
