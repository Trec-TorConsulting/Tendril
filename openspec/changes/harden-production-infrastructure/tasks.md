## 1. Health Endpoints
- [ ] 1.1 Add lightweight HTTP health server to scheduler (`/healthz`, `/readyz` on port 8080)
- [ ] 1.2 Add `/health` endpoint to MQTT worker webhook app
- [ ] 1.3 Add `/api/health` Next.js API route to web app
- [ ] 1.4 Add startup probe support to API (`/health` with higher failure threshold)

## 2. Scheduler Resilience
- [ ] 2.1 Add leadership heartbeat (re-validate advisory lock every 60s)
- [ ] 2.2 Expose task health state (last successful run timestamps)
- [ ] 2.3 Graceful shutdown on leadership loss

## 3. Kubernetes Probes
- [ ] 3.1 Add liveness + readiness + startup probes to API deployment
- [ ] 3.2 Add liveness + readiness probes to Scheduler deployment
- [ ] 3.3 Fix MQTT Worker probes (replace `/docs` with `/health`)
- [ ] 3.4 Add liveness + readiness probes to Web deployment (use `/api/health`)
- [ ] 3.5 Add startup probes to MQTT Worker and Web

## 4. Security Hardening
- [ ] 4.1 Add securityContext to MQTT Worker deployment (runAsNonRoot, drop caps, readOnlyRootFilesystem)
- [ ] 4.2 Add securityContext to Scheduler deployment
- [ ] 4.3 Add PodDisruptionBudget for Scheduler

## 5. Sealed Secrets
- [ ] 5.1 Add Sealed Secrets controller manifest
- [ ] 5.2 Create sealed-secrets.yaml (encrypted version of current secrets)
- [ ] 5.3 Add `manifests/secrets.yaml` to .gitignore
- [ ] 5.4 Document secret rotation workflow in docs/

## 6. Redis Persistence
- [ ] 6.1 Create redis-statefulset.yaml with PVC and appendonly config
- [ ] 6.2 Remove redis-deployment.yaml (replaced)
- [ ] 6.3 Update redis-service.yaml if needed for StatefulSet

## 7. Monitoring
- [ ] 7.1 Add `prometheus-fastapi-instrumentator` to API dependencies
- [ ] 7.2 Add `/metrics` endpoint to API
- [ ] 7.3 Add Prometheus metrics to Scheduler (task gauges)
- [ ] 7.4 Add metrics to MQTT Worker webhook app
- [ ] 7.5 Create ServiceMonitor manifests for all services
- [ ] 7.6 Add kube-prometheus-stack Helm values manifest (Prometheus, Grafana, Alertmanager)
- [ ] 7.7 Create Tendril Grafana dashboard ConfigMap (service health, task schedules, request rates)

## 8. Network Policies
- [ ] 8.1 Create default-deny ingress policy for tendril namespace
- [ ] 8.2 Create allow policies: Traefik → API, Traefik → Web
- [ ] 8.3 Create allow policies: API/MQTT/Scheduler → PostgreSQL, Redis, EMQX
- [ ] 8.4 Create egress allow: Scheduler → Gemini API, API → Gemini/Ollama
