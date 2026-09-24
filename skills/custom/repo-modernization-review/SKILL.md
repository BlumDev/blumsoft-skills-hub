---
name: repo-modernization-review
description: >-
  Assess an existing repository for evolutionary modernization and decide per
  module KEEP / REFACTOR / REWRITE / DELETE, backed by evidence from the code:
  reconstructed as-is architecture, simplest target architecture, the delta as
  prioritized work packages, and an explicit rewrite assessment. Report only,
  never changes code or dependencies. Built to be re-run periodically with
  newer models: it reads prior reviews and recorded decisions first and reports
  what changed since. Use when the user wants to assess, modernize or
  re-evaluate an older repo, e.g. "what should we keep, refactor or rewrite",
  "is a rewrite worth it", "modernization plan for this repo", "review this old
  project with a fresh model", "Repo modernisieren", "Altprojekt bewerten",
  "lohnt sich ein Rewrite", "IST/SOLL-Architektur". For line-level quality or
  security findings use code-audit; for implementing the resulting work
  packages use engineering or code-audit --fix.
---

# Repo Modernization Review

The decision layer above a code audit. `code-audit` finds problems line by
line; this skill decides what to do with each part of a repo and in which
order, and whether a rewrite is justified. It produces a report and proposed
backlog entries. It never implements them.

## Hard rules

- **Report only.** No changes to code, config, dependencies, lockfiles or git
  refs (a `git fetch` only when the caller allows it). The only files written
  are the report and, if the caller permits it, backlog entries. Scratch
  output goes to a temp dir outside the repo.
- **Evidence or label.** Every classification, risk and work package cites
  `path:line`, a command and its output, or a git fact. Anything without
  evidence is marked **Assumption**.
- **Code beats docs.** Code, config, deploy files and lockfiles outrank README,
  diagrams, comments and old reviews. Docs are a hypothesis to verify; list
  every contradiction found as doc drift.
- **Newer is not a reason.** A change needs a concrete cost of the status quo
  that is visible in this repo (a bug, a risk, repeated friction, a dead end
  for a planned feature). "Pattern X is the modern way" is not a cost.
  Exception with its own evidence: a runtime or dependency out of security
  support.
- **Business logic is specification.** Special cases, validations and odd
  constants may encode requirements nobody wrote down. When unsure whether
  behavior is intended, keep it and list it as an open question.
- **Recorded decisions stand.** Decisions in `docs/decisions.md`, accepted
  ADRs and owner decisions recorded in the backlog are not re-litigated. A
  proposed (not accepted) ADR is an open proposal, not a decision. Reopen a
  decision only where its premise no longer holds, cite the premise and the
  contradicting evidence, and reopen only the part that fails (as an open
  question to the owner).
- **Measure versions, never recall them.** Outdated versions, deprecations,
  EOL dates and breaking changes come from the package manager, the registry
  (`npm view`, `pip index versions`), the official release schedule or
  endoflife.date, not from model memory. Read-only network lookups for this
  are allowed; name the source in the report.
- **Status claims are claims.** A review or backlog saying "fixed in abc123"
  is checked against the reviewed branch (`git merge-base --is-ancestor`,
  `git branch -r --contains`) and the code at the cited line before it is
  repeated.

## Step 0, Context, basis and depth

1. Read, in this order: `AGENTS.md` / `CLAUDE.md`, any status source they
   declare authoritative (masterplan, roadmap), `docs/backlog.md` (including
   its status frontmatter if present), `docs/decisions.md` and ADRs, the
   newest files in `docs/reviews/` (prior modernization reviews first), then
   README as a hypothesis.
2. Fix the basis: branch and commit SHA of the default branch unless told
   otherwise. Fetch first only if the caller allows writing git refs;
   otherwise use the local remote-tracking ref and state the last fetch time
   (mtime of `.git/FETCH_HEAD`). If the working tree is on another branch or
   dirty, review the committed state (`git show <ref>:<path>`, or a
   `git archive <ref>` export to a temp dir). Record the model doing the review.
3. Fix the scope: own code only. Exclude dependencies, generated code, build
   output, vendored code and forked upstream code. For a fork, determine the
   boundary from git (upstream remote, `git merge-base`, `git diff
   --name-status <base> HEAD`, authorship), not from notes, and state it.
   Sibling repos may be read, read-only, when needed to prove an integration
   contract or that something is superseded.
