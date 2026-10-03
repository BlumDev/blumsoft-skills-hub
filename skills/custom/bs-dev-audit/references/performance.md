# Dimension: performance / efficiency

Find work the code does that it does not need to do. **Every fix here must return
identical results, you change speed, never output.** Measure or reason before
claiming a win; do not trade readability for a micro-optimization that does not
matter on this code path.

Look for:

- **Work inside loops that belongs outside.** Recompiling a regex, reopening a
  connection, re-reading a file, or recomputing an invariant on every iteration.
  Hoist it out.
- **N+1 and I/O in loops.** A query/HTTP/disk call per element where one batched
  call would do. The classic killer, flag it High. Fix: batch, prefetch, or join.
- **Accidental quadratic behavior.** A membership test (`x in list`) inside a loop
  over the same data → use a `set`/`dict`. Repeated `list.insert(0, …)` or string
  `+=` in a loop → use a deque or join. Nested loops over the same collection where
  a single pass with a lookup table works.
- **Needless allocation/copying.** Building a full list to immediately consume it
  once (use a generator/iterator), copying a structure to read it, materializing
  data that streams.
- **Repeated identical computation.** The same pure result computed many times →
  compute once and reuse, or memoize if the call pattern warrants it.
- **Eager work that is often unused.** Expensive setup done unconditionally when
  many call paths never need it → make it lazy.

Why it matters: the wins that count are algorithmic (O(n²) → O(n)) and I/O-shaped
(N calls → 1). Those are worth real effort. CPU micro-tuning rarely is, say so
rather than cluttering the report with it.

Behavior-preserving fix: swap the data structure or algorithm for one with the
same results and lower cost; batch I/O; hoist invariants; make eager work lazy.
After the change, the existing tests must still pass unchanged, if a "perf fix"
needs a test updated, it changed behavior and is not a perf fix.

Caveats to respect:
- Do not introduce a cache without an invalidation story, a stale cache is a
  correctness bug masquerading as a speedup.
- Laziness can move *when* a side effect or exception fires; if the code relies on
  eager evaluation order, flag rather than silently change it.
- Concurrency changes (parallelizing a loop) are **not** behavior-preserving by
  default, they belong in the robustness conversation, not a quiet perf fix.
