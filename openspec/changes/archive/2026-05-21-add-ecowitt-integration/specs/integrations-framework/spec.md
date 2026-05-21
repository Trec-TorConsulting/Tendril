## ADDED Requirements
### Requirement: Ecowitt Connector
The system SHALL integrate with Ecowitt weather stations and soil sensors via webhook push or cloud API polling.

#### Scenario: Receive Ecowitt webhook data
- **WHEN** an Ecowitt gateway pushes data to the integration webhook endpoint
- **THEN** the system parses the Ecowitt payload format and stores weather + soil sensor readings

#### Scenario: Poll Ecowitt cloud API
- **WHEN** an Ecowitt cloud integration is enabled and a poll interval elapses
- **THEN** the system fetches latest device data from `api.ecowitt.net` and stores readings
