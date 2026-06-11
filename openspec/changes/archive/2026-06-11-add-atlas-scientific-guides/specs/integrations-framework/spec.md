## ADDED Requirements
### Requirement: Atlas Scientific Sensor Guides
The system SHALL provide documentation and firmware templates for connecting Atlas Scientific lab-grade probes to Tendril via ESP32 and MQTT.

#### Scenario: User builds Atlas sensor rig
- **WHEN** a user follows the Atlas Scientific wiring guide and flashes the provided ESPHome template
- **THEN** the ESP32 reads pH, EC, DO, and temperature from Atlas EZO circuits and publishes readings to Tendril's MQTT broker
