# Implementation Tasks

## 1. Data model & migration
- [x] 1.1 Add `recurring_interval_days: Mapped[int | None]` to `Task` in [api/app/commercial/models.py](api/app/commercial/models.py)
- [x] 1.2 Alembic migration: add nullable `recurring_interval_days` column (no default → avoids table rewrite)
- [x] 1.3 Keep the Alembic migration **schema-only**; existing-data cleanup is handled by the one-time cross-tenant operation in section 7 (which supersedes any in-place SQL consolidation). Ensure the column is picked up by `migrations/env.py` autogenerate

## 2. Recurrence resolver & completion
- [x] 2.1 Add `next_due(task, from_time)` helper resolving the delta from `recurring_interval_days` (preferred) or the `recurring` string map, extended with `every_2_days`/`every_3_days`
- [x] 2.2 Update `complete_task` in [api/app/commercial/task_routes.py](api/app/commercial/task_routes.py) to spawn the next occurrence via `next_due`, rolling forward: `due = max(now, current_due) + interval`, snapped to routine time-of-day
- [x] 2.3 Add skip action (`POST /v1/tasks/{id}/skip`): close current occurrence (delete or dedicated `skipped` status) and spawn the next occurrence; ensure spawn happens before close so the `_task_exists` tombstone does not block it
- [x] 2.4 Ensure single-complete and bulk-complete both honor recurrence for routine completion

## 3. Generator (recurring seeds)
- [x] 3.1 In [api/app/scheduler/task_generator.py](api/app/scheduler/task_generator.py) `generate_tasks_for_grow`, replace the `range(0, horizon_days, interval_days)` materialization with a single seed per template: set `recurring`, `recurring_interval_days`, and `due_date` = next occurrence
- [x] 3.2 Preserve grow-type/stage filters, automation suppression + verify-task path, rain-skip, and strain-based flush/harvest one-shots
- [x] 3.3 Keep dedup idempotent: only create when no open occurrence exists for (grow, category); confirm `_task_exists` semantics still hold
- [x] 3.4 Update `reset_auto_tasks_for_grow_type_change` to regenerate seeds (not a horizon)

## 4. Routine-grouped API
- [x] 4.1 Add a routine-grouping service projection over existing rows (group by `routine`, sum `estimated_minutes`, omit empty groups)
- [x] 4.2 Add `GET /v1/tasks/routines?grow_cycle_id=&date=` returning grouped response with per-group totals
- [x] 4.3 Add a "complete routine" path (reuse `/bulk` or add `complete_routine`) that completes all tasks in a group and spawns each recurring next occurrence
- [x] 4.4 Follow route/service split rules (no `HTTPException` in service code); add audit calls where mutating

## 5. Frontend
- [x] 5.1 Add routine-card rendering in [web/src/app/dashboard/grows/[id]/tasks-tab.tsx](web/src/app/dashboard/grows/%5Bid%5D/tasks-tab.tsx): collapsible "Morning check — N items, ~M min" with per-item checkboxes and "Complete all"
- [x] 5.2 Default the grow tasks tab and [web/src/app/dashboard/tasks/page.tsx](web/src/app/dashboard/tasks/page.tsx) to a today-first view (due-today + overdue) using existing `due_from`/`due_to`; keep Upcoming/All/Calendar toggles
- [x] 5.3 Wire the skip action into the task card menu and swipe gestures
- [x] 5.4 Show recurrence interval (e.g. "every 3 days") from `recurring_interval_days`

## 6. Types, tests, docs
- [x] 6.1 Regenerate `web/src/lib/api-types.ts` (`cd web && npm run gen:types`) and commit alongside route changes
- [x] 6.2 API unit tests: generator emits one open row per template (not a horizon); completion spawns exactly one future occurrence; overdue completion rolls forward; `every_2_days`/`every_3_days` respawn; skip advances without completing; routine grouping totals. Respect the test-DB gap (no `automation_suppressions`/`stage_transition_tasks` — assert on paths not needing them or stub loaders)
- [x] 6.3 Migration test: materialized duplicates collapse to one open occurrence; history preserved
- [x] 6.4 Web tests: routine card renders grouped items and total; today-first default; skip action
- [x] 6.5 Update task docs (behavior + recurrence model) if user-facing docs reference task generation

