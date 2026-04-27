## ADDED Requirements
### Requirement: Generic MQTT Device Connector
The system SHALL support connecting any MQTT-speaking device via configurable topic subscriptions and JSON payload field mapping.

#### Scenario: Receive data from generic MQTT device
- **WHEN** a generic MQTT device publishes to its configured topic
- **THEN** the MQTT worker parses the payload using the configured field mapping and stores readings in the mapped tent/bucket

#### Scenario: Configure custom field mapping
- **WHEN** a user creates a generic MQTT integration with field mapping `{"temperature": "ambient_temp_f", "humidity": "ambient_humidity"}`
- **THEN** the system maps incoming JSON fields to the corresponding sensor columns
