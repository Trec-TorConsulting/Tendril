# Delta: Grow Assistant Core — Task Engine

## MODIFIED Requirements

### Requirement: Grow-Type-Accurate Task Generation
The task auto-generation engine SHALL produce tasks with intervals, priorities, and content that are specific and accurate to each grow type and growing media.

#### Scenario: DWC grow generates hydro-specific daily routine
- **GIVEN** an active DWC grow cycle
- **WHEN** the task generator runs
- **THEN** morning routine tasks include pH check (daily), EC check (daily), water temp check (daily), and visual health inspection (daily)
- **AND** weekly routine includes reservoir flush & fill with nutrient recipe
- **AND** no soil-specific tasks (top dressing, soil amendment) are generated

#### Scenario: Kratky grow generates minimal passive tasks
- **GIVEN** an active Kratky grow cycle
- **WHEN** the task generator runs
- **THEN** pH check is generated weekly (not daily)
- **AND** water level check is generated every 3 days
- **AND** no reservoir change task is generated (Kratky is never drained)
- **AND** no pump/circulation tasks are generated

#### Scenario: Coco in flower generates multi-daily watering
- **GIVEN** an active coco grow cycle in flowering stage
- **WHEN** the task generator runs
- **THEN** a watering task is generated with guidance for 3-5x daily fertigation
- **AND** dry-back monitoring is generated daily
- **AND** CalMag reminder is generated every 3 days

#### Scenario: Soil grow generates relaxed intervals
- **GIVEN** an active soil grow cycle
- **WHEN** the task generator runs
- **THEN** pH check (runoff) is generated twice per week (not daily)
- **AND** no EC check is generated (organic soil doesn't use EC)
- **AND** top dressing is generated every 14 days during veg/flower

#### Scenario: Outdoor grow is weather-aware
- **GIVEN** an active outdoor soil grow cycle
- **WHEN** the task generator runs
- **THEN** weather check is generated daily
- **AND** pest/animal scouting is generated every 2-3 days
- **AND** watering frequency adapts to rainfall (supplemental only)

## ADDED Requirements

### Requirement: Routine-Based Task Grouping
The system SHALL group auto-generated tasks into named routines (morning, evening, weekly, biweekly, monthly) so users see coherent bundles of work instead of isolated items.

#### Scenario: Morning routine bundles daily checks
- **GIVEN** a grow with daily pH, EC, water temp, and health checks
- **WHEN** tasks are displayed for a given day
- **THEN** those tasks are grouped under a "Morning Check" routine label
- **AND** the total estimated time is shown (e.g., "~10 min")

#### Scenario: Weekly routine bundles maintenance tasks
- **GIVEN** a grow with weekly reservoir change, calibration, and equipment check
- **WHEN** the weekly maintenance day arrives
- **THEN** those tasks are grouped under a "Weekly Maintenance" routine
- **AND** the total estimated time is shown (e.g., "~45 min")

### Requirement: Time-of-Day Aware Scheduling
The system SHALL schedule tasks relative to the user's timezone and light schedule rather than a fixed UTC time.

#### Scenario: Morning tasks use lights-on time
- **GIVEN** a grow with a light schedule of 6 AM on / 12 AM off (local time)
- **WHEN** morning routine tasks are generated
- **THEN** due time is set to 6:30 AM local (lights_on + 30 minutes)

#### Scenario: Fallback to local morning time
- **GIVEN** a grow with no configured light schedule
- **AND** the tenant timezone is "America/Denver"
- **WHEN** morning routine tasks are generated
- **THEN** due time is set to 7:00 AM Mountain Time

### Requirement: Estimated Task Duration
Each auto-generated task SHALL include an estimated duration in minutes so users can plan their time.

#### Scenario: Quick check tasks show short duration
- **GIVEN** a pH check task is generated
- **THEN** `estimated_minutes` is set to 2-3

#### Scenario: Maintenance tasks show longer duration
- **GIVEN** a flush & fill task is generated
- **THEN** `estimated_minutes` is set to 30-45

### Requirement: Automation-Aware Task Suppression
The system SHALL suppress or reduce frequency of manual check tasks when the grow has corresponding automation equipment configured.

#### Scenario: Auto-dosing suppresses daily pH/EC checks
- **GIVEN** a grow with `auto_ph_dosing` enabled in automation settings
- **WHEN** the task generator runs
- **THEN** daily pH check tasks are NOT generated
- **AND** a weekly "Verify pH auto-doser calibration" task is generated instead

#### Scenario: No automation generates full manual schedule
- **GIVEN** a grow with no automation equipment configured
- **WHEN** the task generator runs
- **THEN** all manual check tasks are generated at their standard intervals

### Requirement: Equipment and IPM Task Categories
The system SHALL generate preventive maintenance tasks for equipment and integrated pest management (IPM) that are not tied to nutrient management.

#### Scenario: IPM spray rotation is generated
- **GIVEN** an active grow in vegetative or flowering stage
- **WHEN** the task generator runs
- **THEN** an IPM spray task is generated every 3-5 days (grow-type-dependent)
- **AND** description includes rotation guidance (alternate products to prevent resistance)

#### Scenario: Equipment maintenance is generated
- **GIVEN** an active hydroponic grow
- **WHEN** the task generator runs
- **THEN** pump/fan/filter check tasks are generated on weekly or biweekly cadence
- **AND** pH/EC meter calibration reminder is generated every 14 days

#### Scenario: Photo documentation is generated weekly
- **GIVEN** an active grow cycle
- **WHEN** the task generator runs
- **THEN** a weekly photo documentation task is generated
- **AND** brief says "Take progress photos from consistent angle for time-lapse comparison"
