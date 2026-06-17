---
description: Regenerate web/src/lib/api-types.ts from the FastAPI OpenAPI schema and stage it for commit.
---

$ARGUMENTS

**When to run**
- Any change to an API route: `response_model`, status code, query/path/body param, `operation_id`, or **docstring**.
- CI failure on the `Verify API Types` job.

**Steps**
1. Confirm the Python env has the API deps installed. From repo root, `python -c "import fastapi"` should succeed. If not:
   ```bash
   source api/.venv/bin/activate || python -m venv api/.venv && source api/.venv/bin/activate
   pip install -r api/requirements.txt
   ```
2. Run the regen script:
   ```bash
   cd web && npm run gen:types
   ```
   This shells out to `python api/scripts/export_openapi.py`, then runs `openapi-typescript` to produce `web/src/lib/api-types.ts`.
3. Inspect the diff:
   ```bash
   git diff --stat web/src/lib/api-types.ts
   git diff web/src/lib/api-types.ts | head -200
   ```
   The diff should be **small and explainable** — only the routes/schemas you actually changed. If it's huge, you likely regenerated against the wrong branch or with stale deps.
4. Verify the same command CI runs passes locally:
   ```bash
   cd web && npm run verify:types
   ```
5. Stage and include in the same commit/PR as the route change:
   ```bash
   git add web/src/lib/api-types.ts
   ```

**Notes**
- `npm run gen:types` assumes `python` is on PATH and resolves to an interpreter with the API deps. On macOS dev shells, activate `api/.venv` first.
- `export_openapi.py` sets dummy `DATABASE_URL` / `JWT_SECRET` so it never opens a DB connection. Safe to run anywhere.
- Do not hand-edit `web/src/lib/api-types.ts`. It is fully regenerated each run.
