# Capability: Contextual Prompts

## Purpose
A deterministic, rules-driven system that asks the user the right question at the right time based on grow stage, elapsed time, and missing or stale data. Answers feed the quick-log flow and persist real data, improving the quality of downstream alerting, coaching, and harvest prediction. No LLM is used.

## ADDED Requirements

### Requirement: Eligibility-Based Prompt Generation
The system SHALL generate contextual prompts for a grow only when deterministic eligibility rules are met (stage, elapsed time, missing/stale data).

#### Scenario: Prompt for missing runoff pH
- **WHEN** a coco or soil grow has no runoff pH reading logged for at least the configured interval
- **THEN** the system offers a prompt to log runoff pH

#### Scenario: Trichome check in late flower
- **WHEN** a grow is in late flowering or ripening and a weekly trichome check is due
- **THEN** the system offers a trichome check prompt

#### Scenario: Not eligible, not shown
- **WHEN** a prompt's eligibility conditions are not met
- **THEN** the system does not surface that prompt

### Requirement: Prompt Answering Persists Data
The system SHALL persist real data when a user answers a prompt, using existing logging endpoints.

#### Scenario: Answering logs a reading
- **WHEN** a user answers a numeric-reading prompt
- **THEN** the system records the reading via the existing logging flow and marks the prompt answered

#### Scenario: Confirmation prompt
- **WHEN** a user confirms a light-schedule flip prompt
- **THEN** the system records the confirmation and marks the prompt answered

### Requirement: Non-Intrusive Prompt State Management
The system SHALL track prompt state and limit concurrent prompts, supporting snooze and dismiss.

#### Scenario: Concurrent prompt cap
- **WHEN** more prompts are eligible than the configured concurrent cap
- **THEN** the system surfaces only up to the cap

#### Scenario: Snoozed prompt suppressed
- **WHEN** a user snoozes a prompt
- **THEN** the system does not re-surface it until the snooze interval elapses

#### Scenario: Dismissed prompt not repeated
- **WHEN** a user dismisses a prompt
- **THEN** the system does not surface that prompt again for the current eligibility cycle
