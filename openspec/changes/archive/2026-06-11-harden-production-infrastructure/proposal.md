# Change: Harden Production Infrastructure

## Why
The platform lacks enterprise-grade observability, security hardening, and resilience across several services. The scheduler has no health probes (causing silent failures like missed health checks), MQTT worker and web deployments have incorrect/missing probes, two services run as root, and secrets are committed in plaintext.

## What Changes
- Add dedicated health endpoints to Scheduler (new lightweight HTTP server), MQTT Worker, and Web (Next.js API route)
- Add liveness, readiness, and startup probes to ALL deployments
- Add securityContext hardening to MQTT Worker and Scheduler (matching API/Web patterns)
- Add scheduler leadership heartbeat with periodic re-validation
- Convert secrets.yaml to Sealed Secrets workflow
- Add PodDisruptionBudget for Scheduler
- Upgrade Redis to StatefulSet with PVC for persistence
- Add Prometheus metrics endpoints to API, MQTT Worker, and Scheduler
- Add NetworkPolicy manifests restricting east-west traffic

## Impact
- Affected specs: new `infrastructure` capability spec
- Affected code:
  - `api/app/scheduler/main.py` — add health HTTP server + leadership heartbeat
  - `api/app/scheduler/tasks.py` — expose task health state
  - `api/app/mqtt/webhook.py` — add `/health` endpoint
  - `web/src/app/api/health/route.ts` — new Next.js health route
  - `manifests/*.yaml` — all deployment manifests updated
  - `manifests/sealed-secrets-controller.yaml` — new
  - `manifests/network-policies.yaml` — new
  - `manifests/redis-statefulset.yaml` — replaces redis-deployment.yaml
  - `manifests/servicemonitor.yaml` — new (Prometheus)
