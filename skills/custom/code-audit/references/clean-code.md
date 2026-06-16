# Dimension: clean-code

Readability and structure. Two rules carry most of the weight; lead with them.

## 1. Speaking names (intention-revealing)

A name should tell the reader what the thing is and why it exists, so they never
decode it or read the body to understand a call site. A good name absorbs the
comment that would otherwise explain it.

Look for:
- Cryptic/abbreviated names: `d`, `tmp`, `mgr`, `x2`, `data2`, `do_it`.
- Names that hide intent: `process()`, `handle()`, `info`, `flag`.
- Misleading names: a `get_*` that mutates; a `list` that is a set; a `count`
  holding a sum.
- Inconsistent vocabulary for one concept (`user`/`account`/`member` for the same
  thing), or one word for several concepts.
- Type/Hungarian encoding (`strName`, `lst_items`) where the type is obvious.

Why it matters: code is read far more than written; the decode cost of a bad name
is paid on every read, forever.

Behavior-preserving fix: rename the symbol consistently across its whole scope,
updating every reference. The safest refactoring there is — **except** when the
name is reachable by reflection, string lookups, serialized field names, or is a
public API name. Those are not pure renames: flag them, do not silently change.

## 2. A function does one thing (single responsibility)

One thing, at one level of abstraction, with a name that says what that thing is.
Then it is testable, reusable, and understandable without the rest of the system
in your head.

Look for:
- A name containing "and", or that needs "and" to describe honestly.
- Mixed abstraction levels: high-level orchestration interleaved with low-level
  fiddling in one body.
- A boolean/flag parameter that selects between two behaviors — usually two
  functions wearing a trench coat.
- Long bodies, deep nesting, many parameters, or a `# now do X` comment marking a
  seam between responsibilities.

Why it matters: a unit that does one thing changes for one reason. One that does
three changes for three, and breaks in ways that are hard to localize.

Behavior-preserving fix: extract each responsibility into a well-named helper;
split a flag-parameter function into two named functions; flatten nesting with
guard clauses. Keep the public signature and observable behavior identical.

## Supporting rules

Apply when clearly worth it; do not manufacture findings.

- **Clear control flow.** Deep nesting and tangled conditionals hide the path. Use
  guard clauses, early returns, and extract a complex condition into a named
  boolean (`if is_eligible_for_refund(order):`).
- **No magic values.** Unexplained literals (`if status == 7`, `* 86400`) become
  named constants that document themselves.
- **Dead code.** Unused vars/functions/branches/params mislead. Report them; remove
  in fix mode only when provably unreferenced (mind reflection/dynamic dispatch).
- **Comments.** Flag comments that restate the code or have gone stale; prefer
  self-explaining code. Never delete a comment that explains *why* (intent, a
  workaround, a non-obvious constraint) — that kind is worth keeping.
