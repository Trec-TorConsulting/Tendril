#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="tendril"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST_DIR="$(dirname "$SCRIPT_DIR")/manifests"

echo "=== Deploying Tendril to namespace $NAMESPACE ==="

kubectl apply -f "$MANIFEST_DIR/namespace.yaml"
kubectl apply -f "$MANIFEST_DIR/secrets.yaml"
kubectl apply -f "$MANIFEST_DIR/actions-runner-diagnostics-rbac.yaml"

# Run DB migration
kubectl delete job tendril-db-migrate -n "$NAMESPACE" --ignore-not-found
kubectl apply -f "$MANIFEST_DIR/db-migration-job.yaml"
kubectl wait --for=condition=complete job/tendril-db-migrate -n "$NAMESPACE" --timeout=120s

# Deploy Redis (middleware state) — StatefulSet with persistent storage
kubectl delete deployment tendril-redis -n "$NAMESPACE" --ignore-not-found
kubectl apply -f "$MANIFEST_DIR/redis-statefulset.yaml"
kubectl apply -f "$MANIFEST_DIR/redis-service.yaml"
kubectl rollout status statefulset/tendril-redis -n "$NAMESPACE" --timeout=120s

# Deploy pods
kubectl apply -f "$MANIFEST_DIR/api-deployment.yaml"
kubectl apply -f "$MANIFEST_DIR/api-service.yaml"
kubectl apply -f "$MANIFEST_DIR/mqtt-worker-deployment.yaml"
kubectl apply -f "$MANIFEST_DIR/mqtt-worker-service.yaml"
kubectl apply -f "$MANIFEST_DIR/scheduler-deployment.yaml"
kubectl apply -f "$MANIFEST_DIR/scheduler-service.yaml"
kubectl apply -f "$MANIFEST_DIR/web-deployment.yaml"
kubectl apply -f "$MANIFEST_DIR/web-service.yaml"
kubectl apply -f "$MANIFEST_DIR/vision-detector-deployment.yaml"
kubectl apply -f "$MANIFEST_DIR/vision-detector-service.yaml"
kubectl apply -f "$MANIFEST_DIR/vision-detector-gpu-deployment.yaml"
kubectl apply -f "$MANIFEST_DIR/vision-detector-gpu-service.yaml"
kubectl apply -f "$MANIFEST_DIR/hpa-api.yaml"
kubectl apply -f "$MANIFEST_DIR/hpa-web.yaml"
kubectl apply -f "$MANIFEST_DIR/hpa-mqtt-worker.yaml"
kubectl apply -f "$MANIFEST_DIR/pdb-api.yaml"
kubectl apply -f "$MANIFEST_DIR/pdb-web.yaml"
kubectl apply -f "$MANIFEST_DIR/pdb-mqtt-worker.yaml"
kubectl apply -f "$MANIFEST_DIR/pdb-scheduler.yaml"
kubectl apply -f "$MANIFEST_DIR/network-policies.yaml"

# ServiceMonitor resources require Prometheus Operator CRDs
if kubectl api-resources --api-group=monitoring.coreos.com | grep -q '^servicemonitors'; then
	kubectl apply -f "$MANIFEST_DIR/servicemonitors.yaml"
else
	echo "=== Skipping servicemonitors.yaml (monitoring.coreos.com CRDs not installed) ==="
fi

# Traefik middleware resources require Traefik CRDs
if kubectl api-resources --api-group=traefik.io | grep -q '^middlewares'; then
	kubectl apply -f "$MANIFEST_DIR/security-headers-middleware.yaml"
	kubectl apply -f "$MANIFEST_DIR/www-redirect-middleware.yaml"
else
	echo "=== Skipping Traefik middleware manifests (traefik.io Middleware CRD not installed) ==="
fi

if kubectl api-resources --api-group=traefik.io | grep -q '^serverstransports'; then
	kubectl apply -f "$MANIFEST_DIR/api-servers-transport.yaml"
else
	echo "=== Skipping api-servers-transport.yaml (traefik.io ServersTransport CRD not installed) ==="
fi

kubectl apply -f "$MANIFEST_DIR/ingress.yaml"
kubectl apply -f "$MANIFEST_DIR/api-ingress.yaml"
kubectl apply -f "$MANIFEST_DIR/www-redirect-ingress.yaml"

# Restart deployments to pick up latest images
kubectl rollout restart deployment tendril-api -n "$NAMESPACE"
kubectl rollout restart deployment tendril-mqtt-worker -n "$NAMESPACE"
kubectl rollout restart deployment tendril-scheduler -n "$NAMESPACE"
kubectl rollout restart deployment tendril-web -n "$NAMESPACE"
kubectl rollout restart deployment tendril-vision-detector -n "$NAMESPACE"
kubectl rollout restart deployment tendril-vision-detector-gpu -n "$NAMESPACE"

echo "=== Waiting for rollouts ==="
kubectl rollout status deployment tendril-api -n "$NAMESPACE" --timeout=120s
kubectl rollout status deployment tendril-web -n "$NAMESPACE" --timeout=120s
kubectl rollout status deployment tendril-vision-detector -n "$NAMESPACE" --timeout=120s
kubectl rollout status deployment tendril-vision-detector-gpu -n "$NAMESPACE" --timeout=120s

echo "=== Tendril deployed ==="
kubectl get pods -n "$NAMESPACE"
