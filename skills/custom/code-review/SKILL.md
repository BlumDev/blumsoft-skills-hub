---
name: code-review
description: Use for strict code audits focused on security, performance, maintainability, and type safety before merge or release.
---

# Security and QA Code Review

## Mandatory Checks
1. Security: SQLi, XSS, IDOR, secrets, auth bypass
2. Performance: heavy renders, loops, N+1, import bloat
3. Maintainability: long functions, deep nesting, magic numbers, duplication
4. Types/contracts: loose typing and contract drift

## Output Format
- CRITICAL
- WARNING
- REFACTOR
