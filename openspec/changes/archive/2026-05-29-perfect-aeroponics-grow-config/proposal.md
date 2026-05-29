# Change: Perfect Aeroponics Grow Configuration

## Why
Aeroponics is the highest-performance and highest-risk hydro method. Roots are suspended in air and misted with fine nutrient spray at high pressure. It produces the fastest growth rates but has **zero margin for error** — roots begin dying within seconds to minutes of mist failure, making it the most automation-dependent grow type. Unique concerns include **mist cycle precision** (seconds on/off timing), **nozzle pressure and atomization** (droplet size directly affects oxygen absorption), **root chamber environment** (humidity, temperature, light exclusion), **nozzle clog prevention** (the #1 failure mode), and **high-pressure vs low-pressure aeroponics** (fundamentally different systems). No config exists yet.

## What Changes

### Core Aeroponics-Specific Sections
- **High-pressure vs low-pressure aeroponics** — HPA (true aero, 80+ PSI, 50-micron droplets, accumulator tank, solenoid valves) vs LPA (mist sprayers, 20-60 PSI, larger droplets, more forgiving). Each is essentially a different growing method with different equipment, maintenance, and performance profiles
- **Mist cycle engineering** — On/off timing by growth stage (seedling: 5s on / 3min off, veg: 3s on / 5min off, flower: 5s on / 5min off). Day vs night cycle adjustments. Timer resolution requirements (must handle seconds, not minutes). Cycle optimization by root observation (dry roots = too long off, dripping roots = too long on)
- **Nozzle management** — The critical maintenance item. Nozzle types (mist nozzles, anti-drip nozzles, clone machine sprayers). Clog prevention (inline filter mandatory, low-PPM nutrients, avoid organic additives). Cleaning schedule. Backup nozzles. Spray pattern verification
- **Root chamber design** — Light-tight (any light = algae), temperature controlled (root zone 65-72°F), humidity management (100% during mist, rapid absorption between mists), chamber material (food-safe, opaque), drain design (collect runoff for reservoir return)
- **Pressure system** — Accumulator tank sizing, pressure switch settings, solenoid valve selection, pressure gauge monitoring, compressor vs diaphragm pump
- **Failure mode analysis** — Nozzle clog (single plant starves), pump/compressor failure (all plants die in 1-5 minutes), solenoid stuck closed (no mist), solenoid stuck open (continuous mist, root suffocation), power failure protocol. Each with severity and response time
- **Nutrient approach** — Lower EC than any other hydro method (roots absorb more efficiently from mist). Frequent reservoir changes (small reservoir cycles fast). No organic nutrients (clog nozzles). Synthetic only with fine particle filtration
- **Clone/propagation integration** — Aeroponics is the gold standard for cloning. Clone-specific mist cycles and chamber design

### Stage-by-Stage Config (AERO_STAGES)
- 12 stages with mist cycle timing per stage (the key differentiator)
- Root chamber monitoring per stage
- Nozzle maintenance schedule per stage

## Impact
- Affected code: `api/app/grows/grow_type_configs/aeroponics.py` (new), `__init__.py` (register)
- Affected specs: `grow-type-configs`
