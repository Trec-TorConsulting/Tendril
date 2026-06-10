# Project Context

## Purpose
Tendril is an open-source, multi-tenant SaaS platform for grow monitoring and automation. It combines IoT sensor hardware, a REST/WebSocket API, an AI-powered grow assistant, and a mobile-first PWA to help growers track environmental conditions, manage grow journals, and automate care workflows.

## Repository
- **GitHub**: `https://github.com/Trec-TorConsulting/Tendril.git`
- **License**: AGPL-3.0 (server/web), MIT (ESP32 firmware)
- **Status**: Public (switched from private on 2026-05-14), open-source, enterprise-grade quality standard

## Tech Stack
- **API**: Python 3.14+, FastAPI, SQLAlchemy 2.0 async, asyncpg, Alembic, PostgreSQL with RLS
- **Web**: TypeScript, Next.js 16, React 19, Tailwind CSS 4, shadcn/ui, custom service worker PWA
- **Firmware**: C++ (ESP32-WROOM-32), PlatformIO, Arduino, MQTT via PubSubClient
- **AI**: Google Gemini, Ollama (local LLM), LangChain-style tool calls
- **Infrastructure**: Docker (arm64 builds), k3s, Traefik ingress, Let's Encrypt TLS
- **Services**: EMQX (MQTT broker), PostgreSQL, Redis
- **Billing**: Stripe

## Deployment
- **Production**: k3s Kubernetes cluster with manifests in `manifests/`
- **Local Dev**: Docker Compose (`docker-compose.yml`) with full stack
- **Container Registry**: `192.168.4.10:30500` — local registry with filesystem storage on Longhorn PVC; configurable via `TENDRIL_REGISTRY` env var in `scripts/build.sh`
- **Mirror Images**: `node:26-slim` and `python:3.14-slim-bookworm` mirrored to `192.168.4.10:30500/mirror/` (weekly via `mirror-base-images.yml` workflow)
- **Domains**: Configurable via `DOMAIN` env var (defaults to `tendrilgrow.com`)

## Project Conventions

### Code Style
- Python: PEP 8, type hints on public interfaces, ruff linter, black formatter
- TypeScript: ESLint config in `web/eslint.config.mjs`, strict mode
- Conventional Commits: `feat:`, `fix:`, `chore:`, `security:`, etc.
- All code must pass linting and formatting checks before merge

### Architecture Patterns
- Multi-service monorepo: `api/`, `web/`, `esp32/`, `manifests/`
- Multi-tenant with Account → Tenant hierarchy and explicit `tenant_memberships` join table
- Enterprise RBAC: Platform roles (`super_admin`, `support`, `readonly_admin`, `user`), Tenant roles (`admin`, `member`, `viewer`), Account roles (`owner`, `billing_admin`)
- ~30 granular permissions across 12 domains; route guards use `require_permission()` not direct role checks
- Grow-scoped access via `membership_grow_access` for restricting tenant users
- JWT claims: `pr` (platform role), `tid` (tenant ID), `tr` (tenant role), `gs` (grow scope), `aid` (account ID)
- Stripe billing fields live on `accounts` table, not `tenants`
- PostgreSQL Row-Level Security (RLS) for tenant isolation
- MQTT for device → API sensor ingestion
- Background workers: `mqtt-worker`, `scheduler` (leader election via pg advisory locks)
- FastAPI routers organized by domain (`grows/`, `devices/`, `ai/`, `billing/`, `integrations/`, etc.)
- Integration connectors follow BaseConnector ABC pattern with registry, poll/webhook/persist/discover lifecycle
- Security middleware stack: CSP, HSTS, rate limiting, brute-force protection, CORS

### Testing Strategy
- API: pytest with unit tests in `api/tests/`, async test fixtures
- Web: Vitest for unit/component tests, Playwright e2e tests in `web/e2e/`
- Pre-commit hooks enforce lint and format checks

### Git Workflow
- `main` branch is the primary branch (protected: require PR, 1 approval, status checks, enforced for admins)
- **All changes** must go through a feature branch + pull request — never commit directly to main
- Branch naming: `feat/`, `fix/`, `chore/`, `security/` prefix with kebab-case description
- Conventional commit messages on all commits
- AI assistants creating commits must: create a branch, commit, push, and open a PR
- **Deploys are only done via the full GitHub flow**: branch → commit → push → PR → merge → CI/CD pipeline (no manual deploys, no direct kubectl apply)
- OpenSpec proposals for larger changes
- No secrets, credentials, or PII in tracked files (enforced via .gitignore + pre-commit)

## Security Requirements (OWASP Top 10 Compliance)

All code must be written with OWASP Top 10 2021 compliance as a baseline:

