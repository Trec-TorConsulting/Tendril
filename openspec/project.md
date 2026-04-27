# Project Context

## Purpose
Tendril is an open-source, multi-tenant SaaS platform for grow monitoring and automation. It combines IoT sensor hardware, a REST/WebSocket API, an AI-powered grow assistant, and a mobile-first PWA to help growers track environmental conditions, manage grow journals, and automate care workflows.

## Tech Stack
- **API**: Python 3.12+, FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **Web**: TypeScript, Next.js 15, React, Tailwind CSS, shadcn/ui
- **Firmware**: C++ (ESP32-WROOM-32), PlatformIO, MQTT
- **AI**: Google Gemini, Ollama (local LLM), LangChain-style tool calls
- **Infrastructure**: Docker, Kubernetes, EMQX (MQTT broker)
- **Billing**: Stripe

## Project Conventions

### Code Style
- Python: PEP 8, type hints on public interfaces
- TypeScript: ESLint config in `web/eslint.config.mjs`
- Conventional Commits: `feat:`, `fix:`, `chore:`, etc.

### Architecture Patterns
- Multi-service monorepo: `api/`, `web/`, `esp32/`, `manifests/`
- Multi-tenant with `TENANT_ID` scoping across all data
- MQTT for device → API sensor ingestion
- Background workers: `mqtt-worker`, `scheduler`
- FastAPI routers organized by domain (`grows/`, `devices/`, `ai/`, `billing/`, etc.)

### Testing Strategy
- API: pytest with unit tests in `api/tests/`
- Web: Vitest for unit/component tests, e2e tests in `web/e2e/`

### Git Workflow
- `main` branch is the primary branch
- Feature branches with conventional commit messages
- OpenSpec proposals for larger changes

## Domain Context
- A "grow" is a tracked cultivation cycle with strains, tents, feedings, and journal entries
- "Buckets" are monitored containers within a grow (DWC, Kratky, soil, etc.)
- ESP32 devices publish sensor data (temperature, humidity, soil moisture) via MQTT
- The AI assistant provides grow recommendations based on sensor data and grow history

## Important Constraints
- Must remain self-hostable — no hard dependency on proprietary cloud services
- ESP32 firmware must work with standard WROOM-32 boards
- PWA must work offline for core journal/feeding features

## External Dependencies
- PostgreSQL (primary datastore)
- EMQX or compatible MQTT broker
- Google Gemini API (optional, for AI features)
- Stripe (optional, for SaaS billing)
- OpenWeather API (optional, for weather integration)
