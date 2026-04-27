<div align="center">

# 🌱 Tendril

**Open-source grow monitoring & automation platform**

ESP32 IoT sensors · FastAPI backend · Next.js PWA · AI grow assistant

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Firmware: MIT](https://img.shields.io/badge/Firmware-MIT-green.svg)](esp32/LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org)
[![PlatformIO](https://img.shields.io/badge/PlatformIO-ESP32-orange.svg)](https://platformio.org)

</div>

---

Tendril is a self-hostable, multi-tenant platform for monitoring and automating grow environments. It connects ESP32 sensor hardware to a real-time dashboard with AI-powered recommendations — whether you're running a single tent or managing a commercial operation.

## Features

- **Real-time environment monitoring** — Temperature, humidity, and soil moisture via ESP32 sensors over MQTT
- **Grow journal & feeding logs** — Track every grow cycle, feeding schedule, and observation with photos
- **AI grow assistant** — Chat-based recommendations powered by Google Gemini or local Ollama models, grounded in your actual sensor data and grow history
- **Multi-tenant architecture** — Isolated data per tenant with role-based access
- **Outdoor & soil grows** — Plot management, soil tests, pest tracking, companion planting, runoff monitoring
- **Strain & yield tracking** — Log strains, record yields, compare across grows
- **Automation workflows** — Configurable rules and scheduled tasks for alerts and actions
- **Mobile-first PWA** — Installable, offline-capable, with pull-to-refresh and swipe gestures
- **Barcode scanning** — Scan nutrients and products directly from your phone
- **Weather integration** — Local weather data alongside your sensor readings
- **Notifications** — Web push alerts for sensor thresholds and health checks
- **Commercial features** — API keys, audit logs, custom grow types, Stripe billing
- **Kubernetes-ready** — Full manifest set with HPA autoscaling, ingress, and DB migrations

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Tendril Platform                         │
├─────────────┬─────────────┬──────────────┬─────────────────────┤
│             │             │              │                     │
│  tendril-   │  tendril-   │  tendril-    │  tendril-           │
│  web        │  api        │  mqtt-worker │  scheduler          │
│             │             │              │                     │
│  Next.js    │  FastAPI    │  MQTT →      │  Background         │
│  PWA        │  REST +     │  Sensor      │  health checks,     │
│  React 19   │  WebSocket  │  ingestion   │  alerts, retention  │
│  Tailwind   │  AI chat    │              │                     │
│             │             │              │                     │
└──────┬──────┴──────┬──────┴───────┬──────┴─────────────────────┘
       │             │              │
       │        ┌────┴────┐    ┌────┴────┐
       │        │ Postgres │    │  EMQX   │
       │        │   + S3   │    │  MQTT   │
       │        └─────────┘    └────┬────┘
       │                            │
       │                     ┌──────┴──────┐
       │                     │   ESP32     │
       │                     │   Sensors   │
       │                     │  BME680 +   │
       │                     │  Soil Probe │
       │                     └─────────────┘
```

| Service | Description | Tech |
|---------|-------------|------|
| **tendril-api** | REST API, WebSocket AI chat, auth, billing | Python 3.12, FastAPI, SQLAlchemy, Alembic |
| **tendril-web** | Dashboard, grow management, mobile PWA | TypeScript, Next.js 16, React 19, Tailwind, shadcn/ui |
| **tendril-mqtt-worker** | Ingests sensor data from MQTT broker | Python, aiomqtt |
| **tendril-scheduler** | Background tasks: health checks, alerts, data retention | Python |
| **esp32 firmware** | Reads sensors, publishes to MQTT | C++, Arduino, PlatformIO |

## Project Structure

```
tendril/
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── ai/             # AI assistant (Gemini, Ollama, tools, reports)
│   │   ├── auth/           # JWT authentication
│   │   ├── automation/     # Workflow automation
│   │   ├── billing/        # Stripe integration
│   │   ├── buckets/        # Monitored containers
│   │   ├── commercial/     # API keys, audit logs, custom grow types
│   │   ├── devices/        # Device management & provisioning
│   │   ├── grows/          # Grows, tents, journals, feedings, strains, yields
│   │   ├── mqtt/           # MQTT client, handlers, auth webhook
│   │   ├── notifications/  # Web push alerts
│   │   ├── outdoor/        # Plots, soil tests, pests, companions, runoff
│   │   ├── scheduler/      # Background task runner
│   │   ├── sensors/        # Sensor data routes
│   │   ├── tenants/        # Multi-tenant management
│   │   └── weather/        # Weather integration
│   ├── migrations/         # Alembic database migrations
│   └── tests/              # pytest test suite
├── web/                    # Next.js PWA frontend
│   ├── src/
│   │   ├── app/            # Next.js routes (auth, dashboard, platform, marketing)
│   │   ├── components/     # React components + shadcn/ui library
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Utilities and API client
│   │   └── types/          # TypeScript type definitions
│   └── e2e/                # End-to-end tests
├── esp32/                  # ESP32 IoT firmware
│   └── src/                # Arduino C++ (BME680 + capacitive soil sensor)
├── manifests/              # Kubernetes deployment manifests
├── scripts/                # Build and deploy scripts
└── openspec/               # Specs and change proposals
```

## Getting Started

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | API backend |
| Node.js | 20+ | Web frontend |
| PostgreSQL | 15+ | Database |
| PlatformIO | Latest | ESP32 firmware |
| MQTT Broker | EMQX or Mosquitto | Sensor data transport |

### 1. API

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env   # Edit with your database URL, secrets, etc.

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000` with interactive docs at `/v1/docs`.

### 2. Web

```bash
cd web
npm install
npm run dev
```

The web app runs at `http://localhost:3000`.

### 3. ESP32 Firmware

```bash
cd esp32
cp src/config.example.h src/config.h
# Edit config.h with your WiFi, MQTT broker, and device settings

pio run            # Compile
pio run -t upload  # Flash to device
pio device monitor # View serial output
```

The firmware reads from a BME680 (temperature, humidity, gas resistance) and a capacitive soil moisture sensor, publishing data over MQTT every 30 seconds.

## Deployment

### Docker

Build images for API and web:

```bash
# Build both
./scripts/build.sh

# Or individually
./scripts/build.sh api
./scripts/build.sh web
```

### Kubernetes

Full manifest set included for production deployment:

```bash
# Deploy everything
./scripts/deploy.sh
```

This applies: namespace → secrets → DB migration job → API + MQTT worker + scheduler + web deployments → services → ingress. HPA autoscaling is configured for both API and web.

| Manifest | Purpose |
|----------|---------|
| `namespace.yaml` | `tendril` namespace |
| `db-migration-job.yaml` | Runs Alembic migrations |
| `api-deployment.yaml` | API server pods |
| `mqtt-worker-deployment.yaml` | MQTT ingestion worker |
| `scheduler-deployment.yaml` | Background task scheduler |
| `web-deployment.yaml` | Next.js frontend pods |
| `hpa-api.yaml` / `hpa-web.yaml` | Horizontal Pod Autoscalers |
| `ingress.yaml` | Ingress routing |

## API Endpoints

The API exposes 30+ route groups. Key areas:

| Group | Endpoints | Description |
|-------|-----------|-------------|
| `/v1/auth` | Login, register, refresh | JWT authentication |
| `/v1/grows` | CRUD + lifecycle | Grow cycle management |
| `/v1/tents` | CRUD | Grow tent/room management |
| `/v1/buckets` | CRUD | Monitored containers (DWC, Kratky, soil) |
| `/v1/sensors` | Query | Sensor data timeseries |
| `/v1/feeding` | Log, schedule | Nutrient feeding records |
| `/v1/journal` | CRUD + photos | Grow journal entries |
| `/v1/strains` | CRUD | Strain database |
| `/v1/ai` | Chat, reports | AI grow assistant (WebSocket) |
| `/v1/devices` | Register, provision | ESP32 device management |
| `/v1/automation` | Rules, triggers | Automation workflows |
| `/v1/weather` | Current, forecast | Weather integration |
| `/v1/outdoor` | Plots, soil, pests | Outdoor grow management |
| `/v1/billing` | Stripe webhooks | Subscription management |
| `/v1/admin` | Tenant management | Admin panel |

Full OpenAPI docs available at `/v1/docs` when running.

## AI Assistant

Tendril includes a built-in AI grow assistant accessible via WebSocket chat:

- **Google Gemini** — Cloud-based, high-quality recommendations
- **Ollama** — Self-hosted local models for full privacy
- **Context-aware** — Pulls in your sensor data, grow history, and journal entries
- **Tool calls** — Can query your data, generate reports, and trigger actions
- **Reports** — Automated grow health reports based on sensor trends

## ESP32 Hardware

### Supported Sensors

| Sensor | Measurements | Interface |
|--------|-------------|-----------|
| BME680 | Temperature, humidity, pressure, gas resistance | I2C (SDA: 21, SCL: 22) |
| Capacitive soil moisture | Soil moisture % | Analog (GPIO 34) |

### Wiring (ESP32-WROOM-32)

| ESP32 Pin | Connection |
|-----------|------------|
| GPIO 21 (SDA) | BME680 SDA |
| GPIO 22 (SCL) | BME680 SCL |
| GPIO 34 | Soil moisture signal |
| 3.3V | Sensor VCC |
| GND | Sensor GND |

### MQTT Topics

Devices publish sensor readings and heartbeats to topics scoped by device ID. The MQTT worker authenticates devices via a webhook and routes data to the appropriate tenant.

## Development

### Running Tests

```bash
# API tests
cd api && pytest

# Web tests
cd web && npm test

# Web type checking
cd web && npm run type-check

# Web linting
cd web && npm run lint
```

### OpenSpec Workflow

This project uses [OpenSpec](openspec/AGENTS.md) for spec-driven development. Larger changes go through a proposal → review → implement → archive lifecycle. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Current Specs

| Spec | Description |
|------|-------------|
| `bucket-monitoring` | Container-level monitoring (pH, EC, water level) |
| `camera-health-checks` | Visual health assessment via camera |
| `environment-monitoring` | Temperature, humidity, CO2, VPD tracking |
| `grow-assistant-core` | AI assistant capabilities and tool framework |
| `integrations-framework` | Plugin architecture for third-party devices and services |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, coding guidelines, and the PR workflow.

## Documentation

| Guide | Description |
|-------|-------------|
| [Architecture Overview](docs/architecture.md) | System design, services, data flow |
| [Self-Hosting Guide](docs/self-hosting.md) | Deploy with Docker Compose or Kubernetes |
| [Configuration Reference](docs/configuration.md) | All environment variables and config options |
| [ESP32 Hardware Guide](docs/esp32-hardware.md) | BOM, wiring, calibration, flashing |
| [API Reference](docs/api-reference.md) | Auth flows, endpoints, WebSocket chat |
| [Developer Guide](docs/development.md) | Local setup, testing, conventions |
| [Security Policy](SECURITY.md) | Vulnerability reporting |
| [Changelog](CHANGELOG.md) | Version history |

## License

This project is dual-licensed:

| Component | License | File |
|-----------|---------|------|
| API, Web, Manifests, Scripts | [AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html) | [LICENSE](LICENSE) |
| ESP32 Firmware (`esp32/`) | [MIT](https://opensource.org/licenses/MIT) | [esp32/LICENSE](esp32/LICENSE) |

The AGPL-3.0 ensures that anyone running a modified version of the server must share their changes. The ESP32 firmware uses MIT so you can freely flash and modify it on your own hardware without source-sharing obligations.

© Tobey Rector
```
