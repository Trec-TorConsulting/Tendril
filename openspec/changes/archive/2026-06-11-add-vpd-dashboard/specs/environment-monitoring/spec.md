## ADDED Requirements

### Requirement: VPD Dashboard
The system SHALL provide a dedicated VPD (Vapor Pressure Deficit) dashboard showing real-time readings, historical trends, and stage-aware zone visualization for all monitored tents.

#### Scenario: View current VPD for active tent
- **WHEN** a user navigates to the VPD dashboard
- **THEN** the system displays the current VPD reading for each tent with a color-coded zone indicator (optimal green, caution yellow, stress red) based on the current grow stage

#### Scenario: View VPD 24-hour trend
- **WHEN** a user views the VPD dashboard for a specific tent
- **THEN** the system displays a line chart of VPD values over the last 24 hours with stage-appropriate zone bands overlaid

#### Scenario: Adjust leaf temperature offset
- **WHEN** a user adjusts the leaf temperature offset slider (0-5°F below ambient)
- **THEN** the system recalculates displayed VPD using the offset and updates all visualizations in real-time

#### Scenario: Stage-aware zone colors
- **WHEN** the grow is in vegetative stage
- **THEN** VPD zones use veg targets (0.8-1.2 kPa optimal) and in flower stage use flower targets (1.0-1.5 kPa optimal)

### Requirement: Extended Tent Sensor API Response
The system SHALL expose all stored tent sensor columns (vpd, co2, lux, dew_point_f, par_ppfd, voc, air_pressure) in the tent sensor reading API response.

#### Scenario: Tent sensor response includes VPD
- **WHEN** a client fetches tent sensor readings via the API
- **THEN** the response includes vpd, co2, lux, dew_point_f, par_ppfd, voc, and air_pressure fields alongside ambient_temp_f and ambient_humidity
