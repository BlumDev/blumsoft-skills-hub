# Web vulnerabilities & threat reference

A consolidated reference for security review: the auditor mindset, a catalog of common web vulnerabilities, and how to scan for them. Think like an attacker, defend like an expert.

## Auditor mindset

Apply these principles to every system you review.

| Principle | Application |
|-----------|-------------|
| Assume breach | Design as if the attacker is already inside |
| Zero trust | Never trust, always verify |
| Defense in depth | Multiple layers, no single point of failure |
| Least privilege | Minimum required access only |
| Fail secure | On error, deny access (never fail open) |

Never trust user input; validate everything at multiple layers. Fail securely without information leakage. Prefer practical, actionable fixes over theoretical risk. Shift security left (early in the SDLC) and favor automation and continuous monitoring. Weigh business risk and impact in every decision.

### Threat modeling

Before scanning, answer:
1. What are we protecting? (Assets: secrets, PII, business data)
2. Who would attack? (Threat actors)
3. How would they attack? (Attack vectors)
4. What is the impact? (Business risk)

Use STRIDE, PASTA, or attack trees. Map entry points (APIs, forms, file uploads), data flows (input -> process -> output), trust boundaries (where auth/authz is enforced), and high-value assets.

### When to engage

Use this reference for security audits, SDLC/CI-CD control reviews, vulnerability investigation, and validation of authentication, authorization, and data-protection controls. Do not run intrusive tests in production without written approval, and do not treat this as a substitute for legal counsel or formal compliance certification.

---

## Vulnerability catalog

Organized by category. Each entry: definition, root cause, impact, mitigation.

### Injection

**SQL Injection** — Malicious SQL inserted into inputs to manipulate queries. Cause: no input validation, unparameterized queries. Impact: unauthorized data access/manipulation, DB compromise. Fix: parameterized queries/prepared statements, input validation, least-privilege DB accounts.

**Cross-Site Scripting (XSS)** — Malicious scripts injected into pages viewed by other users. Cause: insufficient output encoding, no input sanitization. Impact: session hijacking, credential theft, defacement. Fix: output encoding, CSP, input sanitization. (DOM-based XSS: unsafe client-side DOM manipulation with user input; fix with safe DOM APIs and CSP.)

**Command Injection** — Arbitrary OS commands executed via the app. Cause: unsanitized input passed to a shell. Impact: full system compromise, exfiltration, lateral movement. Fix: avoid shell execution, whitelist commands, strict validation.

**XML / LDAP / XPath Injection** — Query manipulation via malicious input. Cause: improper input handling in query construction. Impact: data exposure, auth bypass, information disclosure. Fix: input validation, parameterized queries, escape special characters.

**Server-Side Template Injection (SSTI)** — Malicious code injected into template engines. Cause: user input embedded in template expressions. Impact: RCE, server compromise. Fix: sandbox template engines, keep user input out of templates.

### Authentication & session

**Session Fixation** — Attacker sets the victim's session ID before login. Cause: session ID not regenerated after auth. Fix: regenerate session ID on authentication.

**Brute Force** — Automated password guessing. Cause: no lockout, rate limiting, or CAPTCHA. Fix: account lockout, rate limiting, MFA, CAPTCHA.

**Session Hijacking** — Stealing or predicting valid session tokens. Cause: weak token generation, insecure transmission. Fix: secure random tokens, HTTPS, HttpOnly/Secure cookie flags.

**Credential Stuffing** — Leaked credentials reused across services. Cause: password reuse, no breach detection. Fix: MFA, breach-password checks, unique-credential requirements.

**Insecure "Remember Me"** — Weak persistent auth tokens. Fix: strong token generation, proper expiration, secure storage.

**CAPTCHA Bypass** — Circumventing bot detection. Fix: reCAPTCHA v3, layered bot detection, rate limiting.

**Account Enumeration** — Different responses reveal valid accounts. Fix: uniform responses and timing.

### Sensitive data exposure

**IDOR (Insecure Direct Object References)** — Direct access to internal objects via user-supplied references. Cause: missing authorization checks on object access. Fix: access-control validation, indirect reference maps.

