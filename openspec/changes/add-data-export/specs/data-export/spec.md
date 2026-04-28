## ADDED Requirements

### Requirement: CSV Export
The system SHALL provide CSV export for any list data including grows, sensor readings, expenses, and tasks.

#### Scenario: Export sensor data for analysis
- **WHEN** a grower requests CSV export of sensor data for a date range
- **THEN** the system returns a CSV file with columns: timestamp, temperature, humidity, soil_moisture, and any other sensor fields, filtered to the requested date range

### Requirement: PDF Grow Report
The system SHALL generate a comprehensive PDF report for any grow including summary, stage timeline, sensor charts, expenses, yields, and health notes.

#### Scenario: Commercial grower needs compliance report
- **WHEN** a grower requests a PDF report for a completed grow
- **THEN** the system generates a formatted PDF with grow details, stage dates, environmental data summaries, input logs, and harvest yield data
