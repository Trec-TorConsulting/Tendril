## ADDED Requirements

### Requirement: Sensor Trend Drift Detection
The system SHALL analyze sensor reading trends over 24-hour windows and generate alerts when pH drifts more than 0.3 or EC drifts more than 0.2 from the rolling average.

#### Scenario: pH drift detected
- **WHEN** a new pH reading is 0.3+ higher or lower than the 24-hour rolling average for that bucket
- **THEN** a `drift` alert is generated with the direction and magnitude

#### Scenario: Trend direction indicator
- **WHEN** bucket sensor data is displayed (card or detail view)
- **THEN** pH and EC show a trend arrow (↑ rising, ↓ falling, → stable) based on recent readings

---

### Requirement: Reservoir Flush Countdown
The system SHALL track days since last flush/fill per bucket and display a countdown based on configurable intervals per growth stage.

#### Scenario: Flush countdown display
- **WHEN** a bucket card or detail view is displayed
- **THEN** the days remaining until the next recommended flush are shown

#### Scenario: Overdue flush alert
- **WHEN** a bucket exceeds the configured flush interval for its current growth stage
- **THEN** a critical alert is generated naming the bucket and days overdue

---

### Requirement: Harvest Yield Tracking
The system SHALL allow users to log wet and dry harvest weights per bucket and calculate grams-per-plant and grams-per-watt metrics.

#### Scenario: Log harvest yield
- **WHEN** a user logs yield data via `POST /api/buckets/{id}/yield`
- **THEN** the yield is stored and metrics (grams/plant, grams/watt) are calculated

#### Scenario: Yield display
- **WHEN** a harvested bucket's detail view is opened
- **THEN** yield metrics are displayed (wet weight, dry weight, g/plant, g/watt if configured)
