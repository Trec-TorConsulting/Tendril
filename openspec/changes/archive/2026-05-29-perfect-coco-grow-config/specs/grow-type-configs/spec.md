## ADDED Requirements

### Requirement: Coco CalMag Science and Supplementation
The system SHALL explain coco's cation exchange chemistry (Ca/Mg lockout), provide buffering protocol for new coco, ongoing CalMag dosing by stage, deficiency symptom identification, and adjustments for LED lights and RO water.

#### Scenario: Brown spots appearing on coco-grown plant
- **WHEN** a coco grower reports brown spots on lower/middle leaves
- **THEN** the system diagnoses likely CalMag deficiency (the #1 coco problem), verifies CalMag is being used at every feeding, checks if RO water is used (needs more CalMag), checks if LED lights (increases demand), and provides corrective dosing

### Requirement: Coco Preparation and Buffering Protocol
The system SHALL provide coco preparation guidance including rinsing (remove salts/dust), CalMag buffering soak (24h in CalMag solution), coco/perlite mixing ratios, brick rehydration instructions, and pre-buffered brand recommendations.

#### Scenario: Grower using raw coco bricks
- **WHEN** a grower is preparing raw coco coir bricks for first use
- **THEN** the system provides: rehydrate brick in warm water, rinse thoroughly until runoff EC is below 0.5, soak in CalMag solution (5 ml/gal) for 24 hours, drain, mix with perlite (70/30 ratio recommended), and verify pH of prepared media is 5.8-6.2

### Requirement: Coco Fertigation Frequency Schedule
The system SHALL provide stage-specific fertigation frequency targets (seedling 1x/day through flower 3-6x/day), with the principle that every watering in coco MUST contain nutrients (never plain water except during final flush).

#### Scenario: Coco grower asks about watering with plain water
- **WHEN** a coco grower asks about alternating nutrient feedings with plain water
- **THEN** the system advises: NEVER use plain water in coco (except final flush). Coco's cation exchange sites release locked-up sodium and chloride when flushed with plain water, creating toxic conditions. Every irrigation must contain nutrients + CalMag.

### Requirement: Coco Dryback Monitoring and Crop Steering
The system SHALL define dryback percentage targets for coco by growth stage (vegetative 5-10%, generative/flower 10-20%), pot weight tracking methods (hand feel, kitchen scale), and never-dry-completely warnings with explanation of consequences (anaerobic conditions, salt concentration, hydrophobic surface).

#### Scenario: Coco completely dries out
- **WHEN** a coco grower lets their media dry completely
- **THEN** the system alerts: coco becomes hydrophobic when bone dry (water runs off instead of absorbing), salt concentration spikes to damaging levels, and beneficial microbes die. Recovery: slow rehydration with dilute nutrient solution from bottom (set pot in tray of solution), multiple small feedings over 24 hours

### Requirement: Coco Runoff EC Management
The system SHALL track input-vs-runoff EC as the primary diagnostic for coco grows, with interpretation guidance (rising runoff EC = salt buildup, falling runoff EC = hungry plant), target runoff percentage (10-20%), and flush trigger thresholds.

#### Scenario: Coco runoff EC consistently 50%+ above input
- **WHEN** a coco grower measures consistent runoff EC significantly above input EC
- **THEN** the system recommends: increase runoff percentage to 25-30% for next 2-3 feedings, if EC doesn't normalize then flush with half-strength nutrient solution until runoff EC matches input, review input EC (may be too high for current stage)

### Requirement: Coco Stage-by-Stage Configuration
The system SHALL provide 12-stage grow configuration for coco with fertigation frequency per stage, dryback targets, CalMag dosing, pot-up schedule, and environment variants.

#### Scenario: Coco grower in late flower needs irrigation guidance
- **WHEN** a coco grower is in week 6 of flower
- **THEN** the system provides: 4-6 fertigation events per day (every 2-3 hours during lights on), 15-20% dryback overnight (generative steering), EC 1.6-2.0 + CalMag, target 15-20% runoff, monitor runoff EC for salt buildup weekly
