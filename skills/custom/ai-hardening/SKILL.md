---
name: ai-hardening
description: >-
  Defensively review AI/LLM/agent code for the LLM-specific attack surface and
  harden it. Covers prompt injection (direct and indirect via retrieved or
  tool-returned content), insecure handling of model output (output fed to
  eval/SQL/shell/HTML), excessive agency (over-powered tools, missing human-in-
  the-loop), system-prompt and secret leakage, RAG/vector access control and
  poisoning, and unbounded token/cost/loop consumption. Two modes: a prioritized
  findings report (default), or hardening fixes applied with approval that keep
  legitimate behavior intact while closing the attack path. Use whenever code
  calls an LLM API, builds prompts, defines tools/functions for a model, runs or
  consumes an MCP server, does retrieval-augmented generation, or implements an
  agent, and the user wants to review, audit, secure, or harden it against
  attacks, e.g. "is my agent safe from prompt injection", "harden this LLM
  endpoint", "review my tool definitions for abuse", "can this RAG pipeline be
  poisoned", "secure my MCP server". For non-AI code security (SQL injection,
  authz, secrets) use the code-audit skill's security dimension instead.
---

# AI / LLM Hardening

Defensive review of AI/LLM/agent code against the attacks that are specific to
putting a language model in the loop. This is hardening existing code, finding
weaknesses so they can be closed, not building attacks.

Classic appsec (SQLi, authz, secrets in non-AI code) belongs to the **code-audit**
skill's `security` dimension. This skill covers what that one explicitly does not:
the LLM attack surface. The two are complementary, for an AI service you usually
want both.

## The two-channel mental model

Almost every LLM vulnerability is one confusion: **the model cannot reliably tell
instructions from data.** Anything that lands in the context window, the user
message, a retrieved document, a tool's return value, a web page the agent
fetched, a filename, can carry instructions the model may follow. So the whole
game is:

1. **Treat every byte the model did not get from you as untrusted**, including the
   model's *own output*.
2. **Keep untrusted content out of the instruction channel**, or mark it clearly
   as data the model must not obey.
3. **Constrain what the model can *do*** (tools, permissions) so that a successful
   injection has a small blast radius.

Read `references/llm-threats.md` for the full catalog mapped to code checks. Load
it when you start the review.

## Modes and the behavior contract

- **Report (default).** Identify weaknesses, explain the attack, propose the fix.
- **Harden (with approval).** A hardening fix *intentionally* changes behavior on
  the malicious path, it blocks an injection, rejects a tool call, truncates a
  runaway loop. That is the point, but it is a semantic change: apply only with
  explicit approval, keep the legitimate path working, and verify with tests where
  they exist. If a guard might reject valid input (over-blocking), say so.

## Workflow

1. **Map the AI surface.** Find where the code: calls an LLM; assembles prompts
   (system + user + retrieved + tool results); defines tools/functions the model
   can call; runs or consumes an MCP server; retrieves into the context (RAG);
   acts on model output. List these, they are your trust boundaries.
2. **Trace untrusted content into the prompt.** For each thing entering the context
   window, ask: is it attacker-influenceable (user input, a fetched page, a DB row,
   a tool result, a document)? If yes, it can carry injected instructions.
3. **Trace model output to its sinks.** Where does the response go? Rendered as
   HTML (XSS), run as SQL/shell/code (RCE), used as a file path, passed to another
   tool, or auto-executed? Output to a dangerous sink is the second half of most
   exploits.
4. **Inventory agency.** What tools can the model invoke, with what permissions?
   Which actions are irreversible, outbound, or sensitive (send money, delete,
   email, write files, make network calls)? Is there a loop/iteration bound?
5. **Check against the catalog** in `references/llm-threats.md` and report,
   prioritized by reachability and blast radius.

## Prioritize

Rank by: can untrusted content reach the model (reachability) × what a successful
injection can then do (agency/blast radius). An agent that takes web content and
can call a shell tool with no confirmation is critical. A chatbot that only ever
returns text to the same user who typed the input is low-risk for the same flaw.
Do not flood the report with theoretical issues on paths an attacker cannot reach. Mark uncertain reachability as "needs confirmation".

## Report output

```
# AI Hardening Review: <target>

**AI surface:** <LLM calls / tools / RAG / MCP found> · **Safety net:** <tests?>

## Summary
<the 1-3 highest-blast-radius weaknesses>

## Findings
### Critical / High
- `file:line`, [<threat, e.g. indirect-prompt-injection>] <title>
  Attack: <how untrusted content reaches the model / a sink, and what it achieves>.
  Blast radius: <what the model can do once injected>.
  Fix: <defensive change, isolation, allowlist, output validation, confirmation>.
### Medium / Low
- ...

## Suggested order of attack
1. <reduce blast radius first, clamp agency, then close injection vectors>
```

## Boundaries

- Defensive only: identify and close weaknesses. Do not write working exploits,
  jailbreak payloads, or injection strings beyond the minimal proof needed to show
  a finding is real.
- Model-behavior tuning (refusals, alignment, eval of answer quality) is out of
  scope, this is about code-level attack surface, not prompt-engineering quality.
- Non-AI appsec: auditing existing code → code-audit `security` dimension; writing/designing new secure code → the **security** skill.
