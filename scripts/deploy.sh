#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="tendril"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST_DIR="$(dirname "$SCRIPT_DIR")/manifests"

echo "=== Deploying Tendril to namespace $NAMESPACE ==="

kubectl apply -f "$MANIFEST_DIR/namespace.yaml"
kubectl apply -f "$MANIFEST_DIR/secrets.yaml"

# Run DB migration
kubectl delete job tendril-db-migrate -n "$NAMESPACE" --ignore-not-found
kubectl apply -f "$MANIFEST_DIR/db-migration-job.yaml"
kubectl wait --for=condition=complete job/tendril-db-migrate -n "$NAMESPACE" --timeout=120s

# Deploy Redis (middleware state)
kubectl apply -f "$MANIFEST_DIR/redis-deployment.yaml"
kubectl apply -f "$MANIFEST_DIR/redis-service.yaml"

# Deploy pods
kubectl apply -f "$MANIFEST_DIR/api-deployment.yaml"
kubectl apply -f "$MANIFEST_DIR/api-service.yaml"
kubectl apply -f "$MANIFEST_DIR/mqtt-worker-deployment.yaml"
kubectl apply -f "$MANIFEST_DIR/mqtt-worker-service.yaml"
kubectl apply -f "$MANIFEST_DIR/scheduler-deployment.yaml"
kubectl apply -f "$MANIFEST_DIR/web-deployment.yaml"
kubectl apply -f "$MANIFEST_DIR/web-service.yaml"
kubectl apply -f "$MANIFEST_DIR/ingress.yaml"
kubectl apply -f "$MANIFEST_DIR/hpa-api.yaml"

# Restart deployments to pick up latest images
kubectl rollout restart deployment tendril-api -n "$NAMESPACE"
kubectl rollout restart deployment tendril-mqtt-worker -n "$NAMESPACE"
kubectl rollout restart deployment tendril-scheduler -n "$NAMESPACE"
kubectl rollout restart deployment tendril-web -n "$NAMESPACE"

echo "=== Waiting for rollouts ==="
kubectl rollout status deployment tendril-api -n "$NAMESPACE" --timeout=120s
kubectl rollout status deployment tendril-web -n "$NAMESPACE" --timeout=120s

echo "=== Tendril deployed ==="
kubectl get pods -n "$NAMESPACE"
