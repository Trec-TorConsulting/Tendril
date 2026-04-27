## ADDED Requirements

### Requirement: Tenant-Scoped Analytics
The system SHALL provide analytics charts and trends scoped to the authenticated tenant's data.

#### Scenario: Sensor trend charts
- **WHEN** a user views analytics for a bucket
- **THEN** the system displays pH, EC, temperature, humidity, and VPD trends over configurable time ranges

### Requirement: Crop Steering Analysis
The system SHALL provide crop steering recommendations based on sensor data and growth stage.

#### Scenario: Crop steering view
- **WHEN** a user requests crop steering analysis for a bucket
- **THEN** the system returns irrigation strategy recommendations based on dry-back patterns and VPD

### Requirement: Strain Leaderboard
The system SHALL provide strain performance rankings based on yield, grow duration, and quality ratings within the tenant's data.

#### Scenario: View leaderboard
- **WHEN** a user views the strain leaderboard
- **THEN** the system displays strains ranked by average yield and quality from the tenant's historical grows

### Requirement: Historical Data Overlay
The system SHALL allow overlaying data from past grows onto current grow charts for comparison.

#### Scenario: Overlay past grow
- **WHEN** a user selects a past grow to overlay
- **THEN** the chart displays both current and historical sensor data aligned by grow day
