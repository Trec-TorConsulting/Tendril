## Context
Tendril is a greenfield multi-tenant SaaS platform for hydroponic/indoor grow monitoring and automation. It replaces the single-tenant grow-assistant with a production-grade architecture supporting unlimited tenants, secure IoT device connectivity, and a modern React frontend. It supports both indoor and outdoor/greenhouse grows, with weather integration for outdoor environments. Deployed initially on a K3S home lab cluster with a path to cloud migration.

## Goals
- Multi-tenant isolation at the database level (PostgreSQL RLS)
- Secure IoT device pairing and communication (EMQX + TLS + per-device credentials)
- Modern, responsive frontend (Next.js + React)
- Flexible authentication supporting email/password + multiple social/enterprise providers
- Full feature parity with grow-assistant at launch
- Clean API design suitable for third-party integrations and mobile apps

## Non-Goals
- Mobile native apps (v1 is responsive web only)
- Cloud migration (stays on K3S for now)
- Custom firmware builder for ESP32 (customers get pre-flashed kits per grow type)
- White-labeling

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Customer Site                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────┐  │
│  │ WiFi Cam │  │ WiFi Cam │  │ ESP32 Sensor Hub             │  │
│  │ (RTSP)   │  │ (RTSP)   │  │ pH, EC, Water Temp, Air T/H │  │
│  │          │  │          │  │ Water Level                  │  │
│  └────┬─────┘  └────┬─────┘  └──────────┬───────────────────┘  │
│       │              │                   │                      │
│       └──────────────┴───────────────────┘                      │
│                      │ MQTT over TLS (port 8883)                │
│                      │ Device cert / token auth                 │
└──────────────────────┼──────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                     K3S Cluster                                  │
│                                                                  │
│  ┌────────────────┐    ┌──────────────────────────────────────┐  │
│  │ EMQX Broker    │    │ Traefik Ingress                     │  │
│  │ - TLS termination│   │ - tendril.app → Next.js             │  │
│  │ - ACL per device│   │ - api.tendril.app → FastAPI          │  │
│  │ - Topic routing │   └──────┬───────────────────────────────┘  │
│  └───────┬────────┘          │                                   │
│          │                   │                                   │
│          ▼                   ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │ tendril-api (Deployment, scales horizontally)           │     │
│  │ FastAPI — HTTP API + WebSocket AI chat                  │     │
│  │ ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐   │     │
│  │ │ Auth    │ │ Tenant   │ │ Grows    │ │ AI Chat    │   │     │
│  │ │ Routes  │ │ Context  │ │ Buckets  │ │ WebSocket  │   │     │
│  │ │ RBAC    │ │ RLS      │ │ Sensors  │ │ Ollama     │   │     │
│  │ └─────────┘ └──────────┘ └──────────┘ └────────────┘   │     │
│  └─────────────────────────┬───────────────────────────────┘     │
│                            │                                     │
│  ┌─────────────────────────┼───────────────────────────────┐     │
│  │ tendril-mqtt-worker (Deployment, scales by device count)│     │
│  │ MQTT subscriber — ingests sensor data from all tenants  │     │
│  │ ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐  │     │
│  │ │ MQTT Client  │ │ Sensor       │ │ EMQX Auth/ACL   │  │     │
│  │ │ Subscribe    │ │ Ingestion    │ │ Webhooks        │  │     │
│  │ │ t/+/d/+/#   │ │ Parse+Store  │ │ Device Verify   │  │     │
│  │ └──────────────┘ └──────────────┘ └─────────────────┘  │     │
│  └─────────────────────────┼───────────────────────────────┘     │
│                            │                                     │
│  ┌─────────────────────────┼───────────────────────────────┐     │
│  │ tendril-scheduler (Deployment, single replica + leader) │     │
│  │ Background tasks — health checks, alerts, retention     │     │
│  │ ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐  │     │
│  │ │ Health Check │ │ Alert Eval   │ │ Data Retention  │  │     │
│  │ │ (12h/tent)   │ │ Threshold    │ │ Prune old data  │  │     │
│  │ │ Ollama AI    │ │ Notify       │ │ Daily reports   │  │     │
│  │ └──────────────┘ └──────────────┘ └─────────────────┘  │     │
│  └─────────────────────────┼───────────────────────────────┘     │
│                            │                                     │
│  ┌─────────────────────────▼───────────────────────────────┐     │
│  │ PostgreSQL (RLS enabled)                                │     │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │     │
│  │ │ tenants  │ │ users    │ │ devices  │ │ grows      │  │     │
│  │ │          │ │          │ │          │ │ buckets    │  │     │
│  │ │          │ │          │ │          │ │ sensors    │  │     │
│  │ └──────────┘ └──────────┘ └──────────┘ └────────────┘  │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                  │
│  ┌──────────────────────────────┐  ┌─────────────────────────┐   │
│  │ tendril-web (Deployment)     │  │ Ollama (GPU - Node05)   │   │
│  │ Next.js PWA                  │  │ - AI Chat               │   │
│  │ - SSR landing/auth pages     │  │ - Health Checks         │   │
│  │ - SPA dashboard              │  │ - Coach Tips            │   │
│  │ - Responsive (mobile-first)  │  │                         │   │
│  └──────────────────────────────┘  └─────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### Deployment Pods

