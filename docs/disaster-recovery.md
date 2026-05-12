# Disaster Recovery

This document describes backup, restore, and recovery procedures for Tendril deployments.

---

## 1. Components & Data at Risk

| Component | Data | Loss Impact |
|-----------|------|-------------|
| **PostgreSQL** | User accounts, tenants, grows, sensor readings, journals, feedings, billing | **Critical** — total platform loss |
| **MinIO / S3** | Journal photos, grow images | **High** — media history lost |
| **EMQX** | Transient MQTT messages, ACL config | **Low** — sensors reconnect automatically |
| **Redis** | Rate limiting & brute-force state | **None** — ephemeral, rebuilds on restart |
| **Kubernetes Secrets** | JWT key, API keys, encryption keys | **Critical** — auth & billing break |

---

## 2. Backup Strategy

### 2.1 PostgreSQL (Primary Database)

**Automated daily backups** — choose one approach:

#### Option A: pg_dump (simple, single-instance)

```bash
#!/bin/bash
# /etc/cron.d/tendril-backup — runs daily at 2 AM UTC
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

pg_dump -U tendril -Fc tendril > "$BACKUP_DIR/tendril_${TIMESTAMP}.dump"

# Retain 30 days
find "$BACKUP_DIR" -name "*.dump" -mtime +30 -delete
```

#### Option B: WAL archiving (point-in-time recovery)

```yaml
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'aws s3 cp %p s3://tendril-wal-archive/%f'
```

#### Option C: Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: tendril-db-backup
  namespace: tendril
spec:
  schedule: "0 2 * * *"   # Daily 2 AM UTC
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:16-alpine
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -U tendril -Fc tendril | \
                gzip > /backups/tendril_$(date +%Y%m%d).dump.gz
            env:
            - name: PGHOST
              value: postgresql.postgresql.svc.cluster.local
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: tendril-secrets
                  key: DB_PASSWORD
            volumeMounts:
            - name: backups
              mountPath: /backups
          volumes:
          - name: backups
            persistentVolumeClaim:
              claimName: tendril-backups
          restartPolicy: OnFailure
```

**Recommended retention:**

| Tier | Frequency | Retention |
|------|-----------|-----------|
| Daily | Every 24h | 30 days |
| Weekly | Sunday 2 AM | 12 weeks |
| Monthly | 1st of month | 12 months |

### 2.2 MinIO / S3 (Object Storage)

```bash
# Mirror to offsite S3 bucket
mc mirror --remove --overwrite minio/tendril-photos s3/tendril-photos-backup
```

Or enable **S3 versioning** on the bucket to allow object-level recovery:

```bash
mc version enable minio/tendril-photos
```

### 2.3 Kubernetes Secrets

```bash
# Export secrets (store encrypted, never in git)
kubectl get secret tendril-secrets -n tendril -o yaml | \
  sops --encrypt --input-type yaml --output-type yaml /dev/stdin > secrets-backup.enc.yaml
```

Store encrypted backups in a separate, access-controlled location (e.g., 1Password, Vault, encrypted S3 bucket).

---

## 3. Restore Procedures

### 3.1 Full Database Restore

```bash
# 1. Stop the API to prevent writes
kubectl scale deployment tendril-api -n tendril --replicas=0

# 2. Restore from dump
pg_restore -U tendril -d tendril --clean --if-exists tendril_20260512.dump

# 3. Run any pending migrations
kubectl apply -f manifests/db-migration-job.yaml
kubectl wait --for=condition=complete job/tendril-db-migrate -n tendril --timeout=120s

# 4. Restart the API
kubectl scale deployment tendril-api -n tendril --replicas=2
```

### 3.2 Point-in-Time Recovery (WAL)

```bash
# 1. Stop PostgreSQL
# 2. Restore base backup
# 3. Create recovery.conf:
restore_command = 'aws s3 cp s3://tendril-wal-archive/%f %p'
recovery_target_time = '2026-05-12 14:30:00 UTC'
# 4. Start PostgreSQL — it replays WAL to the target time
```

### 3.3 S3/MinIO Object Recovery

```bash
# Restore full bucket from backup
mc mirror s3/tendril-photos-backup minio/tendril-photos
```

### 3.4 Secret Rotation After Compromise

If secrets are compromised, rotate **all** of these:

```bash
# 1. Generate new JWT secret (invalidates all sessions — users must re-login)
openssl rand -hex 32

# 2. Generate new integration encryption key
python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"

# 3. Rotate in Kubernetes
kubectl edit secret tendril-secrets -n tendril

# 4. Restart all services
kubectl rollout restart deployment -n tendril
```

| Secret | Impact of Rotation |
|--------|--------------------|
| JWT_SECRET | All users logged out, must re-login |
| INTEGRATION_ENCRYPTION_KEY | Stored integration credentials become unreadable — users must re-enter |
| S3_SECRET_KEY | Generate new key in MinIO, update secret |
| GEMINI_API_KEY | Generate new key in Google AI Studio |
| STRIPE_SECRET_KEY | Generate new key in Stripe Dashboard |

---

## 4. Recovery Time Objectives

| Scenario | RTO | RPO | Procedure |
|----------|-----|-----|-----------|
| Pod crash / OOM | < 1 min | 0 | K8s auto-restart via liveness probe |
| Node failure | < 5 min | 0 | K8s reschedules pods to healthy nodes |
| Database corruption | < 30 min | ≤ 24h | Restore from daily pg_dump |
| Database corruption (WAL) | < 1h | ≤ minutes | Point-in-time recovery |
| Full cluster loss | < 2h | ≤ 24h | Rebuild from manifests + restore DB |
| Secret compromise | < 1h | 0 | Rotate secrets, restart services |

---

## 5. Testing Your Backups

**Schedule quarterly DR drills:**

```bash
# 1. Restore backup to a test database
createdb tendril_dr_test
pg_restore -U tendril -d tendril_dr_test tendril_latest.dump

# 2. Run migrations against it
DATABASE_URL="postgresql+asyncpg://tendril:tendril@localhost:5432/tendril_dr_test" \
  python -m alembic upgrade head

# 3. Run the test suite against it
DATABASE_URL="postgresql+asyncpg://tendril:tendril@localhost:5432/tendril_dr_test" \
  pytest --tb=short -q

# 4. Clean up
dropdb tendril_dr_test
```

**Checklist:**
- [ ] Backup file is not zero bytes
- [ ] pg_restore completes without errors
- [ ] Alembic migrations apply cleanly
- [ ] Test suite passes
- [ ] Sensor readings present with correct timestamps
- [ ] Journal photos accessible

---

## 6. Monitoring & Alerts

Set up alerts for backup failures:

```yaml
# Example: Prometheus alert rule
- alert: BackupFailed
  expr: kube_job_status_failed{job_name=~"tendril-db-backup.*"} > 0
  for: 1h
  labels:
    severity: critical
  annotations:
    summary: "Tendril database backup failed"
```

Monitor these metrics:
- Backup job success/failure status
- Backup file size (alert on zero-byte or significantly smaller than previous)
- Time since last successful backup (alert if > 26 hours)
- Database disk usage trending (alert at 80% capacity)
