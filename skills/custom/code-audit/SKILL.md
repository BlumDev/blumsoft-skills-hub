---
name: code-audit
description: >-
  Audit existing code (a whole repo, a directory, a single file, or a pointed-at
  function/class) along one or more quality dimensions, then either report the
  findings or safely fix them. Dimensions: clean-code (speaking names, single
  responsibility), reuse/DRY, simplicity (de-over-engineering), performance/
  efficiency, security, and robustness (error handling, edge cases, validation,
  concurrency). Two modes: a prioritized findings report (default), or a
  behavior-preserving auto-fix (--fix) that applies safe refactorings and then
  runs the project's tests/build to prove valid-input behavior is unchanged. Use
  this whenever the user wants to review, audit, check, harden, clean up, tidy,
  refactor, simplify, speed up, or improve the quality / readability /
  maintainability / safety / robustness of code that already exists, e.g.
  "review this module", "is this function doing too much", "find duplication in
  src/", "make this faster without changing results", "audit this file for
  security", "harden the error handling", "clean up cli.py safely". For reviewing
  only the current uncommitted diff before a merge, prefer /code-review instead.
  For hardening AI/LLM/agent code against prompt injection and tool abuse, use
  the ai-hardening skill instead (this skill points you there when it sees such
  code).
---

# Code Audit

