# Change: Add Smart Task Timing (Lights- and Timezone-Aware Scheduling)

## Why
Task generation ([api/app/scheduler/task_generator.py](api/app/scheduler/task_generator.py), [tasks.py](api/app/scheduler/tasks.py)) runs on a fixed 6h cycle with **no timezone awareness** (an explicit TODO in the code) and **no light-cycle awareness**. As a result, watering/fertigation tasks can land at 3 AM, dark-period checks are mistimed, and due dates never trigger reminders. Tasks should be generated and scheduled at the moment they make sense for the grow's light schedule and the user's timezone, and due tasks should remind the user.

## What Changes
- Make task generation **timezone-aware** using the tenant/grow timezone, resolving the existing TODO.
- Make task timing **light-cycle-aware**: schedule lights-on tasks (watering, fertigation, inspection) at/near lights-on, and dark-period tasks during the dark period, based on the grow's configured light schedule.
- Add **due-date reminders**: when a task's due time approaches/passes, notify the user (in-app always, push for high/urgent priority) via the existing notification service.
- Preserve existing template semantics (grow-type + stage filters, routine intervals); only the *timing* of generation/scheduling and reminders change.

## Impact
- Affected specs:
  - task-scheduling (NEW capability)
- Affected code (expected):
  - api/app/scheduler/task_generator.py (timezone + light-cycle timing)
  - api/app/scheduler/tasks.py (reminder job)
  - api/app/notifications/service.py (due reminders)
  - relevant grow/tent model fields for light schedule + timezone
- Data model impact:
  - MAY add a light-schedule/timezone field if not already present (new tables/columns approved); reminder state can reuse task fields
- Security impact:
  - tenant-scoped; respects notification preferences
- Breaking changes:
  - none; falls back to current behavior when timezone/light-schedule unknown