4. Choose the depth: take the highest row whose condition matches, and say
   why:

| Depth | When | Output |
|---|---|---|
| Deep | production use with real users, data or external integrations, or explicitly asked | Standard plus data model, auth and every integration boundary in detail |
| Standard | repo in active development or maintenance | full report, modules at package or directory level |
| Triage | repo paused, retired or experimental, or under ~2k lines of own code | repo-level verdict (continue / maintenance only / archive), top 3 risks, one page |

## Step 1, Reconstruct the as-is (IST)

- **Repo map**: modules with a one-line responsibility, entry points, lines of
  own code per module (measured, e.g. `git ls-files <dir> | xargs wc -l`, or
  `cloc`/`tokei` if installed).
- **Stack and versions** from manifests and lockfiles.
- **Build, test, deploy**: the real commands from package scripts, CI, Docker
  and deploy config, and whether CI actually runs the tests. Run tests, type
  check or lint only if cheap and safe: no network side effects, no
  production credentials, no GPU or model loading, and no writes into the
  repo (prefer `python -B`, redirect caches and build info to a temp dir; if a
  command writes into the tree anyway, do not run it). Record results; if not
  run, say so and why.
- **Runtime structure**: processes, services, databases, external APIs, taken
  from deploy config, compose files and env var NAMES (never values).
- **Dependency direction**: who imports whom across modules (a sampled import
  graph is enough). Flag domain code importing UI, transport or infrastructure.
- **Doc drift**: every place where docs or comments contradict the code.

## Step 2, Analyze

Delegate depth instead of re-implementing it:

- Apply the **code-audit** references for `security`, `robustness`,
  `reuse-and-simplicity` and `clean-code` in report mode; `performance` only
  when there is a concrete performance symptom. This skill sets the scope, so
  skip code-audit's "ask which dimension" step. Do not read everything:
  sample the churn hotspots (`git log --format= --name-only | sort | uniq -c |
  sort -rn`), the largest files, and the paths behind open findings. Keep only
  findings that change a module decision or belong in the top risks.
- AI/LLM/agent code: **ai-hardening**. ABAP: **sap-abap-review**.

Own checks, no other skill covers them:

- **Architecture**: module boundaries, coupling (cross-module imports),
  dependency direction, where state lives, error-handling strategy, config
  management (one place vs scattered env reads), API boundaries.
- **Data model** (Standard and Deep): schema and migrations, constraints,
  indices for the hot queries, transaction boundaries, tenant isolation if the
  app is multi-tenant, backup of the data that matters.
- **Tests**: list the 5 to 10 most important business rules and map each to a
  test (`path`) or "none". Quality over percentages; quote coverage only if the
  tooling already exists.
- **Dependencies**: run the ecosystem's read-only commands (`npm outdated`,
  `npm audit --omit=dev`, `pip list --outdated` or `uv pip list --outdated
  --python <env>`, `pip-audit`, `dotnet list package --outdated`, ...). If an
  audit tool is missing, say so instead of installing it. Flag majors behind,
  deprecated or unmaintained packages, known vulnerabilities, runtimes past
  EOL, and libraries the current platform version already replaces. If the
  environment belongs to another repo, count only packages the own code
  imports directly. Never install or upgrade.
- **Business rules to preserve**: implicit rules, special cases, validations,
  integration behavior, constants with domain meaning, each with `path:line`.
  This list is the contract any refactor or rewrite must keep.

## Step 3, Classify modules

One row per module (package, directory or a file that stands alone). A row
may point to several work packages. No decision from style preference.

- **KEEP**: works, tested or low risk, no concrete cost visible. The default
  when there is no evidence of cost. "KEEP (decided)" when an owner decision
  covers it; cite it.
- **REFACTOR**: the structure is sound, the implementation has a concrete cost
  (bug-prone, duplicated logic that already diverged, untestable). Incremental
  and behavior-preserving.
- **REWRITE** (module-level): only if the design itself causes the defects
  (not just the code), refactoring would touch most of it anyway, AND its
  contract is small enough that parity can be proven. Name the parity check and
  the characterization tests to write first.
