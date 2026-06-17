---
description: Tendril API (FastAPI + SQLAlchemy async) conventions — auto-attached to Python files under api/.
applyTo: "api/**/*.py"
---

# Tendril API — Per-file rules

Read [`api/AGENTS.md`](../../api/AGENTS.md) for the full guide. Key rules enforced here:

## Routes vs service split
- `routes.py` is HTTP-only: Pydantic schemas, `Depends`, status codes, audit calls.
- `service.py` holds domain logic. First positional arg is `session: AsyncSession`. **Never** raise `HTTPException` from service code — raise a typed error and let the route translate.
- Query-builder helpers return `sqlalchemy.Select` and are named `*_query`.

## Database
- All DB I/O is `async`. Always `await`.
- Use `get_tenant_db` (RLS-aware) for tenant data. `get_db` for cross-tenant admin work only.
- Sessions are `expire_on_commit=False` — refetch if you need post-commit state.

## Pagination
Use `app.pagination.PaginationParams` / `paginate` / `PaginatedResponse[T]`. Don't re-implement offset/limit.

## Audit logs
Mutations call `app.audit.record_audit(...)` from the route. It's a no-op outside commercial tenants and uses a savepoint — safe to call unconditionally.

## Config
- All env reads live in `app/config.py`. Don't add `os.environ.get(...)` elsewhere.
- Required vars: `DATABASE_URL`, `JWT_SECRET`. Failing fast at import is intentional.

## Lint / type-check
- `ruff check --config api/pyproject.toml api/` is the blocking gate.
- Adding a module to `[[tool.mypy.overrides]]` strict list is a one-way ratchet — don't remove entries.
- Per-file ruff ignores go in `[tool.ruff.lint.per-file-ignores]`, not inline `# noqa` (except for genuine one-offs).

## OpenAPI contract
Any change to a route's response_model, status code, params, `operation_id`, or **docstring** changes the OpenAPI schema and breaks the `Verify API Types` CI job. Run `npm run gen:types` in `web/` and commit `web/src/lib/api-types.ts` in the same PR.

## Pitfalls
- `redirect_slashes=False` — `/foo` and `/foo/` are distinct routes.
- New top-level model packages must be imported in `api/migrations/env.py` or autogenerate misses them.
- The lifespan handler seeds reference data and swallows exceptions; don't depend on seed completion in handlers.
