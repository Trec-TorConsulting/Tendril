## ADDED Requirements
### Requirement: TrolMaster Connector
The system SHALL integrate with TrolMaster commercial controllers (Hydro-X, Aqua-X) to read environment and irrigation data (pending API access).

#### Scenario: Poll TrolMaster environment data
- **WHEN** a TrolMaster integration is enabled and API access is available
- **THEN** the system fetches temperature, humidity, CO2, VPD, and light data from Hydro-X controllers
