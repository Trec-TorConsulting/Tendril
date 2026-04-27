# Capability: Environment Monitoring

## Purpose
Tent-level environmental monitoring for temperature, humidity, VPD, and automated alerting. Ambient readings are stored at the tent level (not per-bucket) in the `tent_sensor_readings` table.

### Data Sources
- **ESP32 IoT Devices**: Publish ambient data via MQTT topic `t/{tenant_id}/d/{device_id}/sensor/ambient`
- **Manual Entry**: API endpoint `POST /v1/tent-sensors` for users without hardware sensors
- **Weather API**: Open-Meteo integration for outdoor/greenhouse tents (30-min polling)

### Data Model
- **TentSensorReading**: id, tenant_id, tent_id, device_id (optional), ambient_temp_f, ambient_humidity, recorded_at
- **Tent**: environment_type (indoor/outdoor/greenhouse), location (lat/lng), camera_url

## Requirements

### Requirement: Tent Sensor Readings
The system SHALL store ambient temperature and humidity readings at the tent level (not per-bucket) via MQTT ingestion or manual API entry.

#### Scenario: MQTT ambient ingestion
- **WHEN** an ESP32 publishes ambient data to `t/{tenant_id}/d/{device_id}/sensor/ambient`
- **THEN** the reading is stored in `tent_sensor_readings` with tent_id, device_id, and timestamp

#### Scenario: Manual ambient entry
- **WHEN** a user submits a reading via `POST /v1/tent-sensors` with tent_id, ambient_temp_f, and/or ambient_humidity
- **THEN** the reading is stored in `tent_sensor_readings`

#### Scenario: Latest reading retrieval
- **WHEN** `GET /v1/tent-sensors/latest/{tent_id}` is called
- **THEN** the most recent ambient reading for that tent is returned

#### Scenario: Ambient trend retrieval
- **WHEN** `GET /v1/tent-sensors/trends/{tent_id}` is called with a time range
- **THEN** aggregated ambient data (hourly averages) is returned for charting

#### Scenario: Ambient readings list
- **WHEN** `GET /v1/tent-sensors?tent_id={id}` is called
- **THEN** the last 50 readings for that tent are returned in reverse chronological order


### Requirement: VPD Calculation
The system SHALL calculate Vapor Pressure Deficit from temperature and humidity readings and display it in the environment gauges.

#### Scenario: VPD display
- **WHEN** temperature and humidity data is available for a tent
- **THEN** VPD is calculated and displayed in the environment gauge section


### Requirement: Environmental Alerts
The system SHALL generate alerts when sensor values exceed configured thresholds (temperature, humidity, pH, EC, water level).

#### Scenario: Alert generation
- **WHEN** a sensor reading exceeds the configured safe range for the tent
- **THEN** an alert is created with severity (warning or critical) and displayed in the UI

#### Scenario: Alert acknowledgment
- **WHEN** a user acknowledges an alert via `POST /api/alerts/acknowledge`
- **THEN** the alert is dismissed and removed from the active alerts list

#### Scenario: Alerts in chat
- **WHEN** new alerts are generated while the chat panel is visible
- **THEN** the alerts are shown inline in the chat panel for visibility


### Requirement: Tent Configuration
The system SHALL allow per-tent configuration of target ranges (temperature, humidity, VPD), light schedule, hydro type, and other grow parameters with full CRUD (create/upsert, read single, read list, update, delete).

#### Scenario: Update tent config
- **WHEN** a user updates tent settings via `PUT /api/tent-config/{tent_id}`
- **THEN** the configuration is persisted and used for alert thresholds and context enrichment

#### Scenario: Delete tent config
- **WHEN** a user deletes a tent configuration via `DELETE /api/tent-config/{tent_id}`
- **THEN** the configuration is removed from the database


### Requirement: Tuya Device Discovery
The system SHALL scan the local network for Tuya-based devices (Vivosun GrowHub) to assist with initial setup.

#### Scenario: Device scan
- **WHEN** `GET /api/sensors/discover` is called
- **THEN** the system broadcasts on the LAN and returns discovered Tuya device IDs and IPs


### Requirement: Grow Journal
The system SHALL maintain a global activity feed of events (sensor readings, daily reports, knowledge facts, alerts) across all tents.

#### Scenario: View journal
- **WHEN** `GET /api/journal` is called
- **THEN** the most recent events are returned in reverse chronological order

#### Scenario: Daily AI reports
- **WHEN** `GET /api/journal/reports` is called
- **THEN** the last 14 AI-generated daily health reports are returned
