## ADDED Requirements

### Requirement: DWC Scale Tier Profiles
The system SHALL provide scale-specific configuration profiles for DWC grows at five tiers: solo bucket (1 plant), small tent (2-8 plants), multi-tent (9-24 plants), commercial room (25-100 plants), and warehouse (100+ plants). Each tier SHALL define reservoir management strategy, monitoring approach, labor requirements, recommended equipment differences, and cost tracking guidance.

#### Scenario: Solo bucket grower views DWC config
- **WHEN** a user requests DWC config with `scale=solo`
- **THEN** the system returns configuration emphasizing single-bucket reservoir management, manual pH/EC checking, and minimal equipment

#### Scenario: Commercial grower views DWC config
- **WHEN** a user requests DWC config with `scale=commercial`
- **THEN** the system returns configuration including batch tracking hooks, shared reservoir strategies, automated dosing requirements, regulatory compliance fields, and labor scheduling guidance

### Requirement: DWC Autoflower vs Photoperiod Differentiation
The system SHALL provide strain-type-specific stage durations, light schedules, and training suitability guidance for both autoflower and photoperiod cannabis in DWC. Autoflower stages SHALL have shorter, fixed vegetative periods and note that light schedule does not trigger flowering.

#### Scenario: Autoflower DWC grow stage durations
- **WHEN** a user requests DWC config with `strain_type=auto`
- **THEN** the system returns stage durations appropriate for autoflowers (shorter veg, no light-schedule-triggered flower transition) and notes that training techniques requiring extended veg recovery (mainlining, heavy defoliation) are not recommended

#### Scenario: Photoperiod DWC grow stage durations
- **WHEN** a user requests DWC config with `strain_type=photo`
- **THEN** the system returns stage durations with flexible veg length and 12/12 light flip transition guidance

### Requirement: DWC Water Source Handling
The system SHALL provide water source profiles for RO water, municipal tap water (chlorine and chloramine treatment), well water, and softened water. Each profile SHALL include starting water chemistry targets, CalMag adjustment tables, and pre-treatment steps specific to DWC reservoir management.

#### Scenario: RO water user views DWC water guidance
- **WHEN** a grower indicates they use RO water
- **THEN** the system provides CalMag supplementation requirements (typically 1-2 ml/gal before base nutrients), notes about low mineral buffering causing pH instability, and recommendation to add a small amount of tap water for buffering

#### Scenario: Chlorinated tap water user views DWC water guidance
- **WHEN** a grower indicates they use municipal tap water
- **THEN** the system provides chlorine removal guidance (let sit 24h or use dechlorinator), chloramine warning (does NOT off-gas — requires treatment), and baseline mineral content expectations

### Requirement: DWC Monitoring Thresholds for Automation
The system SHALL define four-tier monitoring thresholds (info, warning, alert, critical) for every DWC-relevant sensor reading. Thresholds SHALL include response time requirements and escalation rules. The thresholds endpoint SHALL be consumable by the automation rules engine.

#### Scenario: Water temperature exceeds warning threshold
- **WHEN** DWC reservoir water temperature rises above 72°F
- **THEN** the system classifies this as a `warning` with response guidance "Add frozen water bottles, check room ventilation"
- **AND** if temperature exceeds 78°F, classifies as `critical` with guidance "Root rot imminent — add Hydroguard, lower temp immediately, consider water chiller"

#### Scenario: pH drifts outside target range
- **WHEN** DWC reservoir pH reads below 5.3 or above 6.5
- **THEN** the system classifies as `alert` with response guidance
- **AND** if pH reads below 4.5 or above 7.5, classifies as `critical` with "Immediate reservoir change required"

### Requirement: DWC Advanced Techniques
The system SHALL provide guidance for advanced DWC techniques including CO2 supplementation (PPFD/CO2 correlation tables), foliar feeding schedules, beneficial microbe programs beyond Hydroguard, silica supplementation timing, and reservoir additives.

#### Scenario: Grower enables CO2 supplementation
- **WHEN** a DWC grower indicates CO2 supplementation is active
- **THEN** the system provides PPFD targets adjusted for elevated CO2 (up to 1500 PPFD at 1200-1500 ppm CO2), temperature tolerance increases (up to 85°F), and VPD recalculation guidance

### Requirement: DWC Nutrient Brand Alternatives
The system SHALL provide nutrient dosing conversions for at least five popular nutrient lines (General Hydroponics Flora Trio, Jack's 321, Athena Pro, Advanced Nutrients pH Perfect, FloraNova) mapped to each DWC growth stage.

#### Scenario: Grower uses Jack's 321 instead of GH Flora Trio
- **WHEN** a grower selects Jack's 321 as their nutrient line
- **THEN** the system provides per-stage dosing (Part A grams/gal, Part B grams/gal, Epsom salt grams/gal) equivalent to the GH Flora Trio recommendations

### Requirement: DWC Harvest Decision Matrix
The system SHALL provide a harvest readiness decision matrix incorporating trichome ratios by desired effect (energetic/balanced/sedative), flush timing by plant condition, strain-specific harvest windows, and environmental manipulation guidance for color and terpene enhancement in the final days.

#### Scenario: Grower checks harvest readiness
- **WHEN** a DWC grower is in late flower or ripening stage
- **THEN** the system provides a checklist: trichome stage assessment guide, recommended flush duration by nutrient line, environmental manipulation options (temperature drop, humidity reduction, extended dark period), and drying preparation steps

### Requirement: DWC Photo Documentation Protocol
The system SHALL define what to photograph at each DWC growth stage, including root zone photos (top and underwater), canopy shots, and problem documentation protocol. Photo guidance SHALL specify timing intervals and comparison angles for growth tracking.

#### Scenario: Grower enters seedling stage
- **WHEN** a DWC grow transitions to seedling stage
- **THEN** the system suggests: photograph root tips emerging from net pot (daily), overhead canopy shot (every 3 days), and reservoir water clarity shot (at each reservoir change)

## MODIFIED Requirements

### Requirement: DWC Stage-by-Stage Configuration
The system SHALL provide comprehensive stage-by-stage configuration for DWC grows covering 12 stages (germination through curing) with environment variants for indoor, outdoor, and greenhouse settings. Each stage SHALL include environmental targets, reservoir parameters, nutrient specifications, tasks, health checks, common problems with solutions, training techniques, and transition signals. Each stage SHALL additionally include autoflower duration variants, photo documentation guidance, and scale-specific task adjustments.

#### Scenario: DWC early vegetative stage indoor
- **WHEN** a DWC grow is in early vegetative stage indoors
- **THEN** the system provides: temperature targets (75-82°F day / 68-75°F night), humidity (50-70%), VPD (0.8-1.2 kPa), light (18/6 at 300-500 PPFD), reservoir pH (5.5-6.0), EC (0.6-1.0), water temp (65-72°F), GH Flora Trio dosing, Hydroguard dosing, weekly tasks, health checks, common problems, and applicable training techniques (LST, topping)

#### Scenario: DWC config served via API with optional filters
- **WHEN** a client requests `GET /v1/grow-types/dwc/config?scale=small_tent&strain_type=auto`
- **THEN** the system returns the full DWC config with stage durations adjusted for autoflower and equipment/task lists filtered to small tent scale
