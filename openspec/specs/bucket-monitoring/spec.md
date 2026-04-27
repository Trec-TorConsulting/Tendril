# Capability: Bucket Monitoring

## Purpose
Per-bucket DWC (Deep Water Culture) hydroponic monitoring system. Tracks individual plant buckets with sensor readings, growth milestones, journal entries, and dose profiles.

### Data Model
- **Buckets**: `{tent_id}-{position}` composite ID, label, strain, growth_stage, status, notes, key dates, last_flush_fill
- **Sensor Readings**: pH, EC, PPM, water_temp_f, dissolved_oxygen, water_level_pct, soil_moisture, soil_temp, runoff_ph, runoff_ec (ambient temp/humidity moved to tent-level — see environment-monitoring)
- **Journal**: Per-bucket event log (dosed, flushed, milestones, notes)
- **Dose Profiles**: Per-bucket pH/EC/PPM targets

### Hardware Integration
- **ESP32-S3-DevKitC-1**: One per bucket, publishes to MQTT `grow/{tent_id}/{position}/sensors`
- **Sensors**: Atlas EZO (pH, EC, DO), DS18B20 (water temp), DHT22 (ambient), JSN-SR04T (water level)
- **Manual Entry**: UI and API support manual sensor logging when hardware is unavailable

## Requirements

### Requirement: Bucket CRUD
The system SHALL support creating, reading, updating, and deleting buckets with position, label, strain, growth stage, status, notes, and key milestone dates.

#### Scenario: Create bucket
- **WHEN** a user creates a bucket via `POST /api/buckets` with tent_id, position, and label
- **THEN** the bucket is persisted with a composite ID `{tent_id}-{position}`

#### Scenario: Update bucket metadata
- **WHEN** a user updates a bucket's strain, growth stage, status, notes, or milestone dates
- **THEN** the changes are persisted and reflected in the UI

#### Scenario: Delete bucket cascades
- **WHEN** a user deletes a bucket
- **THEN** all associated sensor readings, journal entries, and dose profiles are also deleted


### Requirement: Sensor Data Ingestion
The system SHALL accept sensor readings from ESP32 boards via MQTT and from manual entry via the API, storing them with timestamps.

#### Scenario: MQTT sensor ingestion
- **WHEN** an ESP32 publishes a JSON payload to `grow/{tent_id}/{position}/sensors`
- **THEN** the system stores the reading in `bucket_sensor_readings` with the current timestamp

#### Scenario: Manual sensor entry
- **WHEN** a user submits a reading via `POST /api/buckets/{id}/sensors`
- **THEN** the reading is stored identically to an MQTT reading

#### Scenario: Sensor history retrieval
- **WHEN** `GET /api/buckets/{id}/sensors` is called
- **THEN** the last 100 readings are returned in reverse chronological order


### Requirement: Bucket Detail View
The system SHALL display a read-only detail view when a bucket card is tapped/clicked, showing all sensor data, milestones, journal history, dose targets, notes, and a sensor trend chart.

#### Scenario: Open detail view
- **WHEN** a user taps a bucket card in the grid
- **THEN** a full-screen modal opens with current readings (pH, EC, PPM, water temp, DO, water level, ambient), sensor trend chart, key dates, dose targets, notes, and journal entries

#### Scenario: Chart rendering
- **WHEN** the detail view opens and there are 2+ sensor readings
- **THEN** a canvas chart plots pH, EC, and water temp trends over time


### Requirement: Bucket Journal
The system SHALL maintain a per-bucket event journal with full CRUD (create, read single, read list, update, delete) for logging doses, flushes, milestones, and freeform notes.

#### Scenario: Add journal entry
- **WHEN** a user or system adds a journal entry via `POST /api/buckets/{id}/journal`
- **THEN** the entry is stored with event_type, JSON payload, and timestamp

#### Scenario: View journal
- **WHEN** `GET /api/buckets/{id}/journal` is called
- **THEN** the last 50 entries are returned in reverse chronological order

#### Scenario: Read single journal entry
- **WHEN** `GET /api/buckets/journal/{entry_id}` is called
- **THEN** the single entry is returned with its payload

#### Scenario: Update journal entry
- **WHEN** a user updates a journal entry via `PUT /api/buckets/journal/{entry_id}`
- **THEN** the event_type and/or payload are updated

#### Scenario: Delete journal entry
- **WHEN** a user deletes a journal entry via `DELETE /api/buckets/journal/{entry_id}`
- **THEN** the entry is removed


### Requirement: Dose Profiles
The system SHALL store per-bucket dose target profiles (pH min/max, EC target, PPM target) with full CRUD and history, used for dosing automation and alert thresholds.

#### Scenario: Set dose profile
- **WHEN** a user sets a dose profile via `POST /api/buckets/{id}/dose`
- **THEN** the profile is stored and used for alert threshold calculations

#### Scenario: View dose profile history
- **WHEN** `GET /api/buckets/{id}/dose/history` is called
- **THEN** all dose profiles (active and inactive) for the bucket are returned

