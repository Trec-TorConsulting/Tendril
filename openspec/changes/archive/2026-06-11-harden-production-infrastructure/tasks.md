## 1. Health Endpoints
- [x] 1.1 Add lightweight HTTP health server to scheduler (`/healthz`, `/readyz` on port 8080)
- [x] 1.2 Add `/health` endpoint to MQTT worker webhook app
- [x] 1.3 Add `/api/health` Next.js API route to web app
- [x] 1.4 Add startup probe support to API (`/health` with higher failure threshold)

## 2. Scheduler Resilience
- [x] 2.1 Add leadership heartbeat (re-validate advisory lock every 60s)
- [x] 2.2 Expose task health state (last successful run timestamps)
- [x] 2.3 Graceful shutdown on leadership loss

## 3. Kubernetes Probes
- [x] 3.1 Add liveness + readiness + startup probes to API deployment
- [x] 3.2 Add liveness + readiness probes to Scheduler deployment
- [x] 3.3 Fix MQTT Worker probes (replace `/docs` with `/health`)
- [x] 3.4 Add liveness + readiness probes to Web deployment (use `/api/health`)
- [x] 3.5 Add startup probes to MQTT Worker and Web

## 4. Security Hardening
- [x] 4.1 Add securityContext to MQTT Worker deployment (runAsNonRoot, drop caps, readOnlyRootFilesystem)
- [x] 4.2 Add securityContext to Scheduler deployment
- [x] 4.3 Add PodDisruptionBudget for Scheduler

## 5. Sealed Secrets
- [x] 5.1 Add Sealed Secrets controller manifest
- [x] 5.2 Create sealed-secrets.yaml (encrypted version of current secrets) — operational: tooling + docs in place, run `kubeseal` per docs/secret-management.md
- [x] 5.3 Add `manifests/secrets.yaml` to .gitignore
- [x] 5.4 Document secret rotation workflow in docs/

## 6. Redis Persistence
- [x] 6.1 Create redis-statefulset.yaml with PVC and appendonly config
- [x] 6.2 Deprecate redis-deployment.yaml (replaced, marked with header comment)
- [x] 6.3 Update redis-service.yaml for StatefulSet (headless)

## 7. Monitoring
- [x] 7.1 Add `prometheus-fastapi-instrumentator` to API dependencies
- [x] 7.2 Add `/metrics` endpoint to API
- [x] 7.3 Add Prometheus metrics to Scheduler (task gauges)
- [x] 7.4 Add metrics to MQTT Worker webhook app
- [x] 7.5 Create ServiceMonitor manifests for all services
- [x] 7.6 Add kube-prometheus-stack Helm values manifest (Prometheus, Grafana, Alertmanager)
- [x] 7.7 Create Tendril Grafana dashboard ConfigMap (service health, task schedules, request rates)

## 8. Network Policies
- [x] 8.1 Create default-deny ingress policy for tendril namespace
- [x] 8.2 Create allow policies: Traefik → API, Traefik → Web
- [x] 8.3 Create allow policies: API/MQTT/Scheduler → PostgreSQL, Redis, EMQX
- [x] 8.4 Create egress allow: Scheduler → Gemini API, API → Gemini/Ollama
