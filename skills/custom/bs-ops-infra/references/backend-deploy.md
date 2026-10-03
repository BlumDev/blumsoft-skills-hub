# Backend & deployment

## Backend priorities

1. Data model and contracts first
2. AuthN/AuthZ and validation everywhere
3. Consistent error contracts
4. N+1 avoidance and transactional integrity
5. Operational scalability and observability

## Deployment procedures

Learn to think, not memorize scripts. Every deployment is unique; understand the WHY and adapt to your platform.

### Platform selection

| What you deploy | Target |
|-----------------|--------|
| Static site / JAMstack | Vercel, Netlify, Cloudflare Pages |
| Simple web app (managed) | Railway, Render, Fly.io |
| Simple web app (control) | VPS + PM2/Docker |
| Microservices | Container orchestration |
| Serverless | Edge functions, Lambda |

### Pre-deployment checklist

- [ ] All tests passing, code reviewed and approved
- [ ] Production build successful, no warnings
- [ ] Environment variables verified, secrets current
- [ ] Database migrations ready (if any)
- [ ] Backup done, rollback plan documented
- [ ] Team notified, monitoring ready

### Deployment workflow (5 phases)

1. **Prepare**, verify code, build, env vars. Never deploy untested code.
2. **Backup**, save current state. You can't rollback without it.
3. **Deploy**, execute with monitoring open. Don't walk away.
4. **Verify**, health check, logs, key flows. Trust but verify.
5. **Confirm or rollback**, all good? Confirm. Issues? Rollback.

### Post-deployment verification

Check the health endpoint (service running), error logs (no new errors), key user flows (critical features work), and performance (response times acceptable).

Window: active monitoring first 5 minutes, confirm stable at 15 minutes, final verification at 1 hour, review metrics next day.

### Rollback

| Symptom | Action |
|---------|--------|
| Service down | Rollback immediately |
| Critical errors | Rollback |
| Performance >50% degraded | Consider rollback |
| Minor issues | Fix forward if quick |

| Platform | Rollback method |
|----------|-----------------|
| Vercel/Netlify | Redeploy previous commit |
| Railway/Render | Rollback in dashboard |
| VPS + PM2 | Restore backup, restart |
| Docker | Previous image tag |
| K8s | kubectl rollout undo |

Principles: rollback first and debug later; one rollback, not multiple changes; communicate to the team; post-mortem once stable.

### Zero-downtime strategies

- **Rolling** (replace instances one by one), standard release
- **Blue-green** (switch traffic between environments), high-risk change, easy rollback
- **Canary** (gradual traffic shift), when you need validation with real traffic

### Emergency procedures

When a service is down: assess the symptom, restart if unclear, rollback if restart doesn't help, investigate after stable. Investigation order: logs (errors, exceptions), resources (disk, memory), network (DNS, firewall), dependencies (database, APIs).

### Anti-patterns

| Don't | Do |
|-------|-----|
| Deploy on Friday | Deploy early in week |
| Rush deployment | Follow the process |
| Skip staging | Always test first |
| Deploy without backup | Backup before deploy |
| Walk away after deploy | Monitor 15+ min |
| Multiple changes at once | One change at a time |

### Best practices

Prefer small, frequent deploys over big releases. Use feature flags for risky changes, automate repetitive steps, document every deployment, review what went wrong after issues, and test rollback before you need it.

> Every deployment is a risk. Minimize risk through preparation, not speed.
