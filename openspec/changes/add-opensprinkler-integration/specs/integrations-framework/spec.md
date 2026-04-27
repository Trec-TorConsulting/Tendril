## ADDED Requirements
### Requirement: OpenSprinkler Connector
The system SHALL integrate with OpenSprinkler irrigation controllers via their local REST API to read zone status and trigger watering.

#### Scenario: Poll zone status
- **WHEN** an OpenSprinkler integration is enabled and a poll interval elapses
- **THEN** the system fetches zone on/off states, remaining run times, and flow sensor data

#### Scenario: Trigger zone from automation
- **WHEN** a Tendril automation rule fires with an OpenSprinkler zone action
- **THEN** the system calls the OpenSprinkler `/cm` endpoint to start/stop the specified zone
