# Skill eval — answer key (kept OUTSIDE the test repo)

Target repo: D:/Repos/skill-eval-lab  — graded against code-audit + ai-hardening.

## code-audit dimension findings (expected)

### security
- S1 accounts.py:6 — hardcoded secret `ADMIN_TOKEN = "sk_live_..."`.
- S2 accounts.py:12 — SQL injection (string-concatenated email into query).
- S3 accounts.py:17 — command injection (`os.system` with user email).
- S4 accounts.py:25 — weak hash MD5 for passwords.
- S5 accounts.py:27 — SQL injection (f-string UPDATE with email/hash).

### robustness
- R1 accounts.py:10 — `d["email"]`/`d["name"]` assume keys exist → KeyError on missing input (no validation).
- R2 accounts.py:20-21 — bare `except: pass` swallows all errors.
- R3 accounts.py:26-28 — sqlite connection never closed (no `with`/close); resource leak.
- R4 assistant.py:18 — `run_tool` uses `os` without importing it → NameError (also a bug).

### clean-code
- C1 accounts.py:9 — non-speaking names: function `proc`, param `d`.
- C2 accounts.py:9-22 — god function: validates + queries + shells out + mails + swallows errors.
- C3 reports.py — terse names `r`, `s`, `i`, `ln`, `m` (low severity, aggregate).

### performance
- P1 reports.py:4-9 — N+1: one query per id in a loop instead of a batched query.
- P2 reports.py:13-17 — quadratic: `rid in active_list` (list membership) inside a loop → use a set.
- P3 reports.py:22 — regex recompiled every iteration (`re.compile` inside loop).

### reuse
- U1 reports.py:30-40 — `total_eur` and `total_usd` are identical logic (duplication).

### simplicity
- M1 reports.py:43-49 — `FormatterFactory` is over-engineered: factory/strategy for a single format that always returns CsvFormatter.

## ai-hardening findings (expected)

- A1 assistant.py:3 — secret (admin API key) embedded in the system prompt (leakage; assume prompt is extractable).
- A2 assistant.py:7 — prompt injection: untrusted `user_message` concatenated into the instruction channel ("Follow the user's instructions exactly").
- A3 assistant.py:13 — insecure output handling: model output passed to `eval()` → code execution.
- A4 assistant.py:18 — excessive agency: model-controlled string passed to `os.system` with no allowlist / human-in-the-loop.
- A5 assistant.py:22-26 — unbounded consumption: `while True` agent loop with no iteration cap / no max_tokens.

## Grading
- Recall = fraction of the above each skill surfaces.
- Precision = flagged items that are real (penalize invented findings).
- Also note: did the skill load only the relevant dimension references? Did it prioritize (not flood)? Did it correctly mark security/robustness fixes as behavior-changing?
