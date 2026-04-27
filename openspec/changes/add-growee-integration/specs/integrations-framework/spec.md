## ADDED Requirements
### Requirement: Growee Connector
The system SHALL integrate with Growee auto-dosing systems to read pH/EC/temperature data and log dosing events (pending API access).

#### Scenario: Poll Growee device readings
- **WHEN** a Growee integration is enabled and API access is available
- **THEN** the system fetches pH, EC, and temperature readings and stores them in bucket sensor tables
