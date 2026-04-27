## ADDED Requirements

### Requirement: Per-Bucket VPD Calculation
The system SHALL calculate Vapor Pressure Deficit for each bucket using ambient temperature and humidity data (from ESP32 or tent sensors) and display it with optimal range indicators per growth stage.

#### Scenario: VPD calculation and display
- **WHEN** ambient temperature and humidity data is available for a bucket
- **THEN** VPD is calculated and displayed in the bucket detail view with a color-coded range indicator

#### Scenario: VPD out of range alert
- **WHEN** calculated VPD falls outside the optimal range for the bucket's current growth stage
- **THEN** a warning alert is generated

---

### Requirement: Nutrient Calculator
The system SHALL provide a nutrient calculator that recommends dosing amounts based on current vs. target EC/PPM and reservoir volume, supporting common nutrient lines.

#### Scenario: Calculate nutrient dose
- **WHEN** a user inputs current EC, target EC, and reservoir volume
- **THEN** the system calculates and displays ml of each nutrient component to add

#### Scenario: Preset nutrient lines
- **WHEN** a user selects a nutrient line (e.g., General Hydroponics Flora)
- **THEN** the calculator uses the preset component ratios for that line
