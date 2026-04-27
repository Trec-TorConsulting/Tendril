## ADDED Requirements

### Requirement: Multi-Channel Notifications
The system SHALL support sending notifications via Discord, Slack, Email, and SMS, configurable per tenant.

#### Scenario: Configure Discord webhook
- **WHEN** a tenant owner adds a Discord webhook URL in settings
- **THEN** notifications are sent to the Discord channel for alerts matching the configured severity

### Requirement: Alert Evaluation
The system SHALL evaluate sensor data against configurable thresholds and generate alerts scoped to the tenant.

#### Scenario: pH out of range
- **WHEN** a bucket's pH reading falls outside the configured range
- **THEN** the system creates an alert and dispatches notifications to configured channels

### Requirement: Data Retention
The system SHALL automatically prune sensor data older than the tenant's configured retention period.

#### Scenario: Default retention
- **WHEN** no custom retention is configured
- **THEN** sensor data older than 180 days is pruned daily

#### Scenario: Custom retention
- **WHEN** a tenant configures a 365-day retention period
- **THEN** sensor data older than 365 days is pruned daily
