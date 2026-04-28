## ADDED Requirements

### Requirement: Outdoor Weather Integration
The system SHALL integrate weather data into every stage decision: frost protection triggers (row covers/cold frames when temp <35°F), heat stress protocols (shade cloth when >95°F, deep watering), rain-skip irrigation logic (skip watering when >0.5" rain forecast), wind protection (stake when >20mph forecast), and storm preparation.

#### Scenario: Late spring frost warning after transplant
- **WHEN** weather forecast shows overnight low below 35°F and plants are outdoors
- **THEN** the system alerts the grower with frost protection protocol: cover plants with row covers or move containers to shelter, mulch heavily around base, avoid watering (wet soil + frost = worse damage), and resume normal care once overnight lows consistently above 40°F

### Requirement: Natural Photoperiod Management
The system SHALL provide natural photoperiod tracking by latitude including flower trigger date estimation (when daylight drops below 14 hours), light deprivation technique (covering plants to force early flower), autoflower outdoor advantages, and supplemental lighting to prevent premature flowering.

#### Scenario: Outdoor photo grower at 42° latitude
- **WHEN** a photoperiod plant is growing outdoors at 42°N latitude
- **THEN** the system calculates: summer solstice ~15.3h daylight, flower trigger (~14h daylight) around August 1-10, full flower commitment by August 20-25, target harvest October 1-15 (depending on strain), and warns if first frost date is before expected harvest completion

### Requirement: Companion Planting Integration
The system SHALL provide a companion planting guide specific to cannabis outdoor grows including beneficial companions (basil, marigold, lavender, clover, dill), harmful neighbors to avoid, spacing guidance, trap cropping strategy, and integration with the plot grid designer.

#### Scenario: Planning companion plants for a new outdoor grow
- **WHEN** a grower is setting up an outdoor soil grow plot
- **THEN** the system suggests: basil between plants (repels aphids/thrips, 12" spacing), marigold borders (nematode deterrent), crimson clover as ground cover (nitrogen fixation, living mulch), and lavender at plot edges (attracts pollinators, repels deer)

### Requirement: In-Ground Soil Building
The system SHALL provide multi-season soil building guidance: soil testing protocol (N-P-K, pH, CEC, micronutrients), amendment recommendations based on test results, cover crop rotations between grows, composting integration, mulch layering, no-till permanent bed management, and biochar/humic acid programs.

#### Scenario: First-year outdoor soil grower
- **WHEN** a grower is starting a new outdoor in-ground grow
- **THEN** the system recommends: send soil sample for testing first, amend based on results (lime if pH <6.0, sulfur if >7.0, compost for organic matter <5%), deep mulch 3-4 inches, plant cover crop after harvest (crimson clover + winter rye), plan to build soil for 1-2 seasons before expecting peak results

### Requirement: Growing Degree Days (GDD) Tracking
The system SHALL calculate and track Growing Degree Days using base temperature 50°F/10°C, provide GDD-based stage transition triggers (not calendar dates), integrate with weather data for automatic daily accumulation, and predict harvest maturity based on accumulated GDD.

#### Scenario: Checking harvest readiness via GDD
- **WHEN** an outdoor soil grow has been accumulating GDD
- **THEN** the system shows: current accumulated GDD, target GDD for strain maturity (e.g., 2200-2500 GDD for a 10-week flower strain), estimated days remaining based on weather forecast, and percentage complete toward harvest maturity

### Requirement: Hardiness Zone Integration
The system SHALL auto-detect USDA hardiness zone from latitude/longitude, determine growing season parameters (last frost, first frost, season length), adjust stage timelines by zone, and recommend compatible companion plants for the zone.

#### Scenario: Grower sets location for outdoor grow
- **WHEN** a grower provides latitude/longitude for their outdoor grow
- **THEN** the system auto-detects hardiness zone (e.g., Zone 6b), determines last spring frost (~April 15), first fall frost (~October 15), growing season ~180 days, and adjusts all stage timelines to fit within the frost-free window

### Requirement: Outdoor Pest & Wildlife Management
The system SHALL provide outdoor-specific pest and wildlife management including deer deterrent strategies, rabbit barriers, caterpillar treatment (BT), powdery mildew prevention (airflow/defoliation), budrot/botrytis moisture management, and a full IPM protocol for outdoor cannabis.

#### Scenario: Grower finds caterpillar damage in buds
- **WHEN** a grower reports caterpillar damage during flowering
- **THEN** the system provides emergency protocol: inspect ALL buds immediately (caterpillars cause budrot from inside), remove visible caterpillars by hand, apply BT (Bacillus thuringiensis) spray — safe during flower, reapply every 5-7 days and after rain, remove any damaged/rotting bud material immediately, and increase inspection frequency to daily

### Requirement: Outdoor Soil Stage-by-Stage Configuration
The system SHALL provide 12-stage grow configuration for outdoor soil with GDD-based stage transitions, weather-integrated guidance per stage, companion planting schedule, hardiness zone adjustments, and in-ground vs raised bed variants.

#### Scenario: Outdoor soil grower views vegetative stage config
- **WHEN** an outdoor soil grow enters vegetative growth (post-transplant, hardened off)
- **THEN** the system provides: GDD accumulation target for stage transition, weather monitoring (frost risk fading, heat stress increasing), companion planting now active, pest scouting protocol (weekly visual inspection), watering depth and frequency for stage, soil amendment schedule if needed, and natural photoperiod information (long days = vegetative growth)