Audit code that already exists along the dimension(s) the user asks for, then
either **report** the findings or **fix** them. Fixes never change what the
software does for valid inputs; see [the behavior contract](#fix-mode-the-behavior-contract).

This is not a diff reviewer. `/code-review` and `/simplify` operate on the
current change set (uncommitted diff). This skill points at any existing code
the user names, touched or not.

## Dimensions

Each dimension has a focused rule set in a reference file. **Load only the
reference(s) for the dimension(s) in play** — do not read all of them every time.

| Dimension | Focus | Reference |
|---|---|---|
| `clean-code` | speaking names, one-thing functions (SRP), control flow, magic values, dead code, comments | `references/clean-code.md` |
| `reuse` | duplication, DRY, missed vs over-abstraction | `references/reuse-and-simplicity.md` |
| `simplicity` | over-engineering, YAGNI, simpler equivalents, right altitude | `references/reuse-and-simplicity.md` |
| `performance` | algorithmic cost, work-in-loops (N+1/I/O), needless allocation/copying, caching | `references/performance.md` |
| `security` | injection, authz/authn, secrets, unsafe deserialization, path/SSRF, crypto, trust boundaries | `references/security.md` |
| `robustness` | error/exception handling, edge cases, resource cleanup, input validation, concurrency | `references/robustness.md` |

If the code is AI/LLM/agent code (calls an LLM API, builds prompts, defines
tools/functions for a model, runs an MCP server, does RAG), this skill's security
dimension does not cover the LLM-specific attack surface. Say so and point the
user at the **ai-hardening** skill.

## Choosing dimensions

Parse the invocation as `code-audit [target] [dimensions...] [--fix]`.

- **Only audit the dimension(s) the user asked for.** If they say "check naming",
  do clean-code, not a full sweep. If they name several ("security and
  robustness"), do those.
- **If no dimension is named and none is clearly implied, ask which** — offer the
  list above plus "all". Do not silently run everything; a six-dimension report on
  an unscoped request is noise the user did not ask for.
- "audit everything" / "full review" / "all dimensions" → run all six and
  prioritize hard across them.

`target` is an optional path or a region description ("the `parse_report`
function", "lines 200-340 of dashboard.py"). If absent, ask or default to the
unit in focus, never silently audit a giant repo. If the target is large, propose
a starting scope (worst offenders, or one module) rather than dumping a
thousand-line report.

## Two modes

- **Report (default).** Find issues, explain why each matters, propose a concrete
  fix. Change nothing.
- **Fix (`--fix`).** Apply fixes under the behavior contract below, then verify.

## Step 0 — Scope and detect the stack

1. Resolve `target` to concrete files. Exclude what you must never touch:
   dependencies (`node_modules`, `.venv`, `vendor`), generated code, build output,
   migrations, lockfiles, minified assets. When unsure if a file is generated,
   check for a header marker or ask.
2. Identify the language(s) and the project's conventions so suggestions match
   the surrounding code. Read a couple of neighboring files first; do not impose a
   foreign style.

## Step 1 — Establish a green baseline (required before any fix)

You cannot prove you preserved behavior without knowing the starting state.
Before changing anything in `--fix` mode:

1. Find the project's verification commands (`package.json` scripts, `Makefile`,
   `pyproject.toml`/`tox.ini`, `*.csproj`, CI config): tests, type check, build,
   linter.
2. Run them and record the result. **If you cannot identify the command, ask the
   user which command proves the code works. Do not guess, do not skip.**
3. If the baseline is red, or there are no tests, stop and say so. Then work in
   conservative mode (only the most obviously safe changes, backed by a type
   check/build) or ask how to proceed. Never refactor on top of an unknown
   baseline and claim behavior is preserved.

In report mode you need not run anything, but still note whether a safety net
exists — it changes how risky the suggested fixes are.

## Fix mode: the behavior contract

The core promise: **for valid inputs, the software does exactly what it did
before.** Honor it per dimension, because "preserve behavior" means different
things across them:

- **Quality dimensions (`clean-code`, `reuse`, `simplicity`, `performance`):**
  strictly behavior-preserving for *all* inputs. A performance fix changes speed,
  never results. Allowed refactorings: rename; extract function/variable/constant;
  inline; guard clauses / early returns; split a function; dedupe identical logic;
  remove provably-dead code; replace an algorithm/data structure with one that
  returns identical results. Forbidden without explicit approval: changing logic,
  observable output, error/exception semantics, public API signatures, serialized
  formats, or concurrency semantics.
- **`security` and `robustness`:** hardening *intentionally* changes behavior on
  invalid, malicious, or edge inputs (it rejects, validates, fails safe). That is
  the fix, not a violation. But it is **not** a pure refactoring. So: **report
  these by default and apply only with explicit approval**, clearly labeled as a
  semantic change. The constraint that still holds: behavior for *valid* inputs
  must stay identical.

In every mode:

1. **Baseline first.** A green run from Step 1 is required before automated fixing.
2. **Small, atomic steps.** One logical change at a time; re-run verification after
   each. If it goes red, revert that step and report it instead. Never batch ten
   refactorings and hope.
3. **Stay in scope.** Touch only what a finding requires. Do not reformat untouched
   lines, reorder imports, or "improve" adjacent code — that pollutes the diff and
   hides the real change. Match existing style.
4. **Verify at the end** and report the result explicitly.
5. **Summarize** each change as: what, why, "verified by <command>". Anything not
   safely fixable stays a reported suggestion.

If preserving behavior and applying a fix ever conflict, **preserving behavior
wins** — downgrade that item to a reported suggestion.

## Prioritize, do not flood

The failure mode of every audit tool is noise: 400 trivial nits burying the three
that matter, training the reader to ignore the report.

- Rank by impact. A 300-line function doing five things, or an unparameterized SQL
  string, outranks a variable named `tmp`.
- Group similar findings ("12 functions use single-letter loop vars") instead of
  listing each.
- If something is uniformly fine, say so in one line. Silence on the trivial is a
  feature.
- Severity: **High** = hurts correctness/security/changeability now. **Medium** =
  clear cost. **Low** = polish; mention briefly or in aggregate.

## Report mode output

```
# Code Audit: <target>

**Scope:** <files/region> · **Dimensions:** <which ran> · **Safety net:** <tests? baseline green?>

## Summary
<2-4 sentences: overall health, the 1-3 things that matter most.>

## Findings
### High
- `path/to/file.py:line` — [<dimension>] <short title>
  Problem: <what>. Why it matters: <impact>.
  Fix: <concrete change>. <If security/robustness: note it changes behavior on bad input.>
### Medium
- ...
### Low
<aggregate where possible>

## Suggested order of attack
1. <highest-leverage fix first>
2. ...
```

Keep each finding tight enough to act on without a follow-up question.

## Boundaries

- Not a bug hunt on the current diff — that is `/code-review`. If you spot a bug
  while reading, mention it as an aside; do not pivot the whole audit to it.
- Not architecture redesign. Renaming and splitting functions is in scope;
  re-drawing module boundaries is a design conversation — raise it, do not
  silently undertake it.
- Not LLM/agent attack hardening — that is the **ai-hardening** skill.