| Pod | Replicas | Scaling Trigger | Resource Profile |
|-----|----------|-----------------|------------------|
| `tendril-api` | 2+ | HTTP request volume | CPU-bound, low memory |
| `tendril-mqtt-worker` | 1-3 | Device count / msg throughput | I/O-bound, moderate memory |
| `tendril-scheduler` | 1 (leader election) | N/A — single instance | CPU spikes during AI calls |
| `tendril-web` | 2+ | Page request volume | Low CPU, low memory |

All pods share the same codebase (`tendril/api/`) but run different entrypoints:
- `tendril-api`: `uvicorn app.main:app`
- `tendril-mqtt-worker`: `python -m app.mqtt.worker`
- `tendril-scheduler`: `python -m app.scheduler.main`

## Decisions

### 1. Multi-Tenancy: Shared DB + RLS
- **Decision**: Single PostgreSQL database, `tenant_id UUID` on every data table, Row-Level Security policies enforce isolation
- **Why**: Simplest to operate, cheapest, good enough for thousands of tenants. Schema-per-tenant adds migration complexity; DB-per-tenant is overkill at this scale
- **Implementation**: Every query goes through a `set_tenant(tenant_id)` context that sets `app.current_tenant` session variable; RLS policies filter automatically

### 2. Authentication: Built-in JWT + Social Providers
- **Decision**: Core auth is email/password with bcrypt + JWT (access + refresh tokens). Social login via OAuth2 (Google, GitHub, Apple, Discord). Optional Auth0/Firebase/Supabase as identity providers via adapter pattern
- **Why**: Maximum flexibility. Built-in auth means no external dependency for core flow. Adapter pattern lets customers or deployments plug in enterprise IdPs
- **Implementation**: `python-jose` for JWT, `authlib` for OAuth2 flows, adapter interface for external IdPs

### 3. IoT Device Security
- **Decision**: Each ESP32 ships with a unique device ID + pre-shared key (PSK). Customer pairs via QR code scan in web app. EMQX authenticates devices via HTTP auth webhook to FastAPI
- **Why**: X.509 certs are ideal but complex to provision on ESP32 at scale. PSK + device ID is simpler for v1, upgradeable to certs later
- **Pairing flow**: QR code contains device_id → user scans in app → API links device to tenant → EMQX webhook validates device_id+PSK on connect → device publishes to `t/{tenant_id}/d/{device_id}/sensor/#`
- **ACL enforcement**: EMQX HTTP ACL webhook checks device→tenant mapping. Devices can only publish to their tenant's topics

### 4. Frontend: Next.js PWA (App Router)
- **Decision**: Next.js 14+ with App Router, React Server Components for landing/auth pages, client components for dashboard SPA. Configured as a Progressive Web App (installable, offline-capable)
- **Why**: SSR for SEO (landing pages, docs), React ecosystem for dashboard components, built-in API routes for BFF pattern if needed. PWA gives native-app feel on mobile without app store distribution
- **Styling**: Tailwind CSS + shadcn/ui components
- **PWA features**:
  - Service worker with `next-pwa` for offline caching (dashboard shell, static assets, recent data)
  - Web App Manifest (name, icons, theme color, display: standalone)
  - Push notifications via Web Push API (sensor alerts, health check results)
  - Add-to-homescreen prompt on mobile
  - Background sync for sensor data submitted while offline

### 5. API Design
- **Decision**: RESTful API at `api.tendril.app`, versioned (`/v1/`), all endpoints require Bearer token except auth routes. Tenant context derived from JWT claims
- **Rate limiting**: Traefik middleware per IP + per-tenant limits in app layer
- **WebSocket**: `/v1/ws/chat` for AI chat (authenticated via ticket token)

### 6. Camera Strategy (v1)
- **Decision**: Customers provide camera snapshot URLs (RTSP/HTTP). Backend fetches snapshots on-demand via customer-configured URLs stored per tent. No NAT traversal in v1
- **Why**: NAT traversal/relay is complex. Most WiFi cameras support local RTSP + cloud viewing. For health checks, we fetch snapshots from configured URLs
- **Future**: Consider WebRTC relay or Tailscale/WireGuard tunnel for direct access

