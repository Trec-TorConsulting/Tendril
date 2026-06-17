---
description: Create, review, and apply a new Alembic migration for the Tendril API.
---

$ARGUMENTS

**Prerequisites**
- Postgres is running locally (`docker-compose up -d postgres`).
- `api/.venv` is activated with `pip install -r api/requirements.txt -r api/requirements-dev.txt`.
- The model change is already written in `api/app/<domain>/models.py`.
- If you added a brand-new top-level package containing models, register it in `api/migrations/env.py` first or autogenerate will miss the tables.

**Steps**
1. Generate the revision:
   ```bash
   cd api
   alembic revision --autogenerate -m "short imperative description"
   ```
2. **Review the generated file** in `api/migrations/versions/`. Autogenerate is reliable for: new tables, new columns, dropped columns, simple index changes. It frequently **misses**:
   - `server_default` changes
   - Enum value additions / renames
   - Check constraints
   - Comment / docstring changes
   - Data migrations (always hand-written)

   Edit the `upgrade()` / `downgrade()` functions to fix anything missing or wrong. Both directions must be implemented and reversible.
3. Test forward + backward locally:
   ```bash
   alembic upgrade head
   alembic downgrade -1
   alembic upgrade head
   ```
4. Run the relevant tests:
   ```bash
   pytest tests/unit/test_migrations_audit.py -q
   pytest tests/unit/ -q -k <related_domain>
   ```
5. Lint:
   ```bash
   ruff check --config pyproject.toml app/ migrations/
   ```
6. If model changes alter API responses, also regenerate types — see [regen-api-types.prompt.md](regen-api-types.prompt.md).
7. Commit the new revision file plus the model change in one PR.

**Production deploy notes**
- Migrations run as both a `Job` (`manifests/db-migration-job.yaml`) and the API pod's init container. Either path will apply the new revision; both must succeed with the same image tag.
- For long-running migrations (large `ALTER TABLE`, backfills) split into multiple revisions: schema change first, backfill next, constraint tightening last. This keeps the init container under its timeout and avoids blocking new pods.
- RLS-protected tables: new tables with a `tenant_id` column need an explicit RLS policy in the migration. Search existing migrations for `CREATE POLICY` for the template.

**Pitfalls**
- Never edit a migration that has already been applied to any environment. Add a new revision instead.
- `alembic revision` (without `--autogenerate`) creates an empty file — use it for pure data migrations or when autogenerate would produce the wrong thing.
- `down_revision` is auto-set to the current head. If you generate two migrations on separate branches that both target the same parent, merge them with `alembic merge`.
