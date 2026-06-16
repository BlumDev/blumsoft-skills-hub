# Dimension: security

Find places where untrusted input reaches a sensitive operation. This is
**defensive** review of existing code — spotting weaknesses so they can be closed,
not building attacks.

**A security fix usually changes behavior on malicious/invalid input — that is the
point, but it means these are not pure refactorings.** Report them by default;
apply only with explicit approval; keep valid-input behavior identical. Flag, do
not "fix and hope".

Trace untrusted input (request params, headers, file contents, env, CLI args,
DB rows, LLM output, anything crossing a trust boundary) to where it is used:

- **Injection.** User data concatenated into a SQL query, shell command, HTML, a
  template, an `eval`/`exec`, a file path, an LDAP/NoSQL filter, or a log line.
  Fix: parameterized queries / prepared statements; `subprocess` with an arg list
  (never `shell=True` on user data); contextual output encoding; allowlists.
- **Path traversal & file access.** A filename/path from input used to read/write
  without normalizing and confining to an allowed root (`../../etc/passwd`). Fix:
  resolve, then verify the result stays under the intended directory.
- **SSRF & unsafe outbound requests.** A URL/host from input fetched server-side,
  letting it reach internal services or metadata endpoints. Fix: allowlist hosts/
  schemes; block private/link-local ranges.
- **Unsafe deserialization.** `pickle`, `yaml.load` (non-safe), Java/`.NET`
  deserializers, or `eval`-based parsing on untrusted bytes → remote code
  execution. Fix: safe loaders (`yaml.safe_load`, JSON), schema validation.
- **AuthZ/AuthN gaps.** An endpoint/action missing an ownership or role check
  (IDOR: acting on `id` from the request without verifying the caller owns it);
  trusting a client-supplied role/flag; auth check that can be bypassed by an
  alternate path. Fix: enforce server-side, per request, closest to the resource.
- **Secrets.** Hard-coded keys/passwords/tokens; secrets logged or in error
  messages; credentials in source/config committed to the repo. Fix: move to env/
  secret store, reference by name, scrub from logs. (Report the leak — do not print
  the secret value in the finding.)
- **Crypto misuse.** Home-rolled crypto; weak/Broken primitives (MD5/SHA1 for
  passwords, ECB, static IVs); plaintext password storage; `==` comparison of
  secrets (timing). Fix: vetted libraries; a password hash (bcrypt/argon2);
  constant-time compares.
- **Sensitive data exposure.** PII/tokens in logs, error responses, or analytics;
  verbose stack traces returned to clients. Fix: redact, generic error to caller,
  detail to server logs only.
- **Missing limits.** No size/rate cap on uploads, request bodies, or expansions
  (zip-bomb, billion-laughs) → resource exhaustion. Fix: bound inputs.

Why it matters: one reachable injection or missing authz check is worth more
attention than any number of style issues — it is a breach, not a blemish.

For each finding state: the **source** of untrusted input, the **sink** it reaches,
the **impact** if exploited, and the concrete fix. Rank by reachability and blast
radius. If you cannot confirm the input is actually attacker-controlled, say so —
mark it "needs confirmation" rather than crying wolf.

**Scope note:** if the code is AI/LLM/agent code, the LLM-specific attack surface
(prompt injection, tool abuse, insecure model-output handling) is **not** covered
here — point the user at the **ai-hardening** skill.
