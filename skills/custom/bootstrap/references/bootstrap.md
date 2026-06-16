# Bootstrapping a project

Turn an idea or an existing repo into a decision-complete plan plus the minimum set of artifacts so implementation starts immediately. Clarify scope, pick the smallest architecture that ships, then iterate. Use the greenfield path for a new project, the takeover path for an existing repo.

## Greenfield kickoff

### Inputs to gather (ask if missing)
- Product goal + success metric.
- Target users + top 3 use cases.
- Tech constraints (stack, hosting, budget, timeline).
- Any existing context (related repos, prior art, integrations).

### Early decisions to make
- Scope: what is in and out (no gold-plating).
- Minimal viable architecture that can ship.
- The first vertical slice (end-to-end, demoable).
- Verification: tests, checks, and a demo path.

### Initial deliverables (create/update as needed)
1. `PROJECT_CONTEXT.md` - goal, users, scope, constraints, stack, deployment target.
2. `FEATURES/README.md` plus the first feature spec(s) in `FEATURES/` - one spec per feature, with acceptance criteria.
3. `DECISIONS.md` - short ADR-style list of choices with tradeoffs and rationale.
4. An implementation plan: 3-6 milestones, each with a verification gate (commands + smoke tests).

## Existing-repo takeover

Goal: get an unfamiliar repo into a working, understood state and record what you learned. Work the checklist top to bottom; do not skip the run/test steps.

1. **Clone and inspect** - clone the repo, list the top-level layout, read `README`, `CONTRIBUTING`, and any `docs/`.
2. **Identify the stack** - language(s), framework(s), package manager, runtime versions. Read the manifest (`package.json`, `pyproject.toml`, `go.mod`, `pom.xml`, `Cargo.toml`, etc.) and any lockfile.
3. **Install dependencies** - use the pinned package manager/version. Note required system deps, env vars, and `.env.example` keys (never the secret values).
4. **Find the build/run/test commands** - check manifest scripts, `Makefile`/`Taskfile`, CI config (`.github/workflows`, `.gitlab-ci.yml`), and container files (`Dockerfile`, `docker-compose.yml`).
5. **Map entry points** - the main binary/server, CLI entry, HTTP routes or handlers, background workers, and how config is loaded.
6. **Identify conventions** - directory structure, naming, lint/format config, test layout, branching/commit style. Match these; do not reformat.
7. **Run it** - start the app locally and confirm it boots. Record exact commands and any setup gotchas.
8. **Run the tests** - execute the suite, note pass/fail, coverage, flaky or skipped tests, and how long it takes.
9. **Note tech debt and risks** - dead code, TODO/FIXME, missing tests, outdated deps, security smells, single points of failure. Mention; do not fix yet.
10. **Document findings** - write or update `PROJECT_CONTEXT.md` (stack, entry points, how to build/run/test, deployment) and `DECISIONS.md` (notable existing choices and any open questions). Capture the run/test commands so the next person skips the rediscovery.

## Discovery and early architecture

- Define the problem and the smallest end-to-end slice that proves it. Prefer one working path over many half-built ones.
- Choose the minimal viable architecture that can ship; add structure only when a concrete need forces it.
- Identify data sources, external integrations, and storage early; these usually drive the design.
- Make boundaries explicit: separate components with clear inputs/outputs so each can be built and tested alone.
- Plan verification up front: for each milestone, define the command and smoke test that proves it works.
- Expect to refactor. Keep the architecture simple and unopinionated so it absorbs change instead of locking in early guesses.

### Anti-patterns
- Big-bang design before a single slice runs end-to-end.
- Speculative abstractions, config, and error handling nobody asked for.
- Onboarding to a repo without ever running its build, app, and tests.
- Refactoring or reformatting adjacent code during takeover.
- Leaving findings undocumented, forcing the next person to rediscover the build/run/test commands.

## Guidelines
1. Clarify scope and success metric before building anything.
2. Pick the smallest architecture that ships; add complexity only when proven necessary.
3. Drive everything through one end-to-end vertical slice first.
4. On takeover, prove the repo builds, runs, and tests pass before changing it.
5. Match existing conventions; do not reformat or refactor unprompted.
6. Record decisions and tradeoffs in `DECISIONS.md` as you make them.
7. Keep `PROJECT_CONTEXT.md` the single source for stack, entry points, and run/build/test commands.
8. Define a verification gate per milestone.
9. Note tech debt and risks; fix only what the task requires.
10. Expect multiple iterations; keep the design easy to change.