### 7. Project Structure
```
tendril/
├── api/                          # FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI app + startup
│   │   ├── config.py             # Environment config
│   │   ├── database.py           # PostgreSQL + RLS setup
│   │   ├── auth/
│   │   │   ├── jwt.py            # Token create/verify
│   │   │   ├── oauth.py          # Social login providers
│   │   │   ├── middleware.py     # Auth middleware
│   │   │   └── adapters/        # Auth0, Firebase, etc.
│   │   ├── tenants/
│   │   │   ├── models.py         # Tenant + User models
│   │   │   ├── service.py        # Tenant CRUD
│   │   │   └── routes.py         # Tenant API
│   │   ├── devices/
│   │   │   ├── models.py         # Device models
│   │   │   ├── service.py        # Pairing, provisioning
│   │   │   ├── routes.py         # Device API
│   │   │   └── mqtt_auth.py      # EMQX webhook handlers
│   │   ├── grows/
│   │   │   ├── models.py
│   │   │   ├── service.py
│   │   │   ├── routes.py
│   │   │   └── grow_types.py        # Grow type profiles registry + seed data
│   │   ├── buckets/
│   │   │   ├── models.py
│   │   │   ├── service.py
│   │   │   └── routes.py
│   │   ├── sensors/
│   │   │   ├── models.py
│   │   │   ├── service.py
│   │   │   └── routes.py
│   │   ├── ai/
│   │   │   ├── chat.py           # WebSocket AI chat
│   │   │   ├── health_check.py   # Vision health checks
│   │   │   └── coach.py          # Coach tips
│   │   ├── notifications/
│   │   │   ├── service.py
│   │   │   ├── routes.py
│   │   │   └── channels/        # Discord, Slack, Email, SMS
│   │   ├── weather/
│   │   │   ├── models.py         # WeatherReading model
│   │   │   ├── service.py        # Open-Meteo fetch, cache, store
│   │   │   ├── routes.py         # Weather API (current, forecast, history)
│   │   │   └── alerts.py         # Frost, heat, rain, wind, UV alert logic
│   │   ├── billing/
│   │   │   ├── service.py        # Stripe Checkout, Customer, Webhook handling
│   │   │   ├── routes.py         # Billing API (create checkout, portal link)
│   │   │   └── webhooks.py       # Stripe webhook event handlers
│   │   ├── reference/
│   │   │   ├── models.py         # ReferenceStrain, NutrientProduct, seed data models
│   │   │   ├── service.py        # Otreeba sync, Open Food Facts barcode lookup
│   │   │   └── routes.py         # Strain autocomplete, barcode scan, seed data lists
│   │   ├── scheduler/
│   │   │   ├── main.py            # Scheduler entrypoint (standalone process)
│   │   │   ├── leader.py          # Leader election (single active instance)
│   │   │   └── tasks.py           # Health checks, retention, reports
│   │   └── mqtt/
│   │       ├── worker.py          # MQTT worker entrypoint (standalone process)
│   │       ├── client.py          # EMQX connection
│   │       ├── handlers.py        # Sensor message handlers
│   │       └── auth_webhook.py    # EMQX auth/ACL webhook handlers
│   ├── migrations/               # Alembic DB migrations
│   ├── tests/
│   │   ├── conftest.py           # Fixtures: test DB, tenant factory, auth helpers
│   │   ├── unit/
│   │   │   ├── test_auth.py
│   │   │   ├── test_tenant_isolation.py
│   │   │   ├── test_rbac.py
│   │   │   ├── test_device_pairing.py
│   │   │   └── test_owasp.py     # Cross-tenant, injection, token tampering
│   │   ├── integration/
│   │   │   ├── test_api_grows.py
│   │   │   ├── test_api_buckets.py
│   │   │   ├── test_api_sensors.py
│   │   │   ├── test_mqtt_auth.py
│   │   │   └── test_mqtt_ingestion.py
│   │   └── security/
│   │       ├── test_access_control.py
│   │       ├── test_injection.py
│   │       └── test_auth_failures.py
│   ├── Dockerfile
│   └── requirements.txt
├── web/                          # Next.js frontend
│   ├── app/
│   │   ├── (auth)/              # Auth pages (login, register, forgot)
│   │   ├── (marketing)/         # Landing, pricing, docs
│   │   ├── dashboard/           # Authenticated SPA
│   │   │   ├── page.tsx         # Dashboard home
│   │   │   ├── grows/
│   │   │   ├── analytics/
│   │   │   ├── chat/
│   │   │   ├── settings/
│   │   │   ├── devices/        # Device management + pairing
│   │   │   └── strains/
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                  # shadcn/ui
│   │   └── dashboard/           # Dashboard-specific
│   ├── lib/
│   │   ├── api.ts               # API client
│   │   ├── auth.ts              # Auth helpers
│   │   └── mqtt.ts              # MQTT WebSocket for live data
│   ├── public/
│   │   ├── manifest.json        # PWA manifest
│   │   ├── sw.js                # Service worker (generated)
│   │   └── icons/               # PWA icons (192, 512)
│   ├── Dockerfile
│   ├── next.config.js           # next-pwa config
│   ├── package.json
│   └── tailwind.config.ts
├── manifests/                    # K8s deployment manifests
│   ├── namespace.yaml
│   ├── api-deployment.yaml       # tendril-api (HTTP + WebSocket)
│   ├── mqtt-worker-deployment.yaml  # tendril-mqtt-worker (MQTT ingestion)
│   ├── scheduler-deployment.yaml    # tendril-scheduler (background tasks)
│   ├── web-deployment.yaml       # tendril-web (Next.js PWA)
│   ├── api-service.yaml
│   ├── mqtt-worker-service.yaml  # Internal only (EMQX webhooks)
│   ├── web-service.yaml
│   ├── ingress.yaml
│   ├── db-migration-job.yaml
│   ├── hpa-api.yaml              # HorizontalPodAutoscaler for API
│   └── secrets.yaml
├── esp32/                        # ESP32 firmware (reference)
│   ├── src/
│   │   ├── main.cpp
│   │   ├── mqtt_client.cpp
│   │   ├── sensors.cpp
│   │   └── config.h
│   └── platformio.ini
└── README.md
```

