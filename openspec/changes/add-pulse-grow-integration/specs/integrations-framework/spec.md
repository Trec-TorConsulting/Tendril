## ADDED Requirements

### Requirement: Pulse Grow Connector
The system SHALL provide a Pulse Grow connector that polls the Pulse API for environmental sensor data from Pulse One, Pulse Pro, and Pulse Hub devices and maps readings to TentSensorReading and BucketSensorReading tables.

#### Scenario: Poll Pulse devices for ambient data
- **WHEN** a Pulse integration is enabled with valid API key and device mappings
- **THEN** the system polls `GET /all-devices` at the configured interval
- **AND** writes a TentSensorReading for each mapped device with temperature, humidity, VPD, CO2, lux, dew point, PAR/PPFD, air pressure, and VOC fields

#### Scenario: Poll Pulse Hub sensors for bucket data
- **WHEN** a Pulse Hub sensor is mapped to a bucket via IntegrationDeviceMap
- **THEN** the system polls `GET /sensors/{id}/recent-data` and writes a BucketSensorReading with the appropriate fields (soil_moisture, ph, ec)

#### Scenario: Invalid API key
- **WHEN** the Pulse API returns 401 Unauthorized
- **THEN** the system logs the error in IntegrationSyncLog with status "error"
- **AND** increments error_count on the IntegrationConfig
- **AND** does NOT retry until the next poll cycle

#### Scenario: Pulse API unavailable
- **WHEN** the Pulse API returns 5xx or times out
- **THEN** the system logs the error and retries on the next poll cycle
- **AND** does NOT disable the integration

### Requirement: Pulse Device Auto-Discovery
The system SHALL provide an auto-discovery endpoint that fetches available Pulse devices and sensors for a given integration config, enabling users to map external devices to tents and buckets.

#### Scenario: Discover Pulse devices
- **WHEN** a user triggers discovery via `POST /v1/integrations/{id}/discover`
- **THEN** the system calls the Pulse API with the stored API key
- **AND** returns a list of devices with external_id, name, type, and latest reading preview

#### Scenario: Discovery with invalid credentials
- **WHEN** discovery is triggered with an invalid API key
- **THEN** the system returns 502 with a descriptive error message

### Requirement: Pulse Config Validation
The system SHALL validate Pulse integration config using a typed schema requiring an API key field.

#### Scenario: Valid Pulse config
- **WHEN** a user creates an integration with type "pulse" and a valid api_key
- **THEN** the system accepts the config and encrypts credentials

#### Scenario: Missing API key
- **WHEN** a user creates a Pulse integration without an api_key field
- **THEN** the system returns 422 with a validation error

### Requirement: Extended Tent Sensor Schema
The system SHALL support storing VPD, CO2, lux, dew point, PAR/PPFD, air pressure, and VOC data in TentSensorReading, enabling richer environmental monitoring from Pulse and future integrations.

#### Scenario: Store extended sensor data from integration
- **WHEN** a connector provides VPD, CO2, lux, dew_point_f, par_ppfd, air_pressure, or voc values
- **THEN** the system stores them in the corresponding TentSensorReading columns

#### Scenario: Store extended sensor data from MQTT
- **WHEN** an ESP32 device publishes VPD, CO2, or other extended fields via MQTT
- **THEN** the MQTT handler accepts and stores the fields in TentSensorReading

#### Scenario: Backward compatibility
- **WHEN** a reading only contains temperature and humidity
- **THEN** the extended columns remain NULL with no errors

## MODIFIED Requirements

### Requirement: Polling Sync Worker
The system SHALL run background polling tasks for cloud-API-based integrations on configurable intervals.

#### Scenario: Scheduled poll executes
- **WHEN** a polling interval elapses for an enabled integration
- **THEN** the system fetches latest data from the external API and inserts sensor readings

#### Scenario: Poll failure handling
- **WHEN** a poll fails due to network or API error
- **THEN** the system logs the error in IntegrationSyncLog and retries on next interval
- **AND** does NOT disable the integration automatically

#### Scenario: Pulse bulk poll optimization
- **WHEN** a Pulse integration poll executes
- **THEN** the system uses `GET /all-devices` for a single HTTP call per cycle
- **AND** matches response devices to IntegrationDeviceMap entries by external_id

### Requirement: Device Mapping
The system SHALL map external devices/sensors to Tendril tents and buckets, so data flows into the correct context for AI analysis.

#### Scenario: Map external device to tent
- **WHEN** a tenant configures a device mapping with tent_id
- **THEN** ambient sensor data from that device is stored as TentSensorReading for that tent

#### Scenario: Map external device to bucket
- **WHEN** a tenant configures a device mapping with bucket_id
- **THEN** sensor data from that device is stored as BucketSensorReading for that bucket

#### Scenario: Map Pulse Hub sensor to bucket
- **WHEN** a Pulse Hub sensor (VWC, pH, EC) is mapped to a bucket
- **THEN** the system writes BucketSensorReading entries with the sensor-appropriate fields
