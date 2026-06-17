# Tendril API — Agent Guide

FastAPI + SQLAlchemy 2.0 (async) + Alembic + PostgreSQL with Row-Level Security.

> Cross-references: [openspec/AGENTS.md](../openspec/AGENTS.md) for spec workflow, [`web/AGENTS.md`](../web/AGENTS.md) for the consumer, [`manifests/AGENTS.md`](../manifests/AGENTS.md) for deploy.

## Layout

```
api/app/
  main.py              # FastAPI app factory + router wiring + lifespan
  config.py            # Settings dataclass — fails fast if required env vars missing
  database.py          # Async engine, get_db, get_tenant_db (RLS), Base
  audit.py             # record_audit() — commercial-tenant audit logs
  storage.py           # S3/MinIO photo helpers
  pagination.py        # PaginationParams + PaginatedResponse + paginate()
  logging_config.py
  <domain>/            # One package per bounded context
    routes.py          # HTTP-only — schemas + endpoints, delegate to service
    service.py         # Domain logic (no FastAPI imports, returns ORM/dataclasses)
    models.py          # SQLAlchemy ORM
    ...
api/migrations/versions/  # Alembic revisions
api/tests/unit/           # pytest-asyncio tests
api/scripts/              # export_openapi.py, etc.
```

## Conventions

### Routes vs service split (PR #192 / #208 / #209 / #210)
- **`routes.py` is HTTP-only.** Pydantic schemas, FastAPI `Depends`, status codes, audit calls.
- **`service.py` is domain logic.** First positional arg is always `session: AsyncSession`. Returns ORM rows, dataclasses, or primitives. **Never raise `HTTPException`** — raise typed errors (e.g. `DevicePairingError(status_code, detail)`) and let routes translate.
- Query builders that feed pagination: name them `*_query` and return `sqlalchemy.Select`.

See [`app/devices/service.py`](app/devices/service.py) and [`app/devices/routes.py`](app/devices/routes.py) for the canonical pattern.

### Database access
- All DB I/O is **async** (`AsyncSession`, `await session.execute(...)`).
- `get_db` → plain session, no tenant context.
- `get_tenant_db(tenant_id)` → sets `app.current_tenant` for RLS via `set_config()`. Use this for any per-tenant data.
- `expire_on_commit=False` is the default — re-fetch if you need post-commit state.

### Pagination
Always use [`app/pagination.py`](app/pagination.py):
```python
@router.get("/items", response_model=PaginatedResponse[ItemResponse])
async def list_items(
    pagination: Annotated[PaginationParams, Depends()],
    session: Annotated[AsyncSession, Depends(get_tenant_db)],
):
    query = service.items_query(...)
    items, total = await paginate(session, query, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)
```

### Audit logging
Mutations on commercial-plan tenants must call [`record_audit()`](app/audit.py) from the route handler. It silently no-ops for non-commercial tenants and uses a savepoint so audit failures never roll back the caller.

### Configuration
- Settings come from `os.environ` via [`app/config.py`](app/config.py). `DATABASE_URL` and `JWT_SECRET` are required.
- For tests, [`tests/conftest.py`](tests/conftest.py) sets dummy env vars **before** importing `app`.
- Never add `os.environ` reads outside `config.py`.

## Commands

All from repo root unless noted.

```bash
# Activate venv
source api/.venv/bin/activate

# Lint (CI gate, blocking)
ruff check --config api/pyproject.toml api/

# Format
ruff format --config api/pyproject.toml api/

# Type-check baseline (non-blocking, surfaces all errors)
mypy --config-file api/pyproject.toml

# Type-check strict subset (blocking — keep this list in sync with pyproject.toml)
mypy --config-file api/pyproject.toml \
  api/app/automation/suppression.py \
  api/app/automation/critical_alerts_defaults.py \
  api/app/mqtt/dedup.py \
  api/app/integrations/connectors/retry.py \
  api/app/analytics/service.py \
  api/app/admin/service.py \
  api/app/devices/service.py

# Tests (require running Postgres — see docker-compose.yml)
cd api && pytest -q
cd api && pytest tests/unit/test_devices.py -q          # single file
cd api && pytest tests/unit/test_devices.py::test_pair  # single test

# Run the API locally
cd api && uvicorn app.main:create_app --factory --reload
```

## Migrations

```bash
cd api
# Auto-generate from model changes
alembic revision --autogenerate -m "short description"
# Review the generated file in api/migrations/versions/ — autogen often misses
# server_default changes, enum renames, and check constraints.
alembic upgrade head
alembic downgrade -1   # roll back one
```

- `api/migrations/env.py` imports every model package — if you add a new top-level package with models, register it there or autogenerate will miss it.
- Migrations run in prod as a `Job` (see [`manifests/db-migration-job.yaml`](../manifests/db-migration-job.yaml)) **and** as an init container on the API pod.
- Long-form note: there is no automatic squash. Keep migrations focused.

## OpenAPI / TS client

Any route change (response_model, status code, query/path/body params, `operation_id`, docstring) shifts the OpenAPI schema and **breaks the `Verify API Types` CI job**. Regenerate before pushing:

```bash
cd web && npm run gen:types
git add web/src/lib/api-types.ts
```

The `gen:types` npm script runs `python api/scripts/export_openapi.py` and then `openapi-typescript`. Bundle the regen in the same PR as the route change.

## Gotchas

- **`redirect_slashes=False`** in `create_app()` — routes are exact. `/foo/` and `/foo` are different.
- Long string literals in seed files / templates need a per-file ignore in `[tool.ruff.lint.per-file-ignores]`. Don't disable rules globally.
- `S101` (assert) and `S106` (hardcoded passwords) are allowed in `tests/**`; do not move them.
- `B008` is ignored project-wide because FastAPI's `Depends(...)` in defaults is intentional.
- New strict-mypy modules are a **one-way ratchet**: only add to the override list, never remove.
- Lifespan auto-seeds reference data and **swallows exceptions** as non-fatal. Don't rely on seed completion in request handlers; use explicit reads.
