## ADDED Requirements
### Requirement: ESPHome MQTT Templates
The system SHALL provide pre-built ESPHome YAML templates that publish sensor data to Tendril's MQTT broker in the expected topic and payload format.

#### Scenario: ESPHome device sends sensor data
- **WHEN** an ESPHome-flashed device publishes a JSON payload to `t/{tenant_id}/d/{device_id}/sensor/readings`
- **THEN** the existing MQTT handler parses and stores the readings in BucketSensorReading or TentAmbientReading

#### Scenario: User configures ESPHome template
- **WHEN** a user copies a Tendril ESPHome template and fills in WiFi/MQTT credentials
- **THEN** the device connects to EMQX and begins publishing sensor data without any API changes
