## Context
Auto-task generation loops over 79 templates, and for each matching template runs `for day_offset in range(0, horizon_days, interval_days)`, inserting one `Task` row per occurrence. With a 7-day horizon this materializes daily checks as 7 rows each. Measured volume for one grow (7-day horizon):

| grow type / stage | distinct templates | task rows created |
|---|---|---|
| dwc / vegetative | 17 | **52** |
| aquaponics / vegetative | 17 | 58 |
| coco / flowering | 14 | 52 |
| soil / vegetative | 12 | 32 |

The morning routine alone for dwc/veg is 32 of those 52 rows (pH, EC, water-temp, health each daily → 7 rows; top-off every 2 days → 4). The generator re-runs every 6h and re-extends the horizon; pending rows never expire, so backlog is unbounded and scales with grow count.

The `Task` model already carries `recurring`, `recurring_parent_id`, `routine`, and `estimated_minutes`, and `complete_task` already spawns the next occurrence for a recurring task — the generator simply doesn't use these. This change realigns generation with the model the app already has.

## Goals / Non-Goals
- Goals:
  - Cut open auto-task row count from O(templates × horizon days) to O(templates) per grow.
  - Present daily care as a small number of routine checklists, not dozens of cards.
  - Prevent unbounded overdue backlog (roll forward, don't backfill).
  - Fix the `every_N_days` recurrence gap.
  - Preserve all horticultural coverage: same grow-type/stage filters, automation suppression, strain-based harvest/flush one-shots.
- Non-Goals:
  - Rewriting template *content* or merging horticulturally distinct checks (a separate content pass).
  - Task *timing* intelligence (timezone/light-cycle/reminders) — owned by `add-smart-task-timing`.
  - Changing manual task CRUD semantics.

## Decisions

### Decision 1: Recurring seed rows, not a materialized horizon
Generate at most **one open (`pending`/`in_progress`) auto task per (grow, category, routine)** — the next due occurrence. The generation loop drops the inner `range(0, horizon, interval)` and inserts a single row with `recurring_interval_days = tmpl.interval_days` and `recurring` set to the human label (`daily`, `every_2_days`, `weekly`, …). The existing `_task_exists`/dedup guard keeps re-runs idempotent.
- Alternatives considered: (a) keep materializing but hide future rows in the UI — rejected, backlog still grows in the DB and overdue math stays broken; (b) shrink horizon to 1 day — rejected, still 1 row per check per day and loses the recurrence contract.

### Decision 2: Persist interval as an integer column
Add `recurring_interval_days: int | None` to `tasks`. Auto tasks set it from the template; manual tasks may leave it null and keep using the `recurring` string. A single resolver `next_due(task, from_time)` computes the delta from `recurring_interval_days` when present, else from the `recurring` string map (extended with `every_2_days`/`every_3_days`). This fixes the latent gap where those UI options never respawned.
- Alternatives considered: encoding everything in the `recurring` string (e.g. `every_3_days`) — workable but stringly-typed and awkward for 14/30/90-day intervals; the int column is simpler to compute with and index.

### Decision 3: Roll forward on completion/skip (no backfill)
When a recurring task is completed or skipped, the next occurrence's `due_date` is `max(now, current_due) + interval`, snapped to the routine's time-of-day. This guarantees exactly one open occurrence and that it is never already overdue at creation — so a grower who ignores the app for a week returns to *one* pending check per routine, not seven.

### Decision 4: Routine grouping is a read-time projection
Add `GET /v1/tasks/routines?grow_cycle_id=&date=` returning tasks grouped by `routine` for the target day with an aggregate `estimated_minutes` per group. No schema change beyond Decision 2 — it's a projection over existing rows. "Complete routine" reuses the existing bulk endpoint (each task still spawns its own next occurrence via the single-complete path, so the bulk path is extended to honor recurrence for routine completion).

### Decision 5: Today-first default view
Frontend defaults the list to due-today + overdue using the existing `due_from`/`due_to` query params; "Upcoming" and "All" remain one tap away. No new backend filter is required.

### Decision 6: One-time cleanup-and-regenerate (supersedes in-place consolidation)
Rather than collapsing and backfilling existing rows in SQL, a one-time operation **deletes every open (`pending`/`in_progress`) `source='auto'` task across all tenants and all grows (active and past), then regenerates recurring seeds for active grows only** using the new generator. Regeneration produces correct seeds by construction, so no interval backfill or per-row mapping is required. Manual (`source='manual'`), AI (`source='ai'`), and completed/cancelled rows are never touched; past/finished grows are cleaned but not repopulated (a finished grow needs no care tasks).

Because it must call app logic (async session, timezone loaders, suppression) that is impractical in raw Alembic SQL, it ships as an **idempotent management script** — `api/scripts/cleanup_and_regen_tasks.py` — run once **after** the schema migration and code deploy. It uses `app.database.async_session_factory()` for a cross-tenant session (the same pattern the scheduler's `generate_all_tasks` uses to see every tenant), and commits the delete **before** regeneration so the `_task_exists` tombstone cannot block regen (the same ordering as `reset_auto_tasks_for_grow_type_change`). A k8s `Job` (mirroring `manifests/db-migration-job.yaml`) invokes it in production.
- Alternatives considered: in-place SQL consolidation (collapse + backfill interval) — rejected as more error-prone (must infer intervals from `routine`) and redundant once regen is authoritative.

## Risks / Trade-offs
- **Test harness gap** → `automation_suppressions` and `stage_transition_tasks` tables don't exist in the unit test DB (`create_all` only). Generation tests must assert on the seed/dedup logic paths that don't require those tables, or stub the loaders — mirror the existing route try/except pattern.
- **`_task_exists` tombstone** → it filters by `source='auto'` but not status, so a cancelled row blocks same-day regeneration. The cleanup must **delete** (not cancel) open auto rows and commit before regen, and skip must spawn-then-cancel in that order.
- **OpenAPI drift** → new endpoint + params change the schema; regenerate `web/src/lib/api-types.ts` (blocking `Verify API Types` gate) in the same PR.
- **Cleanup on large fleets** → the cross-tenant delete + regen runs per tenant with a commit per tenant to bound transaction size and lock time; per-grow failures are isolated (log and continue), and a `--dry-run` reports counts before any write.

## Migration Plan
1. Add nullable `recurring_interval_days` column (no default → no table rewrite).
2. Deploy generator + completion changes (backward compatible: old materialized rows still complete normally).
3. Run the one-time cleanup-and-regenerate operation (`api/scripts/cleanup_and_regen_tasks.py`, or the k8s Job) to delete open auto tasks across all tenants/grows and regenerate recurring seeds for active grows. Run with `--dry-run` first to review counts.
4. Rollback: drop the column and revert code; materialized generation resumes on the next 6h cycle. No history is lost — cleanup only removed open auto tasks (manual/AI/completed preserved), and active grows are repopulated by regen (or by the scheduler if the script is not re-run).

## Open Questions
- Should `every_2_days`/`every_3_days` be surfaced as first-class routine labels, or normalized to the numeric interval only? (Leaning: keep the label for display, drive logic from the integer.)
- Should routine grouping also apply on the cross-grow `/dashboard/tasks` page, or only per-grow? (Leaning: both, grouped within grow.)
