# API security & auth

Guide for building secure APIs (REST, GraphQL, WebSocket) and implementing authentication/authorization. Covers input validation, rate limiting, data protection, then JWT, sessions, OAuth2, and access control.

## When to use

- Designing or securing API endpoints.
- Implementing authentication (session, JWT, OAuth2/OIDC, SSO) or authorization (RBAC, permissions, ownership).
- Hardening against injection, DDoS, and the OWASP API Top 10.
- Debugging auth issues or preparing for a security audit.

---

# Part 1: API security

## Input validation & injection prevention

Never trust user input. Validate type, range, and format; use allowlists, not blocklists.

### Use parameterized queries (never string concatenation)

```javascript
// VULNERABLE - SQL injection
const query = `SELECT * FROM users WHERE id = '${userId}'`;
// Attack: GET /api/users/1' OR '1'='1  -> returns all users

// SAFE - parameterized
if (!/^\d+$/.test(userId)) {
  return res.status(400).json({ error: 'Invalid user ID' });
}
const user = await db.query(
  'SELECT id, email, name FROM users WHERE id = $1',
  [userId]
);
```

Or use an ORM with proper escaping (Prisma `findUnique`, etc.) and `select` only non-sensitive fields.

### Validate request bodies with a schema

```javascript
const { z } = require('zod');

const createUserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
    .regex(/[A-Z]/).regex(/[a-z]/).regex(/[0-9]/),
  name: z.string().min(2).max(100),
  age: z.number().int().min(18).max(120).optional()
});

function validateRequest(schema) {
  return (req, res, next) => {
    try {
      schema.parse(req.body);
      next();
    } catch (error) {
      res.status(400).json({ error: 'Validation failed', details: error.errors });
    }
  };
}

app.post('/api/users', validateRequest(createUserSchema), handler);
```

### Sanitize output to prevent XSS

```javascript
const DOMPurify = require('isomorphic-dompurify');

const sanitizedContent = DOMPurify.sanitize(content, {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
  ALLOWED_ATTR: ['href']
});
```

Validation checklist: validate all inputs; parameterized queries or ORM; check data types and ranges; sanitize HTML; validate file uploads (type, size, content); use allowlists.

## Rate limiting & DDoS protection

Rate limiting blocks brute force, throttles abuse, and reduces cost. Use a distributed store (Redis) so limits hold across instances. Apply stricter limits to auth endpoints.

```javascript
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const redis = new Redis({ host: process.env.REDIS_HOST, port: process.env.REDIS_PORT });

// General API limit
const apiLimiter = rateLimit({
  store: new RedisStore({ client: redis, prefix: 'rl:api:' }),
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.user?.userId || req.ip
});

// Strict limit for auth endpoints
const authLimiter = rateLimit({
  store: new RedisStore({ client: redis, prefix: 'rl:auth:' }),
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true
});

app.use('/api/', apiLimiter);
app.use('/api/auth/login', authLimiter);
app.use('/api/auth/register', authLimiter);
```

Return standard headers so clients can back off:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1640000000
Retry-After: 900
```

For tiered limits, key by user and vary `max` by plan (free/pro/enterprise), tracking counts with `redis.incr` + `redis.expire` and returning `429` with limit metadata when exceeded.

## Data protection & secure headers

- Use HTTPS/TLS for all traffic; encrypt sensitive data at rest.
- Never store sensitive data in a JWT payload (JWTs are signed, not encrypted).
- Configure CORS to allow only trusted origins.
- Set security headers via Helmet (CSP, `frameguard: deny`, `hidePoweredBy`, `noSniff`, HSTS with `maxAge`, `includeSubDomains`, `preload`).

## Error handling

Log the full error server-side; return a generic message to the client. Map known errors to safe responses.

```javascript
// BAD - leaks DB details: "Unique constraint failed on (`email`)"
res.status(500).json({ error: error.message });

