# Refactor Task Engine

## Summary
Overhaul the auto-task generation system to produce grow-type-accurate, time-aware, routine-grouped tasks with estimated durations, conditional logic, and progressive disclosure — transforming the current list of isolated reminders into an enterprise-grade daily workflow system.

## Motivation
The current task engine has significant usability and accuracy gaps:

1. **All tasks fire at 9 AM UTC** — no timezone awareness, no relation to light schedule or time-of-day relevance.
2. **No routine grouping** — tasks are individual items; users see 8-12 scattered items instead of "Morning Check (5 min)" and "Weekly Maintenance (45 min)".
3. **Grow-type intervals are wrong** — Kratky (designed to be passive) gets daily checks; soil gets unnecessary daily pH; coco in flower needs multi-daily watering but says "daily".
4. **Missing critical tasks** — no IPM rotation, equipment maintenance, meter calibration, photo documentation, nutrient prep, or deep clean tasks.
5. **No estimated duration** — users can't plan their day or know if a task takes 2 minutes or 60 minutes.
6. **No conditional/dismissible logic** — if you have auto-dosing, daily pH/EC tasks are noise with no way to suppress.
7. **Descriptions are educational essays** — useful for first-time growers, annoying for experienced ones on day 50 of the same task.

## Goals
- Tasks accurately reflect what each grow type/media ACTUALLY needs at each stage
- Time-of-day relevance (morning checks vs evening checks vs light-schedule-relative)
- Routine-based grouping (Morning, Evening, Weekly, Monthly bundles)
- Estimated duration per task so users can plan
- Equipment/automation awareness to suppress irrelevant tasks
- Progressive disclosure (quick checklist default, educational on expand/first-time)
- Add missing task categories (IPM, equipment, calibration, documentation)

## Non-Goals
- Changing the Task database model schema (reuse existing fields)
- Changing the frontend UI/UX significantly (task cards stay the same)
- Changing the scheduler infrastructure (leader election, intervals)
- Adding new API endpoints (existing CRUD is sufficient)

## Scope
- **Backend**: `api/app/scheduler/task_generator.py` — complete rewrite of `TASK_TEMPLATES` and generation logic
- **Backend**: Add `routine` and `estimated_minutes` fields to Task model (additive migration)
- **Frontend**: Minor updates to display routine grouping and duration badges
- **No breaking changes** to existing API contracts

## Risks
- Existing tasks in production will not retroactively update (acceptable — new tasks generate correctly going forward)
- Users with custom workflows built around current task timing may notice changes
