## ADDED Requirements

### Requirement: Season Comparison Analytics
The system SHALL provide a grow comparison endpoint and dashboard that normalizes time-series data by day-in-grow for side-by-side analysis of 2-4 grows.

#### Scenario: Compare two grows by pH over time
- **WHEN** a user selects 2 grows and the pH metric
- **THEN** the system returns daily-average pH for each grow aligned by day-in-grow (day 1 = started_at) as overlay line data

#### Scenario: Compare grows with different durations
- **WHEN** one grow lasted 60 days and another 80 days
- **THEN** the chart shows both series on the same X axis (day-in-grow), with the shorter grow ending at day 60

#### Scenario: View summary statistics
- **WHEN** a user compares multiple grows
- **THEN** the system shows a table with per-grow averages (pH, EC, VPD, temp), total yield, grow duration, and quality rating

#### Scenario: Auto-detect comparable grows
- **WHEN** a user views a grow detail page
- **THEN** the system identifies other completed grows with the same strain and grow type and offers a "Compare" button

#### Scenario: Improvement indicators
- **WHEN** comparing a recent grow to a previous one with the same strain
- **THEN** the system shows improvement/regression arrows (e.g., ↑ yield +12%, ↓ avg EC -0.3)
