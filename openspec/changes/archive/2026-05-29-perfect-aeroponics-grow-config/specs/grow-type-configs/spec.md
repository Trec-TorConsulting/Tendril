## ADDED Requirements

### Requirement: High-Pressure vs Low-Pressure Aeroponics Guide
The system SHALL differentiate between high-pressure aeroponics (HPA: 80+ PSI, 50-micron droplets, accumulator tank) and low-pressure aeroponics (LPA: 20-60 PSI, larger droplets, pump-based) with separate equipment requirements, performance expectations, maintenance profiles, and difficulty ratings.

#### Scenario: Grower chooses between HPA and LPA
- **WHEN** a grower is setting up an aeroponic system
- **THEN** the system presents: HPA (fastest growth, highest yields, most expensive, most maintenance, advanced growers only) vs LPA (simpler, more forgiving, still faster than DWC, good entry point to aeroponics)

### Requirement: Aeroponics Mist Cycle Engineering
The system SHALL provide mist on/off cycle timing specific to each growth stage, day vs night adjustments, and cycle optimization guidance based on root observation (dry roots = increase mist, dripping roots = decrease mist). Timer resolution SHALL support seconds-level precision.

#### Scenario: Aeroponic grower in vegetative stage
- **WHEN** a grower's aeroponic plants are in vegetative stage
- **THEN** the system provides: HPA mist cycle (3-5 seconds on / 3-5 minutes off during lights on, 3-5 seconds on / 8-10 minutes off during lights off) with root observation checkpoints

### Requirement: Aeroponics Nozzle Management
The system SHALL provide nozzle maintenance protocol including clog prevention (inline filtration requirements), cleaning schedules (weekly inspection, monthly deep clean), backup nozzle strategy, spray pattern verification, and nozzle type selection by system pressure.

#### Scenario: One plant showing wilting while others are healthy
- **WHEN** a single plant in an aeroponic system shows stress while neighbors are fine
- **THEN** the system diagnoses likely nozzle clog at that position, provides: inspect nozzle spray pattern, clean or replace nozzle, check inline filter, verify no root tissue blocking nozzle, and emphasizes that nozzle clogs are the #1 aeroponic failure

### Requirement: Aeroponics Root Chamber Design
The system SHALL provide root chamber specifications including light exclusion requirements (any light = algae), temperature targets (65-72°F root zone), humidity dynamics (100% during mist, rapid absorption between mists), material recommendations (food-safe, opaque), and drain design for reservoir return.

#### Scenario: Algae developing in root chamber
- **WHEN** green algae appears inside the aeroponic root chamber
- **THEN** the system diagnoses light leak, provides: inspect all seams/joints/access ports for light entry, cover with opaque material, add light traps at cable pass-throughs, and warns that algae clogs nozzles (cascading failure)

### Requirement: Aeroponics Failure Mode Response
The system SHALL define failure modes with response times: nozzle clog (single plant, minutes to wilt), pump failure (all plants, 1-5 minutes to damage), solenoid stuck closed (no mist, same as pump failure), solenoid stuck open (continuous mist, root suffocation over hours), power failure (all systems down). Each SHALL have severity, detection method, and response protocol.

#### Scenario: Aeroponic pump fails
- **WHEN** the mist pump stops running in an aeroponic system
- **THEN** the system triggers `critical` alert: "AERO PUMP FAILURE — roots drying in 1-5 minutes. Manually spray roots with nutrient solution while troubleshooting. Switch to backup pump. If no backup, consider emergency conversion to DWC (fill chamber partially with nutrient solution and add air stone)."

### Requirement: Aeroponics Stage-by-Stage Configuration
The system SHALL provide 12-stage grow configuration for aeroponics with mist cycle timing per stage, root chamber environmental targets, nozzle maintenance schedule, and lower-than-standard EC targets reflecting higher root zone absorption efficiency.

#### Scenario: Aeroponic grower starting seedlings
- **WHEN** an aeroponic grow begins seedling stage
- **THEN** the system provides: rooted clones or seedlings with established root systems placed in net pots, initial mist cycle (5s on / 2-3 min off — more frequent for young roots), very low EC (0.2-0.4), and notes that seedlings must have visible root mass before entering the aeroponic chamber
