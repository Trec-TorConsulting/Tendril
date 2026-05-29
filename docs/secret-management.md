# Secret Management with Sealed Secrets

Tendril uses [Bitnami Sealed Secrets](https://sealed-secrets.netlify.app/) to store
encrypted secrets in Git. The Sealed Secrets controller (running in `kube-system`)
decrypts them into native Kubernetes Secrets at deploy time.

## Prerequisites

```bash
# Install kubeseal CLI (macOS)
brew install kubeseal

# Verify controller is running
kubectl get pods -n kube-system -l app.kubernetes.io/name=sealed-secrets
```

## Sealing Secrets

1. Create a plain `secrets.yaml` from the example:
   ```bash
   cp manifests/secrets.yaml.example manifests/secrets.yaml
   # Edit secrets.yaml with real values
   ```

2. Seal it:
   ```bash
   kubeseal \
     --controller-name=sealed-secrets-controller \
     --controller-namespace=kube-system \
     --format yaml \
     < manifests/secrets.yaml \
     > manifests/sealed-secrets.yaml
   ```

3. Commit `sealed-secrets.yaml` (never commit `secrets.yaml`).

## Rotating a Secret

1. Update the value in your local `secrets.yaml`
2. Re-seal:
   ```bash
   kubeseal \
     --controller-name=sealed-secrets-controller \
     --controller-namespace=kube-system \
     --format yaml \
     < manifests/secrets.yaml \
     > manifests/sealed-secrets.yaml
   ```
3. Apply:
   ```bash
   kubectl apply -f manifests/sealed-secrets.yaml
   ```
4. Restart affected deployments:
   ```bash
   kubectl rollout restart deployment/tendril-api -n tendril
   kubectl rollout restart deployment/tendril-mqtt-worker -n tendril
   kubectl rollout restart statefulset/tendril-scheduler -n tendril
   ```

## Rotating the Sealed Secrets Key

The controller rotates its signing key every 30 days by default. Old keys remain
active for decryption. To force rotation:

```bash
# Delete the current key (controller will generate a new one)
kubectl delete secret -n kube-system -l sealedsecrets.bitnami.com/sealed-secrets-key

# Re-seal all secrets with the new key
kubeseal --controller-name=sealed-secrets-controller \
  --controller-namespace=kube-system \
  --format yaml < manifests/secrets.yaml > manifests/sealed-secrets.yaml
```

## Emergency: Decrypting Without Controller

If the controller is down and you need to recover secrets, the private keys are
stored as Kubernetes secrets in `kube-system`:

```bash
kubectl get secret -n kube-system -l sealedsecrets.bitnami.com/sealed-secrets-key -o yaml
```

Back these up securely (offline, encrypted) for disaster recovery.

## Files

| File | Purpose | In Git? |
|------|---------|---------|
| `manifests/secrets.yaml.example` | Template with placeholder values | Yes |
| `manifests/secrets.yaml` | Real values (local only) | **No** (.gitignore) |
| `manifests/sealed-secrets.yaml` | Encrypted version for deployment | Yes |
| `manifests/sealed-secrets-controller.yaml` | Controller install reference | Yes |