## Database Schema (Core Tables)

### Pricing Tier Feature Gating

Tier limits are enforced in the API middleware layer. The `tenants.plan` column determines the active tier.

| Feature | Seedling (Free) | Grower ($14.99) | Pro ($29.99) | Commercial ($79.99) |
|---------|----------------|-----------------|--------------|---------------------|
| Tents | 1 | 2 | 5 | Unlimited |
| Buckets | 2 | 10 | 25 | Unlimited |
| Devices | 0 (manual entry) | 5 | Unlimited | Unlimited |
| Sensor history | 7 days | 90 days | 1 year | 2 years |
| AI chat | — | ✅ | ✅ | ✅ |
| AI health checks | — | ✅ (2/day) | ✅ (10/day) | ✅ (unlimited) |
| AI coach tips | — | ✅ | ✅ | ✅ |
| AI insights (harvest/nutrient/anomaly) | — | — | ✅ | ✅ |
| Crop steering | — | — | ✅ | ✅ |
| Automation rules | — | — | ✅ (10 rules) | Unlimited |
| Environment schedules | — | Basic (light on/off) | Full (light/fan/HVAC) | Full |
| Push notifications | — | ✅ | ✅ | ✅ |
| Discord/Slack alerts | — | — | ✅ | ✅ |
| SMS alerts | — | — | — | ✅ |
| Email alerts | — | ✅ | ✅ | ✅ |
| Data export (CSV) | — | ✅ | ✅ | ✅ |
| PDF grow reports | — | — | ✅ | ✅ |
| Team members | 1 (owner only) | 1 | 3 | 5 |
| Task management | — | — | — | ✅ |
| Audit trail | — | — | — | ✅ |
| Harvest workflow (dry/cure) | — | — | ✅ | ✅ |
| Strain leaderboard | — | ✅ | ✅ | ✅ |
| Historical data overlay | — | — | ✅ | ✅ |
| Weather integration (outdoor) | — | ✅ | ✅ | ✅ |
| Weather-based automation rules | — | — | ✅ | ✅ |
| Custom grow types | — | — | ✅ | ✅ |
| Strain database + autocomplete | ✅ | ✅ | ✅ | ✅ |
| Nutrient barcode scanning | — | ✅ | ✅ | ✅ |
| API access | — | — | — | ✅ |

**Enforcement**: A `TierGate` middleware checks `tenant.plan` against a feature registry. Returns 403 with an upgrade prompt when a limit is exceeded. Counting queries (e.g., tent count) use a lightweight cache (Redis or in-memory with 5min TTL) to avoid per-request DB hits.

