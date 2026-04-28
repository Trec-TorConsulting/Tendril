## ADDED Requirements

### Requirement: RDWC Plumbing Architecture Guide
The system SHALL provide plumbing architecture guidance for RDWC systems including pipe diameter sizing by site count, gravity-return vs pump-return configurations, waterfall vs current-culture flow patterns, fitting types (uniseal vs bulkhead), and overflow protection. Guidance SHALL scale from 2-site hobby builds to 50+ site commercial installations.

#### Scenario: Grower plans a 6-site RDWC build
- **WHEN** a grower is setting up a 6-site RDWC system
- **THEN** the system recommends: 2-inch supply lines, 3-inch return lines for gravity flow, minimum 800 GPH circulation pump, control bucket at system low point, and air-gap overflow on each site

### Requirement: RDWC Central Reservoir Management
The system SHALL provide central reservoir management guidance including control bucket sizing rules (total volume = sites × bucket size + 30%), sensor placement for accurate system-wide readings, automated dosing integration points, and single-point monitoring strategy.

#### Scenario: Grower monitors from control bucket
- **WHEN** a grower checks pH/EC at the control bucket
- **THEN** the system provides guidance that readings represent system average after circulation stabilization (wait 15-30 minutes after dosing) and notes that individual sites may vary slightly based on root uptake rates

### Requirement: RDWC Flow Distribution Monitoring
The system SHALL track and alert on flow distribution across connected sites, detecting uneven flow, line blockages, and dead zones. Flow rate targets SHALL be defined per system size.

#### Scenario: Flow rate drops at one site
- **WHEN** a flow sensor at site 4 reads 50% below target GPH
- **THEN** the system triggers an alert indicating possible line blockage or root mass obstruction at site 4, with troubleshooting steps

### Requirement: RDWC Cross-Contamination Protocol
The system SHALL provide quarantine and containment procedures for pathogen events in RDWC systems, including site isolation (valve closure), system-wide flush procedures, and post-event sterilization protocol.

#### Scenario: Root rot detected in one RDWC site
- **WHEN** root rot is identified in a single connected site
- **THEN** the system recommends: immediately close isolation valves for affected site, treat affected bucket independently, add Hydroguard system-wide, monitor all other sites for 48 hours, and provides system flush procedure if contamination spreads

### Requirement: RDWC Failure Mode Response
The system SHALL define failure mode responses for circulation pump failure, line clogs, leaks, and power outages with severity ratings and response time requirements.

#### Scenario: Circulation pump failure in RDWC
- **WHEN** the circulation pump stops (detected via flow sensor or manual check)
- **THEN** the system classifies this as `critical` — all sites lose nutrient circulation within minutes. Response: ensure each site has its own air stone (sites survive as standalone DWC temporarily), troubleshoot pump, and provides maximum safe downtime before plant stress

### Requirement: RDWC Stage-by-Stage Configuration
The system SHALL provide 12-stage grow configuration specific to RDWC including system prime/fill procedures, central dosing approach (dose in control bucket, circulate, re-check), per-stage flow rate adjustments, and system drain/clean procedures at harvest.

#### Scenario: RDWC grower starts a new grow cycle
- **WHEN** an RDWC grower begins germination stage
- **THEN** the system provides: system prime procedure (fill, circulate 24h, check for leaks, adjust pH), site preparation, and notes that seedlings start in separate propagation until roots reach water level before connecting to the system
