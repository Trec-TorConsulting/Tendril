## ADDED Requirements

### Requirement: Task Management
The system SHALL provide task assignment and tracking for team members (Commercial tier).

#### Scenario: Create and assign task
- **WHEN** a tenant owner or member creates a task (e.g., "Check pH in Tent A", "Refill reservoir")
- **THEN** the task is assigned to a team member with a due date, priority, and optional tent/bucket linkage

#### Scenario: Task completion
- **WHEN** a team member marks a task as complete
- **THEN** the system records who completed it, when, and optionally attaches a photo or note

#### Scenario: Recurring tasks
- **WHEN** a user creates a recurring task (e.g., "Weekly reservoir change")
- **THEN** the system automatically creates new task instances on the configured schedule

### Requirement: Audit Trail
The system SHALL log all significant user actions for accountability and review (Commercial tier).

#### Scenario: Action logging
- **WHEN** a user performs a write action (create, update, delete, dose trigger, stage advance, setting change)
- **THEN** the system records the user, action type, resource, timestamp, and before/after values

#### Scenario: View audit log
- **WHEN** a tenant owner views the audit trail
- **THEN** the system displays a filterable, paginated list of actions with user, resource, and timestamp

#### Scenario: Audit log retention
- **WHEN** audit log entries age past the tenant's retention period
- **THEN** the system retains audit logs for a minimum of 1 year regardless of data retention settings