**Data Leakage** — Inadvertent disclosure of sensitive data. Fix: DLP, encryption, access controls.

**Unencrypted Data Storage** — Sensitive data stored without encryption. Fix: full-disk/database encryption, secure key management.

**Information Disclosure** — System details leaked via errors/responses. Cause: verbose errors, debug in production. Fix: generic error messages, disable debug, secure logging.

### Security misconfiguration

**Missing Security Headers** — Absent protective HTTP headers. Impact: XSS, clickjacking, protocol downgrade. Fix: implement CSP, X-Content-Type-Options, X-Frame-Options, HSTS.

**Default Passwords** — Unchanged vendor defaults. Fix: mandatory password changes, strong policies.

**Directory Listing** — Server exposes directory contents. Fix: disable indexing, use default index files.

**Unprotected API Endpoints** — APIs without auth/authz. Fix: OAuth/API keys, access controls, rate limiting.

**Open Ports and Services** — Unnecessary services exposed. Fix: port audits, firewall rules, service minimization.

**Misconfigured CORS** — Overly permissive cross-origin policies (wildcard origins). Fix: whitelist trusted origins, validate CORS headers.

**Unpatched Software** — Outdated, vulnerable software. Fix: patch management, vulnerability scanning, automated updates.

### XML processing

**XXE (XML External Entity)** — Parser abused to access files or internal systems. Cause: external entity processing enabled. Impact: file disclosure, SSRF, DoS. Fix: disable external entities, use safe parsers.

**Entity Expansion / XML Bomb (Billion Laughs)** — Nested/recursive entities exhaust resources. Fix: limit entity expansion, restrict input size, schema validation, processing timeouts.

### Broken access control

**Inadequate Authorization** — Access controls not properly enforced. Fix: RBAC, centralized IAM, regular access reviews.

**Privilege Escalation** — Gaining access beyond intended permissions. Fix: least privilege, patching, privilege monitoring.

**Forceful Browsing** — URL manipulation to reach restricted resources. Fix: server-side access controls, unpredictable resource paths.

**Missing Function-Level Access Control** — Privileged functions protected only at the UI. Fix: server-side authorization for all functions, RBAC.

### Insecure deserialization

**RCE via Deserialization** — Code execution through malicious serialized objects. Cause: untrusted data deserialized without validation. Fix: avoid deserializing untrusted data, integrity checks, type validation/whitelisting.

**Data Tampering** — Unauthorized modification of serialized data. Fix: digital signatures, HMAC, encryption.

**Object Injection** — Malicious object instantiation during deserialization. Fix: type restrictions, class whitelisting, secure libraries.

### API security

**Insecure API Endpoints** — APIs without proper controls. Fix: OAuth/JWT, HTTPS, input validation, rate limiting.

**API Key Exposure** — Leaked credentials (hardcoded keys, insecure storage). Fix: secure storage, rotation, environment variables.

**Lack of Rate Limiting** — No throttling on request frequency. Impact: DoS, abuse, resource exhaustion. Fix: per-user/IP limits, throttling, DDoS protection.

**Inadequate Input Validation** — APIs accept unvalidated input. Fix: strict validation, parameterized queries, WAF.

**API Abuse** — Exploiting API functionality maliciously. Fix: strong auth, behavior/anomaly analysis.

### Communication security

**Man-in-the-Middle** — Interception of communication. Cause: unencrypted channels. Fix: TLS/SSL, certificate pinning, mutual auth.

**Weak Transport Layer Security** — Outdated protocols (SSLv2/3), weak ciphers. Fix: TLS 1.2+, strong cipher suites, HSTS, forward secrecy, certificate validation.

**Insecure Protocols** — Unencrypted HTTP, Telnet, FTP. Fix: HTTPS, SSH, SFTP, VPN tunnels.

### Client-side

**Insecure Cross-Origin Communication** — Relaxed CORS/SOP. Fix: strict CORS, CSRF tokens, origin validation.

**Browser Cache Poisoning** — Manipulation of cached content. Fix: Cache-Control headers, HTTPS, integrity checks.

**Clickjacking** — UI redress tricking users into clicking hidden elements. Fix: X-Frame-Options, CSP frame-ancestors, frame-busting.