#### Scenario: Update dose profile
- **WHEN** a user updates a dose profile via `PUT /api/buckets/dose/{profile_id}`
- **THEN** the pH/EC ranges and nutrient profile are updated

#### Scenario: Delete dose profile
- **WHEN** a user deletes a dose profile via `DELETE /api/buckets/dose/{profile_id}`
- **THEN** the profile is removed


### Requirement: Sensor Reading CRUD
The system SHALL support full CRUD on individual sensor readings: create, read single by ID, read list/history, and delete.

#### Scenario: Read single sensor reading
- **WHEN** `GET /api/buckets/sensors/{reading_id}` is called
- **THEN** the single reading is returned

#### Scenario: Delete sensor reading
- **WHEN** `DELETE /api/buckets/sensors/{reading_id}` is called
- **THEN** the reading is removed


### Requirement: Bucket Milestones
The system SHALL expose per-bucket milestone dates (germinated, transplanted, veg, flower, harvest) via a dedicated API endpoint.

#### Scenario: View milestones
- **WHEN** `GET /api/buckets/{id}/milestones` is called
- **THEN** a dictionary of milestone key-value pairs is returned


### Requirement: Harvest Yield Tracking
The system SHALL support full CRUD on harvest yield records including create, read single, read list, update, and delete.

#### Scenario: Record yield
- **WHEN** a user records a yield via `POST /api/buckets/{id}/yields`
- **THEN** the wet/dry weight and notes are stored

#### Scenario: Read single yield
- **WHEN** `GET /api/buckets/yields/{yield_id}` is called
- **THEN** the single yield entry is returned

#### Scenario: Update yield
- **WHEN** a user updates a yield via `PUT /api/buckets/yields/{yield_id}`
- **THEN** the wet/dry weight and/or notes are updated

#### Scenario: Delete yield
- **WHEN** a user deletes a yield via `DELETE /api/buckets/yields/{yield_id}`
- **THEN** the yield entry is removed


### Requirement: Bucket Photos
The system SHALL support full CRUD on per-bucket photos including create (upload), read (list + serve image), update (caption), and delete.

#### Scenario: Upload photo
- **WHEN** a user uploads a photo via `POST /api/buckets/{id}/photos`
- **THEN** the image is stored with an optional caption

#### Scenario: Update photo caption
- **WHEN** a user updates a photo's caption via `PUT /api/buckets/photos/{photo_id}`
- **THEN** the caption is updated

#### Scenario: Delete photo
- **WHEN** a user deletes a photo via `DELETE /api/buckets/photos/{photo_id}`
- **THEN** the photo and its image data are removed


### Requirement: Feeding Schedules
The system SHALL support full CRUD on feeding schedule templates including create, read (single + list), update, and delete.

#### Scenario: Create feeding schedule
- **WHEN** a user creates a schedule via `POST /api/feeding-schedules`
- **THEN** the schedule is stored with name, nutrient_line, and stages

#### Scenario: Update feeding schedule
- **WHEN** a user updates a schedule via `PUT /api/feeding-schedules/{id}`
- **THEN** the name, nutrient_line, and/or stages are updated

#### Scenario: Delete feeding schedule
- **WHEN** a user deletes a schedule via `DELETE /api/feeding-schedules/{id}`
- **THEN** the schedule is removed


### Requirement: Strain Library
The system SHALL support full CRUD on strains including create, read (single + list with search), update, and delete, plus strain grow history.

#### Scenario: Create strain
- **WHEN** a user creates a strain via `POST /api/strains`
- **THEN** the strain is stored with name, breeder, genetics, flowering_weeks, yield, THC%, CBD%

#### Scenario: Update strain
- **WHEN** a user updates a strain via `PUT /api/strains/{id}`
- **THEN** the fields are updated

#### Scenario: Strain grow history
- **WHEN** `GET /api/strains/{id}/history` is called
- **THEN** all buckets that have grown this strain are returned


### Requirement: Reservoir Tracking
The system SHALL track reservoir-level pH/EC readings and flush/fill events, propagating reservoir readings to all buckets in the tent.

#### Scenario: Log reservoir reading
- **WHEN** a user logs a pH/EC reading via `POST /api/reservoir/{tent_id}/log`
- **THEN** the reading is stored and applied to all active buckets in that tent

#### Scenario: Record reservoir change
- **WHEN** a user records a flush/fill via `POST /api/reservoir/{tent_id}/changed`
- **THEN** the timestamp is stored and the flush/fill age is displayed on bucket cards


### Requirement: Bulk Fill Operations
The system SHALL support bulk-applying pH/EC/PPM readings to all buckets in a tent via the reservoir log endpoint.

#### Scenario: Bulk fill
- **WHEN** a user enters pH/EC/PPM in the bulk fill bar and clicks apply
- **THEN** the reading is logged via the reservoir endpoint and all bucket cards update
