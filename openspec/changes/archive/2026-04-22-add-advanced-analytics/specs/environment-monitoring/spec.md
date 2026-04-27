## ADDED Requirements

### Requirement: Light Schedule & DLI Tracking
The system SHALL track light schedules per tent and calculate Daily Light Integral (DLI) from configured wattage, PAR efficiency, and photoperiod hours.

#### Scenario: DLI display
- **WHEN** light wattage and schedule are configured for a tent
- **THEN** the calculated DLI is displayed in the environment gauges

#### Scenario: Light schedule visualization
- **WHEN** a tent view is displayed with light schedule configured
- **THEN** a visual bar shows the current light on/off status and schedule

---

### Requirement: Environmental Scoring
The system SHALL calculate a daily "Grow Score" (0-100) from weighted environmental factors (VPD consistency, pH/EC stability, water temp, reservoir freshness, light adherence, DO levels) and display trends.

#### Scenario: Daily score display
- **WHEN** a tent view is displayed
- **THEN** the current day's grow score badge is shown

#### Scenario: Score trend
- **WHEN** a user views the score history
- **THEN** a 30-day trend chart is displayed with factor breakdown

#### Scenario: Score in AI context
- **WHEN** a daily health check or chat message is processed
- **THEN** the current grow score and its weakest factors are included in the AI context prompt
