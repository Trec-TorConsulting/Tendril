## ADDED Requirements
### Requirement: Pulse Grow Connector
The system SHALL integrate with the Pulse Grow REST API to poll environment data from Pulse One, Pulse Pro, and Pulse Hub devices.

#### Scenario: Poll Pulse device readings
- **WHEN** a Pulse integration is enabled and a poll interval elapses
- **THEN** the system fetches latest readings from `api.pulsegrow.com` and stores temperature, humidity, VPD, light, and CO2 data in the mapped tent's ambient readings

#### Scenario: Discover Pulse devices
- **WHEN** a user triggers device discovery for their Pulse integration
- **THEN** the system fetches all devices from the Pulse API and presents them for mapping to tents
