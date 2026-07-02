## 1. Backend — timezone awareness
- [ ] 1.1 Resolve the effective timezone for a grow (grow → tent → tenant default → UTC). Add a helper `resolve_grow_timezone(grow)`.
- [ ] 1.2 Update `api/app/scheduler/task_generator.py` to compute task `due_date`/scheduled time in the grow's local timezone, resolving the existing timezone TODO.
- [ ] 1.3 Add a light-schedule source: reuse an existing light-schedule field if present, else add a `light_on_time`/`light_off_time` (or photoperiod) field to the grow/tent model + migration.

## 2. Backend — light-cycle-aware timing
- [ ] 2.1 Classify each task template as lights-on, dark-period, or anytime (add a `timing` attribute to `TaskTemplate`).
- [ ] 2.2 When generating tasks, set the scheduled/suggested time to align with the grow's light cycle (lights-on tasks near lights-on; dark-period tasks during dark).
- [ ] 2.3 Ensure generation still respects routine intervals and grow-type/stage filters (no change to eligibility, only timing).

## 3. Backend — due-date reminders
- [ ] 3.1 Add a scheduler reminder job that finds tasks whose due time is approaching/passed and not yet reminded.
- [ ] 3.2 Dispatch reminders in-app always; web push for high/urgent priority, honoring notification preferences.
- [ ] 3.3 Track `reminded_at` on the task (or reminder state) to avoid duplicate reminders.

## 4. Frontend
- [ ] 4.1 Show localized due times on tasks (`web/src/app/dashboard/tasks/page.tsx`) in the user's timezone.
- [ ] 4.2 Add a light-schedule/timezone setting UI if a new field was introduced.

## 5. Testing
- [ ] 5.1 Unit tests for `resolve_grow_timezone` precedence.
- [ ] 5.2 Test that lights-on tasks schedule near lights-on and dark tasks during dark for a sample schedule.
- [ ] 5.3 Test due-reminder job fires once (reminded_at prevents duplicates) and respects priority-based push.
- [ ] 5.4 Test fallback when timezone/light schedule is unknown (no crash, current behavior).
- [ ] 5.5 Migration test if a new field/column was added.

## 6. Validation
- [ ] 6.1 Run `openspec validate add-smart-task-timing --strict --no-interactive`.
- [ ] 6.2 Regenerate API types if models changed; run lint + API + web tests.
