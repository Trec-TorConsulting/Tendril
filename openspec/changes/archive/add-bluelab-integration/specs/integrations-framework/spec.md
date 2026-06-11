## ADDED Requirements
### Requirement: Bluelab Connector
The system SHALL integrate with Bluelab Connect devices to read pH, EC, and temperature data (pending API access).

#### Scenario: Poll Bluelab device readings
- **WHEN** a Bluelab integration is enabled and API access is available
- **THEN** the system fetches pH, EC, and temperature readings and stores them in bucket sensor tables
