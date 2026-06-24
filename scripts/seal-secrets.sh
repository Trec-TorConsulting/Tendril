#!/usr/bin/env bash
#
# seal-secrets.sh — encrypt manifests/secrets.yaml into a committable
# SealedSecret using kubeseal + the in-cluster controller key.
#
# The output (manifests/sealed-secrets.yaml) can only be decrypted by the
# sealed-secrets controller running in THIS cluster, so it is safe to commit
# to git — unlike the plaintext manifests/secrets.yaml (which is gitignored).
#
# Prereqs:
#   - kubeseal CLI:  https://github.com/bitnami-labs/sealed-secrets/releases
#   - kubectl context pointed at the target cluster
#   - the sealed-secrets controller installed (see
#     manifests/sealed-secrets-controller.yaml)
#
# Usage:
#   cp manifests/secrets.yaml.example manifests/secrets.yaml   # fill in values
#   ./scripts/seal-secrets.sh
#   git add manifests/sealed-secrets.yaml && git commit ...
#   kubectl apply -f manifests/sealed-secrets.yaml
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST_DIR="$(dirname "$SCRIPT_DIR")/manifests"
SRC="$MANIFEST_DIR/secrets.yaml"
OUT="$MANIFEST_DIR/sealed-secrets.yaml"

CONTROLLER_NAME="${SEALED_SECRETS_CONTROLLER_NAME:-sealed-secrets-controller}"
CONTROLLER_NS="${SEALED_SECRETS_CONTROLLER_NAMESPACE:-kube-system}"

if ! command -v kubeseal >/dev/null 2>&1; then
  echo "error: kubeseal not found on PATH." >&2
  echo "       Install it: https://github.com/bitnami-labs/sealed-secrets/releases" >&2
  exit 1
fi

if [ ! -f "$SRC" ]; then
  echo "error: $SRC not found." >&2
  echo "       Create it first: cp $MANIFEST_DIR/secrets.yaml.example $SRC" >&2
  exit 1
fi

echo "Sealing $SRC → $OUT"
echo "  controller: $CONTROLLER_NAME (namespace $CONTROLLER_NS)"

kubeseal \
  --controller-name="$CONTROLLER_NAME" \
  --controller-namespace="$CONTROLLER_NS" \
  --format yaml \
  < "$SRC" \
  > "$OUT"

echo "Done. $OUT is encrypted and safe to commit."
echo "Next:"
echo "  git add $(realpath --relative-to="$(pwd)" "$OUT" 2>/dev/null || echo "$OUT")"
echo "  kubectl apply -f $OUT"