// GOOD
console.error('User creation error:', error);
if (error.code === 'P2002') {
  return res.status(400).json({ error: 'Email already exists' });
}
res.status(500).json({ error: 'An error occurred while creating user' });
```

## OWASP API Security Top 10

1. Broken Object Level Authorization - verify the user can access the specific resource.
2. Broken Authentication - use strong, standard auth mechanisms.
3. Broken Object Property Level Authorization - control which properties a user can read/write.
4. Unrestricted Resource Consumption - rate limit and set quotas.
5. Broken Function Level Authorization - check role/permission per function.
6. Unrestricted Access to Sensitive Business Flows - protect critical workflows.
7. Server Side Request Forgery (SSRF) - validate and sanitize outbound URLs.
8. Security Misconfiguration - apply hardening and security headers.
9. Improper Inventory Management - document and secure every endpoint.
10. Unsafe Consumption of APIs - validate data from third-party APIs.

---

# Part 2: Authentication & authorization

**Authentication (AuthN)**: who are you (verify identity, issue credentials, manage login/logout). **Authorization (AuthZ)**: what can you do (permission checks, RBAC, ownership, policy).

Choose a strategy by context:
- **Session-based**: server stores state, session ID in cookie. Simple, stateful, easy revocation.
- **Token-based (JWT)**: stateless, self-contained, scales horizontally.
- **OAuth2/OpenID Connect**: delegated auth, social login, enterprise SSO.

Design steps: define users/tenants/flows and the threat model; pick auth strategy and token lifecycle; design the authorization model and enforcement points; plan secrets storage, rotation, logging, and audit.

## Password security

Hash with bcrypt (salt rounds >= 12) or argon2; never store plaintext. Enforce a strong policy.

```typescript
import bcrypt from 'bcrypt';
import { z } from 'zod';

const passwordSchema = z.string()
  .min(12)
  .regex(/[A-Z]/).regex(/[a-z]/).regex(/[0-9]/).regex(/[^A-Za-z0-9]/);

async function hashPassword(password: string) {
  return bcrypt.hash(password, 12);
}
async function verifyPassword(password: string, hash: string) {
  return bcrypt.compare(password, hash);
}
```

On login failure, return a generic "Invalid credentials" - never reveal whether the user exists.

## JWT authentication

Structure: `header.payload.signature`. Issue a short-lived access token and a long-lived refresh token.

```typescript
import jwt from 'jsonwebtoken';

function generateTokens(userId: string, email: string, role: string) {
  const accessToken = jwt.sign(
    { userId, email, role },
    process.env.JWT_SECRET!,
    { expiresIn: '15m', issuer: 'your-app', audience: 'your-app-users' }
  );
  const refreshToken = jwt.sign(
    { userId },
    process.env.JWT_REFRESH_SECRET!,
    { expiresIn: '7d' }
  );
  return { accessToken, refreshToken };
}

// Middleware: verify access token, attach user
function authenticate(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }
  try {
    req.user = jwt.verify(authHeader.substring(7), process.env.JWT_SECRET!, {
      issuer: 'your-app', audience: 'your-app-users'
    });
    next();
  } catch (err) {
    const expired = err.name === 'TokenExpiredError';
    return res.status(401).json({ error: expired ? 'Token expired' : 'Invalid token' });
  }
}
```

### Refresh token flow

Store refresh tokens **hashed** in the database so they can be verified and revoked. Verify the JWT signature, confirm the hashed token exists and is unexpired, then issue a new access token.

```typescript
class RefreshTokenService {
  async storeRefreshToken(userId: string, refreshToken: string) {
    await db.refreshTokens.create({
      token: await hash(refreshToken),  // hash before storing
      userId,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    });
  }

  async refreshAccessToken(refreshToken: string) {
    let payload;
    try {
      payload = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET!) as { userId: string };
    } catch {
      throw new Error('Invalid refresh token');
    }
    const stored = await db.refreshTokens.findOne({
      where: { token: await hash(refreshToken), userId: payload.userId, expiresAt: { $gt: new Date() } },
    });
    if (!stored) throw new Error('Refresh token not found or expired');

    const user = await db.users.findById(payload.userId);
    if (!user) throw new Error('User not found');

    const accessToken = jwt.sign(
      { userId: user.id, email: user.email, role: user.role },
      process.env.JWT_SECRET!, { expiresIn: '15m' }
    );
    return { accessToken };
  }

  async revokeRefreshToken(refreshToken: string) {
    await db.refreshTokens.deleteOne({ token: await hash(refreshToken) });
  }
  async revokeAllUserTokens(userId: string) {
    await db.refreshTokens.deleteMany({ userId });  // logout all devices
  }
}
```

JWT rules: use a strong secret (256-bit min) from env, never hardcoded; validate issuer and audience; keep no sensitive data in the payload; blacklist or revoke on logout. Store tokens in httpOnly cookies, not localStorage (XSS-exposed).

## Session-based authentication

Use a shared store (Redis) and secure cookie flags. Destroy the session and clear the cookie on logout.

```typescript
import session from 'express-session';
import RedisStore from 'connect-redis';

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',  // HTTPS only
    httpOnly: true,                                  // no JS access
    maxAge: 24 * 60 * 60 * 1000,
    sameSite: 'strict',                              // CSRF protection
  },
}));