```sql
-- Tenant isolation
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),          -- NULL for social-only users
    display_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'owner',    -- owner, member, viewer
    auth_provider VARCHAR(50) DEFAULT 'local', -- local, google, github, etc.
    auth_provider_id VARCHAR(255),       -- External provider user ID
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    device_id VARCHAR(100) UNIQUE NOT NULL,  -- Hardware ID (burned into ESP32)
    psk_hash VARCHAR(255) NOT NULL,          -- Hashed pre-shared key
    label VARCHAR(255),
    tent_id UUID,                            -- Which tent this device belongs to
    status VARCHAR(50) DEFAULT 'paired',     -- paired, active, offline, revoked
    last_seen TIMESTAMPTZ,
    firmware_version VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS policy example
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON devices
    USING (tenant_id = current_setting('app.current_tenant')::UUID);

-- All existing grow-assistant tables get tenant_id UUID column + RLS policies:
-- tents, grow_cycles, buckets, bucket_sensor_readings, bucket_journal_entries,
-- bucket_photos, dose_profiles, dose_logs, feeding_schedules, strains,
-- yields, pump_logs, health_evals, alerts, notifications, camera_configs

-- grow_cycles extended with grow type:
-- ALTER TABLE grow_cycles ADD COLUMN grow_type VARCHAR(30) DEFAULT 'DWC';
--   Values: 'DWC', 'RDWC', 'NFT', 'Ebb & Flow', 'Drip/Top Feed',
--           'Aeroponics', 'Kratky', 'Coco Coir', 'Rockwool', 'Soil',
--           'Outdoor Soil', 'Outdoor Container'

-- bucket_sensor_readings extended with additional sensor types:
-- ALTER TABLE bucket_sensor_readings ADD COLUMN dissolved_oxygen DOUBLE PRECISION;
-- ALTER TABLE bucket_sensor_readings ADD COLUMN flow_rate DOUBLE PRECISION;
-- ALTER TABLE bucket_sensor_readings ADD COLUMN soil_moisture DOUBLE PRECISION;
-- ALTER TABLE bucket_sensor_readings ADD COLUMN soil_temp DOUBLE PRECISION;
-- ALTER TABLE bucket_sensor_readings ADD COLUMN runoff_ph DOUBLE PRECISION;
-- ALTER TABLE bucket_sensor_readings ADD COLUMN runoff_ec DOUBLE PRECISION;
-- ALTER TABLE bucket_sensor_readings ADD COLUMN mist_pressure DOUBLE PRECISION;

-- Grow type profiles (seed data, not tenant-specific)
CREATE TABLE grow_type_profiles (
    id VARCHAR(30) PRIMARY KEY,              -- e.g., 'DWC', 'Coco Coir'
    category VARCHAR(30) NOT NULL,           -- 'hydroponic_active', 'hydroponic_passive', 'soilless_media', 'traditional_media', 'outdoor'
    display_name VARCHAR(50) NOT NULL,
    description TEXT,
    relevant_sensors TEXT DEFAULT '[]',       -- JSON array of sensor column names
    primary_sensors TEXT DEFAULT '[]',        -- JSON array (shown on dashboard gauges)
    irrelevant_sensors TEXT DEFAULT '[]',     -- JSON array (hidden from UI)
    unique_fields TEXT DEFAULT '[]',          -- JSON array of extra bucket fields for this type
    default_ph_min DOUBLE PRECISION,
    default_ph_max DOUBLE PRECISION,
    default_ec_ranges TEXT DEFAULT '{}',      -- JSON: {"seedling": 0.4, "veg": [0.8, 1.2], ...}
    default_water_temp_min DOUBLE PRECISION,
    default_water_temp_max DOUBLE PRECISION,
    nutrient_strength_pct TEXT,               -- e.g., '50-75%', '75-100%'
    feeding_approach TEXT,
    health_check_focus TEXT DEFAULT '[]',     -- JSON array of what to look for
    key_questions TEXT DEFAULT '[]',          -- JSON array of questions to ask user
    available_automations TEXT DEFAULT '[]',  -- JSON array of automation types
    common_problems TEXT DEFAULT '[]',        -- JSON array
    ai_prompt_context TEXT,                   -- Injected into all AI prompts
    critical_failure_modes TEXT DEFAULT '[]'  -- JSON array of time-critical failures (e.g., NFT pump)
);

-- Grow type terminology map (per grow type, used for UI labels)
-- Stored as JSON column on grow_type_profiles:
-- ALTER TABLE grow_type_profiles ADD COLUMN terminology TEXT DEFAULT '{}';
-- JSON: {"container": "Bucket", "growing_space": "Tent", "contents": "Reservoir",
--        "plant_holder": "Net pot", "medium": "Hydroton", "drainage": null,
--        "feeding": "Reservoir change", "key_concept": "Air gap"}

-- Sensor kit definitions (per grow type category)
-- ALTER TABLE grow_type_profiles ADD COLUMN sensor_kit_sku VARCHAR(50);
-- ALTER TABLE grow_type_profiles ADD COLUMN sensor_kit_sensors TEXT DEFAULT '[]';
-- JSON array of sensor hardware in the physical kit

-- Reference strain database (synced from Otreeba API)
CREATE TABLE reference_strains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    genetics VARCHAR(50),                    -- indica, sativa, hybrid
    indica_pct DOUBLE PRECISION,
    sativa_pct DOUBLE PRECISION,
    lineage TEXT DEFAULT '[]',               -- JSON array of parent strain names
    terpenes TEXT DEFAULT '[]',              -- JSON array: [{"name": "Myrcene", "pct": 0.3}]
    effects TEXT DEFAULT '[]',               -- JSON array: ["relaxing", "euphoric"]
    flowering_weeks_min INTEGER,
    flowering_weeks_max INTEGER,
    difficulty VARCHAR(20),                  -- beginner, intermediate, advanced
    description TEXT,
    source VARCHAR(50) DEFAULT 'otreeba',    -- otreeba, cannlytics, user, community
    external_id VARCHAR(255),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ref_strains_name ON reference_strains(name);
CREATE INDEX idx_ref_strains_slug ON reference_strains(slug);

-- Nutrient product library (from barcode scans + manual entry)
CREATE TABLE nutrient_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    barcode VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    product_line VARCHAR(255),               -- e.g., "Flora Series"
    npk TEXT,                                -- e.g., "3-1-6"
    composition TEXT DEFAULT '{}',           -- JSON: detailed ingredients
    source VARCHAR(50) DEFAULT 'manual',     -- manual, open_food_facts, user_scan
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Custom grow types (user-created, Pro/Commercial tiers)
CREATE TABLE custom_grow_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    base_type VARCHAR(30) NOT NULL,          -- which seed profile it was forked from
    name VARCHAR(100) NOT NULL,
    terminology TEXT DEFAULT '{}',
    relevant_sensors TEXT DEFAULT '[]',
    ph_min DOUBLE PRECISION,
    ph_max DOUBLE PRECISION,
    unique_fields TEXT DEFAULT '[]',
    health_check_focus TEXT DEFAULT '[]',
    key_questions TEXT DEFAULT '[]',
    ai_prompt_context TEXT,
    available_automations TEXT DEFAULT '[]',
    submitted_for_global BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE custom_grow_types ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON custom_grow_types
    USING (tenant_id = current_setting('app.current_tenant')::UUID);

-- Tents table extended with environment type and location for outdoor grows:
-- ALTER TABLE tents ADD COLUMN environment_type VARCHAR(20) DEFAULT 'indoor';
--   Values: 'indoor', 'outdoor', 'greenhouse'
-- ALTER TABLE tents ADD COLUMN latitude DOUBLE PRECISION;
-- ALTER TABLE tents ADD COLUMN longitude DOUBLE PRECISION;
-- ALTER TABLE tents ADD COLUMN location_name VARCHAR(255);

-- Weather data for outdoor/greenhouse tents
CREATE TABLE weather_readings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    tent_id UUID NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    temperature DOUBLE PRECISION,           -- °C
    humidity DOUBLE PRECISION,              -- %
    apparent_temperature DOUBLE PRECISION,  -- °C (feels like)
    vpd DOUBLE PRECISION,                   -- kPa (vapour pressure deficit)
    precipitation DOUBLE PRECISION,         -- mm
    rain_probability DOUBLE PRECISION,      -- % (forecast only)
    uv_index DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,            -- km/h
    wind_gusts DOUBLE PRECISION,            -- km/h
    wind_direction INTEGER,                 -- degrees
    cloud_cover DOUBLE PRECISION,           -- %
    soil_temperature DOUBLE PRECISION,      -- °C (0-18cm avg)
    soil_moisture DOUBLE PRECISION,         -- m³/m³
    et0_evapotranspiration DOUBLE PRECISION,-- mm (reference ET₀)
    weather_code INTEGER,                   -- WMO code
    sunrise TIMESTAMPTZ,
    sunset TIMESTAMPTZ,
    daylight_duration INTEGER,              -- seconds
    is_forecast BOOLEAN DEFAULT FALSE,      -- true for forecast data
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE weather_readings ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON weather_readings
    USING (tenant_id = current_setting('app.current_tenant')::UUID);

CREATE INDEX idx_weather_tent_time ON weather_readings(tent_id, recorded_at DESC);
```

