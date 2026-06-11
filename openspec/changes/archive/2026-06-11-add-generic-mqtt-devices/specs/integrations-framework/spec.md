## ADDED Requirements

### Requirement: Generic MQTT Device Connector
The system SHALL support connecting any MQTT-speaking device via configurable topic subscriptions and JSON payload field mapping, using the existing integration framework.

#### Scenario: Receive data from a generic MQTT device
- **WHEN** a generic MQTT device publishes JSON to its configured topic
- **THEN** the MQTT worker parses the payload using the device map's `sensor_mapping`, maps fields to Tendril sensor columns, and persists readings to the appropriate tent or bucket sensor table

#### Scenario: Configure custom field mapping
- **WHEN** a user creates a device map with `sensor_mapping: {"temperature": "ambient_temp_f", "humidity": "ambient_humidity"}`
- **THEN** the system maps the incoming JSON field `temperature` to `ambient_temp_f` and `humidity` to `ambient_humidity` on each received message

#### Scenario: Handle nested JSON payloads
- **WHEN** a device publishes `{"sensor": {"temp": 72.5, "rh": 55}}` and the mapping uses dot-notation `{"sensor.temp": "ambient_temp_f"}`
- **THEN** the system traverses the nested path and extracts the value correctly

#### Scenario: Coerce string values to numeric
- **WHEN** a device publishes `{"ph": "6.2"}` (string instead of number)
- **THEN** the system coerces the value to float before storing

#### Scenario: Ignore unmapped fields gracefully
- **WHEN** a device publishes extra fields not present in the sensor_mapping
- **THEN** the system ignores them without error and only stores mapped fields

#### Scenario: Reject dangerous topic subscriptions
- **WHEN** a user attempts to create an mqtt_generic integration with topic `#` or `+` alone
- **THEN** the system rejects the configuration with a validation error explaining the risk

### Requirement: Dynamic MQTT Topic Subscription
The system SHALL dynamically subscribe to topics configured in mqtt_generic integrations when the MQTT worker starts and when integrations are created or modified.

#### Scenario: Subscribe on worker startup
- **WHEN** the MQTT worker starts
- **THEN** it loads all enabled mqtt_generic integration device maps and subscribes to their configured topics

#### Scenario: New integration created
- **WHEN** a user creates a new mqtt_generic integration with topic `zigbee2mqtt/soil_sensor`
- **THEN** the MQTT worker adds that topic to its active subscriptions within 60 seconds
