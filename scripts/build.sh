#!/usr/bin/env bash
set -euo pipefail

REGISTRY="${TENDRIL_REGISTRY:-your-registry:5000}"
API_IMAGE="${REGISTRY}/tendril-api:latest"
WEB_IMAGE="${REGISTRY}/tendril-web:latest"
PLATFORMS="linux/amd64,linux/arm64"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

build_api() {
    echo "=== Building tendril-api ($PLATFORMS) ==="
    docker buildx build --platform "$PLATFORMS" --push -t "$API_IMAGE" "$PROJECT_DIR/api"
    echo "=== Pushed to $API_IMAGE ==="
}

build_web() {
    echo "=== Building tendril-web ($PLATFORMS) ==="
    docker buildx build --platform "$PLATFORMS" --push -t "$WEB_IMAGE" "$PROJECT_DIR/web"
    echo "=== Pushed to $WEB_IMAGE ==="
}

case "${1:-all}" in
    api)  build_api ;;
    web)  build_web ;;
    all)  build_api && build_web ;;
    *)    echo "Usage: $0 {api|web|all}" && exit 1 ;;
esac
