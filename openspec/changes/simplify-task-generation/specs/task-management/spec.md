# Capability: Task Management

## Purpose
Determine which recurring care tasks exist for a grow and present them with minimal noise. Auto-generated tasks are stored as recurring "seeds" (one open occurrence at a time) and surfaced as routine checklists, so a grower sees a short, actionable list instead of a materialized flood of one-per-day rows.

## ADDED Requirements

### Requirement: Recurring Seed Task Generation
The system SHALL create at most one open (`pending` or `in_progress`) auto-generated task per grow, category, and routine at any time, representing the next due occurrence — rather than materializing every occurrence across a scheduling horizon.

#### Scenario: Daily template yields a single open task
- **WHEN** task generation runs for a grow whose grow type and stage match a daily-interval template
- **THEN** exactly one open auto task exists for that category, carrying its recurrence interval

#### Scenario: Regeneration does not duplicate an open occurrence
- **WHEN** generation runs again while an open occurrence for the same grow and category already exists
- **THEN** no additional task is created for that category

#### Scenario: Grow-type and stage filters preserved
- **WHEN** a template does not match the grow's type or stage
- **THEN** no task is generated for that template

#### Scenario: Automation suppression preserved
- **WHEN** an automation covers a template's category for the grow
- **THEN** the routine task is suppressed and a verification task is generated instead

### Requirement: Recurrence Interval Persistence
The system SHALL persist each recurring task's interval so its next occurrence can be computed on completion, supporting daily, every-2-day, every-3-day, weekly, biweekly, monthly, and longer intervals.

#### Scenario: Auto task stores its interval
- **WHEN** an auto task is generated from a template with an interval of N days
- **THEN** the task records an interval of N days

#### Scenario: Every-N-days recurrence is honored
- **WHEN** a task has an every-2-day or every-3-day recurrence
- **THEN** the system can compute its next occurrence (this case previously produced no next occurrence)

### Requirement: Next-Occurrence Spawn On Completion
Completing a recurring task SHALL create its next occurrence with a due time rolled forward to the future, and SHALL NOT create occurrences for dates already missed.

#### Scenario: Completion spawns the next occurrence
- **WHEN** a user completes a recurring task
- **THEN** a single new open task is created for the next interval

#### Scenario: Overdue completion rolls forward
- **WHEN** a user completes a recurring task whose due date is already in the past
- **THEN** the next occurrence's due time is in the future, not backfilled to the missed date

#### Scenario: Non-recurring task does not spawn
- **WHEN** a user completes a task that has no recurrence
- **THEN** no next occurrence is created

### Requirement: Routine-Grouped Task View
The system SHALL expose auto and manual tasks grouped by routine for a target day, with an aggregate time estimate per routine group.

#### Scenario: Daily checks grouped into one routine
- **WHEN** a grow has multiple morning-routine tasks due on a day
- **THEN** they are returned as a single morning group listing each item

#### Scenario: Group reports aggregate time
- **WHEN** a routine group is returned
- **THEN** it includes the summed estimated minutes of its tasks

#### Scenario: Empty routine omitted
- **WHEN** a routine has no tasks due for the target day
- **THEN** that routine group is not returned

### Requirement: Complete Entire Routine
The system SHALL allow a user to complete every task in a routine group for a day in a single action, and each completed recurring task SHALL spawn its next occurrence.

#### Scenario: Complete-all clears the routine
- **WHEN** a user completes a routine group
- **THEN** all tasks in that group become completed

#### Scenario: Recurring items reschedule
- **WHEN** a routine group containing recurring tasks is completed
- **THEN** each recurring task's next occurrence is created

### Requirement: Today-First Default View
The default task listing SHALL show only tasks that are due today or overdue, with upcoming occurrences available through an explicit opt-in view.

#### Scenario: Default excludes future occurrences
- **WHEN** a user opens the task list without changing filters
- **THEN** only tasks due today or overdue are shown

#### Scenario: Upcoming view is opt-in
- **WHEN** a user selects the upcoming or calendar view
- **THEN** future occurrences are shown

### Requirement: Skip Occurrence
The system SHALL allow a user to skip a single recurring occurrence, advancing to the next occurrence without recording a completion.

#### Scenario: Skip advances the occurrence
- **WHEN** a user skips a recurring task
- **THEN** the current occurrence is closed and the next occurrence is created in the future

#### Scenario: Skipped task is not counted as completed
- **WHEN** a user skips a task
- **THEN** the task is not marked completed and does not appear in completion history

### Requirement: One-Time Task Cleanup And Regeneration
The system SHALL provide a one-time, idempotent, cross-tenant operation that removes every open (`pending` or `in_progress`) auto-generated task for all tenants and all grows — active and past — and then regenerates fresh recurring-seed tasks for active grows only. The operation SHALL preserve manually created tasks, AI-generated tasks, and completed or cancelled task history, and SHALL support a dry-run mode.

#### Scenario: Open auto tasks removed for every tenant and grow
- **WHEN** the cleanup operation runs
- **THEN** every task with source `auto` and status `pending` or `in_progress` is removed for all tenants, across both active and past grows

#### Scenario: Manual and AI tasks preserved
- **WHEN** the cleanup operation runs
- **THEN** tasks with source `manual` or `ai` are not deleted

#### Scenario: Completed and cancelled history preserved
- **WHEN** the cleanup operation runs
- **THEN** tasks with status `completed` or `cancelled` are left unchanged

#### Scenario: Active grows regenerated as recurring seeds
- **WHEN** the cleanup completes for a grow whose status is active
- **THEN** that grow has fresh recurring-seed auto tasks consistent with the new generation model

#### Scenario: Past grows are cleaned but not regenerated
- **WHEN** a grow is completed, archived, or otherwise not active
- **THEN** the operation removes its open auto tasks and generates no new tasks for it

#### Scenario: Failure for one grow does not abort the run
- **WHEN** regeneration fails for a single grow
- **THEN** the operation logs the failure and continues processing the remaining tenants and grows

#### Scenario: Re-running is idempotent
- **WHEN** the operation runs more than once
- **THEN** it creates no duplicate tasks and removes no additional preserved tasks

#### Scenario: Dry run makes no changes
- **WHEN** the operation runs in dry-run mode
- **THEN** it reports the tasks it would delete and regenerate and modifies no data