**HTML5 API Issues** — Insecure use of WebSockets, Storage, Geolocation. Fix: secure API usage, input validation, sandboxing.

**MIME Sniffing** — Content-type confusion. Fix: X-Content-Type-Options: nosniff.

**CSP Bypass** — Weak CSP config defeated. Fix: strict CSP, nonces.

### Denial of service

**DDoS** — Traffic flood from many sources. Fix: DDoS protection services, rate limiting, CDN.

**Application-Layer DoS** — Targeting app logic to exhaust resources. Fix: rate limiting, caching, WAF, code optimization.

**Resource Exhaustion** — Depleting CPU/memory/disk/network. Fix: resource quotas, monitoring, load balancing.

**Slowloris** — Partial HTTP requests hold connections open. Fix: connection timeouts, request limits, reverse proxy.

### SSRF

**Server-Side Request Forgery** — Server manipulated into requesting internal resources. Cause: unvalidated user-controlled URLs. Impact: internal network access, data theft, cloud metadata access. Fix: URL whitelisting, network segmentation, egress filtering.

**Blind / Time-Based Blind SSRF** — No direct response; success inferred out-of-band or via timing. Fix: allowlists, WAF, network restrictions, request timeouts, anomaly detection.

### Other notable

| Vulnerability | Root cause | Fix |
|---|---|---|
| HTTP Parameter Pollution | Inconsistent parsing | Strict parsing, validation |
| Insecure Redirects | Unvalidated targets | Whitelist destinations |
| File Inclusion (LFI/RFI) | Unvalidated paths | Whitelist files, disable RFI |
| Inadequate Session Timeout | Excessive timeouts | Idle termination, timeouts |
| Insufficient Logging | Missing infrastructure | SIEM, alerting |
| Business Logic Flaws | Insecure design, missing server-side validation | Threat modeling, abuse-case testing, server-side validation |
| Race Conditions | Missing synchronization | Proper locking |

### Mobile & IoT

| Vulnerability | Root cause | Fix |
|---|---|---|
| Insecure Mobile Storage | Plaintext, weak crypto | Keychain/Keystore, encrypt |
| Insecure Mobile Transmission | HTTP, cert failures | TLS, cert pinning |
| Insecure Mobile APIs | Missing auth/validation | OAuth/JWT, validation |
| App Reverse Engineering | Hardcoded creds | Obfuscation, RASP |
| Weak IoT Auth / Defaults | Default passwords, no TLS | Unique creds, MFA, TLS |
| IoT Firmware Flaws | Old firmware, design flaws | Updates, segmentation |
| IoT Privacy | Excessive collection | Data minimization |

---

## OWASP Top 10 (2025, draft — not final)

> Note: the 2025 list is a release candidate; ordering and categories may still shift before release. The 2021 Top 10 remains the stable reference. Treat the table below as illustrative of the expected direction, not canonical.

| Rank | Category | Focus |
|------|----------|-------|
| A01 | Broken Access Control | IDOR, SSRF (now merged here), who can access what |
| A02 | Security Misconfiguration | Defaults, headers, exposed services, cloud/container configs |
| A03 | Software Supply Chain (new) | Dependencies, CI/CD, build integrity |
| A04 | Cryptographic Failures | Weak crypto, exposed secrets |
| A05 | Injection | User input reaching system commands/queries |
| A06 | Insecure Design | Flawed architecture |
| A07 | Authentication Failures | Session and credential management |
| A08 | Integrity Failures | Unsigned updates, tampered/deserialized data |
| A09 | Logging & Alerting Failures | Blind spots, no monitoring |
| A10 | Exceptional Conditions (new) | Error handling, fail-open states |

Key 2025 shifts: SSRF folded into A01; A02 elevated for cloud/container; A03 supply chain is new and a major focus; A10 exceptional conditions is new; emphasis moves from symptoms to root causes.

---

## Supply chain security (A03)

| Vector | Risk | Question |
|--------|------|----------|
| Dependencies | Malicious packages | Do we audit new deps? |
| Lock files | Integrity attacks | Are they committed? |
| Build pipeline | CI/CD compromise | Who can modify it? |
| Registry | Typosquatting | Verified sources? |

