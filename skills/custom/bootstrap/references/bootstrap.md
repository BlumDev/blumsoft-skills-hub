# Bootstrapping a project

Turn an idea or an existing repo into a decision-complete plan plus the minimum set of artifacts so implementation starts immediately. Clarify scope, pick the smallest architecture that ships, then iterate.

## Kickoff

### Inputs to ask for (if missing)
- Product goal + success metric
- Target users + top 3 use cases
- Tech constraints (stack, hosting, budget, timeline)
- Existing repo context (if any): entry points, current issues, deployment

### Decisions to make
- Scope: what is in and out (no gold-plating).
- Minimal viable architecture that can ship.
- The first vertical slice (end-to-end).
- Verification: tests, checks, and a demo path.

### Deliverables (create/update as needed)
1. `PROJECT_CONTEXT.md`
2. `FEATURES/README.md` plus the first feature spec(s) in `FEATURES/`
3. `DECISIONS.md` (short ADR-style list, include tradeoffs)
4. An implementation plan: 3-6 milestones with verification gates (commands + smoke tests)

## Discovery: is this an LLM task?

Not every problem benefits from LLM processing. Evaluate task-model fit before writing code.

**Suited to LLMs:**

| Characteristic | Why it fits |
|----------------|-------------|
| Synthesis across sources | Combining information from multiple inputs |
| Subjective judgment with rubrics | Grading, evaluation, classification with criteria |
| Natural language output | Goal is human-readable text, not structured data |
| Error tolerance | Individual failures do not break the system |
| Batch processing | No conversational state between items |
| Domain knowledge in training | Model already has relevant context |

**Not suited to LLMs:**

| Characteristic | Why it fails |
|----------------|--------------|
| Precise computation | Math, counting, exact algorithms are unreliable |
| Real-time requirements | Latency too high for sub-second responses |
| Perfect accuracy | Hallucination makes 100% impossible |
| Proprietary data dependence | Model lacks the context |
| Sequential dependencies | Each step depends heavily on the previous result |
| Deterministic output | Same input must produce identical output |

### Manual prototype first
Before automating, validate fit with one representative input in the model interface. This takes minutes and prevents hours of wasted work. It answers:
- Does the model have the required knowledge?
- Can it produce the output format you need?
- What quality should you expect at scale?
- What are the obvious failure modes?

If the manual prototype fails, the automated system will fail. If it succeeds, you have a baseline and a prompt template.

## Architecture

### Staged pipeline
Structure LLM projects as stages that are **discrete** (clear boundaries), **idempotent** (re-runs reproduce results), **cacheable** (intermediate results persist), and **independent** (each runs separately).

```
acquire → prepare → process → parse → render
```

1. **Acquire**: fetch raw data (APIs, files, databases)
2. **Prepare**: transform into prompt format
3. **Process**: execute LLM calls (expensive, non-deterministic)
4. **Parse**: extract structured data from outputs
5. **Render**: generate final outputs (reports, files, visualizations)

Only stage 3 is non-deterministic and expensive. Separating it lets you re-run LLM calls only when needed while iterating fast on parsing and rendering.

### File system as state machine
Track pipeline state with files, not databases or in-memory structures. Each unit gets a directory; stage completion is marked by file existence.

```
data/{id}/
├── raw.json         # acquire complete
├── prompt.md        # prepare complete
├── response.md      # process complete
├── parsed.json      # parse complete
```

To check if an item needs work: test whether the output file exists. To re-run a stage: delete its output and downstream files. To debug: read the intermediate files. This gives natural idempotency, human-readable debugging, simple parallelization, and trivial caching.

### Structured output design
When outputs must be parsed programmatically, prompt design determines parsing reliability. Specify exact format with examples, explicit section markers, a note that output will be parsed programmatically, and constrained values (enumerated options, score ranges).

```
Analyze the following and respond in exactly this format:

## Summary
[Your summary here]

## Score
Rating: [1-10]

## Details
- Key point 1
- Key point 2

Follow this format exactly because I will be parsing it programmatically.
```

LLMs do not follow instructions perfectly. Build parsers that use flexible regex, provide sensible defaults for missing sections, and log failures rather than crashing.

### Single vs multi-agent
Single-agent pipelines fit batch processing with independent, non-interacting items and simpler cost/complexity management. Multi-agent fits parallel exploration, tasks exceeding one context window, and cases where specialized sub-agents improve quality. The real reason for multi-agent is **context isolation**, not role-playing: sub-agents get fresh context windows for focused subtasks, preventing context degradation on long tasks.

### Architectural reduction
Start minimal; add complexity only when proven necessary. Removing specialized tools often improves performance (Vercel's d0 went from 17 tools at 80% success to 2 primitives, bash + SQL, at 100%).

Reduce when: your data layer is well-documented and consistent, the model has enough reasoning capability, your tools were constraining rather than enabling, or you spend more time on scaffolding than outcomes.

Keep complexity when: data is messy or poorly documented, the domain needs knowledge the model lacks, safety requires limiting capabilities, or operations genuinely benefit from structured workflows.

### Cost estimation
Estimate before starting and track throughout.

```
Total cost = (items × tokens_per_item × price_per_token) + API overhead
```

Estimate input and output tokens per item, multiply by item count, add 20-30% buffer for retries. If actuals exceed estimates, reduce context, use smaller models for simpler items, or reuse partial results. Parallelism reduces wall-clock time, not token cost.

## Development

### Agent-assisted iteration
Generate, test, fix, repeat: describe the goal and constraints, let the agent produce an initial implementation, then iterate on specific failures and refine prompts and architecture. Provide clear requirements upfront, break the project into discrete components, test each before moving on, and keep the agent on one task at a time.

### Plan
1. **Task analysis**: input, output, task type (synthesis/generation/classification/analysis), acceptable error rate, value per completion.
2. **Manual validation**: test one example, evaluate quality and format, identify failure modes, estimate tokens.
3. **Architecture**: single vs multi-agent, tools and data sources, storage/caching, parallelization.
4. **Cost**: items × tokens × price, plus development time and operational costs.
5. **Development**: stage-by-stage implementation, per-stage testing, iteration milestones, deployment.

Expect to refactor. Mature agent systems require multiple architectural iterations. Structures added for today's model limitations become tomorrow's constraints, so keep the architecture simple and test across model strengths to confirm the harness is not limiting performance.

### Anti-patterns
- **Skipping manual validation**: automating before verifying the model can do the task.
- **Monolithic pipelines**: one script with no persistent intermediate outputs; hard to debug and iterate.
- **Over-constraining the model**: guardrails and pre-filtering the model could handle itself; test whether scaffolding helps or hurts.
- **Ignoring cost until production**: token costs compound at scale.
- **Perfect parsing requirements**: expecting flawless format adherence instead of robust parsers.
- **Premature optimization**: caching and parallelization before the basic pipeline works.

## Guidelines
1. Validate task-model fit with manual prototyping before building automation.
2. Structure pipelines as discrete, idempotent, cacheable stages.
3. Use the file system for state management and debugging.
4. Design prompts for structured, parseable output with explicit format examples.
5. Start with minimal architecture; add complexity only when proven necessary.
6. Estimate costs early and track throughout.
7. Build robust parsers that handle output variations.
8. Expect and plan for multiple architectural iterations.
9. Test whether scaffolding helps or constrains the model.
10. Use agent-assisted development for rapid iteration.
