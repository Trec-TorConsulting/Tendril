## ADDED Requirements

### Requirement: Pure Kratky vs Modified Kratky Decision Guide
The system SHALL differentiate between pure Kratky (fill once, never intervene) and modified Kratky (strategic top-offs for cannabis), with guidance on when modified approach is necessary, top-off protocol (concentration, volume, maximum fill height relative to air root line), and frequency expectations.

#### Scenario: Kratky grower's water level drops below 25%
- **WHEN** a Kratky container's water level drops below 25% of original volume
- **THEN** the system recommends Modified Kratky top-off: add half-strength nutrient solution ONLY to the bottom of the water root zone (never above the air root line), and provides visual guide showing safe fill height

### Requirement: Kratky Container Selection Guide
The system SHALL provide container selection guidance including material requirements (food-safe, opaque), sizing calculator by expected plant size, seal quality requirements, and common container options with pros/cons.

#### Scenario: New Kratky grower choosing containers
- **WHEN** a grower is selecting containers for a Kratky grow
- **THEN** the system presents: 5-gallon bucket (recommended for cannabis, lasts full grow), 3-gallon (adequate for autos), mason jar (herbs only, too small for cannabis), with emphasis that container MUST be opaque (paint it if transparent) and lid MUST seal tightly

### Requirement: Kratky Air Root Zone Management
The system SHALL provide air root zone education including the progression of water level drop, air root vs water root function, why overfilling kills (drowns air roots), healthy air gap visual progression, and air gap monitoring protocol.

#### Scenario: Grower asks why Kratky plant is drooping after top-off
- **WHEN** a Kratky plant shows wilting shortly after a water top-off
- **THEN** the system diagnoses overfilling (water covered air roots), explains the air root/water root dual system, and advises: drain excess water below air root line, allow air roots to recover (24-48 hours), and never fill above the air root boundary again

### Requirement: Kratky EC/pH Drift Management
The system SHALL define acceptable pH and EC drift ranges for Kratky systems where reservoir changes are not practical, including when drift indicates normal behavior vs a problem, and emergency intervention thresholds.

#### Scenario: Kratky pH has drifted from 5.8 to 6.8 over two weeks
- **WHEN** a Kratky container's pH rises by 1.0 over two weeks
- **THEN** the system classifies as normal Kratky behavior (pH naturally rises as plant consumes acidic nutrients), notes this is acceptable within 5.5-7.0 range, and only recommends intervention if pH exceeds 7.5 or the plant shows deficiency symptoms

### Requirement: Kratky Stage-by-Stage Configuration Enhancement
The existing Kratky stage-by-stage config SHALL be enhanced with scale profiles, auto/photo strain duration variants, water source handling, monitoring thresholds, nutrient brand alternatives, and photo documentation protocol matching the DWC gold standard.

#### Scenario: Autoflower Kratky grower views config
- **WHEN** a grower requests Kratky config with `strain_type=auto`
- **THEN** the system returns stage durations optimized for autoflowers (shorter veg, total 70-90 days), notes that autos are ideal for Kratky (shorter cycle means less nutrient depletion risk), and adjusts container sizing recommendation (3-gallon sufficient for most autos)
