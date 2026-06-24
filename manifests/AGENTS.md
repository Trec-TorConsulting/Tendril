# Tendril Kubernetes Manifests — Agent Guide

Plain YAML manifests applied via `kubectl apply`. No Helm, no Kustomize. Cluster is **k3s** with Traefik as the default ingress controller.

> Cross-references: [`scripts/deploy.sh`](../scripts/deploy.sh) for the apply order, [`docs/self-hosting.md`](../docs/self-hosting.md) for ops, [`api/AGENTS.md`](../api/AGENTS.md) for what the workloads do.

## Layout

```
manifests/
  namespace.yaml                       # tendril namespace
  secrets.yaml                         # GITIGNORED — real values
  secrets.yaml.example                 # template, checked in
  sealed-secrets-controller.yaml       # SealedSecrets CRD controller
  api-deployment.yaml / api-service.yaml / api-ingress.yaml / hpa-api.yaml / pdb-api.yaml
  web-deployment.yaml / web-service.yaml / hpa-web.yaml / pdb-web.yaml
  mqtt-worker-deployment.yaml / mqtt-worker-service.yaml / hpa-mqtt-worker.yaml / pdb-mqtt-worker.yaml
  scheduler-deployment.yaml / scheduler-service.yaml / pdb-scheduler.yaml
  redis-statefulset.yaml / redis-service.yaml
  db-migration-job.yaml                # alembic upgrade head — applied before rollouts
  ingress.yaml                         # main host
  www-redirect-ingress.yaml / www-redirect-middleware.yaml
  api-servers-transport.yaml           # Traefik ServersTransport (TLS to backends)
  security-headers-middleware.yaml     # Traefik Middleware: HSTS, CSP, X-Frame-Options
  network-policies.yaml                # default-deny ingress + selective allow
  servicemonitors.yaml                 # Prometheus scrape config
  kube-prometheus-values.yaml          # values for the kube-prometheus chart (reference)
  grafana-dashboard-configmap.yaml
  minio-storage-alert-cronjob.yaml
```

## Conventions

### Namespace, naming, labels
- Everything lives in the `tendril` namespace.
- Workload name: `tendril-<component>` (e.g. `tendril-api`, `tendril-mqtt-worker`).
- Selectors use **only** `app: tendril-<component>`. Don't add labels the Service/HPA selectors don't match.

### Image registry
- Internal registry: `192.168.4.10:30500/tendril-<component>:latest`.
- Always set `imagePullPolicy: Always` while we ship a moving `:latest` tag — rollouts depend on `kubectl rollout restart` re-pulling.

### Secrets
- `manifests/secrets.yaml` is the **live** Secret and is gitignored.
- `secrets.yaml.example` is the canonical list of required keys — keep in sync when you add a config key in [`api/app/config.py`](../api/app/config.py).
- Production should migrate to SealedSecrets (controller manifest already present). For ad-hoc dev, plain `kubectl apply -f secrets.yaml` is fine.

### Workload hardening (apply to every new Deployment)
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: [ALL]
volumeMounts:
  - { name: tmp, mountPath: /tmp }   # paired with an emptyDir
```

### Resilience patterns
- **HPA**: every user-facing deployment (api, web, mqtt-worker) has one. CPU 70% / memory 80% targets.
- **PDB**: every deployment with `replicas >= 2` has a PodDisruptionBudget (`minAvailable: 1`).
- **Topology spread + pod anti-affinity**: spread across hostnames, prefer not co-locating replicas.
- **Node exclusion**: `node05` is excluded via `nodeAffinity` (hardware reasons — keep it).
- **Rolling updates**: `maxUnavailable: 0`, `maxSurge: 1`. Combined with PDB, this gives zero-downtime deploys.

### Migrations
- `db-migration-job.yaml` runs `alembic upgrade head` as a one-shot Job.
- `api-deployment.yaml` also runs migrations as an **init container** — so pod restarts converge on schema head even if the Job was skipped.
- Keep both in sync (same image, same envFrom).

### Network policies
Default-deny ingress + allow rules per workload (Traefik in `kube-system` → api/web, etc.). When adding a workload, add an allow rule in [`network-policies.yaml`](network-policies.yaml) or it will be unreachable.

## Commands

```bash
# Full deploy from a clean checkout
./scripts/deploy.sh

# Apply a single manifest
kubectl apply -f manifests/api-deployment.yaml

# Force a rollout (re-pull :latest)
kubectl rollout restart deployment tendril-api -n tendril
kubectl rollout status   deployment tendril-api -n tendril --timeout=120s

# Re-run migrations
kubectl delete job tendril-db-migrate -n tendril --ignore-not-found
kubectl apply -f manifests/db-migration-job.yaml
kubectl wait --for=condition=complete job/tendril-db-migrate -n tendril --timeout=120s

# Tail logs
kubectl logs -n tendril -l app=tendril-api -f --tail=100

# Diff before apply (server-side)
kubectl diff -f manifests/api-deployment.yaml
```

## Gotchas

- **Selector immutability.** A Deployment's `spec.selector.matchLabels` cannot change after creation. To rename, delete + recreate.
- **`envFrom: secretRef: tendril-secrets`** means every key in the Secret becomes an env var. Adding a key to `secrets.yaml` is enough — don't also add an `env:` entry.
- **Traefik middleware names are namespaced.** Reference as `tendril-security-headers@kubernetescrd` from an Ingress, not the bare name.
- **PDB + single replica = stuck drains.** If you scale a Deployment to 1, also drop its PDB or set `minAvailable: 0`.
- **`servicemonitors.yaml`** requires the Prometheus Operator CRDs. It will fail to apply on a vanilla cluster — skip it if you don't run kube-prometheus.
- **The deploy script does not apply network-policies.yaml, pdb-*, or hpa-mqtt-worker/web.** Apply those manually after the first deploy: `kubectl apply -f manifests/` (or individually).
- `manifests/secrets.yaml` regenerated from `.example` will overwrite real values. Always edit in place or use SealedSecrets.
