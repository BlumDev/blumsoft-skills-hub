# Infrastructure & ops

Specialist on-demand reference for IaC, Kubernetes, CI pipelines, and incident handling.

## Infrastructure-as-Code (Terraform)

Workflow:
1. Define environments, providers, version constraints, and security constraints.
2. Design composable modules; choose a remote state backend.
3. Run plan/apply with reviews and policy gates.
4. Validate drift, costs, and rollback before applying.

Modules:
- Hierarchical root/child modules; composition over duplication (DRY).
- Use `for_each`, dynamic blocks, conditionals; prefer data sources over hardcoded values.
- Semantic versioning; test with Terratest (unit + integration).
- Validate inputs with variable validation and pre/postconditions.

State & security:
- Remote backends: S3, Azure Storage, GCS, Terraform Cloud, Consul.
- Lock state (DynamoDB, GCS, Redis); encrypt at rest and in transit.
- Treat state as critical infra: automated backups, versioning, point-in-time recovery.
- Mark sensitive variables; never expose secrets in state or output.
- State ops: import, move, remove, refresh for recovery.

Multi-environment:
- Workspaces vs separate backends; isolate state per environment.
- Branch-based GitOps promotion; environment-specific variable overrides.

CI/CD & policy:
- Pipelines: GitHub Actions, GitLab CI, Azure DevOps, Jenkins.
- Policy-as-code: OPA/Sentinel. Security scan: tfsec, Checkov, Terrascan.
- Automated plan validation; manual approval gate before apply.

Rules:
- Always plan before apply; review the diff.
- Pin provider/module versions for reproducibility.
- Drift detection and continuous compliance checks.

## Kubernetes

Workflow:
1. Gather workload requirements, compliance needs, scale targets.
2. Define cluster topology, networking, security boundaries.
3. Choose GitOps tooling and rollout strategy.
4. Validate in staging; define rollback and upgrade plans.

Platform:
- Managed: EKS, AKS, GKE. Self-managed: kubeadm, kops, kubespray.
- Multi-cluster: Cluster API, fleet management, cross-cluster networking.
- Lifecycle: upgrades, node management, etcd backup/restore (Velero).

GitOps (OpenGitOps principles): declarative, versioned/immutable in Git, pulled automatically, continuously reconciled.
- Tools: ArgoCD, Flux v2. Repo patterns: app-of-apps, mono vs multi-repo.
- Progressive delivery: Argo Rollouts, Flagger; canary, blue/green, A/B.
- Secrets: External Secrets Operator, Sealed Secrets, Vault.

Config & IaC:
- Helm, Kustomize overlays, cdk8s; Cluster API for provisioning.
- Policy: OPA/Gatekeeper, Kyverno, Falco, admission controllers.

Security:
- Pod Security Standards (restricted/baseline/privileged).
- Network policies, mTLS via service mesh, micro-segmentation.
- Image scanning, signing (Sigstore), SBOM, SLSA supply chain.
- CIS benchmarks; runtime detection (Falco).

Service mesh: Istio (advanced traffic/security), Linkerd (lightweight, auto-mTLS), Cilium (eBPF), Gateway API for ingress.

Observability: Prometheus/Thanos (metrics), Loki/Fluent Bit (logs), Jaeger/OpenTelemetry (tracing), Grafana (dashboards).

Multi-tenancy & scaling:
- Namespace isolation, RBAC, resource quotas, limit ranges, priority/QoS classes.
- Autoscaling: HPA, VPA, Cluster Autoscaler, KEDA (event-driven).
- Right-size workloads; spot instances; cost via KubeCost/OpenCost.

Safety: no production changes without approval and rollback plan; test policy/admission changes in staging first.

## CI pipelines (GitLab CI)

Stage structure: `build` -> `test` -> `deploy`. Use specific image tags (`node:20`, not `latest`).

Core patterns:
- Cache dependencies per ref: `key: ${CI_COMMIT_REF_SLUG}`, `paths: [node_modules/]`.
- Pass build output via `artifacts` (with `expire_in`); test coverage via cobertura report.
- Docker build: `docker:24` + `docker:24-dind`, login with `$CI_REGISTRY_*`, tag with `$CI_COMMIT_SHA`.
- Multi-env deploy: YAML anchor template (`&deploy_template`) configuring kubectl context; `deploy:staging` on `develop`, `deploy:production` `when: manual` on `main`.
- Terraform pipeline: stages `validate` (init -backend=false, validate, fmt -check) -> `plan` (artifact tfplan) -> `apply` (`-auto-approve tfplan`, `when: manual`).
- Security: include SAST/Dependency/Container-Scanning templates; Trivy image scan on HIGH,CRITICAL.
- Dynamic child pipelines: generate YAML as artifact, `trigger: include: artifact:` with `strategy: depend`.

Best practices: manual gates for production, `environment:` for deployment tracking, merge-request pipelines, CI/CD variables for secrets, monitor pipeline performance.

## Troubleshooting & incident response

### Debugging method (devops-troubleshooter)
Gather facts (logs, metrics, traces) first, then form and test hypotheses methodically with minimal system impact. Apply the minimal fix, then add monitoring to prevent recurrence.

Domain checklist:
- K8s: `kubectl` resource inspection; pod issues (init/sidecar, resource limits, OOMKilled, CPU throttling); CNI/DNS/ingress; PV/storage.
- Network/DNS: tcpdump, dig, nslookup; LB health, security groups, service-mesh routing/retries.
- Performance: CPU/mem/IO profiling, memory leaks, GC; DB query plans, connection-pool exhaustion, deadlocks; cache (Redis/Memcached).
- App/services: service-to-service comms, API auth, message-queue consumer lag (Kafka/RabbitMQ/SQS), config drift.
- CI/CD: build/test failures, GitOps (ArgoCD/Flux) deploy issues, rollback, registry/image pull failures.
- Cloud: CloudWatch / Azure Monitor / Cloud Logging; serverless function errors.
- IaC: Terraform state issues, provider problems, resource drift.

### Incident response (SRE)

First 5 minutes:
1. Assess severity & impact: affected users, business/SLA impact, blast radius.
2. Establish command: Incident Commander (single decision-maker), Communication Lead, Technical Lead, war room.
3. Stabilize: feature flags, traffic throttling, circuit breakers, rollback recent changes, scale resources, post initial status.

Investigation: distributed tracing + metrics correlation + log aggregation; error-budget burn rate; change correlation (deploys/config); dependency mapping; cascading-failure analysis (retry storms, thundering herds).

Resolution: apply minimal viable fix; assess rollback risk; staged rollout with monitoring; validate SLIs, user experience, dependency health, capacity headroom.

Communication: internal updates every 15 min during active incident (tech detail per audience); external status page; support briefing; regulatory notice if required.

Severity classes:
- P0/SEV-1 (full outage or breach): immediate 24/7; ack < 15 min, resolve < 1 h; updates every 15 min + exec.
- P1/SEV-2 (major degradation): ack < 1 h; resolve < 4 h; hourly updates.
- P2/SEV-3 (minor impact): ack < 4 h; resolve < 24 h.
- P3/SEV-4 (cosmetic): next business day; resolve < 72 h.

Post-incident: blameless post-mortem (timeline, five-whys root cause, contributing factors, tracked action items). Improvements: new alerts/SLIs, runbook automation/self-healing, resilience patterns. Track MTTR/MTTD.

Reliability patterns: circuit breakers, bulkhead isolation, graceful degradation, retry with exponential backoff + jitter.

Principles: speed matters but accuracy more (a wrong fix can worsen it); fix first, understand later; document everything; learn and improve.