function requireAuth(req, res, next) {
  if (!req.session.userId) return res.status(401).json({ error: 'Not authenticated' });
  next();
}
```

Session-based auth needs explicit CSRF protection (`sameSite` plus CSRF tokens for state-changing requests).

## OAuth2 / social login

Delegate authentication to a provider (Passport.js). Find-or-create the local user from the profile, then issue your own tokens.

```typescript
import passport from 'passport';
import { Strategy as GoogleStrategy } from 'passport-google-oauth20';

passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID!,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
  callbackURL: '/api/auth/google/callback',
}, async (accessToken, refreshToken, profile, done) => {
  try {
    let user = await db.users.findOne({ googleId: profile.id });
    if (!user) {
      user = await db.users.create({
        googleId: profile.id,
        email: profile.emails?.[0]?.value,
        name: profile.displayName,
      });
    }
    return done(null, user);
  } catch (error) {
    return done(error, undefined);
  }
}));

app.get('/api/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));
app.get('/api/auth/google/callback',
  passport.authenticate('google', { session: false }),
  (req, res) => {
    const tokens = generateTokens(req.user.id, req.user.email, req.user.role);
    res.redirect(`${process.env.FRONTEND_URL}/auth/callback?token=${tokens.accessToken}`);
  }
);
```

## Authorization patterns

Always enforce authorization server-side, after authentication. Authentication alone is not authorization.

### Role-based access control (RBAC)

```typescript
enum Role { USER = 'user', MODERATOR = 'moderator', ADMIN = 'admin' }

const roleHierarchy: Record<Role, Role[]> = {
  [Role.ADMIN]: [Role.ADMIN, Role.MODERATOR, Role.USER],
  [Role.MODERATOR]: [Role.MODERATOR, Role.USER],
  [Role.USER]: [Role.USER],
};
const hasRole = (userRole: Role, required: Role) => roleHierarchy[userRole].includes(required);

function requireRole(...roles: Role[]) {
  return (req, res, next) => {
    if (!req.user) return res.status(401).json({ error: 'Not authenticated' });
    if (!roles.some(r => hasRole(req.user.role, r)))
      return res.status(403).json({ error: 'Insufficient permissions' });
    next();
  };
}

app.delete('/api/users/:id', authenticate, requireRole(Role.ADMIN), handler);
```

### Permission-based access control

Map roles to fine-grained permissions (e.g. `read:users`, `write:posts`) and check that the user holds all required permissions. More granular than role checks; preferred when roles alone are too coarse.

### Resource ownership

For per-record access, verify the requesting user owns the resource (admins bypass). Return `404` if missing, `403` if not owner.

```typescript
function requireOwnership(resourceType: 'post' | 'comment', idParam = 'id') {
  return async (req, res, next) => {
    if (!req.user) return res.status(401).json({ error: 'Not authenticated' });
    if (req.user.role === Role.ADMIN) return next();

    const resource = resourceType === 'post'
      ? await db.posts.findById(req.params[idParam])
      : await db.comments.findById(req.params[idParam]);
    if (!resource) return res.status(404).json({ error: 'Resource not found' });
    if (resource.userId !== req.user.userId)
      return res.status(403).json({ error: 'Not authorized' });
    next();
  };
}

app.put('/api/posts/:id', authenticate, requireOwnership('post'), handler);
```

---

# Quick reference

**Do:**
- HTTPS everywhere; require auth on protected endpoints.
- Validate and sanitize all input; parameterized queries or ORM.
- Hash passwords (bcrypt rounds >= 12); store refresh tokens hashed.
- Short-lived access tokens (15-30 min) plus revocable refresh tokens.
- Rate limit, with stricter limits on auth endpoints.
- Configure CORS for trusted origins; set security headers (Helmet).
- Use httpOnly + secure + sameSite cookies; rotate secrets.
- Log security events (failed logins, auth failures); add MFA where possible.

**Don't:**
- Store plaintext passwords or weak/hardcoded secrets.
- Trust client-side auth checks or unvalidated client data.
- Put sensitive data in JWT payloads or store tokens in localStorage.
- Expose stack traces or DB errors to clients.
- Build SQL by string concatenation; disable CORS wholesale.
- Skip token expiration, rate limiting, or server-side validation.
- Log secrets, tokens, or credentials.

**Common pitfalls:** JWT secret committed to Git (use `process.env`, fail fast if unset); weak password policy (enforce length + complexity or a strength library); missing authorization checks (verify ownership/role per request); insecure password reset (use secure, expiring tokens); no CSRF protection on session auth.
