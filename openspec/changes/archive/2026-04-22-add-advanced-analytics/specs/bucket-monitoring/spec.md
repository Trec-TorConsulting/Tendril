## ADDED Requirements

### Requirement: Crop Steering Dashboard
The system SHALL display crop steering signals (dry-back percentage, EC ramp) with recommended generative vs. vegetative steering actions based on current growth stage.

#### Scenario: Steering recommendation
- **WHEN** the crop steering view is opened for a tent
- **THEN** dry-back %, EC ramp, and a recommended steering action are displayed based on recent sensor data

#### Scenario: Steering history
- **WHEN** a user views crop steering history
- **THEN** a timeline chart shows generative/vegetative balance signals over the past 14 days

---

### Requirement: Multi-Grow History
The system SHALL support archiving completed grow cycles and comparing performance metrics across multiple grows.

#### Scenario: Archive grow
- **WHEN** a user archives a grow cycle
- **THEN** all bucket data (sensors, journal, milestones, yields, photos) is snapshot into a completed grow record

#### Scenario: Compare grows
- **WHEN** a user selects two completed grow cycles for comparison
- **THEN** side-by-side metrics are displayed (total yield, avg pH/EC, duration, strain performance)

---

### Requirement: Data Export
The system SHALL support exporting grow cycle data as CSV and PDF reports including sensor history, journal entries, milestone timeline, yield data, and photos.

#### Scenario: CSV export
- **WHEN** a user exports a grow cycle as CSV
- **THEN** a file is generated with all sensor readings, journal entries, and yield data

#### Scenario: PDF report
- **WHEN** a user exports a grow cycle as PDF
- **THEN** a formatted report is generated with summary stats, sensor charts, photos, and milestone timeline

---

### Requirement: Pump Automation Dashboard
The system SHALL provide a UI for sending dose commands (pH up, pH down, nutrient) to ESP32 boards via MQTT, with safety limits and journal logging.

#### Scenario: Send dose command
- **WHEN** a user clicks a dose button (e.g., "pH Down 5ml") for a bucket
- **THEN** an MQTT command is published to `grow/{tent_id}/{position}/dose/cmd` and logged in the bucket journal

#### Scenario: Safety limit
- **WHEN** a dose command would exceed the configured maximum dose per interval
- **THEN** the command is rejected and a warning is displayed
