## Context
All Tendril services must meet enterprise production standards: observable, secure, resilient, and recoverable. Single-site deployment (no DR), but full HA within the cluster.

## Goals
- Every pod restartable/replaceable with zero manual intervention
- Silent failures detected and recovered within 5 minutes
- Least-privilege security on all workloads
- Secrets never in git (sealed at rest, decrypted only in-cluster)
- Metrics available for alerting (Prometheus-compatible)
- Redis data survives pod restarts

## Non-Goals
- Multi-site disaster recovery (single site constraint)
- Blue/green deployments (deferred)
- Service mesh (Traefik suffices for now)
- Auto-scaling scheduler (single-leader by design)

## Decisions

### Health Endpoints
- **Scheduler**: Embed a minimal `aiohttp` server on port 8080 with `/healthz` (liveness — event loop alive) and `/readyz` (readiness — leader lock held + last task ran within expected window)
- **MQTT Worker**: Add `/health` to existing FastAPI webhook app (already runs on 8081)
- **Web**: Next.js API route at `/api/health` returning 200 with `{ status: "ok" }`
- **API**: Already has `/health` and `/health/ready` — add startupProbe

### Leadership Heartbeat
- Scheduler re-validates advisory lock every 60s via `SELECT pg_advisory_lock_status()`
- On loss: graceful shutdown → k8s restarts pod → re-election

### Sealed Secrets
- Install Sealed Secrets controller (Bitnami)
- Replace `secrets.yaml` with `sealed-secrets.yaml` (encrypted)
- Add `secrets.yaml` to `.gitignore`
- Document rotation workflow

### Redis Persistence
- Convert Deployment → StatefulSet with 1Gi PVC (appendonly.aof)
- Keep single replica (cache layer, not critical-path HA)

### Prometheus Metrics
- API: `/metrics` via `prometheus-fastapi-instrumentator`
- Scheduler: Custom gauge metrics (last_run_timestamp, task_error_count)
- MQTT Worker: FastAPI metrics on webhook app
- ServiceMonitor CRDs for auto-discovery
- Deploy kube-prometheus-stack (Prometheus, Grafana, Alertmanager) via Helm values manifest

### Network Policies
- Default deny ingress per namespace
- Allow: Traefik → API/Web, API → PostgreSQL/Redis/EMQX, MQTT Worker → PostgreSQL/Redis/EMQX, Scheduler → PostgreSQL/Gemini egress

## Risks / Trade-offs
- Sealed Secrets adds operational complexity (need `kubeseal` CLI for secret updates) → mitigate with documented workflow
- Scheduler health server adds a dependency (aiohttp) → minimal, well-tested library
- Redis StatefulSet needs Longhorn StorageClass available → already deployed

## Migration Plan
1. Add health endpoints (no manifest changes yet) — deploy, verify
2. Update manifests with probes + security contexts — rolling restart
3. Deploy Sealed Secrets controller, seal existing secrets, remove plaintext
4. Convert Redis to StatefulSet — brief cache loss (acceptable)
5. Add NetworkPolicies in audit mode first, then enforce
6. Add ServiceMonitors (assumes Prometheus operator or kube-prometheus-stack)

## Resolved Questions
- **Monitoring stack**: Include kube-prometheus-stack (Prometheus, Grafana, Alertmanager)
- **StorageClass**: `longhorn` (Longhorn is deployed on the cluster)