### 8. Testing Strategy

All three backend pods share the same codebase, so a single test suite covers everything.

| Layer | Tool | Scope | Run When |
|-------|------|-------|----------|
| **Unit** | pytest | Service logic, auth, RLS isolation, input validation, RBAC, OWASP controls | Every PR |
| **Integration** | pytest + testcontainers (PostgreSQL) | API endpoints end-to-end, tenant isolation, MQTT auth webhooks, device pairing, sensor ingestion | Every PR |
| **Security** | pytest | Cross-tenant access attempts, SQL injection payloads, expired/tampered tokens, RBAC violations, SSRF probes | Every PR |
| **Frontend** | Vitest + React Testing Library | Components, auth flows, dashboard rendering, PWA manifest validation | Every PR |
| **E2E** | Playwright | Full flows: signup → pair device → create grow → add bucket → view sensor data → AI chat | Pre-release |
| **Dependency scan** | Dependabot + Snyk | Python + Node.js vulnerability scanning | Daily + every PR |
| **Lint + Type** | ruff + mypy (Python), ESLint + TypeScript (frontend) | Code quality, type safety | Every PR |

**CI Pipeline** (GitHub Actions):
```
PR opened/updated
  ├── lint + type-check (parallel)
  ├── unit + integration + security tests (parallel, testcontainers)
  ├── frontend tests (parallel)
  ├── dependency scan
  └── build Docker images (verify they build)

Merge to main
  ├── all above
  ├── E2E tests (Playwright against staging)
  ├── build + push images to registry
  └── deploy to K3S (staging → production)
```

