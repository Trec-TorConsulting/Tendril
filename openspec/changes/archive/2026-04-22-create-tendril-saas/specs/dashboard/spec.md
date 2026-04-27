## ADDED Requirements

### Requirement: Tenant Dashboard
The system SHALL provide a dashboard view showing camera hero, bucket status, grow score, environment gauges, AI coach, and alerts for the active tent.

#### Scenario: Dashboard with active grow
- **WHEN** a user loads the dashboard and has an active grow
- **THEN** the system displays camera snapshot, bucket chips with pH/EC, grow score ring, environment gauges, AI coach tip, and active alerts

#### Scenario: Dashboard without active grow
- **WHEN** a user loads the dashboard with no active grow
- **THEN** the bucket strip is hidden and the active grow chip shows "None" with a link to create a grow

#### Scenario: Dashboard with outdoor grow
- **WHEN** a user loads the dashboard and the active tent has `environment_type = "outdoor"` or `"greenhouse"`
- **THEN** the dashboard displays a weather widget showing: current temperature, humidity, VPD, UV index, wind speed, weather condition icon, and a compact 24-hour forecast strip with rain probability
- **AND** the environment gauges section uses weather data instead of (or merged with) sensor data

#### Scenario: Weather forecast card
- **WHEN** the dashboard shows an outdoor tent
- **THEN** a 7-day forecast card is shown below the weather widget with daily high/low temps, rain probability, UV max, sunrise/sunset, and weather condition icons

#### Scenario: Weather alerts on dashboard
- **WHEN** active weather alerts exist for an outdoor tent (frost, heat, rain, wind, UV)
- **THEN** the alerts appear prominently in the dashboard alerts section with weather-specific icons and recommended actions

### Requirement: Grow Detail with Inline Buckets
The system SHALL display grow details with bucket cards that expand to show full 6-tab bucket detail inline.

#### Scenario: Open bucket inline
- **WHEN** a user clicks a bucket card in the grow detail
- **THEN** the bucket's 6-tab detail (Overview, Sensors, Diary, Photos, Feeding, Pump) expands inline within the grow view

### Requirement: Device Management Page
The system SHALL provide a device management page for listing, pairing, renaming, and revoking devices.

#### Scenario: Pair new device
- **WHEN** a user clicks "Pair Device" and scans a QR code
- **THEN** the device is linked to their tenant and appears in the device list
