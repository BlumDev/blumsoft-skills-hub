---
name: bs-dev-security
description: >-
  Writing secure code and designing secure systems: secure backend/frontend
  coding patterns, API security, authentication/authorization, and an OWASP-style
  web-vulnerability reference. Loads focused references on demand. Use when
  implementing or designing security-sensitive features, e.g. "how should I store
  passwords", "secure this API endpoint", "implement OAuth/session auth", "what
  are the top risks for this web app", "harden this upload handler". For AUDITING
  existing code to find vulnerabilities use the bs-dev-audit skill (security
  dimension); for hardening AI/LLM/agent code against prompt injection and tool
  abuse use the bs-ai-harden skill.
---

# Security

Writing secure code and designing secure systems. Each area has a focused
reference; load only what the task needs.

## References

| When | Read |
|---|---|
| Writing secure backend or frontend code (input handling, injection, output encoding) | `references/secure-coding.md` |
| Securing an API, and authentication/authorization patterns | `references/api-and-auth.md` |
| Threat reference: OWASP-style web vulnerabilities and how to scan for them | `references/threats.md` |

## Boundaries

- Auditing existing code to find vulnerabilities → **bs-dev-audit** skill (security dimension).
- Hardening AI/LLM/agent code against attacks → **bs-ai-harden** skill.
