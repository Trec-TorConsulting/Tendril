# Change: Simplify Auto-Task Generation (Recurring Seeds + Routine Bundling)

## Why
Auto-task generation ([api/app/scheduler/task_generator.py](api/app/scheduler/task_generator.py)) **materializes every occurrence** of every matching template across a rolling 7-day horizon. A single DWC grow in vegetative stage produces **52 task rows per week** from 17 templates — five *separate* cards (pH, EC, water-temp, health, top-off) every single morning. The horizon is re-extended every 6 hours and pending tasks never expire, so the backlog grows without bound and multiplies per grow (10 grows ≈ 520 open rows). The current UX ships a "Complete all overdue" bulk button — a workaround that confirms the flood is a known pain point.

The data model already has the tools to fix this (`recurring`, `recurring_parent_id`, `routine`, `estimated_minutes` on [Task](api/app/commercial/models.py)), and `complete_task` already spawns the next recurring occurrence — but generation ignores them and materializes instead. There is also a latent bug: the UI offers `every_2_days`/`every_3_days` recurrence, but the completion `delta_map` only handles daily/weekly/biweekly/monthly, so those never respawn.

## What Changes
- **BREAKING (data model)**: Generate **one recurring "seed" task per template per grow** (the next due occurrence) instead of materializing the full horizon. Add a `recurring_interval_days` column so the next occurrence can be computed for any interval (1, 2, 3, 7, 14, 30, 90 days).
- Completing (or skipping) a recurring task **rolls the next occurrence forward** to a future due time — never backfilling missed days — so overdue tasks can't pile up.
- Add a **routine-grouped view**: daily checks collapse into a single "Morning check" checklist card with an aggregate time estimate and a **complete-all-in-routine** action, instead of 5 separate cards.
- Default the task list to a **today-first view** (due-today + overdue only); future occurrences move to an opt-in "Upcoming"/calendar view.
- Add a **skip/snooze** action that advances a single occurrence without marking it done.
- **One-time cleanup + regen (ALL tenants, ALL grows)**: ship an idempotent operation that **deletes every open auto task** across every tenant and every grow — active and past — and then **regenerates recurring seeds for active grows only**. This migrates existing installs off the materialized flood in one pass. Manual tasks, AI tasks, and completed/cancelled history are preserved; past/finished grows are cleaned but not repopulated.

## Impact
- Affected specs: `task-management` (NEW capability)
- Affected code:
  - [api/app/scheduler/task_generator.py](api/app/scheduler/task_generator.py) — recurring-seed generation (replaces materialized loop); preserves grow-type/stage filters, automation suppression, and strain harvest one-shots
  - [api/app/commercial/task_routes.py](api/app/commercial/task_routes.py) — interval-aware recurrence spawn, routine-grouped endpoint, skip action
  - [api/app/commercial/models.py](api/app/commercial/models.py) — `recurring_interval_days` column
  - `api/migrations/versions/` — add `recurring_interval_days` column (schema only)
  - `api/scripts/cleanup_and_regen_tasks.py` (NEW) + `manifests/cleanup-regen-tasks-job.yaml` (NEW) — one-time cross-tenant cleanup + regeneration
  - [web/src/app/dashboard/grows/[id]/tasks-tab.tsx](web/src/app/dashboard/grows/%5Bid%5D/tasks-tab.tsx), [web/src/app/dashboard/tasks/page.tsx](web/src/app/dashboard/tasks/page.tsx) — routine cards + today-first default
  - `web/src/lib/api-types.ts` — regenerated from OpenAPI
- Relationship to pending work: **orthogonal** to `add-smart-task-timing` (which changes *when* tasks fire — timezone/light-cycle/reminders). This change reduces *how many* tasks exist and *how* they are presented. The two compose cleanly.
- Breaking changes: task row semantics change (recurring seed vs materialized). No public API contract is removed; new fields/endpoints are additive.
