## ADDED Requirements

### Requirement: Rockwool Slab Conditioning Protocol
The system SHALL provide mandatory slab conditioning guidance: new rockwool has pH 7.0-8.0 and MUST be pre-soaked in pH 5.0-5.5 nutrient solution for 24 hours, drained, re-soaked, and verified via runoff pH before planting.

#### Scenario: New rockwool slab straight from packaging
- **WHEN** a grower is preparing new rockwool slabs
- **THEN** the system provides: soak in pH 5.0-5.5 solution with EC 1.0-1.2 for 24 hours, drain fully, re-soak for 4-8 hours, check runoff pH (must be below 6.0), and warns that skipping conditioning is the #1 rockwool mistake causing early pH lockout

### Requirement: Rockwool Crop Steering
The system SHALL provide comprehensive crop steering guidance specific to rockwool including vegetative steering (5-10% dryback, frequent irrigation, lower EC), generative steering (15-25% dryback, fewer irrigations, higher EC), transition timelines by growth stage, and weight-based dryback calculation methods.

#### Scenario: Transitioning from veg to flower steering
- **WHEN** a rockwool grower flips to 12/12 light schedule
- **THEN** the system provides: transition from vegetative to generative steering over 3-5 days, increase overnight dryback target from 5-10% to 15-20%, delay first morning irrigation by 1-2 hours, raise EC by 0.3-0.5, and reduce total daily shot count by 20-30%

### Requirement: Rockwool Shot-Based Irrigation
The system SHALL define precision shot parameters per growth stage including shot volume (ml per slab), shot count per day, first shot timing (triggered by light on + transpiration start), last shot timing (2-3 hours before lights off), and P1/P2/P3 irrigation phases.

#### Scenario: Rockwool grower in peak flower
- **WHEN** a rockwool grow is in mid-flower (week 4-5)
- **THEN** the system provides: 10-15 shots per day, shot volume 75-100ml per slab, first shot 30-60 min after lights on when slab weight starts dropping, last shot 2 hours before lights off, P1 shots (first 3-4) restore overnight dryback, P2 shots (midday) maintain moisture, P3 shots (late) set up overnight dryback target

### Requirement: Rockwool Slab Weight Tracking
The system SHALL track slab weight as the primary monitoring metric, defining field capacity (100% saturated weight), dry weight (0%), target daytime ranges (60-80%), overnight dryback targets by steering strategy, and measurement methods (manual scale, substrate sensors).

#### Scenario: Grower calibrates slab weight tracking
- **WHEN** a grower sets up weight tracking for a new rockwool slab
- **THEN** the system provides: saturate slab fully and weigh (field capacity = 100%), weigh dry slab out of package (0% baseline), target daily range 60-80% of saturation weight, measure first thing in morning (overnight dryback reading) and before/after irrigations

### Requirement: Rockwool Cube-to-Slab Propagation
The system SHALL define the cube-to-slab propagation pathway: seeds in 1-inch cubes, transplant to 4-inch cubes when roots emerge, transplant to slabs when roots penetrate cube sides. Each transition SHALL include timing signals, technique, and post-transplant care.

#### Scenario: Roots visible at sides of 4-inch cube
- **WHEN** a rockwool grower sees white roots emerging from the sides of 4-inch cubes
- **THEN** the system indicates ready for slab transplant: place cube on pre-conditioned slab, position drip stake in cube center, irrigate to field capacity, ensure drainage slits are open, and begin shot-based irrigation schedule

### Requirement: Rockwool Stage-by-Stage Configuration
The system SHALL provide 12-stage grow configuration for rockwool with shot-based irrigation parameters, dryback targets with steering mode transitions, slab weight tracking targets, and cube-to-slab transplant timing.

#### Scenario: Rockwool grower views complete stage guide
- **WHEN** a grower requests rockwool config
- **THEN** the system returns stages with rockwool-specific parameters: shot count, shot volume (ml), first/last shot timing, dryback % targets, steering mode (vegetative/generative), slab weight targets, and environmental specs
