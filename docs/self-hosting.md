# Self-Hosting Guide

This guide walks through deploying Tendril on your own infrastructure. Choose Docker Compose for simplicity or Kubernetes for production scale.

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Disk | 20 GB | 50 GB+ (photos grow over time) |
| OS | Linux (arm64 or amd64), macOS | Ubuntu 22.04+ / Debian 12+ |
| Docker | 24.0+ | Latest |
| Docker Compose | 2.20+ | Latest |

### Optional

| Tool | Purpose |
|------|---------|
| Ollama | Local AI models — install from [ollama.com](https://ollama.com) |
| go2rtc | RTSP camera proxy — required for RTSP/RTMP camera streams. Install from [github.com/AlexxIT/go2rtc](https://github.com/AlexxIT/go2rtc) |
| PlatformIO | Only if flashing ESP32 firmware |

## Quick Start with Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/Trec-TorConsulting/Tendril.git
cd Tendril
```

### 2. Configure environment

Create a `.env` file in the project root:

```bash
# Required — generate a strong secret
JWT_SECRET=change-me-to-a-random-64-char-string

# Database (defaults work with bundled PostgreSQL)
DATABASE_URL=postgresql+asyncpg://tendril:tendril@postgres:5432/tendril

# Domain — your hostname
DOMAIN=tendrilgrow.com
CORS_ORIGINS=https://tendrilgrow.com

# MinIO / S3 (defaults work with bundled MinIO)
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=change-me-in-production
S3_BUCKET=tendril-photos

# MQTT (defaults work with bundled EMQX)
MQTT_BROKER_HOST=emqx
MQTT_BROKER_PORT=1883

# Optional — AI (Ollama primary, Gemini fallback)
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=mistral-nemo:12b
OLLAMA_VISION_URL=http://host.docker.internal:11434
OLLAMA_VISION_MODEL=llava:7b
GEMINI_API_KEY=your-key-here

# Optional — Billing
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# Optional — OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Optional — Web Push Notifications
VAPID_PRIVATE_KEY=
VAPID_EMAIL=mailto:admin@example.com
```

> **Security**: Generate `JWT_SECRET` with: `openssl rand -hex 32`

### 3. Start the stack

```bash
docker compose up -d
```

This starts:
- **PostgreSQL** — Database (port 5432)
- **EMQX** — MQTT broker (port 1883, dashboard at 18083)
- **MinIO** — S3 storage (API 9000, console at 9001)
- **Tendril API** — REST + WebSocket (port 8000)
- **Tendril Web** — Frontend (port 3000)
- **MQTT Worker** — Sensor data ingestion
- **Scheduler** — Background tasks
- **Migrate** — Runs DB migrations on startup (exits after)

### 4. Verify

```bash
# Check all services are healthy
docker compose ps

# API health check
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/v1/docs

# Open the web app
open http://localhost:3000
```

### 5. Create your first account

Open `http://localhost:3000` and register. The first user creates the first tenant.

## Production Deployment

### Reverse Proxy (nginx)

Put Tendril behind a reverse proxy with TLS:

```nginx
server {
    listen 443 ssl http2;
    server_name tendrilgrow.com;

    ssl_certificate     /etc/letsencrypt/live/tendrilgrow.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tendrilgrow.com/privkey.pem;

    # Web frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API
    location /v1/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support for AI chat
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
    }

    # Health check (no auth)
    location /health {
        proxy_pass http://localhost:8000;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name tendrilgrow.com;
    return 301 https://$host$request_uri;
}
```

### Kubernetes

See the full K8s deployment in `manifests/`. Deploy with:

```bash
# Edit manifests/secrets.yaml with your values first
./scripts/deploy.sh
```

Deployment order (handled by the script):
1. Namespace creation
2. Secrets
3. DB migration job (waits for completion)
4. API + MQTT worker + Scheduler + Web deployments
5. Services + Ingress

The API and Web have Horizontal Pod Autoscalers configured (`hpa-api.yaml`, `hpa-web.yaml`).

### External PostgreSQL

To use an external PostgreSQL instance instead of the bundled one:

1. Remove the `postgres` service from `docker-compose.yml`
2. Set `DATABASE_URL` to your external database:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@db.example.com:5432/tendril
   ```
3. Ensure the database exists and the user has full DDL permissions (for migrations)
4. Run migrations: `docker compose run --rm migrate`

**PostgreSQL requirements:**
- Version 15+
- Row-Level Security support (enabled by default)
- Extensions: `uuid-ossp` (for UUID generation)

### External S3 (AWS, Cloudflare R2, etc.)

Replace MinIO with any S3-compatible storage:

```bash
S3_ENDPOINT=https://s3.us-east-1.amazonaws.com  # or omit for AWS default
S3_ACCESS_KEY=AKIA...
S3_SECRET_KEY=your-secret
S3_BUCKET=your-bucket-name
```

### EMQX Configuration

The bundled EMQX works out of the box. For production:

1. **Enable authentication**: Configure EMQX HTTP auth webhook pointing to `http://api:8000/v1/devices/mqtt-auth`
2. **Enable TLS**: Mount certificates and configure port 8883
3. **Set ACL rules**: Restrict devices to their own topic paths (`t/{tenant}/d/{device}/#`)

EMQX dashboard: `http://localhost:18083` (default: admin/public)

## Upgrading

```bash
git pull origin main
docker compose build
docker compose up -d
```

The `migrate` service runs automatically on `up` to apply any new database migrations.

## Backups

### PostgreSQL

```bash
# Dump
docker compose exec postgres pg_dump -U tendril tendril > backup.sql

# Restore
docker compose exec -T postgres psql -U tendril tendril < backup.sql
```

### MinIO (Photos)

```bash
# Install mc (MinIO client)
brew install minio/stable/mc  # or download from minio.io

# Configure
mc alias set tendril http://localhost:9000 minioadmin minioadmin

# Backup
mc mirror tendril/tendril-photos ./backup/photos/

# Restore
mc mirror ./backup/photos/ tendril/tendril-photos
```

## Troubleshooting

### Services not starting

```bash
# Check logs
docker compose logs api
docker compose logs mqtt-worker
docker compose logs scheduler

# Check health
docker compose ps
```

### Database connection issues

```bash
# Verify PostgreSQL is running
docker compose exec postgres pg_isready -U tendril

# Check connection string
docker compose exec api python -c "from app.config import get_settings; print(get_settings().database_url)"
```

### MQTT not receiving data

```bash
# Check EMQX is running
docker compose logs emqx

# Subscribe to all topics for debugging
docker compose exec emqx emqx_ctl topics list

# Check mqtt-worker logs
docker compose logs mqtt-worker -f
```

### ESP32 not connecting

1. Verify WiFi credentials in `config.h`
2. Check MQTT host/port — use your server's LAN IP, not `localhost`
3. Monitor serial output: `pio device monitor`
4. Check EMQX client list: `http://localhost:18083` → Clients
