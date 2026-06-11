## ADDED Requirements
### Requirement: Tuya Connector
The system SHALL integrate with Tuya OpenAPI to read smart plug/sensor states and toggle devices.

#### Scenario: Poll Tuya device states
- **WHEN** a Tuya integration is enabled and a poll interval elapses
- **THEN** the system fetches power consumption, on/off state, temperature, and humidity from mapped Tuya devices

#### Scenario: Toggle Tuya device from automation
- **WHEN** a Tendril automation rule fires with a Tuya toggle action
- **THEN** the system calls the Tuya device control API to turn the device on or off