1. **A01 Broken Access Control**: RLS on all tenant data; JWT auth required on all endpoints except auth routes; enterprise RBAC with platform/tenant/account roles; permission-based route guards (`require_permission()`); grow-scoped access control
2. **A02 Cryptographic Failures**: bcrypt for passwords; JWT HS256 with mandatory `JWT_SECRET`; TLS enforced via HSTS; no secrets in code
3. **A03 Injection**: SQLAlchemy parameterized queries only; no raw SQL; React auto-escaping for XSS
4. **A04 Insecure Design**: Threat modeling via OpenSpec proposals; security review for auth/data changes
5. **A05 Security Misconfiguration**: Security headers middleware (CSP, X-Frame-Options, etc.); minimal container privileges (`runAsNonRoot`, `readOnlyRootFilesystem`, drop all capabilities)
6. **A06 Vulnerable Components**: Dependabot / dependency scanning; pin major versions; regular updates
7. **A07 Auth Failures**: Rate limiting on auth endpoints; brute-force protection; short-lived access tokens (15min); refresh token rotation
8. **A08 Data Integrity Failures**: Input validation on all API endpoints (Pydantic models); CSRF protection; signed JWTs
9. **A09 Logging & Monitoring**: Structured logging; audit trail for auth events; health check endpoints
10. **A10 SSRF**: Validate/allowlist external URLs; no user-controlled redirects to internal services

### Security Policies
- `SECURITY.md`: Responsible disclosure process
- Secrets managed via Kubernetes Secrets or environment variables only
- `.gitignore` covers: `secrets.yaml`, `config.h`, `.env`, `*.pem`, `*.key`
- Pre-commit hooks scan for leaked credentials
- Container images run as non-root with read-only filesystems

## Domain Context
- A "grow" is a tracked cultivation cycle with strains, tents, feedings, and journal entries
- "Buckets" are monitored containers within a grow (DWC, Kratky, soil, etc.)
- ESP32 devices publish sensor data (temperature, humidity, soil moisture) via MQTT
- The AI assistant provides grow recommendations based on sensor data and grow history
- **This is a cannabis-first platform** — all features, AI outputs, recommendations, and UX are designed for cannabis cultivation

## Cannabis-First Quality Philosophy

**Every AI response, recommendation, alert, and automated action in this platform MUST follow this priority order:**

1. **Plant health & resin production** — healthy, unstressed plants channel energy into trichome development
2. **Terpene preservation & expression** — protect volatile terpenes with proper environment (temps, airflow, timing)
3. **Cannabinoid maturity & potency** — proper harvest windows, trichome development, never rush
4. **Bag appeal & bud structure** — dense, frosty, properly cured flower
5. **Yield (DEAD LAST)** — never recommend actions that trade quality for quantity

### Cannabis-Specific Ideal Ranges (enforce across all AI and alerting)
- Water temp (hydro): 66-68°F target, acceptable 64-70°F, caution 70-72°F, warning >72°F, critical >75°F.
- Water temp (aeroponics): 62-68°F target 65°F (misted roots need cooler temps).
- Reservoir pH (hydro): 5.5-6.2 (sweet spot 5.8). Drift > 0.5/day = flag.
- Coco pH: 5.8-6.3 (sweet spot 6.0).
- Soil pH: 6.0-7.0 (sweet spot 6.5).
- Air temp (veg): 70-85°F day, 65-72°F night.
- Air temp (flower): 65-80°F day (quality zone 72-78°F), 60-68°F night. Night drop (DIF) 10-15°F enhances terpenes.
- Air temp (late flower): 68-75°F day, 58-65°F night — protect volatile terpenes.
- Humidity (veg): 60-70%. VPD 0.8-1.2 kPa.
- Humidity (transition): 45-55%. Drop from veg levels.
- Humidity (flower): 40-55%. Above 55% = botrytis risk.
- Humidity (late flower): 35-45%. Dense buds trap moisture — mold risk highest now.
- EC (veg): 0.8-1.4 (strain dependent).
- EC (flower): 1.2-2.0 (peak mid-flower at 1.8-2.0 MAX, reduce final 2 weeks to 1.0-1.4).
- EC >2.2 is yield-chasing territory — salt stress destroys terpene expression.
- Dissolved oxygen: >6mg/L. Below 5 = root health emergency.

### Application of Quality Philosophy
- **AI Health Checks**: Score based on how well environment supports quality flower, not biomass
- **AI Chat**: All advice framed through cannabis science; never suggest yield-maximizing at quality's expense
- **Coach Tips**: Every tip should optimize for terps/cannabinoids/quality
- **Feeding Advice**: Dial for quality (proper EC curves, flush timing, terpene-protective temps)
- **Alerts & Notifications**: Threshold alerts use cannabis-optimal ranges, not generic plant ranges
- **Harvest Predictions**: Optimize for trichome maturity, never rush for speed
- **Anomaly Detection**: Quality-threatening anomalies are always high severity

## Important Constraints
- Must remain self-hostable — no hard dependency on proprietary cloud services
- ESP32 firmware must work with standard WROOM-32 boards
- PWA must work offline for core journal/feeding features
- Enterprise-grade quality: comprehensive testing, security hardening, documentation

## External Dependencies
- PostgreSQL (primary datastore)
- EMQX or compatible MQTT broker
- Google Gemini API (optional, for AI features)
- Stripe (optional, for SaaS billing)
- OpenWeather API (optional, for enhanced weather data via OpenWeather connector)
- Ecowitt cloud API / gateway webhook (optional, for weather stations and soil probes)
- Pulse Grow API (optional, for Pulse One/Pro/Hub environmental monitors)
- MinIO or S3-compatible storage (optional, for photo uploads)
