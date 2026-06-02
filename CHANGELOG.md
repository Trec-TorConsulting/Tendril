# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.1.0] — 2026-06-02

### Added
- **Device command framework** — Send commands to ESP32 devices via MQTT with confirmation tracking (#120)
- **Enhanced alerts UI** — Trend-based, composite, and escalation alerts with full frontend management (#119, #120)
- **Field canvas** — Draw.io-style interactive field layout designer replacing the old plot tool (#110)
- **Plant photo diagnosis** — Structured multi-issue diagnosis with severity, confidence, and treatments
- **Plant identification** — Strain identification from photos via Ollama + Gemini vision
- **AI chat with tool-calling** — Chat assistant can query sensors, update settings, look up references
- **Health check photo linking** — Photos attached to health evaluations and displayed in history (#108)
- **Feeding advice caching** — AI feeding recommendations cached until next health check
- **Health status dashboard card** — Overview widget showing latest health score (#97, #98)
- **DB-backed configuration** — Nutrient knowledge, ESPHome templates, and reference data migrated to database (#95, #96)
- **Scheduler leadership heartbeat** — Advisory lock-based leader election with heartbeat monitoring (#99)
- **Tuya integration** — Smart device control via Tuya Cloud API with pH/EC sensor support (#112–#114)
- **Notification tables** — Migration 0004 creates notification channels, preferences, push subscriptions, and log
- **Knowledge Base** — Auto-seeded 5 categories and 21 support articles on startup
- **Reference data seeding** — Auto-seeds 20 strains and 34 nutrient products on startup
- **Feeding mixing order** — Products displayed in correct application order
- **Rate limiting configuration** — Configurable via `RATE_LIMIT_IP` and `RATE_LIMIT_TENANT` env vars

### Changed
- **AI architecture: Ollama-first with Gemini fallback** — All AI features (chat, health check, diagnose, identify, coach tips, insights, feeding advice) now use local Ollama as primary with automatic Gemini cloud fallback. Users never see "AI unavailable" unless both providers are down (#104, #105, #128, #129)
- **Separate vision inference** — Vision models run on a dedicated CPU node (`OLLAMA_VISION_URL`) while chat runs on GPU (`OLLAMA_BASE_URL`) (#104)
- **Python 3.14** — API upgraded from 3.12 to 3.14 (#100, #101)
- **Graceful shutdown** — API pods now have 60s termination grace period with 5s pre-stop hook to drain in-flight requests (#124)
- **Health check scoring** — AI guided to score based on plant health observations, not record-keeping completeness (#125)
- **Data staleness in AI prompts** — All AI contexts now include sensor age warnings and staleness flags (#122, #123)
- Production rate limits increased to 120 IP / 600 tenant per minute
- GitHub Actions CI updated to Node.js 24 runtime

### Fixed
- **AI health check crash** — Previous eval issues stored as `list[dict]` caused `AttributeError: 'dict' object has no attribute 'lower'` (#126)
- **Health check response validation** — Gemini returning issues as dicts caused Pydantic `ValidationError` (#127)
- **Feeding advice logic bug** — Gemini fallback success still raised HTTP 503 due to incorrect exception nesting (#129)
- **Diagnose response parsing** — Unexpected AI response shapes no longer crash with `ValidationError` (#129)
- **Health check camera timeout** — Camera ESP32 offline no longer blocks entire health check (#129)
- **RDWC batch propagation** — Header water changes propagate to site buckets correctly (#115, #117)
- **Tuya pH handling** — Prevent stale log pH from overwriting fresh status values (#112, #113, #114)
- **Outdoor grow UI** — Defensive guards and UI adaptation for soil/outdoor grow types (#116, #118)
- **CI lint** — Suppress false-positive F823 ruff lint on forward-referenced models (#121)
- **Scheduler tasks** — Fixed session handling in dunning and purge jobs
- **Support routes** — Fixed `user.id` → `user.user_id` across all endpoints
- **Team page** — Fixed paginated response extraction
- **Analytics page** — Fixed API shape mismatch causing crash
- **Reference search** — Fixed empty results via auto-seeding on startup

---

## [1.0.0] — 2026

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
