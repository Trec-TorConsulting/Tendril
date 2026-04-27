# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- Comprehensive documentation suite (`docs/`)
- Docker Compose for full local development stack
- SECURITY.md and CODE_OF_CONDUCT.md
- AGPL-3.0 license for server, MIT license for ESP32 firmware
- CONTRIBUTING.md with development and OpenSpec workflow guides

---

## [0.1.0] — 2025

Initial extraction from HomeLab-Redo mono-repo as a standalone project.

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
