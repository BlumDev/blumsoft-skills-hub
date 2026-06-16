---
name: ai-systems
description: >-
  Building AI/LLM features and agents: prompt engineering, MCP servers,
  retrieval-augmented generation (RAG), and agent/graph orchestration. Loads
  focused references on demand. Use when designing or implementing LLM-backed
  features, e.g. "design a prompt for X", "build an MCP server", "set up a RAG
  pipeline", "structure an agent with langgraph", "improve retrieval quality".
  For hardening AI/agent code against prompt injection and tool abuse use the
  ai-hardening skill; for general code quality/security of the implementation use
  the code-audit skill.
---

# AI Systems

Building practical AI/LLM features. Each area has a focused reference; load only
what the task needs.

## References

| When | Read |
|---|---|
| Designing prompts, choosing a prompting framework | `references/prompt-engineering.md` |
| Building or consuming an MCP server / tools for a model | `references/mcp.md` |
| RAG: chunking, embeddings, vector stores, reranking | `references/rag.md` |
| Multi-step agents, state graphs, routing, human-in-the-loop | `references/agents.md` |

## Boundaries

- Hardening AI/agent code against attacks (prompt injection, insecure output
  handling, excessive agency) → **ai-hardening** skill.
- General code quality, security, robustness of the implementation → **code-audit**.
