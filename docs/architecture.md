# Architecture Overview

This document describes Tendril's system architecture, service boundaries, data flow, and key design decisions.

## System Diagram

```
                                   ┌──────────────────┐
                                   │    Web Browser    │
                                   │  (Next.js PWA)    │
                                   └────────┬─────────┘
                                            │ HTTPS / WSS
                                   ┌────────┴─────────┐
                                   │     Ingress       │
                                   │  (nginx / Traefik)│
                                   └──┬────────────┬───┘
                                      │            │
                            ┌─────────┴──┐   ┌────┴──────────┐
                            │ tendril-web │   │  tendril-api  │
                            │  (Next.js)  │   │  (FastAPI)    │
                            │  Port 3000  │   │  Port 8000    │
                            └─────────────┘   └───┬──────┬────┘
                                                  │      │
                               ┌──────────────────┤      ├───────────────┐
                               │                  │      │               │
                          ┌────┴─────┐    ┌───────┴──┐  ┌┴────────┐ ┌───┴──────┐
                          │PostgreSQL │    │  MinIO   │  │  EMQX   │ │ Ollama / │
                          │  (RLS)   │    │  (S3)    │  │  MQTT   │ │ Gemini   │
                          └────┬─────┘    └──────────┘  └────┬────┘ └──────────┘
                               │                              │
                    ┌──────────┤                              │
                    │          │                              │
          ┌────────┴───┐ ┌────┴──────────┐          ┌───────┴────────┐
          │  tendril-   │ │   tendril-    │          │    ESP32       │
          │  scheduler  │ │   mqtt-worker │          │    Sensors     │
          └─────────────┘ └───────────────┘          └────────────────┘
```

## Services

### tendril-api

The primary HTTP API and WebSocket server. Handles all client requests.

| Aspect | Detail |
|--------|--------|
| Runtime | Python 3.12, FastAPI, Uvicorn |
| Database | SQLAlchemy 2.0 (async), asyncpg driver |
| Auth | JWT (HS256) with access + refresh tokens |
| Middleware | Security headers (CSP, HSTS, X-Frame-Options), rate limiting, brute-force protection |
| File storage | S3/MinIO via boto3 |
| AI | Google Gemini + Ollama (local LLM) via HTTP |

**Router modules** (30+ route groups):

| Domain | Routers | Prefix |
|--------|---------|--------|
| Auth | `auth` | `/v1/auth` |
| Tenants | `tenants` | `/v1/tenants` |
| Devices | `devices` | `/v1/devices` |
| Grows | `grow-types`, `tents`, `grows`, `buckets`, `journal`, `photos`, `feeding`, `strains`, `yields` | `/v1/grows`, `/v1/tents`, etc. |
| Sensors | `sensors`, `tent-sensors` | `/v1/sensors`, `/v1/tent-sensors` |
| AI | `ai` | `/v1/ai` |
| Automation | `automation` | `/v1/automation` |
| Notifications | `notifications` | `/v1/notifications` |
| Billing | `billing` | `/v1/billing` |
| Outdoor | `plots`, `soil`, `pests`, `yields`, `companions`, `intelligence`, `containers`, `runoff` | `/v1/grows/*`, `/v1/outdoor/*` |
| Integrations | `integrations` | `/v1/integrations` |
| Commercial | `custom-grow-types`, `tasks`, `audit`, `api-keys` | `/v1/custom-grow-types`, etc. |
| Admin | `admin` | `/v1/admin` |

### tendril-web

The frontend Progressive Web App. Installable on mobile and desktop with offline support.

| Aspect | Detail |
|--------|--------|
| Framework | Next.js 16, React 19 |
| Styling | Tailwind CSS 4, shadcn/ui |
| State | React hooks, server components |
| PWA | next-pwa with service worker |
| Charts | Recharts |
| Forms | React Hook Form + Zod validation |
| Animations | Framer Motion |

**Route groups:**
- `(auth)` — Login, register, email verification
- `(marketing)` — Landing page, pricing
- `dashboard/` — Main grow dashboard with widget layout
- `platform/` — Settings, billing, admin

### tendril-mqtt-worker

A headless Python process that subscribes to MQTT topics and writes sensor data to PostgreSQL.

| Aspect | Detail |
|--------|--------|
| Library | aiomqtt (async MQTT client) |
| Topics | `t/{tenant_id}/d/{device_id}/sensor/#`, `t/{tenant_id}/d/{device_id}/status` |
| Reconnect | Auto-reconnect with 5s backoff |
| Data routing | `sensor/ambient` → `tent_sensor_readings`, `sensor/readings` → `bucket_sensor_readings` |

### tendril-scheduler

A background task runner using PostgreSQL advisory locks for leader election. Only one replica runs tasks at a time.

| Aspect | Detail |
|--------|--------|
| Leader election | `pg_try_advisory_lock(999001)` |
| Health checks | AI-powered grow health evaluations (every 12h) |
| Alerts | Sensor threshold monitoring |
| Data retention | Cleanup of old readings |
| Weather | Open-Meteo polling for outdoor grows (every 30min) |
| Integration polling | Polls enabled integrations (Pulse, OpenWeather, Ecowitt) on configurable intervals, persists readings to sensor tables |
| Reports | Daily/weekly grow summaries |

### ESP32 Firmware

Arduino C++ firmware for ESP32-WROOM-32 boards. Reads sensors and publishes to MQTT.

