## ADDED Requirements

### Requirement: SQLite Database Support
The system SHALL support SQLite as the default database, with data stored in a file at a configurable path (default: `/data/grow.db`). PostgreSQL SHALL remain available as an optional backend.

#### Scenario: SQLite default
- **WHEN** no database URL is configured
- **THEN** the system uses SQLite at `/data/grow.db`

#### Scenario: PostgreSQL configured
- **WHEN** a `DATABASE_URL` starting with `postgresql://` is provided
- **THEN** the system uses PostgreSQL

---

### Requirement: Optional MQTT
The system SHALL function fully without an MQTT broker. Sensor data can be entered manually via the API. MQTT is only required when using ESP32 hardware sensors.

#### Scenario: No MQTT configured
- **WHEN** no MQTT broker URL is provided in configuration
- **THEN** the system starts without MQTT, manual sensor entry is available, and no MQTT errors are logged

#### Scenario: MQTT configured
- **WHEN** an MQTT broker URL is provided
- **THEN** the system connects and listens for ESP32 sensor data on configured topics

---

### Requirement: Optional Sensor Hardware
The system SHALL function fully without ESP32 sensor hardware. All sensor fields support manual entry via the UI and API.

#### Scenario: No sensors connected
- **WHEN** no ESP32 boards are publishing sensor data
- **THEN** the bucket cards show "—" for sensor values and the manual entry button is prominently displayed
