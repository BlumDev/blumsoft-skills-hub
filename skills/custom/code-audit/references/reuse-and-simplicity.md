# Dimensions: reuse & simplicity

Two related dimensions. `reuse` is about not repeating what exists; `simplicity`
is about not building more than the problem needs. Both reduce the code a future
reader must hold in their head.

## reuse / DRY

Look for:
- **True duplication:** the same non-trivial logic in several places. It drifts out
  of sync — a fix applied to one copy and not the others is a classic bug source.
- **Reinventing what exists:** a hand-rolled helper that duplicates a stdlib
  function, an existing utility in this repo, or a dependency already on the
  manifest. Check the codebase before suggesting a new abstraction.
- **Copy-paste-modify:** near-identical blocks differing only in a value or type —
  candidates for one parameterized unit.

Why it matters: one source of truth means one place to fix and one place to read.

Behavior-preserving fix: extract one well-named unit and call it from each site.

**Counter-rule — do not over-couple.** Coincidental similarity is not duplication.
Two blocks that look alike today but change for different reasons should stay
separate; merging them creates a false abstraction that fights every future
change. Prefer a little duplication over the wrong abstraction. Only dedupe logic
that is genuinely *the same rule*.

## simplicity / de-over-engineering

Look for:
- **Speculative generality:** abstraction, config, hooks, or plugin points with a
  single caller and no second use in sight. YAGNI — built for a future that has not
  arrived.
- **Indirection without payoff:** a factory that makes one thing, a wrapper that
  forwards unchanged, a strategy interface with one strategy, an interface/protocol
  with one implementation.
- **A simpler equivalent exists:** a manual loop that a comprehension/`map`/builtin
  expresses; a hand-rolled state machine for a three-line conditional; a custom
  class where a tuple/dict/dataclass suffices.
- **Wrong altitude:** a function reaching across three layers to do its job; logic
  living far from the data it operates on.
- **Defensive cruft for impossible states:** null checks on values that cannot be
  null here, catch-all handlers that swallow everything "just in case".

Why it matters: every abstraction is a thing to learn before you can change the
code. Unused flexibility is pure cost — you pay to carry it and never collect.

Behavior-preserving fix: inline the single-use abstraction; replace the hand-rolled
construct with the language/stdlib equivalent; collapse pass-through layers. Keep
observable behavior identical.

Test for both dimensions: *would a senior engineer call this overcomplicated or
needlessly repeated?* If 200 lines could be 50 with no loss, that is the finding.