## 7. One-time cleanup & regeneration (cross-tenant — ALL tenants, ALL grows)
> Goal: migrate existing installs off the materialized flood in one pass. This is fully self-contained so any implementer can build it without further design input.
- [x] 7.1 Create idempotent async script `api/scripts/cleanup_and_regen_tasks.py`. Bootstrap a cross-tenant session with `app.database.async_session_factory()` (same pattern as the scheduler's `generate_all_tasks` — the background/admin session sees every tenant, so no per-tenant RLS filter is needed). Read all env/config only via `app/config.py`
- [x] 7.2 Cleanup step: delete every task where `source == 'auto'` AND `status IN ('pending','in_progress')`, for ALL tenants and ALL grows — active and past, including auto tasks with a null `grow_cycle_id`. Use a single `DELETE ... WHERE` (optionally chunked). **Commit the delete BEFORE regeneration** so the `_task_exists` tombstone cannot block regen
- [x] 7.3 Preserve set (never delete): `source IN ('manual','ai')` and `status IN ('completed','cancelled')`
- [x] 7.4 Regen step: select every `GrowCycle` with `status == 'active'` across all tenants and call the new recurring-seed `generate_tasks_for_grow` for each. Do **not** regenerate for non-active grows (completed/archived/harvested) — those are cleaned only
- [x] 7.5 Fault isolation: wrap each grow in `try/except`, log the exception, and continue (mirror `generate_all_tasks`). Commit per tenant (or per grow batch) to bound transaction size and lock time. Track running totals
- [x] 7.6 CLI flags: `--dry-run` (compute and print delete/regen counts, write nothing), `--tenant <uuid>` (scope to one tenant for testing/staged rollout), `--yes` (non-interactive, required in the Job). Print a final summary line: tenants processed, grows cleaned, auto tasks deleted, tasks regenerated, errors
- [x] 7.7 Idempotency: deletion is naturally idempotent; regeneration must rely on the generator's one-open-occurrence dedup so a second run produces no duplicates. Verify a back-to-back re-run is a no-op beyond logging
- [x] 7.8 Add k8s Job manifest `manifests/cleanup-regen-tasks-job.yaml` mirroring [manifests/db-migration-job.yaml](manifests/db-migration-job.yaml), with `command: ["python", "-m", "scripts.cleanup_and_regen_tasks", "--yes"]`, `envFrom` the `tendril-secrets` secret, `PYTHONPATH=/app`, and `restartPolicy: OnFailure`. Document that it runs **once, after** the schema migration (1.2) and the code deploy (sections 2–4)
- [x] 7.9 Tests (`api/tests/`): seed a tenant with materialized-style pending auto tasks on an active grow AND a completed grow, plus `manual`, `ai`, and already-`completed` tasks. Run the cleanup and assert: all open `auto` tasks removed everywhere; `manual`/`ai`/`completed`/`cancelled` preserved; the completed grow is not regenerated; `--dry-run` writes nothing; a second run is idempotent. Respect the test-DB harness gap (no `automation_suppressions`/`stage_transition_tasks` tables): assert the DELETE side, and either stub the generator loaders or catch its expected failure per the route try/except pattern
- [x] 7.10 Runbook: document sequencing (migrate → deploy → dry-run → run Job), expected output, and rollback in the change notes / ops docs

## 8. Validation
- [x] 8.1 `ruff check --config api/pyproject.toml api/` and `mypy` strict subset pass
- [x] 8.2 `npm run lint` and `npm run verify:types` pass in `web/`
- [x] 8.3 `openspec validate simplify-task-generation --strict --no-interactive` passes
