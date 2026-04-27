## ADDED Requirements

### Requirement: Sensor Data Ingestion
The system SHALL ingest sensor data from IoT devices via MQTT and store readings scoped to the device's tenant.

#### Scenario: MQTT sensor data received
- **WHEN** an ESP32 publishes pH, EC, water temp, air temp, humidity, water level, dissolved oxygen, flow rate, soil moisture, soil temp, or runoff pH/EC data
- **THEN** the system stores the reading linked to the device's bucket and tenant

#### Scenario: Grow-type sensor filtering
- **WHEN** sensor data is displayed for a bucket
- **THEN** only sensors marked as "relevant" in the bucket's grow type profile are shown in the UI and included in alerts

### Requirement: Sensor API
The system SHALL provide CRUD operations for sensor readings, scoped to the authenticated tenant.

#### Scenario: List sensor readings
- **WHEN** a user requests sensor readings for a bucket with optional time range
- **THEN** only readings belonging to the user's tenant are returned

#### Scenario: Latest sensor reading
- **WHEN** a user requests the latest reading for a bucket
- **THEN** the most recent reading for each sensor type is returned

### Requirement: Sensor Drift Analysis
The system SHALL calculate pH and EC drift trends over configurable time windows.

#### Scenario: Drift calculation
- **WHEN** a user requests drift analysis for a bucket
- **THEN** the system returns trend direction, rate of change, and time to out-of-range prediction using the grow type's pH/EC thresholds as the "in-range" baseline

### Requirement: Dose Profiles and Pump Control
The system SHALL provide CRUD operations for dose profiles and pump triggering, scoped to the authenticated tenant.

#### Scenario: Trigger dose
- **WHEN** a user triggers a dose for a bucket
- **THEN** the system publishes a pump command via MQTT to the device and logs the dose

### Requirement: Feeding Schedules
The system SHALL provide CRUD operations for feeding schedules, scoped to the authenticated tenant.

#### Scenario: Weekly feeding view
- **WHEN** a user requests this week's feeding schedule for a bucket
- **THEN** the system returns the scheduled feedings for the current week, adjusted for grow type nutrient strength recommendations (e.g., 50-75% for DWC, 75-100% for coco, N/A for living soil)
