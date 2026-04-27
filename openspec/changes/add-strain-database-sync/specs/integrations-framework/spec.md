## ADDED Requirements
### Requirement: Strain Database Sync
The system SHALL auto-populate strain genetics data from external databases when a user selects a strain for their grow.

#### Scenario: User searches for a strain
- **WHEN** a user types a strain name in the grow creation form
- **THEN** the system provides autocomplete suggestions from its strain database

#### Scenario: Strain genetics enrich AI context
- **WHEN** a grow has a strain profile with flowering time, sensitivity, and yield data
- **THEN** the AI feeding and health advice incorporates strain-specific characteristics
