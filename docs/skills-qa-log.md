# Skills QA Log

Record of the quality tests run against the consolidated skill set, so results
are reproducible rather than living only in a chat session.

## Test fixture

`tests/skill-eval/` holds the reusable fixture:

- `fixture/` , a small Python "billing-demo" repo (`src/accounts.py`, `reports.py`,
  `assistant.py`) seeded with 18 deliberate defects across every code-audit
  dimension plus the ai-hardening (LLM) attack surface.
- `answer-key.md` , the graded answer key (which defect lives where). **Do NOT
  show the answer key to a skill-under-test agent** , give it only `fixture/src/`,
  then grade its findings against the key.

## Round 1 , code-audit & ai-hardening (defect-finding skills)

Method: blind subagent runs (skill given only the fixture), graded against the key,
plus a no-skill baseline for the value delta.

| Skill | Recall | Precision | Notes |
|---|---|---|---|
| `code-audit` (all dimensions) | 16/17 non-AI defects | high (0 invented) | missed one resource-leak (R3) hidden inside a function already flagged for SQLi |
| `ai-hardening` (assistant.py) | 5/5 | high | + extras (max_tokens, unpinned model) |
| baseline (no skill) | ~18/18 | flat list | found everything incl. R3, but no prioritization / no behavior-preservation labeling |

**Finding:** on a small dense fixture a thorough baseline finds as much; the skill
value is discipline (severity ordering, fix order, behavior-preservation marking,
AI vs non-AI routing), which scales with repo size. The fixture cannot show the
recall advantage and has no precision "bait", so treat recall/precision here as a
floor, not a benchmark.

**Optimization applied & verified:** sharpened `code-audit/references/robustness.md`
resource-leak check ("scan every function that opens a resource, even ones flagged
for something else"). Re-test then found R3 **and** an additional cursor leak.

## Round 2 , the 6 umbrella skills (knowledge/methodology)

Method: one thorough QA subagent per umbrella, reading SKILL.md + every reference,
checking substance (trim damage), dangling links, staleness, coverage gaps, and
description/routing sharpness.

**Result:** routing was sharp everywhere and no reference was gutted by trimming,
but the deep read surfaced real defects the earlier spot-check missed. All fixed
(commit `405c4a3` + the cosmetic pass after it):

| Umbrella | Defects fixed |
|---|---|
| `web` | missing `with_server.py` bundled (E2E path now runs); ui-ux vs frontend-design font conflict scoped |
| `ai-systems` | `rag.md` stale LangChain imports modernized + `text-embedding-3` |
| `security` | `api-and-auth.md` OAuth-token-in-URL, non-deterministic refresh-token lookup, outdated rate-limit-redis/connect-redis; `threats.md` OWASP-2025 labeled draft |
| `platform` | `containers.md` Python track + base-image bumps; `observability.md` Jaeger to OTLP; `infra-ops.md` real Terraform/k8s/GitHub-Actions added |
| `bootstrap` | `docs.md` now defines the promised deliverable doc templates |
| cross-cutting | routing boundaries (`/code-review`, `ai-systems`, bidirectional security/code-audit/ai-hardening); em/en-dashes stripped; superpowers path + placeholder mismatch fixed |

## How to re-run

1. Defect skills: give a fresh agent only `tests/skill-eval/fixture/src/` + the
   skill path, ask for a report-mode audit, grade against `answer-key.md`.
2. Umbrella skills: give a fresh agent a skill's directory, ask it to QA every
   reference (substance, dangling links, staleness, coverage, routing).
3. After any fix: `./scripts/skills/validate.ps1`, then
   `./scripts/skills/sync.ps1 -Profile freelancer-fullstack -Targets claude`.
