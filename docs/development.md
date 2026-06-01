# Developer Guide

Everything you need to contribute code to Tendril — local setup, project structure, testing, and the change workflow.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.14+ | [python.org](https://python.org) or `brew install python@3.14` |
| Node.js | 20+ | [nodejs.org](https://nodejs.org) or `brew install node` |
| PostgreSQL | 15+ | `brew install postgresql@16` or use Docker |
| PlatformIO | Latest | `pip install platformio` or [VS Code extension](https://platformio.org) |
| Docker + Compose | Latest | [docker.com](https://docker.com) |

## Local Development Setup

### Option A: Full Docker Stack (Recommended for first run)

```bash
docker compose up -d
```

This starts all services including PostgreSQL, EMQX, and MinIO. See the [Self-Hosting Guide](self-hosting.md) for details.

### Option B: Services Locally (Better for active development)

Run infrastructure in Docker, services natively:

```bash
# Start only infrastructure
docker compose up -d postgres emqx minio

# Terminal 1: API
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+asyncpg://tendril:tendril@localhost:5432/tendril"
export JWT_SECRET="dev-secret"
export MQTT_BROKER_HOST="localhost"
export MQTT_BROKER_PORT="1883"
export S3_ENDPOINT="http://localhost:9000"
export S3_ACCESS_KEY="minioadmin"
export S3_SECRET_KEY="minioadmin"
export CORS_ORIGINS="http://localhost:3000"
export DOMAIN="localhost"
export LOG_LEVEL="DEBUG"
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Terminal 2: Web
cd web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000/v1 npm run dev

# Terminal 3: MQTT Worker (optional — only if testing sensors)
cd api
source .venv/bin/activate
python -m app.mqtt.worker

# Terminal 4: Scheduler (optional — only if testing background tasks)
cd api
source .venv/bin/activate
python -m app.scheduler.main
```

## Project Structure

```
tendril/
├── api/                          # Python / FastAPI backend
│   ├── app/
│   │   ├── main.py               # App factory, router registration
│   │   ├── config.py             # Settings from env vars
│   │   ├── database.py           # SQLAlchemy engine, RLS sessions
│   │   ├── storage.py            # S3/MinIO file operations
│   │   ├── auth/                 # JWT, OAuth2, middleware
│   │   ├── ai/                   # AI assistant (routes, context, Gemini, Ollama, tools)
│   │   ├── grows/                # Core domain: grows, tents, buckets, journals, etc.
│   │   ├── devices/              # ESP32 device management
│   │   ├── mqtt/                 # MQTT client, message handlers, auth webhook
│   │   ├── scheduler/            # Background tasks with leader election
│   │   ├── outdoor/              # Outdoor grow features
│   │   ├── integrations/         # Third-party connectors (Pulse, OpenWeather, Ecowitt)
│   │   ├── billing/              # Stripe integration
│   │   ├── notifications/        # Web push
│   │   ├── automation/           # Rules engine
│   │   ├── commercial/           # API keys, audit, custom grow types
│   │   ├── admin/                # Platform admin routes
│   │   ├── middleware/            # Security headers, rate limiting, brute force
│   │   ├── tenants/              # Multi-tenant models and routes
│   │   ├── sensors/              # Sensor data query routes
│   │   ├── weather/              # Weather API integration
│   │   ├── reference/            # Reference data (nutrients, etc.)
│   │   └── data/                 # Data export/import
│   ├── migrations/               # Alembic migrations
│   │   └── versions/             # Migration scripts
│   └── tests/                    # Test suite
│       ├── conftest.py           # Shared fixtures
│       └── unit/                 # Unit tests
├── web/                          # TypeScript / Next.js frontend
│   ├── src/
│   │   ├── app/                  # Next.js route groups
│   │   │   ├── (auth)/           # Login, register
│   │   │   ├── (marketing)/      # Landing page, pricing
│   │   │   ├── dashboard/        # Main dashboard
│   │   │   └── platform/         # Settings, admin
│   │   ├── components/           # React components
│   │   │   ├── ui/               # shadcn/ui primitives
│   │   │   └── outdoor/          # Outdoor-specific components
│   │   ├── hooks/                # Custom hooks
│   │   ├── lib/                  # Utilities, API client, auth helpers
│   │   └── types/                # TypeScript type definitions
│   ├── e2e/                      # End-to-end tests
│   └── public/                   # Static assets, PWA manifest
├── esp32/                        # C++ / PlatformIO firmware
│   ├── platformio.ini            # Build configuration
│   └── src/
│       ├── main.cpp              # Entry point
│       ├── sensors.cpp/.h        # Sensor reading logic
│       ├── mqtt_client.cpp/.h    # MQTT publishing
│       ├── config.example.h      # Template config
│       └── config.h              # Local config (gitignored)
├── manifests/                    # Kubernetes YAML
├── scripts/                      # Build and deploy scripts
├── docs/                         # Documentation
└── openspec/                     # Specs and change proposals
```

## Code Conventions

### Python (API)

- **Style**: PEP 8, enforced via linter
- **Type hints**: Required on public function signatures
- **Imports**: Standard → third-party → local, with `from __future__ import annotations`
- **Async**: All database and HTTP operations are async
- **Models**: SQLAlchemy 2.0 declarative style with `DeclarativeBase`
- **Schemas**: Pydantic v2 `BaseModel` for request/response validation
- **Routers**: One `APIRouter` per module, registered in `main.py`

### TypeScript (Web)

- **Style**: ESLint config in `web/eslint.config.mjs`
- **Components**: Functional components with hooks
- **UI**: shadcn/ui components in `components/ui/`
- **Forms**: React Hook Form + Zod for validation
- **API calls**: Centralized in `lib/api.ts`
- **Auth**: Token management in `lib/auth.ts`

### C++ (ESP32)

- **Framework**: Arduino (via PlatformIO)
- **Style**: Functions prefixed by module (`mqtt_`, `sensors_`)
- **JSON**: ArduinoJson for all payloads
- **Memory**: Stack allocation preferred, minimize heap usage

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(grows): add DWC grow type configuration
fix(esp32): handle BME680 read failure gracefully
docs: update self-hosting guide with Docker Compose
chore: update dependencies
refactor(api): extract sensor trend calculation
```

Scopes: `api`, `web`, `esp32`, `grows`, `ai`, `outdoor`, `billing`, `auth`, `mqtt`, `scheduler`

## Running Tests

### API Tests

```bash
cd api
source .venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/unit/test_grows.py

# Run with coverage
pytest --cov=app
```

### Web Tests

```bash
cd web

# Run tests in watch mode
npm test

# Run tests once (CI mode)
npm run test:run

# Type checking
npm run type-check

# Linting
npm run lint
```

### ESP32

The firmware doesn't have automated tests. Verify by:
1. Compile: `cd esp32 && pio run`
2. Flash and monitor: `pio run -t upload && pio device monitor`
3. Check serial output for expected sensor readings

## Adding a New API Module

1. **Create the module directory:**
   ```
   api/app/myfeature/
   ├── __init__.py
   ├── models.py      # SQLAlchemy models
   ├── routes.py      # FastAPI router
   └── schemas.py     # Pydantic schemas (optional, can be in routes.py)
   ```

2. **Define models** in `models.py` using the shared `Base`:
   ```python
   from app.database import Base
   from sqlalchemy import Column, String, ForeignKey
   from sqlalchemy.dialects.postgresql import UUID
   import uuid

   class MyModel(Base):
       __tablename__ = "my_table"
       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
       tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
       name = Column(String, nullable=False)
   ```

3. **Create routes** in `routes.py`:
   ```python
   from fastapi import APIRouter, Depends
   from app.auth.middleware import get_current_user, require_permission, CurrentUser
   from app.auth.permissions import MYFEATURE_READ, MYFEATURE_CREATE

   router = APIRouter()

   @router.get("/")
   async def list_items(user: CurrentUser = Depends(require_permission(MYFEATURE_READ))):
       ...

   @router.post("/")
   async def create_item(user: CurrentUser = Depends(require_permission(MYFEATURE_CREATE))):
       ...
   ```

   Use `require_permission()` for fine-grained guards. The permission system resolves
   effective permissions from the user's platform role + tenant role combination.

4. **Register the router** in `api/app/main.py`:
   ```python
   from app.myfeature.routes import router as myfeature_router
   app.include_router(myfeature_router, prefix=f"{settings.api_prefix}/myfeature", tags=["myfeature"])
   ```

5. **Create a migration:**
   ```bash
   cd api
   alembic revision --autogenerate -m "add my_table"
   alembic upgrade head
   ```

## Adding a New Web Page

1. **Create the route** in `web/src/app/`:
   ```
   web/src/app/dashboard/mypage/
   └── page.tsx
   ```

2. **Use the page header component** for consistent layout:
   ```tsx
   import { PageHeader } from "@/components/page-header";

   export default function MyPage() {
     return (
       <div>
         <PageHeader title="My Page" description="Description here" />
         {/* Content */}
       </div>
     );
   }
   ```

3. **Add navigation** in `web/src/components/app-sidebar.tsx` if needed.

## Database Migrations

### Creating a Migration

```bash
cd api
source .venv/bin/activate

# Auto-generate from model changes
alembic revision --autogenerate -m "describe your change"

# Create an empty migration (for manual SQL)
alembic revision -m "describe your change"
```

### Running Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one step
alembic upgrade +1

# Downgrade one step
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history
```

### RLS Considerations

When adding tenant-scoped tables, you need to:
1. Add a `tenant_id` column with a foreign key to `tenants`
2. Create RLS policies in a migration:
   ```sql
   ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;
   CREATE POLICY tenant_isolation ON my_table
       USING (tenant_id = current_setting('app.current_tenant')::uuid);
   ```

## OpenSpec Workflow

For larger changes (new features, architecture changes, breaking changes), use the OpenSpec workflow:

1. **Create a proposal**: `openspec/changes/my-change-name/proposal.md`
2. **Add a task list**: `openspec/changes/my-change-name/tasks.md`
3. **Get review** via PR or discussion
4. **Implement** once approved
5. **Archive** after deployment: move to `openspec/changes/archive/`

See [openspec/AGENTS.md](https://github.com/Trec-TorConsulting/Tendril/blob/main/openspec/AGENTS.md) for the full specification.

## Useful Commands

```bash
# API: Start with auto-reload
cd api && uvicorn app.main:app --reload

# Web: Start dev server with turbopack
cd web && npm run dev

# ESP32: Compile
cd esp32 && pio run

# ESP32: Flash + monitor
cd esp32 && pio run -t upload && pio device monitor

# Docker: Rebuild a single service
docker compose build api && docker compose up -d api

# Docker: View logs
docker compose logs -f api mqtt-worker scheduler

# Database: Open psql shell
docker compose exec postgres psql -U tendril

# EMQX: List connected clients
docker compose exec emqx emqx_ctl clients list

# MinIO: Browse files
open http://localhost:9001  # minioadmin / minioadmin
```
