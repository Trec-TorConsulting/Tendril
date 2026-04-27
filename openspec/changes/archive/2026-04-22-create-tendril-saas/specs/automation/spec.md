## ADDED Requirements

### Requirement: Automation Rules Engine
The system SHALL provide a rules engine that triggers actions based on sensor thresholds and conditions (Pro: 10 rules, Commercial: unlimited).

#### Scenario: pH auto-correction
- **WHEN** a bucket's pH reading drops below a configured threshold (e.g., 5.5 for DWC, 6.0 for soil)
- **THEN** the system triggers the configured dose pump action and logs the automated dose
- **AND** the threshold defaults come from the grow type profile

#### Scenario: Grow-type-specific automations
- **WHEN** a user configures automation rules
- **THEN** only automations available for the grow type are shown (e.g., DWC: reservoir change reminder, water temp alert; NFT: pump failure alert; Aero: nozzle pressure alert; Soil: wet/dry cycle monitoring; Coco: runoff EC alert, CalMag reminder)

#### Scenario: Critical-timing automations
- **WHEN** a grow type has time-critical failure modes (NFT pump failure, aero nozzle clog)
- **THEN** those automation alerts are marked CRITICAL priority with immediate notification on all configured channels

#### Scenario: Temperature-triggered fan control
- **WHEN** a tent's air temperature exceeds a configured threshold
- **THEN** the system publishes an MQTT command to activate the fan and sends a notification

#### Scenario: Rule with cooldown
- **WHEN** a rule triggers and a cooldown period is configured (e.g., 30 minutes)
- **THEN** the rule does not fire again until the cooldown expires, preventing rapid oscillation

#### Scenario: Weather-triggered automation (outdoor grows)
- **WHEN** an outdoor tent's weather data shows a condition matching a rule (e.g., temperature below threshold, rain probability above threshold, UV index above threshold)
- **THEN** the system triggers the configured action (notification, device command) and logs the weather-triggered event

#### Scenario: Frost protection rule
- **WHEN** a user configures a frost protection rule for an outdoor tent (e.g., temp < 5°C)
- **THEN** the system monitors weather forecast and triggers alerts or MQTT commands (e.g., activate heater, send cover reminder) when conditions are forecast within configurable lead time (1h, 3h, 6h, 12h, 24h)

#### Scenario: Tier limit enforcement
- **WHEN** a Pro tier user attempts to create an 11th automation rule
- **THEN** the system returns 403 with an upgrade prompt

### Requirement: Environment Control Scheduling
The system SHALL support time-based schedules for environment devices (lights, fans, humidifiers, heaters, pumps).

#### Scenario: Light schedule
- **WHEN** a user configures a light schedule (e.g., 18/6 for veg, 12/12 for flower)
- **THEN** the system publishes MQTT on/off commands at the scheduled times daily

#### Scenario: Schedule with growth stage linkage
- **WHEN** a bucket advances from veg to flower stage
- **THEN** the system prompts to update the light schedule from 18/6 to 12/12

### Requirement: Custom Reports
The system SHALL generate PDF grow reports with sensor trends, photos, milestones, and yield data (Pro and Commercial tiers).

#### Scenario: Generate grow report
- **WHEN** a user requests a report for a completed grow
- **THEN** the system generates a PDF with sensor averages, photos timeline, stage progression, yield summary, and AI health check history
