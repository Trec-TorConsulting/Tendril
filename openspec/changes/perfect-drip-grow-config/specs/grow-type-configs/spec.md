## ADDED Requirements

### Requirement: Drip Emitter Management
The system SHALL provide emitter management guidance including emitter type selection (drip stakes, drip rings, pressure-compensating), clog detection methods, cleaning protocol (H2O2 flush, acid wash), flow rate verification, and spare emitter strategy.

#### Scenario: Uneven growth across drip-fed plants
- **WHEN** a grower notices some plants growing faster than others in a uniform drip setup
- **THEN** the system recommends: verify flow rate at each emitter (collect output for 1 minute in measuring cup), check for partial clogs, ensure all emitters are same distance from manifold, and provides cleaning protocol for blocked emitters

### Requirement: Drip Runoff Ratio Monitoring
The system SHALL track and interpret runoff volume percentage (target 10-20%) and input-vs-runoff EC/pH delta as the primary diagnostic tool for drip systems. The system SHALL provide guidance interpreting runoff EC higher than input (salt accumulation), runoff EC lower than input (hungry plant), and target runoff percentage per stage.

#### Scenario: Runoff EC is 40% higher than input EC
- **WHEN** a grower measures runoff EC at 3.2 when input EC is 2.0
- **THEN** the system diagnoses salt accumulation in the media, recommends: increase runoff percentage to 25-30% for 2-3 irrigations, consider a plain water flush, reduce input EC by 10-15%, and re-check runoff after next irrigation

### Requirement: Drain-to-Waste vs Recirculating Decision Guide
The system SHALL provide a comprehensive comparison of drain-to-waste (DTW) and recirculating drip configurations including complexity, cost, water usage, pathogen risk, and equipment requirements for each approach.

#### Scenario: Grower choosing between DTW and recirculating
- **WHEN** a grower is configuring a new drip system
- **THEN** the system presents: DTW (simpler, no pathogen risk, 30-40% more water/nutrient waste, recommended for beginners and small grows) vs recirculating (saves water/nutrients, requires UV sterilizer or ozone, pH/EC management more complex, recommended for commercial operations focused on efficiency)

### Requirement: Drip Media-Specific Irrigation Profiles
The system SHALL provide irrigation scheduling specific to each compatible drip media: coco coir (high frequency, CalMag required, never let dry), rockwool slabs (precision shots, dryback monitoring), perlite (fast draining, frequent irrigation), and mixed blends. Each profile SHALL define shot count, volume, and timing per growth stage.

#### Scenario: Coco coir drip grower in mid flower
- **WHEN** a drip grower using coco is in mid flower stage
- **THEN** the system provides: 4-6 irrigation events per day, shot volume to achieve 15-20% runoff, CalMag at 1-2 ml/gal before base nutrients, never let coco dry below 50% saturation, and notes that coco's cation exchange capacity means CalMag is always required

### Requirement: Drip Crop Steering
The system SHALL provide crop steering guidance for drip systems including generative steering (larger dryback, higher EC, less frequent irrigation to promote flowering/ripening) and vegetative steering (lower dryback, lower EC, more frequent irrigation to promote growth). Steering strategies SHALL be mapped to appropriate growth stages.

#### Scenario: Grower wants to push plants into generative mode for flower
- **WHEN** a drip grower transitions from veg to flower
- **THEN** the system provides generative steering targets: increase overnight dryback to 10-15% (from 5% in veg), raise EC by 0.2-0.4, delay first irrigation 1-2 hours after lights on, reduce total shot count, and explains this stress signal promotes flower development

### Requirement: Drip Stage-by-Stage Configuration
The system SHALL provide 12-stage grow configuration specific to drip/top feed with media-dependent irrigation schedules, runoff monitoring targets per stage, and crop steering phase transitions.

#### Scenario: Drip grower viewing complete stage guide
- **WHEN** a grower requests drip config for rockwool media
- **THEN** the system returns all 12 stages with rockwool-specific irrigation parameters: shot count, shot volume (ml), first/last shot timing relative to lights, dryback % targets, runoff EC targets, and crop steering mode per stage
