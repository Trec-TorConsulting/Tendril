## ADDED Requirements
### Requirement: Home Assistant Bridge Connector
The system SHALL integrate with Home Assistant's REST API to read sensor entity states and trigger service actions.

#### Scenario: Poll HA entity states
- **WHEN** a Home Assistant integration is enabled and a poll interval elapses
- **THEN** the system fetches all mapped entity states from HA and stores sensor data in the appropriate tent/bucket tables

#### Scenario: Discover HA entities
- **WHEN** a user triggers entity discovery for their HA integration
- **THEN** the system fetches all entities from `GET /api/states` and presents sensor/switch/climate types for mapping

#### Scenario: Trigger HA service from automation
- **WHEN** a Tendril automation rule fires with an action targeting a Home Assistant service
- **THEN** the system calls `POST /api/services/{domain}/{service}` on the HA instance with the configured parameters
