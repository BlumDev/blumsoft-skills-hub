# Secure coding (backend & frontend)

A defensive secure-coding guide for writing security-first code. Validate inputs, fail securely, apply defense-in-depth, and use secure defaults. Backend practices first, then frontend.

## Backend

### Input validation and injection prevention
- Validate and sanitize all inputs with allowlists; enforce data types, lengths, and formats.
- Use parameterized queries and prepared statements exclusively. Never concatenate user input into SQL, NoSQL, LDAP, or OS commands.
- Configure ORMs securely; parameterize all dynamic query fragments.
- Prevent XXE: disable external entity resolution in XML parsers.
- Enforce payload size limits and content-type validation on every request.

### Output encoding and rendering
- Encode output per context (HTML, JavaScript, CSS, URL).
- Use auto-escaping templates; do not disable escaping.
- Prevent JSON hijacking; format API responses safely.
- Serve files safely: validate content-type, prevent path traversal, restrict download paths.

### Authentication and authorization
- Hash passwords with bcrypt or Argon2 using per-user salts; enforce password policies.
- Implement MFA (TOTP, hardware tokens, backup codes).
- Secure sessions: rotate tokens, invalidate on logout, prevent fixation, enforce timeouts, manage concurrent sessions.
- JWT: verify signatures, validate expiration, reject `alg: none`.
- OAuth 2.0/2.1: use PKCE, validate scopes, secure the authorization-code flow.
- Apply least privilege via RBAC/ABAC and fine-grained, scope-based permissions.

### HTTP security headers and cookies
- Set CSP using nonces or hashes; start in report-only mode, then enforce.
- Set HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy.
- Cookies: HttpOnly, Secure, SameSite; scope to the narrowest domain/path.
- Configure strict, credential-aware CORS; handle preflight correctly. No wildcard with credentials.

### CSRF protection
- Use anti-CSRF tokens (or double-submit cookies) for cookie-based auth on state-changing requests.
- Validate Origin/Referer headers on non-GET requests.
- Enforce SameSite cookies.
- Require authentication for sensitive actions.

### Database security
- Separate DB user privileges; apply role-based access control.
- Encrypt sensitive fields; manage keys properly. Encrypt data in transit and at rest.
- Secure connection credentials and pooling.
- Enable audit logging and change tracking; secure and encrypt backups.

### API security
- Validate every request payload; enforce size and content-type limits.
- Rate-limit with throttling and burst protection (per-user and per-IP).
- Return consistent, security-aware error responses.
- Manage API versions and keys securely.

### External requests (SSRF prevention)
- Allowlist destination URLs and domains; validate and sanitize URLs.
- Restrict protocols; block requests to internal/private networks and metadata endpoints.
- Set request timeouts and response-size limits.
- Validate TLS certificates; consider pinning.

### Error handling, logging, and secrets
- Never leak sensitive data in error messages; fail securely with safe defaults.
- Log authentication events and authorization failures; sanitize logs to prevent injection and exclude sensitive data.
- Maintain tamper-evident audit trails; integrate with SIEM/alerting.
- Store secrets in a vault (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault), not in code; rotate regularly. Never log or commit secrets.
- Keep dependencies updated; monitor for vulnerabilities.

## Frontend

### XSS prevention and output handling
- Prefer `textContent` over `innerHTML` for dynamic content; create/modify elements via safe DOM APIs.
- Sanitize any HTML with an established library (DOMPurify); apply explicit rules for user-generated and rich-text content.
- Encode per context (HTML entities, JS string escaping, URL encoding).
- Use auto-escaping templates; prevent template injection.
- Avoid `document.write`; use modern DOM manipulation instead.

### Content Security Policy
- Configure CSP directives; deploy report-only first, then tighten progressively.
- Restrict scripts with nonce-based, hash-based, or strict-dynamic policies; eliminate inline scripts and inline event handlers.
- Control styles via `style-src` with nonces/hashes; avoid `unsafe-inline`.
- Collect and monitor violation reports.

### Input validation
- Treat client-side validation as UX only; never trust it for security (the server must re-validate).
- Use allowlist validation and predefined value sets.
- Write safe regex; prevent ReDoS.
- Validate file uploads (type, size) and URLs (protocol restrictions, malicious-URL detection).

### CSS handling
- Sanitize dynamic styles; validate CSS properties to prevent style injection.
- Prefer external stylesheets; secure CSS-in-JS.
- Sanitize CSS custom properties used in dynamic theming.
- Apply Subresource Integrity to third-party stylesheets.

### Clickjacking protection
- Set `X-Frame-Options` (DENY/SAMEORIGIN) and CSP `frame-ancestors`.
- Use frame-busting and overlay detection for sensitive operations; apply only in production, relax during iframe-embedded development.
- Require visual confirmation for critical actions.

### Secure redirects and navigation
- Validate redirect targets against an allowlist; prefer identifier-based or fixed-destination mapping over user-supplied URLs.
- Prevent open redirects.
- Validate query parameters and fragments during URL construction.
- Add `rel="noopener noreferrer"` to `target="_blank"` links.
- Validate deep-link/route parameters; prevent path traversal; enforce authorization.

### Authentication and session management (client)
- Store tokens securely; understand localStorage vs sessionStorage trade-offs; handle refresh safely.
- Implement session timeout with activity monitoring and automatic logout.
- Synchronize sessions across tabs via storage events; propagate logout.
- Use WebAuthn/FIDO2 where possible; secure OAuth clients with PKCE and state validation.
- Secure password fields and autocomplete behavior.

### Browser security features
- Apply Subresource Integrity to CDN/third-party resources.
- Adopt Trusted Types to protect DOM sinks.
- Use Feature/Permissions Policy to restrict browser capabilities.
- Enforce HTTPS; prevent mixed content.
- Set Referrer-Policy to limit information leakage.
- Apply Cross-Origin policies (CORP, COEP) for cross-origin isolation.

### Third-party integrations
- Validate third-party scripts; use SRI and CDN fallbacks.
- Sandbox iframes; secure cross-frame communication via validated `postMessage`.
- Minimize analytics data collection; manage consent.
- Protect payment flows: PCI compliance, tokenization, secure form handling.
- Sanitize messages in chat/support widgets.

### Progressive Web App and mobile
- Secure Service Worker caching, updates, and isolation.
- Harden Web App Manifest and deep-link handling.
- Validate push-notification payloads and permissions.
- Secure offline storage and background sync.
- Protect device APIs (geolocation, camera/microphone, sensors) with explicit permissions; disable zoom on sensitive forms.

## Core principles
- Validate inputs with allowlists; maintain a boundary between trusted and untrusted content.
- Apply defense-in-depth and least privilege everywhere.
- Use secure defaults and fail securely.
- Never expose sensitive information in errors, logs, or responses.
- Log security events for detection; keep audit trails.
- Consider security and privacy in every design decision.