| Aspect | Detail |
|--------|--------|
| Platform | PlatformIO, Arduino framework |
| Sensors | BME680 (I2C), capacitive soil moisture (analog) |
| Protocol | MQTT via PubSubClient |
| Reconnect | Auto WiFi + MQTT reconnect |
| Last Will | Publishes `{"status":"offline"}` on disconnect |
| Interval | 30s sensor polling, 60s heartbeat |

## Data Flow

### Sensor Data Pipeline

```
ESP32 reads sensors
    │
    ▼
Publish to MQTT topic: t/{tenant}/d/{device}/sensor/{type}
    │
    ▼
EMQX broker receives and routes
    │
    ▼
mqtt-worker subscribes, parses JSON payload
    │
    ▼
Lookup device → bucket/tent mapping in PostgreSQL
    │
    ▼
Insert into bucket_sensor_readings or tent_sensor_readings
    │
    ▼
Dashboard queries via REST API → displays real-time data
```

### MQTT Topic Structure

```
t/{tenant_id}/d/{device_id}/sensor/readings    → Bucket-level (soil moisture, pH, EC)
t/{tenant_id}/d/{device_id}/sensor/ambient     → Tent-level (temp, humidity, pressure, gas)
t/{tenant_id}/d/{device_id}/status             → Device online/offline (last-will)
```

### AI Chat Flow

```
User sends message via WebSocket
    │
    ▼
API gathers context:
  - Current grow cycle details
  - Recent sensor readings & trends
  - Journal entries & feeding history
  - Tent equipment list
  - Previous health evaluations
    │
    ▼
Build prompt with full grow context
    │
    ▼
Send to Gemini API or local Ollama
    │
    ▼
AI responds with recommendations, can invoke tools:
  - Query sensor data
  - Generate health reports
  - Look up reference data
    │
    ▼
Stream response back to client via WebSocket
```

## Database Design

### Multi-Tenancy via Row-Level Security (RLS)

Tendril uses PostgreSQL RLS for tenant isolation. Every request sets a session variable:

```sql
SET app.current_tenant = '{tenant_uuid}';
```

All tenant-scoped tables have RLS policies that filter by this variable. The `tenant_session()` context manager in Python handles this automatically.

### Key Tables

| Table | Purpose | Scope |
|-------|---------|-------|
| `tenants` | Organizations | Global |
| `users` | User accounts, roles | Global |
| `devices` | Registered ESP32 devices | Tenant |
| `grow_cycles` | Tracked grow cycles | Tenant |
| `tents` | Grow rooms/tents with equipment | Tenant |
| `buckets` | Individual plants/containers within a grow | Tenant |
| `bucket_sensor_readings` | Per-bucket sensor timeseries | Tenant |
| `tent_sensor_readings` | Per-tent ambient sensor timeseries | Tenant |
| `journal_entries` | Grow journal with photos | Tenant |
| `feeding_logs` | Nutrient feeding records | Tenant |
| `strains` | Strain database | Tenant |
| `weather_readings` | Weather data from Open-Meteo, OpenWeather, Ecowitt | Tenant |
| `integration_configs` | Third-party integration credentials and settings | Tenant |
| `integration_device_maps` | Maps external devices to tents/buckets | Tenant |
| `integration_sync_logs` | Sync history and error tracking | Tenant |
| `automations` | Automation rules and triggers | Tenant |

### Migrations

Alembic manages schema migrations in `api/migrations/versions/`. Migrations run as a Kubernetes Job before deployments, or via `alembic upgrade head` locally.

## Security Architecture

### Authentication

- JWT-based with short-lived access tokens (15min) and long-lived refresh tokens (7 days)
- OAuth2 support for Google and GitHub
- Passwords hashed with bcrypt

### Middleware Stack

1. **SecurityHeadersMiddleware** — CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
2. **RateLimiter** — Request rate limiting
3. **BruteForceProtection** — Login attempt throttling
4. **CORS** — Configurable allowed origins

### Device Authentication

ESP32 devices authenticate to EMQX using device ID as username and a pre-shared key as password. The MQTT broker can be configured to validate credentials via an HTTP webhook to the Tendril API.

## Infrastructure

### Kubernetes Deployment

The `manifests/` directory contains a complete production deployment:

| Manifest | Replicas | Notes |
|----------|----------|-------|
| `api-deployment.yaml` | Scalable (HPA) | Stateless, horizontally scalable |
| `web-deployment.yaml` | Scalable (HPA) | Next.js standalone output |
| `mqtt-worker-deployment.yaml` | 1 | Single subscriber per topic set |
| `scheduler-deployment.yaml` | 1+ | Leader election via advisory lock |
| `db-migration-job.yaml` | Job | Runs once per deploy |

### Docker Images

Both `api/Dockerfile` and `web/Dockerfile` produce optimized production images:

- **API**: `python:3.12-slim-bookworm`, ~200MB
- **Web**: Multi-stage build with `node:20-slim`, Next.js standalone output, ~150MB

### External Dependencies

| Service | Required | Purpose |
|---------|----------|---------|
| PostgreSQL 15+ | Yes | Primary datastore with RLS |
| EMQX / Mosquitto | Yes | MQTT broker for sensor data |
| MinIO / S3 | Yes | Photo and file storage |
| Ollama | Optional | Local AI models |
| Google Gemini | Optional | Cloud AI for health checks |
| Stripe | Optional | Subscription billing |
| OpenWeather API | Optional | Enhanced weather data (free 2.5 + One Call 3.0) |
| Ecowitt API/Gateway | Optional | Weather stations, soil probes (webhook + cloud API) |
| Pulse Grow API | Optional | Pulse One/Pro/Hub environmental monitors |
