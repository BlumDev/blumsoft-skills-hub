# Documentation

Create client-ready technical documentation with business context, setup, architecture, and troubleshooting.

## What good docs need

- Lead with intent: why the project exists, before the how.
- Make it runnable: exact commands to install, build, run, and test.
- Show the shape: an architecture overview (Mermaid diagram when it helps).
- State the contracts: API/module inputs, outputs, and conventions.
- Cover failure: prerequisites, env vars (names only), troubleshooting.
- Keep it current: short, factual, append-only where history matters.

## Deliverable templates

These are the documents the bootstrap flow produces. Keep each compact; outline form over prose.

### PROJECT_CONTEXT.md

Single source for stack, entry points, and run/build/test commands.

- **Overview** - goal, target users, top use cases, scope (in/out).
- **Stack** - languages, frameworks, package manager, runtime versions.
- **Run / build / test** - exact commands; prerequisites and `.env` keys (names only).
- **Conventions** - directory layout, naming, lint/format, branching/commit style.
- **Where things live** - entry points, config loading, key modules, deployment target.

### DECISIONS.md

ADR-style, append-only log. One entry per decision; never edit past entries.

Each entry:

- **Decision** - what was chosen, in one line.
- **Context** - the problem or constraint that forced the choice.
- **Alternatives considered** - options rejected and why.
- **Consequences** - what this enables, costs, or locks in.
- **Date** - when decided (YYYY-MM-DD).

### FEATURES/README.md

Index of features; one full spec per feature lives beside it in `FEATURES/`.

- **Per feature** - name, one-line description, status (planned / in progress / done), entry point(s) (file, route, or command).
- **Layout note** - link each feature to its detailed spec file in `FEATURES/`.
