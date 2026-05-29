## ADDED Requirements

### Requirement: Ebb & Flow Flood Cycle Engineering
The system SHALL provide flood cycle frequency and duration tables specific to each compatible growing media (hydroton, rockwool, perlite, coco) at each growth stage. Cycle parameters SHALL include flood frequency, flood duration, soak time, drain time, and night cycle adjustments.

#### Scenario: Grower uses hydroton in ebb and flow
- **WHEN** a grower selects hydroton as their ebb & flow media
- **THEN** the system provides stage-specific flood schedules: seedling (1-2x/day, 15 min floods), veg (4-6x/day, 15 min), flower (3-5x/day, 15 min), and notes that hydroton drains fast and requires more frequent flooding than rockwool

#### Scenario: Grower uses rockwool cubes in ebb and flow
- **WHEN** a grower selects rockwool cubes as their ebb & flow media
- **THEN** the system provides adjusted schedules: seedling (1x/day), veg (2-3x/day), flower (2-3x/day), reflecting rockwool's higher water retention

### Requirement: Ebb & Flow Media Selection Guide
The system SHALL provide a detailed growing media comparison for ebb & flow systems covering hydroton, rockwool cubes, perlite/vermiculite, and coco in pots. Each media entry SHALL include water retention characteristics, flood frequency implications, pros/cons, and pH buffering behavior.

#### Scenario: New grower choosing ebb and flow media
- **WHEN** a grower is setting up their first ebb & flow system
- **THEN** the system presents a comparison table showing hydroton (beginner-friendly, fast-draining, reusable), rockwool (high retention, fewer floods, pH conditioning needed), perlite (lightweight, good aeration), and coco (high retention, CalMag needed)

### Requirement: Ebb & Flow Tray Engineering
The system SHALL provide tray setup guidance including level surface verification (tolerance ≤1/8 inch across tray), overflow fitting height calculation (2/3 of media height), drain fitting placement, tray sizing by plant count, and multi-tray manifold configurations.

#### Scenario: Water not draining evenly from flood tray
- **WHEN** a grower reports standing water on one side of the flood tray after drain cycle
- **THEN** the system diagnoses unlevel tray surface, provides leveling procedure, and warns that standing water promotes root rot and algae

### Requirement: Ebb & Flow Timer Failure Protocol
The system SHALL define failure modes for timer malfunction: stuck ON (continuous flood → overflow risk, root suffocation) and stuck OFF (drought → media dries out). Each failure mode SHALL have severity rating, detection method, and response procedure.

#### Scenario: Timer stuck in ON position
- **WHEN** the flood pump runs continuously beyond the programmed cycle duration
- **THEN** the system classifies as `critical` — overflow imminent if overflow fitting is inadequate, roots may suffocate if media stays flooded. Response: unplug pump, verify timer operation, check overflow fitting height, inspect for relay failure

### Requirement: Ebb & Flow Stage-by-Stage Configuration
The system SHALL provide 12-stage grow configuration specific to ebb & flow with media-dependent flood cycle tables per stage, reservoir management during drain-back, and environmental targets.

#### Scenario: Ebb and flow grower enters flowering stage
- **WHEN** an ebb & flow grow transitions to early flower
- **THEN** the system adjusts flood recommendations based on selected media, provides EC increase guidance, notes to reduce flood frequency slightly from peak veg, and adds night-skip recommendation (no floods during dark period)
