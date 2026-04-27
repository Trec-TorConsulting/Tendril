# Change: Create Tendril SaaS Platform

## Why
The grow-assistant is a single-tenant, LAN-only tool built for personal use. Growing demand from other growers creates an opportunity to turn it into a multi-tenant SaaS product. Customers purchase a sensor kit (pH, EC/TDS, water temp, air temp+humidity, water level, 2x WiFi IP cameras) and the platform manages their grow data, AI insights, and device connectivity securely.

## What Changes
- **NEW**: Greenfield project at `HomeLab-Redo/tendril/` using grow-assistant as the feature template
- **NEW**: FastAPI backend with multi-tenant data isolation (tenant_id + PostgreSQL RLS)
- **NEW**: React/Next.js PWA frontend replacing vanilla JS SPA (installable, offline-capable, push notifications)
- **NEW**: OWASP Top 10 compliance across all API and frontend code
- **NEW**: Authentication system — built-in email/password JWT + social logins (Google, GitHub, Apple, Discord) + Auth0/Firebase/Supabase as optional identity providers
- **NEW**: IoT device provisioning — QR code pairing, per-device MQTT credentials, EMQX ACLs, grow-type-specific sensor kits (1 kit per plant)
- **NEW**: Secure MQTT topic namespacing per tenant (`tenant/{id}/sensor/#`)
- **NEW**: RBAC — account owner, team member, read-only viewer roles
- **NEW**: API key system for sensor/device authentication
- **NEW**: Tenant onboarding flow (signup → verify email → pair kit → configure tent)
- **NEW**: Backend split into 3 pods — API server (HTTP+WebSocket), MQTT worker (sensor ingestion + device auth), Scheduler (health checks, alerts, retention)
- **NEW**: Comprehensive testing — pytest (unit + integration + security), Vitest (frontend), Playwright (E2E), GitHub Actions CI, Dependabot/Snyk
- **NEW**: Pricing tier feature gating (Seedling/Grower/Pro/Commercial) with TierGate middleware
- **NEW**: Automation rules engine — sensor threshold triggers (if pH < 5.5 → dose pump)
- **NEW**: Environment control scheduling — light, fan, HVAC time-based schedules with stage linkage
- **NEW**: Harvest workflow — drying, curing, trimming stages with environment tracking
- **NEW**: Task management — assign, track, and complete team tasks (Commercial tier)
- **NEW**: Audit trail — log all user actions with before/after values (Commercial tier)
- **NEW**: PDF grow reports — sensor trends, photos, milestones, yields
- **NEW**: Weather integration for outdoor/greenhouse grows — Open-Meteo API for hyperlocal weather (temp, humidity, VPD, UV, rain, wind, soil temp/moisture, ET₀), weather dashboard widget, forecast, weather-aware AI health checks, and automatic weather alerts (frost, heat, rain, wind, UV)
- **PORTED**: All grow-assistant features (tents, grows, buckets, sensors, journal, photos, dosing, pump control, AI chat, health checks, coach, analytics, strains, feeding schedules, notifications, data retention)

## Impact
- Affected specs: auth, multi-tenancy, iot-devices, grows, buckets, sensors, ai-assistant, dashboard, analytics, notifications, pwa, security, testing, automation, harvest, teams, weather, grow-type-profiles, reference-data
- Affected code: Entirely new codebase at `tendril/` — no changes to existing grow-assistant
- Infrastructure: New K3S deployment (namespace: `tendril`), shared EMQX broker with tenant ACLs, shared PostgreSQL instance with new database

## Risks
- Scope is large — phased delivery recommended
- EMQX ACL management complexity grows with tenant count
- Camera streaming from customer networks requires NAT traversal or relay strategy
- AI costs (Ollama) scale per-tenant — may need usage limits or tiered plans