Verify package integrity (checksums), pin versions, audit updates, use private registries for critical deps, sign and verify artifacts.

---

## Exceptional conditions (A10)

Fail closed, not open.

| Scenario | Fail-open (bad) | Fail-closed (good) |
|----------|-----------------|--------------------|
| Auth error | Allow access | Deny access |
| Parsing fails | Accept input | Reject input |
| Timeout | Retry forever | Limit and abort |

Check for: catch-all handlers that swallow errors, missing error handling on security operations, race conditions in auth/authz, resource-exhaustion scenarios.

---

## How to scan

### Methodology

1. **Reconnaissance** — Understand the target: tech stack, entry points, data flows.
2. **Discovery** — Identify potential issues: config review, dependency analysis, code-pattern search.
3. **Analysis** — Validate and prioritize: eliminate false positives, score risk, map attack chains.
4. **Reporting** — Deliver actionable findings: reproduction steps, business impact, remediation.

Use SAST (Semgrep, CodeQL, SonarQube), DAST (OWASP ZAP, Burp Suite), dependency scanning (Snyk, OWASP Dependency-Check), and container/infra scanning. Automated scanners miss business-logic flaws; cover those with manual testing and abuse-case analysis.

### High-risk code patterns

| Pattern | Risk | Look for |
|---------|------|----------|
| String concat in queries | Injection | `"SELECT * FROM " + user_input` |
| Dynamic code execution | RCE | `eval()`, `exec()`, `Function()` |
| Unsafe deserialization | RCE | `pickle.loads()`, `unserialize()` |
| Path manipulation | Traversal | User input in file paths |
| Disabled security | Various | `verify=False`, `--insecure` |

### Secret patterns

| Type | Indicators |
|------|------------|
| API keys | `api_key`, `apikey`, high entropy |
| Tokens | `token`, `bearer`, `jwt` |
| Credentials | `password`, `secret`, `key` |
| Cloud | `AWS_`, `AZURE_`, `GCP_` prefixes |

### Cloud checks

Shared responsibility: you own data and application security; the provider owns infrastructure; OS/runtime depends on the service model. Check: IAM least privilege, public storage buckets, tightened security groups, secrets in a secrets manager (not code).

### Verification techniques

| Vulnerability | Verification |
|---------------|--------------|
| Injection | Payload testing with encoded variants |
| XSS | Alert boxes, cookie access, DOM inspection |
| CSRF | Cross-origin form submission |
| SSRF | Out-of-band DNS/HTTP callbacks |
| XXE | External entity to a controlled server |
| Access control | Horizontal/vertical privilege testing |
| Authentication | Credential rotation, session analysis |

---

## Risk prioritization

Risk = Likelihood x Impact. Combine CVSS (base severity) with EPSS (exploit likelihood), asset value, and exposure (internet-facing?).

Decision flow:
- Actively exploited (EPSS > 0.5)? -> **Critical**, immediate action.
- Else CVSS >= 9.0 -> **High**.
- CVSS 7.0-8.9 -> weigh asset value.
- CVSS < 7.0 -> schedule for later.

### Severity classification

| Severity | Criteria |
|----------|----------|
| Critical | RCE, auth bypass, mass data exposure |
| High | Data exposure, privilege escalation |
| Medium | Limited scope, requires conditions |
| Low | Informational, best practice |

---

## Reporting

Every finding answers: **What?** (clear description) **Where?** (file, line, endpoint) **Why?** (root cause) **Impact?** (business consequence) **How to fix?** (specific remediation).

### Anti-patterns

| Do not | Do |
|--------|----|
| Scan without understanding | Map the attack surface first |
| Alert on every CVE | Prioritize by exploitability + asset value |
| Ignore false positives | Maintain a verified baseline |
| Fix symptoms only | Address root causes |
| Scan once before deploy | Scan continuously |
| Trust third-party deps blindly | Verify integrity, audit code |

---

## Critical security headers

```
Content-Security-Policy: default-src 'self'; script-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=()
```

---

## References

- OWASP Top 10, Testing Guide, ASVS
- CWE/SANS Top 25
- NIST Cybersecurity Framework
