# Change: Perfect RDWC (Recirculating DWC) Grow Configuration

## Why
RDWC is the scaled-up evolution of DWC — multiple connected grow sites sharing a central control reservoir via circulation pumps. Its unique concerns are **plumbing architecture** (uniseals, bulkheads, return lines), **flow distribution** across sites, **cross-contamination risk** (one infected site spreads to all via shared water), and **central dosing/monitoring** from a single control bucket. Current profile metadata exists but no stage-by-stage config.

## What Changes

### Core RDWC-Specific Sections (what makes RDWC unique from DWC)
- **Plumbing architecture** — Pipe diameter sizing by site count, gravity vs pump-return configurations, waterfall vs current-culture flow patterns, uniseal vs bulkhead pros/cons, air-gap overflow protection
- **Central reservoir management** — Control bucket sizing (rule: total system volume = sites × bucket size + 30%), sensor placement in control bucket, automated dosing integration (pH/EC dosers), single-point monitoring strategy
- **Flow distribution** — GPH requirements per site, manifold vs daisy-chain plumbing, flow rate monitoring per site, equalization techniques, dead-zone prevention
- **Cross-contamination protocol** — Quarantine procedures (isolate infected site by closing valves), system-wide flush procedures, pathogen spread risk assessment, inline UV sterilization option
- **System sizing calculator** — Total water volume by site count, pump sizing, airline requirements, chiller sizing for total volume, reservoir-to-site ratio
- **Plumbing maintenance** — Cleaning schedule (biofilm in lines), salt deposit removal, leak detection, winterization for outdoor/greenhouse RDWC
- **Failure mode analysis** — Pump failure (all sites affected), line clog (single site starves), leak (water loss rate), power outage protocol (battery backup for circulation)

### Stage-by-Stage Config (RDWC_STAGES)
- 12 stages matching DWC structure but with RDWC-specific reservoir, nutrient, and task differences
- Central dosing approach (dose in control bucket, wait for circulation, re-check)
- System prime and fill procedures at grow start
- System drain and clean procedures at grow end

### Equipment, Troubleshooting, Quick Reference
- RDWC-specific equipment (circulation pump, plumbing fittings, control bucket, inline filter, flow meters)
- Troubleshooting organized by: Plumbing Issues, Flow Distribution, Central Reservoir, Root Zone, Water Quality
- Quick reference with system sizing tables

## Impact
- Affected code: `api/app/grows/grow_type_configs/rdwc.py` (new), `__init__.py` (register)
- Affected specs: `grow-type-configs`
- No breaking changes
