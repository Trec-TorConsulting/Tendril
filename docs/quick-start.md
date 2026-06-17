# Quick Start — 5 Minutes

Get Tendril running locally in under 5 minutes with Docker Compose.

## Prerequisites

- **Docker** 24.0+ ([install](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.20+ (included with Docker Desktop)
- **Git**

No database, MQTT broker, or AI setup needed — all bundled.

## Steps

### 1. Clone the repository

```bash
git clone https://github.com/Trec-TorConsulting/Tendril.git
cd Tendril
```

### 2. Create `.env` file

```bash
cp .env.example .env
```

Edit `.env` and set `JWT_SECRET` to a random string (or keep the default for local testing):

```bash
# For production, generate a strong secret:
openssl rand -hex 32
```

Everything else defaults to local development values.

### 3. Start the stack

```bash
docker compose up -d
```

This starts the full stack: API, Web, PostgreSQL, MQTT, MinIO, Redis, and scheduler.

### 4. Wait for services

```bash
docker compose ps
```

All services should show `healthy` or `running`. Takes 30-60 seconds.

### 5. Create your account

Open **http://localhost:3000** in your browser.

Click **Register**, create your first account. The first user automatically creates your first organization.

### 6. Done!

- **Web app**: http://localhost:3000
- **API docs**: http://localhost:8000/v1/docs
- **EMQX dashboard**: http://localhost:18083 (admin/public)

## What's Running

| Service | Port | Purpose |
|---------|------|---------|
| **tendril-web** | 3000 | Dashboard and grow management |
| **tendril-api** | 8000 | REST API and WebSocket AI chat |
| **PostgreSQL** | 5432 | Database (tendril/tendril) |
| **EMQX** | 1883 | MQTT broker for ESP32 sensors |
| **MinIO** | 9001 | File storage console |
| **Redis** | 6379 | Rate limiting and caching |

## Connecting Sensors

### ESP32 Hardware

1. Flash the firmware (see [ESP32 Hardware Guide](esp32-hardware.md))
2. Set WiFi and MQTT broker to your server's IP address (not `localhost`)
3. Sensors publish to `/t/{tenant_id}/d/{device_id}/telemetry`

### Manual Entry

No sensors? Log readings and observations manually via the **Grow Journal** and **Feeding Log** in the dashboard.

## Next Steps

- **Self-hosting on your server?** → [Self-Hosting Guide](self-hosting.md)
- **Deploying to production?** → [Architecture Overview](architecture.md)
- **Integrating third-party devices?** → See the [README](https://github.com/Trec-TorConsulting/Tendril) for device integrations (Pulse, OpenWeather, Ecowitt)

## Troubleshooting

### Services won't start

```bash
# Check logs
docker compose logs api

# Restart everything
docker compose down
docker compose up -d
```

### Can't access localhost:3000

- Ensure Docker is running
- Check that port 3000 is not in use: `lsof -i :3000`
- Try `docker compose logs web`

### Forgot login

The database is stored in Docker volumes. To reset:

```bash
docker compose down -v    # Remove all volumes
docker compose up -d      # Start fresh
```

## Rate Limits

For local testing, rate limits are disabled. See [Configuration](configuration.md) for production settings.