**Test Fixtures** (`conftest.py`):
- `test_db`: Spins up PostgreSQL via testcontainers, runs Alembic migrations
- `tenant_factory`: Creates isolated tenants with RLS configured
- `auth_client`: Authenticated httpx.AsyncClient with JWT for a test tenant
- `mock_mqtt`: In-memory MQTT broker for sensor ingestion tests

### 9. OWASP Top 10 Compliance
Every component SHALL be built to mitigate the OWASP Top 10 (2021):

| # | Risk | Mitigation |
|---|------|------------|
| A01 | Broken Access Control | PostgreSQL RLS, RBAC middleware, tenant isolation on every query, JWT validation on all endpoints |
| A02 | Cryptographic Failures | bcrypt for passwords, TLS everywhere (MQTT 8883, HTTPS), secrets in K8s Secrets (not env vars), no sensitive data in JWTs |
| A03 | Injection | Parameterized queries (psycopg2 %s placeholders), Pydantic input validation on all endpoints, no raw SQL interpolation |
| A04 | Insecure Design | Threat model per feature, rate limiting, account lockout after failed logins, device pairing requires authenticated user |
| A05 | Security Misconfiguration | Strict CORS (allowed origins only), security headers (CSP, HSTS, X-Frame-Options), no default credentials, Helm/K8s security contexts |
| A06 | Vulnerable Components | Dependabot/Snyk for dependency scanning, pin versions, regular updates |
| A07 | Auth Failures | JWT expiry (15min access, 7d refresh), refresh token rotation, email verification required, brute-force protection |
| A08 | Data Integrity Failures | Input validation via Pydantic, signed JWTs (HS256→RS256 for production), integrity checks on firmware updates |
| A09 | Logging & Monitoring | Structured logging (JSON), auth events logged, failed access attempts tracked, alert on anomalous patterns |
| A10 | SSRF | No user-supplied URLs fetched server-side (camera URLs validated against allowlist patterns), MQTT topic validation |

## Risks / Trade-offs
- **Camera access**: v1 requires customers to expose camera snapshot URLs. May limit adoption for less technical users. Mitigation: clear setup guide, consider relay service in v2
- **EMQX ACL scaling**: HTTP webhook for every MQTT publish adds latency. Mitigation: EMQX caches auth results, tune cache TTL
- **Ollama per-tenant**: AI costs scale linearly. Mitigation: Rate limit AI calls per tenant, queue-based processing
- **Single cluster**: K3S home lab has finite capacity. Mitigation: Plan cloud migration path, keep stateless API layer

## Migration Plan
- No migration — greenfield project. grow-assistant continues running independently
- Future: Optional data export tool from grow-assistant → Tendril tenant import

## Open Questions
- ~~Domain name: tendril.app? tendril.io? tendril.grow?~~ **Resolved**: `tendril.maddscientist.com` for v1; architecture is domain-agnostic (configurable via env var)
- ~~Pricing tiers and limits for free tier~~ **Resolved**: See tier gating matrix above
- ESP32 firmware: build in-house or partner with existing sensor manufacturers?
- Camera relay service timing (v2 or v3?)

