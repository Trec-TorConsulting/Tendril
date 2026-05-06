#!/usr/bin/env bash
set -euo pipefail

REGISTRY="${TENDRIL_REGISTRY:-your-registry:5000}"
API_IMAGE="${REGISTRY}/tendril-api:latest"
WEB_IMAGE="${REGISTRY}/tendril-web:latest"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

build_api() {
    echo "=== Building tendril-api ==="
    docker build --load -t "$API_IMAGE" "$PROJECT_DIR/api"
    docker push "$API_IMAGE"
    echo "=== Pushed to $API_IMAGE ==="
}

build_web() {
    echo "=== Building tendril-web ==="
    docker build --load -t "$WEB_IMAGE" "$PROJECT_DIR/web"
    docker push "$WEB_IMAGE"
    echo "=== Pushed to $WEB_IMAGE ==="
}

case "${1:-all}" in
    api)  build_api ;;
    web)  build_web ;;
    all)  build_api && build_web ;;
    *)    echo "Usage: $0 {api|web|all}" && exit 1 ;;
esac
