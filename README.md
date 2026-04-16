# Tendril SaaS Platform
# Multi-tenant grow monitoring & automation

## Quick Start

### API (FastAPI)
```bash
cd api
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Web (Next.js)
```bash
cd web
npm install
npm run dev
```

### ESP32 Firmware
```bash
cd esp32
pio run
```

## Architecture
- **tendril-api**: FastAPI HTTP API + WebSocket AI chat
- **tendril-mqtt-worker**: MQTT sensor ingestion from ESP32 devices
- **tendril-scheduler**: Background tasks (health checks, alerts, retention)
- **tendril-web**: Next.js PWA frontend

## Deployment
```bash
kubectl apply -f manifests/
```