### 10. Weather Integration: Open-Meteo
- **Decision**: Use Open-Meteo (open-meteo.com) as the weather data provider for outdoor and greenhouse grows. Tents have an `environment_type` field (indoor/outdoor/greenhouse). Outdoor and greenhouse tents store latitude/longitude and receive weather data polling every 30 minutes via the scheduler pod
- **Why**: Open-Meteo is free (no API key required for non-commercial, affordable commercial plan), provides hyperlocal data from multiple national weather services, and includes agriculture-relevant variables (VPD, soil temp/moisture, ET₀ evapotranspiration, UV index). No vendor lock-in — it's open source
- **Variables fetched**: temperature, humidity, apparent temp, VPD, precipitation, rain probability, UV index, wind speed/gusts, cloud cover, soil temperature (0-18cm), soil moisture, ET₀, weather code, sunrise/sunset, daylight duration
- **Implementation**: `app/weather/service.py` calls `https://api.open-meteo.com/v1/forecast` with tent coordinates. Scheduler polls every 30 min. Results cached in `weather_readings` table. Weather data is injected into AI health check prompts for outdoor grows. Frontend shows a weather widget + 7-day forecast when viewing outdoor tents
- **Alerts**: Frost (<4°C), extreme heat (>38°C), heavy rain (>25mm/12h), high wind (>50 km/h gusts), high UV (>8) generate automatic alerts for outdoor tents

### 11. Grow Type Profiles: Contextual Adaptation
- **Decision**: Every grow cycle has a `grow_type` field. A `grow_type_profiles` table stores the profile registry (seed data) defining what sensors, fields, questions, automations, AI prompts, feeding defaults, and alert thresholds are relevant per grow type. The entire UI and backend adapt based on the selected type
- **Why**: A DWC grower and a soil grower have fundamentally different needs. Showing irrelevant fields (water level for soil, soil moisture for DWC) confuses users. Asking wrong health check questions wastes AI calls. Wrong pH defaults cause bad advice. The grow type profile is the single source of truth that makes the app feel purpose-built for each grower
- **Supported types**: DWC, RDWC, NFT, Ebb & Flow, Drip/Top Feed, Aeroponics, Kratky, Coco Coir, Rockwool, Soil, Outdoor Soil, Outdoor Container
- **Implementation**: `app/grows/grow_types.py` contains the registry. On grow creation, the profile pre-fills defaults. UI queries the profile to determine which fields/sensors to show. AI prompts include the profile's `ai_prompt_context`. Alert thresholds default from the profile's pH/EC/temp ranges. Automations are filtered by `available_automations`
- **Critical failures**: NFT pump failure and aero nozzle clog are marked CRITICAL — these grow types have seconds-to-minutes before plant damage. Alerts bypass normal priority and fire immediately on all channels

### 12. Billing: Stripe Checkout
- **Decision**: Integrate Stripe for subscription billing in v1. Simple Checkout Sessions for plan signup and upgrades, Customer Portal for self-service plan management/cancellation, and Webhooks for payment event handling
- **Why**: Stripe is the industry standard for SaaS billing, handles PCI compliance, supports all major payment methods, and has excellent developer docs. Simple Checkout (not embedded pricing page) keeps implementation minimal
- **Implementation**: `app/billing/` module with Stripe SDK. On signup, create Stripe Customer. On plan upgrade, create Checkout Session redirecting to Stripe-hosted page. Stripe webhooks (`checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`) update `tenants.plan` column. Customer Portal link in settings for plan management. Stripe API key stored in K8s Secret
- **Pricing IDs**: Each tier (Grower, Pro, Commercial) maps to a Stripe Price ID. Seedling is free (no Stripe subscription)
- **Webhook security**: Verify Stripe webhook signatures using the endpoint secret. Log all payment events for audit

### 13. Reference Data: External APIs
- **Decision**: Integrate with Otreeba (strain data), Open Food Facts (nutrient barcode scanning), and ship curated seed data (grow media, growth stages, terpenes, nutrient brands, light types)
- **Why**: Pre-populated reference data makes the app feel complete out of the box. Strain autocomplete with genetics/terpenes adds value. Barcode scanning for nutrient bottles reduces manual data entry
- **Implementation**: `app/reference/` module. Otreeba API synced daily by scheduler → `reference_strains` table. Open Food Facts queried on-demand via barcode scan endpoint. Seed data loaded via Alembic migration. Strains, terpenes, nutrient brands, grow media types, and light types are all searchable via API

### 14. Grow-Type Terminology Adaptation
- **Decision**: Every grow type profile includes a `terminology` JSON map defining the correct labels for that grow type. The frontend and AI layer use these labels instead of hardcoded terms
- **Why**: Beginners learn the correct terms for their setup. Experts see familiar language. A DWC grower sees "Bucket" and "Reservoir"; a soil grower sees "Pot" and "Soil"; an outdoor grower sees "Plot" and "Garden". This reduces confusion and builds trust
- **Terminology keys**: `container`, `growing_space`, `contents`, `plant_holder`, `medium`, `drainage`, `feeding`, `key_concept`
- **Implementation**: Frontend has a `useTerminology(growType)` hook that returns the label map. All component labels, tooltips, notifications, and AI prompts pass through this map. The API includes terminology in the grow type profile response
