## MODIFIED Requirements

### Requirement: Bucket Status Display
The system SHALL display each bucket's current status including position, label, strain, growth stage, volume, latest sensor readings, and days since last water change.

#### Scenario: Bucket card shows sensor readings
- **WHEN** a bucket has recorded sensor readings
- **THEN** the system displays the latest pH, EC, PPM, and water temperature on the bucket card

#### Scenario: Bucket card shows days since water change
- **WHEN** a bucket has at least one journal entry with event_type "water_change" or "flushing"
- **THEN** the system displays the number of days since the most recent such entry

#### Scenario: Bucket card shows no water change recorded
- **WHEN** a bucket has no journal entries with event_type "water_change" or "flushing"
- **THEN** the system displays "No water change recorded" in a muted style

#### Scenario: Bucket card signals overdue water change
- **WHEN** a bucket's last water change was more than 10 days ago
- **THEN** the system displays the days-since badge in a warning color (red)

## ADDED Requirements

### Requirement: Bucket Quick Actions
The system SHALL provide quick-action buttons on each bucket card for Water Change and Feed that create both a journal entry and sensor reading in a single interaction.

#### Scenario: User performs quick water change
- **WHEN** user clicks "Water Change" on a bucket card
- **THEN** the system opens a minimal dialog requesting pH, EC, volume (optional), and notes
- **WHEN** user submits the water change dialog
- **THEN** the system creates a JournalEntry (event_type: "water_change") AND a SensorReading for that bucket in one transaction

#### Scenario: User performs quick feed
- **WHEN** user clicks "Feed" on a bucket card
- **THEN** the system opens a dialog requesting nutrients used, pH, EC, volume, and notes
- **WHEN** user submits the feed dialog
- **THEN** the system creates a JournalEntry (event_type: "feeding") AND a SensorReading for that bucket in one transaction

### Requirement: Quick Journal Endpoint
The system SHALL provide a combined endpoint that accepts event metadata and optional sensor readings, creating both records atomically.

#### Scenario: API creates journal entry with sensor reading
- **WHEN** client sends POST to `/journal/quick` with bucket_id, event_type, and sensor fields (pH, EC, water_temp)
- **THEN** the system creates one JournalEntry and one BucketSensorReading linked to the same bucket within a single database transaction

#### Scenario: API creates journal entry without sensor reading
- **WHEN** client sends POST to `/journal/quick` with bucket_id and event_type but no sensor fields
- **THEN** the system creates only a JournalEntry

### Requirement: Last Water Change Computed Field
The system SHALL include a `last_water_change_at` datetime field in the bucket response, derived from the most recent journal entry with event_type "water_change" or "flushing".

#### Scenario: Bucket response includes last water change
- **WHEN** client requests bucket details via GET /buckets or GET /buckets/{id}
- **THEN** the response includes `last_water_change_at` as an ISO datetime or null