- **DELETE**: unused, obsolete, or superseded by an existing component. Prove
  "unused" by searching the WHOLE repo, including config, lint, build, CI and
  deploy files (no imports, routes, script entries, cron or deploy
  references). If dynamic loading, external callers or planned use cannot be
  ruled out, mark it "confirm with owner".
- **Out of scope**: upstream, vendored or generated code; one row, with the
  cost it causes for the own code if any.

The Priority column is the Step 4 tier of the most urgent package for that
module, or "none".

## Step 4, Target (SOLL) and delta

- The target is the **simplest architecture that meets the requirements the
  repo actually has**, described as changes to the as-is, not as a greenfield
  design. New frameworks, service splits, extra abstraction layers or
  technology swaps need evidence that the current setup blocks a real
  requirement.
- The delta becomes work packages. Each has: goal, why (evidence), affected
  paths, dependencies, risk including regression risk, effort (S/M/L), and
  verification (the test or command that proves it done).
- Tiers: 1 security and data integrity, 2 architecture issues with high blast
  radius, 3 missing tests for critical business rules, 4 heavy technical debt,
  5 dependencies, 6 maintainability, 7 cleanups. An item that fits several
  tiers takes the highest. Within a tier, benefit over effort.
- A package that touches untested business logic is preceded by a package that
  writes characterization tests for it. Such a prerequisite inherits the tier
  of the package it unblocks.

## Step 5, Rewrite assessment

State one verdict: **no rewrite**, **selective rewrite** (name the modules), or
**full rewrite**.

A full rewrite is justified only if ALL of these hold, each with evidence:
the evolutionary path is shown to cost more; the business-rule inventory is
complete enough to serve as the spec; data migration is feasible; every
integration is enumerated with its contract; a parallel-run or cut-over plan
exists. Otherwise name the condition that fails. Cost comparison may be rough
and is labeled as an estimate: sum of work-package efforts for the
evolutionary path against own-code size plus business-rule count for a
rewrite. Weigh: size, business-logic density, production use, users and data,
integrations, test coverage, architecture state, stack viability (EOL,
security support).

## Step 6, Report and handover

Write the report in the language of the repo's docs. Path: the repo's review
convention with a `-modernization` suffix, e.g.
`docs/reviews/YYYY-MM-DD-<agent>-modernization.md`; if the repo has no review
location, ask. If the caller forbids writing into the repo, write it where the
caller says.

Header: basis branch and SHA (plus fetch age), model, depth and why, scope
boundary, prior review referenced.

Sections (Triage: only 1, 4, 5 and 9, shortened):

1. **Summary**: 3 to 5 sentences, overall state, verdict, top 3 actions.
2. **Changes since the last review**: resolved, still open, new, as a table.
   On the first modernization review, reconcile the open items of earlier
   audits that bear on a module decision.
3. **Repo map and as-is**: module table, stack, build/test/deploy (what ran,
   with result), runtime, dependency direction, dependencies (measured), doc
   drift. Deep adds data model, auth and integration boundaries.
4. **Risk register**: Severity | Risk | Evidence | Action.
5. **Module classification**: Module | Decision | Reason (evidence) | Risk |
   Priority.
6. **Business rules to preserve**: list with `path:line`, then the rule-to-test
   table from Step 2.
7. **Target architecture**: as changes to the as-is.
8. **Work packages**: grouped by tier, fields as in Step 4.
9. **Rewrite assessment**.
10. **Assumptions, open questions, not covered**: what was sampled, skipped or
    not run.

Sections 1, 5 and 8 must carry the verdict on their own. Everything else is
evidence: tables and one-liners, grouped, "fine" in one line where something
is fine.

Status lives in the backlog, not in the report. If the repo has
`docs/backlog.md` and the caller permits writing, add one open entry per work
package in the repo's format; reference existing entries by ID instead of
duplicating them. Otherwise list the entries as proposed lines at the end of
the report.

## Boundaries

- Implementation is a separate step, one work package at a time, via
  **engineering** (plan, TDD, verification) or **code-audit --fix**. This skill
  never starts it, not even for "obvious" fixes.
- Diff review before a merge is `/code-review`, not this skill.
- Architecture diagrams of the result: **gen-diagram**, which applies the same
  code-beats-docs rule.
