# Workflows, automation & tool design

## Workflow patterns

Implement tasks via a TDD red-green-refactor cycle against a written plan:

- Work from the track's `plan.md`; record progress in the plan file.
- Drive each task with a failing test first, then the minimal code to pass, then refactor.
- Stop at phase checkpoints; treat them as quality gates before moving on.
- Commit per task with clear notes; keep history traceable to plan items.
- Run the verification protocol at each gate; do not advance on red.

## Automation

Durable execution is what makes agent automation reliable: a network hiccup mid-flow must resume exactly where it left off, not lose state or double-charge.

Platform tradeoffs:
- **n8n** — accessible, low-code; sacrifices performance.
- **Temporal** — correct and robust; complex.
- **Inngest** — balances developer experience and reliability.

Core patterns:
- **Sequential** — steps run in order; each output feeds the next input.
- **Parallel** — independent steps run simultaneously; aggregate results.
- **Orchestrator-worker** — a coordinator dispatches work to specialized workers.

Anti-patterns: no durable execution for payments; monolithic workflows; no observability.

Sharp edges (always do):
- Use idempotency keys for every external call.
- Break long workflows into checkpointed steps.
- Set timeouts on all activities.
- Keep side effects out of workflow code.
- Use exponential backoff on retries.
- Keep large data out of the workflow; pass references.
- Handle failures explicitly (e.g. Inngest `onFailure`).

## Orchestration

Use orchestration for multi-step processes across services, distributed (all-or-nothing) transactions, long-running or human-in-the-loop flows, failure recovery that resumes from the last successful step, entity lifecycles, and infra automation. Do not use it for simple CRUD, stateless request/response, pure batch pipelines, or real-time streaming.

**The fundamental rule:** workflows orchestrate, activities touch the outside world.

| | Workflows (orchestration) | Activities (external interactions) |
|---|---|---|
| Role | Business logic, coordination, decisions | API/DB/network calls, notifications |
| Determinism | MUST be deterministic | May be non-deterministic |
| Constraint | No direct external calls | MUST be idempotent |
| State | Auto-preserved across failures | Built-in timeouts + retries; short-lived |

Decision: touches external systems → activity; orchestration/decision logic → workflow.

**Determinism (workflows):**
- Prohibited: threading/locks, `random()`, global/static state, `datetime.now()`, file I/O, network calls, non-deterministic libraries.
- Allowed: `workflow.now()`, `workflow.random()`, pure functions, calling activities.
- Versioning: use the versioning API (`get_version()`), or route new executions to a new workflow type; ensure old events still replay.

**Core patterns:**
- **Saga + compensation** — for each step, register its compensation before executing; on failure, run compensations in reverse (LIFO). Compensations must be idempotent.
- **Entity (actor)** — one long-lived execution per entity (cart, account, inventory); driven by signals, inspected via queries.
- **Fan-out/fan-in** — spawn parallel children, await all, aggregate, handle partial failures. Don't scale one giant workflow; for 1M tasks spawn 1K children × 1K tasks.
- **Async callback** — workflow requests then waits for a signal (human approval, webhook) to resume.

**Resilience:**
- Retry policy: initial interval, backoff coefficient, max interval, max attempts. Mark validation failures, business-rule violations, and permanent errors as non-retryable.
- Idempotency: dedup keys, unique constraints, upserts, processed-ID tracking.
- Heartbeats: long activities report progress so stalls are detected and retried.

Pitfalls: `datetime.now()` in a workflow; threading in workflow code; direct API calls from a workflow; non-idempotent activities; missing timeouts; ignoring payload limits (~2MB/arg). Monitor execution duration, activity failure rates, retries, and pending counts; scale horizontally with workers and task-queue partitioning.

## Tool design

Tools are contracts between deterministic systems and non-deterministic agents. The agent infers the contract from the description, so every ambiguity is a failure mode no prompt can fix. Tool descriptions are prompt engineering.

**Descriptions** answer four questions: what it does (specific, not "helps with"), when to use it (direct + indirect triggers), what inputs it takes (types, constraints, defaults), and what it returns (format + error conditions). Choose defaults that reflect the common case.

**Consolidation:** if a human engineer can't say which tool fits a situation, an agent can't either. Prefer one comprehensive tool that handles a full workflow over several narrow ones that must be chained (e.g. `schedule_event` over `list_users` + `list_events` + `create_event`). This cuts token cost, ambiguity, and selection complexity. Do not consolidate tools with fundamentally different behaviors, different contexts, or independent call sites.

**Architectural reduction:** taken further, prefer primitive general-purpose capabilities (e.g. file-system + command execution with `grep`/`cat`/`find`) over many specialized tools. Works when data is well-documented and consistent and the model can reason over the complexity; fails when data is messy, the domain needs knowledge the model lacks, or safety requires hard limits. Ask of each tool: does it enable new capability, or constrain reasoning the model already has? Build minimal architectures that benefit from better future models.

**Conventions:**
- Verb-noun tool names; consistent parameter and return-field names across the set.
- Response formats: offer `concise` (essential fields) vs `detailed` (full record) to control token usage; tell the agent when to use each.
- Error messages must be actionable for recovery: state what went wrong and how to fix it (retry guidance, corrected format, what's missing).
- MCP tools: always use fully qualified `ServerName:tool_name` to avoid "tool not found" with multiple servers.
- Keep collections to ~10-20 tools; beyond that, use namespacing and umbrella/routing tools.

**Anti-patterns:** vague descriptions ("Search the database"); cryptic params (`x`, `val`, `param1`); generic errors with no recovery path; inconsistent naming (`id` vs `identifier` vs `customer_id`).

**Iterate:** have an agent run the tool across diverse tasks, collect failure modes, and propose improved descriptions; re-test against the same tasks. Evaluate designs for unambiguity, completeness, recoverability, efficiency, and consistency.

## Executing plans

Batch execution with architect-review checkpoints. Announce at start that you are using the executing-plans approach.

1. **Load and review.** Read the plan, review it critically, raise any concerns before starting. If clear, create a todo list and proceed.
2. **Execute a batch** (default: first 3 tasks). Per task: mark in-progress, follow each step exactly, run the specified verifications, mark complete.
3. **Report.** Show what was implemented and the verification output; say "Ready for feedback" and wait.
4. **Continue.** Apply feedback, run the next batch, repeat until done.
5. **Finish.** After all tasks pass, complete the development branch (verify tests, present options, execute the choice).

**Stop and ask** (don't guess) on any blocker mid-batch: missing dependency, failing or unclear test, critical plan gap, or repeated verification failure. Return to review when the plan changes or the approach needs rethinking. Never start implementation on `main`/`master` without explicit consent; set up an isolated worktree first.
