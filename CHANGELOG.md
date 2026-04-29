# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- **Enterprise RBAC** — Full role-based access control overhaul with three-tier model:
  - **Platform roles**: `super_admin`, `support`, `readonly_admin`, `user` — controls SaaS-wide access
  - **Tenant roles**: `admin`, `member`, `viewer` — per-organization permissions via `tenant_memberships` table
  - **Account roles**: `owner`, `billing_admin` — billing ownership via `account_members` table
  - ~30 granular permissions across 12 domains (e.g., `grow:create`, `billing:manage`, `platform:users:manage`)
  - Permission-based route guards (`require_permission()`) replace direct role checks
  - Grow-scoped access control via `membership_grow_access` for restricting users to specific grows
  - Account → Tenant hierarchy separating billing from data access
  - Tenant-switching endpoint (`POST /v1/auth/switch-tenant`) for multi-tenant users
  - Tenant-agnostic refresh tokens; per-tenant access tokens with `pr`, `tid`, `tr`, `gs`, `aid` claims
  - Stripe billing fields moved from Tenant to Account model
  - Migration 0024 with full data backfill and downgrade support
- **Pulse Grow connector** — Polls `api.pulsegrow.com` for Pulse One/Pro/Hub devices. Maps ambient readings (temp, humidity, VPD, CO2, lux, dew point, PAR, pressure, VOC) to TentSensorReading and Hub sensors (soil moisture, pH, EC) to BucketSensorReading. Auto-discovery via `/v1/integrations/{id}/discover`. 26 unit tests.
- **OpenWeather connector** — Polls OpenWeather API (free 2.5 + One Call 3.0) for weather data. Maps current conditions + 7-day forecast to WeatherReading. Dew point calculation via Magnus formula. 20 unit tests.
- **Ecowitt connector** — Dual-mode: webhook push from gateway + cloud API polling. Maps weather station → WeatherReading, soil channels (1–16) → BucketSensorReading, temp/humidity channels → TentSensorReading, leaf wetness → BucketSensorReading. Full imperial-to-metric conversion. Device discovery from cloud API. 23 unit tests.
- **Enhanced Open-Meteo** — Added soil temperature (6cm), dew point, and barometric pressure to weather polling. Forecasts now persisted in WeatherReading. Source tracking (`open_meteo`, `openweather`, `ecowitt`, `manual`).
- **Scheduler reading persistence** — Integration poll loop, webhook receiver, and manual sync now persist readings to sensor tables via `BaseConnector.persist_readings()`. Previously data was polled but only logged, never written to sensor tables. 7 unit tests.
- **Integration device discovery** — `POST /v1/integrations/{id}/discover` endpoint for auto-detecting external devices/sensors.
- **Integration manual sync** — `POST /v1/integrations/{id}/sync` endpoint for triggering immediate polls.
- **Migration 0022** — Extended `tent_sensor_readings` with `vpd`, `co2`, `lux`, `dew_point_f`, `par_ppfd`, `air_pressure`, `voc` columns.
- **Migration 0023** — Extended `weather_readings` with `dew_point_c`, `pressure_hpa`, `soil_temp_c`, `source` columns.
- Comprehensive documentation suite (`docs/`)
- Docker Compose for full local development stack
- SECURITY.md and CODE_OF_CONDUCT.md
- AGPL-3.0 license for server, MIT license for ESP32 firmware
- CONTRIBUTING.md with development and OpenSpec workflow guides

---

## [0.1.0] — 2025

Initial extraction as a standalone open-source project.

### Added

#### Core Platform
- Multi-tenant architecture with PostgreSQL Row-Level Security
- JWT authentication with access/refresh tokens, OAuth2 (Google, GitHub)
- Security middleware: CSP, HSTS, rate limiting, brute-force protection

#### Grow Management
- Grow cycle CRUD with multiple grow types (DWC, Kratky, Soil, Coco, NFT, Ebb & Flow)
- Tent/room management with equipment tracking
- Bucket (plant/container) management with strain linking
- Journal entries with photo uploads (S3/MinIO)
- Feeding logs with nutrient dose profiles
- Strain database with AI enrichment
- Harvest yield tracking and cross-grow comparison

#### Sensors & IoT
- ESP32 firmware: BME680 (temp, humidity, pressure, gas) + capacitive soil moisture
- MQTT sensor data pipeline: ESP32 → EMQX → mqtt-worker → PostgreSQL
- Per-bucket and per-tent sensor reading storage
- Device registration and provisioning
- Last-will-and-testament for device online/offline status

#### AI Assistant
- WebSocket chat with context-aware grow recommendations
- Google Gemini and Ollama (local LLM) support
- AI tool calls: query sensor data, generate reports, lookup references
- Automated health reports with scoring and action items
- Full grow context injection: sensors, journal, feedings, equipment, trends

#### Outdoor Grows
- Plot management
- Soil test logging
- Pest observation tracking
- Companion planting suggestions
- Container and runoff monitoring
- Outdoor intelligence recommendations

#### Automation & Notifications
- Configurable automation rules and triggers
- Background scheduler with PostgreSQL leader election
- Web push notifications (VAPID)
- Health check scheduling (12-hour intervals)
- Weather polling for outdoor grows

#### Commercial Features
- Stripe billing integration (checkout, portal, webhooks)
- API key management
- Audit logging
- Custom grow type definitions
- Platform admin panel

#### Frontend (PWA)
- Next.js 16 with React 19 and Tailwind CSS 4
- shadcn/ui component library
- Installable PWA with offline support
- Mobile-first responsive design
- Command palette (Cmd+K)
- Pull-to-refresh and swipeable cards
- Theme toggle (light/dark/system)
- Barcode scanner for nutrients
- Weather widget
- Confetti celebrations on milestones
- Sparkline charts on dashboard cards
- Customizable widget layout
- Onboarding checklist for new users

#### Infrastructure
- Kubernetes manifests for full production deployment
- Horizontal Pod Autoscalers for API and Web
- Docker multi-stage builds (Python slim, Node standalone)
- Build and deploy scripts (`scripts/build.sh`, `scripts/deploy.sh`)
- Alembic database migrations
- OpenSpec spec-driven development workflow with 5 specs and 22 change proposals
