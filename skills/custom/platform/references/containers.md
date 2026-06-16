# Containers (Docker)

Apply container optimization, security hardening, multi-stage builds, and orchestration based on current best practices. Scope is Docker itself. For Kubernetes, CI/CD pipelines, cloud container services (ECS/Fargate), or complex database persistence, defer to the matching specialist.

## Analyze the setup first

Use Read/Grep/Glob to inspect the project before running shell commands. Locate `Dockerfile*`, `*compose*.yml`/`*compose*.yaml`, and `.dockerignore`. Check the live environment with `docker --version`, `docker info`, `docker ps`, and `docker images` when relevant. Then adapt to what exists: match base images and multi-stage conventions, distinguish dev vs production, and respect any current Compose/Swarm setup.

## Dockerfile optimization & multi-stage builds

- Copy dependency manifests and install before copying source, so layer caching survives source edits.
- Use multi-stage builds to keep the production image small while preserving build flexibility.
- Keep build context lean with a comprehensive `.dockerignore`.
- Choose the base deliberately: Alpine vs distroless vs scratch.
- Consolidate `RUN` commands where it genuinely reduces layers.

```dockerfile
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --production

FROM node:22-alpine AS runtime
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
WORKDIR /app
COPY --from=deps --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=build --chown=nextjs:nodejs /app/dist ./dist
COPY --from=build --chown=nextjs:nodejs /app/package*.json ./
USER nextjs
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
```

### Python track

Same principles apply to Python: install dependencies before copying source, build wheels in a throwaway stage, ship a slim runtime as a non-root user. Set `PYTHONUNBUFFERED=1` so logs stream straight to the container's stdout/stderr (no buffering), and `PYTHONDONTWRITEBYTECODE=1` to skip `.pyc` clutter. The builder compiles dependencies into wheels with `pip wheel`; the runtime installs those prebuilt wheels with no toolchain present. For a FastAPI/ASGI app use a uvicorn-managed gunicorn entrypoint; for Django/WSGI drop the worker class.

```dockerfile
FROM python:3.12-slim AS build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN addgroup --gid 1001 --system appgroup && \
    adduser --uid 1001 --system --ingroup appgroup appuser
WORKDIR /app
COPY --from=build /wheels /wheels
COPY requirements.txt ./
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels
COPY --chown=appuser:appgroup . .
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
# FastAPI / ASGI: gunicorn managing uvicorn workers
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", "--bind", "0.0.0.0:8000"]
# Django / WSGI alternative:
# CMD ["gunicorn", "app.wsgi:application", "--workers", "4", "--bind", "0.0.0.0:8000"]
```

Alternatives to plain `pip`: **uv** (`uv pip install --system -r requirements.txt`, or `uv sync` from `pyproject.toml`/`uv.lock`) is dramatically faster and lock-aware; **Poetry** (`poetry export -f requirements.txt` into the wheel stage, or `poetry install --no-root --only main`) suits projects already standardized on `pyproject.toml`. With either, still split dependency install from source copy to preserve layer caching.

## Security hardening

- Create and run as a non-root user with an explicit UID/GID; add `USER`.
- Manage secrets via Docker secrets or BuildKit build secrets; never bake them into ENV vars or layers.
- Keep base images current and scanned; install only necessary packages to shrink the attack surface.
- Apply runtime constraints: drop capabilities, read-only root filesystem, resource limits.
- Add health checks for monitoring.

```dockerfile
FROM node:22-alpine
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup
WORKDIR /app
COPY --chown=appuser:appgroup package*.json ./
RUN npm ci --only=production
COPY --chown=appuser:appgroup . .
USER 1001
```

## Image size optimization

- Prefer distroless or minimal runtime bases.
- Copy only required artifacts out of build stages; leave build tools behind.
- Clean the package-manager cache in the same `RUN` layer that populates it.

```dockerfile
FROM gcr.io/distroless/nodejs22-debian12
COPY --from=build /app/dist /app
COPY --from=build /app/node_modules /app/node_modules
WORKDIR /app
EXPOSE 3000
CMD ["index.js"]
```

## Docker Compose orchestration

- Define service dependencies with health checks and startup ordering (`depends_on` + `condition: service_healthy`).
- Isolate services with custom networks; mark backend networks `internal`.
- Separate dev/staging/prod configuration; use named volumes for persistence.
- Set resource limits and restart policies for production resilience.

```yaml
services:
  app:
    build:
      context: .
      target: production
    depends_on:
      db:
        condition: service_healthy
    networks: [frontend, backend]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits: { cpus: '0.5', memory: 512M }
        reservations: { cpus: '0.25', memory: 256M }

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB_FILE: /run/secrets/db_name
      POSTGRES_USER_FILE: /run/secrets/db_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets: [db_name, db_user, db_password]
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks: [backend]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  frontend: { driver: bridge }
  backend: { driver: bridge, internal: true }

volumes:
  postgres_data:

secrets:
  db_name: { external: true }
  db_user: { external: true }
  db_password: { external: true }
```

## Development workflow

Use a separate `development` build target. Mount source for hot reload, anonymous-volume the generated dirs (`node_modules`, `dist`), expose debug ports, and override the command.

```yaml
services:
  app:
    build:
      context: .
      target: development
    volumes:
      - .:/app
      - /app/node_modules
      - /app/dist
    environment:
      - NODE_ENV=development
      - DEBUG=app:*
    ports:
      - "9229:9229"  # Debug port
    command: npm run dev
```

## Advanced patterns

Multi-architecture build:

```bash
docker buildx create --name multiarch-builder --use
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest --push .
```

Build cache mount for package managers:

```dockerfile
RUN --mount=type=cache,target=/root/.npm npm ci --only=production
```

BuildKit build-time secret:

```dockerfile
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) && \
    # use API_KEY during build only
```

## Validation

```bash
docker build --no-cache -t test-build . && echo "Build successful"
docker history test-build --no-trunc | head -5
docker scout quickview test-build 2>/dev/null || echo "No Docker Scout"

docker run --rm -d --name validation-test test-build
docker exec validation-test ps aux | head -3   # confirm non-root
docker stop validation-test

docker-compose config && echo "Compose config valid"
```

## Review checklist

- Dependencies copied before source; multi-stage build separates build and runtime.
- Production stage carries only needed artifacts; base image chosen deliberately.
- Non-root user with explicit UID/GID; `USER` set; secrets out of ENV and layers.
- Base images current and scanned; minimal package footprint; health checks present.
- Compose: dependencies gated on health checks, isolated networks (backend internal), resource limits, restart policies.
- Image size: only required files copied, package cache cleaned in-layer, multi-arch considered when needed.
- Dev targets separate from production; ports exposed only as needed.

## Common issues

- **Slow builds / cache misses**: poor layer ordering or large context. Fix with multi-stage builds, `.dockerignore`, dependency cache mounts.
- **Security findings**: outdated bases, hardcoded secrets, root execution. Fix with base updates, secrets management, non-root user.
- **Oversized images (>1GB)**: build tools or junk in the runtime layer. Fix with distroless bases and selective artifact copying.
- **Networking failures**: missing networks, port conflicts, bad service naming. Fix with custom networks and proper service discovery.
- **Broken hot reload**: volume mount or env mismatch. Fix with dev-specific targets and correct volume strategy.
