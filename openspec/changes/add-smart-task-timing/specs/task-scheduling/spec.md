# Capability: Task Scheduling

## Purpose
Time-intelligent generation and scheduling of grow tasks. Tasks are created and timed according to the grow's light cycle and the user's timezone, and due tasks generate reminders — so routine care lands at the right moment rather than on a blind fixed interval.

## ADDED Requirements

### Requirement: Timezone-Aware Task Timing
The system SHALL compute task due and scheduled times in the grow's effective local timezone.

#### Scenario: Local due time
- **WHEN** a task is generated for a grow with a known timezone
- **THEN** its due/scheduled time is computed in that timezone

#### Scenario: Timezone fallback
- **WHEN** no timezone is configured for the grow, tent, or tenant
- **THEN** the system falls back to UTC without error

### Requirement: Light-Cycle-Aware Scheduling
The system SHALL schedule tasks relative to the grow's light cycle based on each task's timing classification.

#### Scenario: Watering scheduled at lights-on
- **WHEN** a lights-on task (e.g., watering or fertigation) is generated
- **THEN** its suggested time aligns with the grow's lights-on time

#### Scenario: Dark-period task
- **WHEN** a dark-period task is generated
- **THEN** its suggested time falls within the grow's dark period

#### Scenario: Unknown light schedule
- **WHEN** the grow's light schedule is unknown
- **THEN** the system schedules the task using existing default behavior

### Requirement: Due-Date Task Reminders
The system SHALL remind users of tasks as their due time approaches or passes, without duplicate reminders.

#### Scenario: Reminder for urgent task
- **WHEN** an urgent task's due time approaches and it has not been reminded
- **THEN** the system sends an in-app reminder and a web push, honoring notification preferences

#### Scenario: No duplicate reminders
- **WHEN** a task has already been reminded
- **THEN** the system does not send another reminder for the same due window
