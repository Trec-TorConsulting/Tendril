# Change: Perfect Rockwool Grow Configuration

## Why
Rockwool is the precision agriculture standard — used by the majority of large-scale commercial cannabis operations. Its defining characteristics are **crop steering via dry-back percentage** (the most advanced irrigation management technique), **precision shot-based irrigation** (multiple small doses timed precisely with the plant's transpiration cycle), **slab conditioning** (new rockwool has high pH that MUST be pre-soaked), **slab weight tracking** (the primary monitoring metric — weight = water content), and **cube-to-slab propagation pathway** (seedlings start in rockwool cubes, transplant to slabs). Rockwool represents the pinnacle of data-driven growing. No config exists yet.

## What Changes

### Core Rockwool-Specific Sections
- **Slab conditioning** — New rockwool pH is 7.0-8.0. MUST pre-soak in pH 5.0-5.5 nutrient solution for 24 hours. Drain, re-soak, verify slab pH in runoff below 6.0. pH conditioning is the #1 rockwool mistake
- **Crop steering deep dive** — THE defining technique for rockwool. Vegetative steering (small dryback 5-10%, frequent irrigations, lower EC, pushes vegetative growth). Generative steering (larger dryback 15-25%, fewer irrigations, higher EC, pushes flowering/ripening). Transition timelines. Weight-based dryback calculation. Commercial crop steering programs (Aroya, Grodan, Pulse)
- **Shot-based irrigation** — Rockwool uses discrete irrigation "shots" rather than continuous watering. Shot volume (ml per slab), shot count per day (ramps from 2-4 in veg to 8-15 in flower), first shot timing (when overnight dryback peaks — triggered by light on + transpiration start), last shot timing (2-3 hours before lights off to allow dryback), P1/P2/P3 phases (morning restore, midday maintenance, afternoon dryback setup)
- **Slab weight tracking** — The most important rockwool metric. Slab at field capacity = 100% (weigh after saturation). Dry slab = 0%. Target daytime: 60-80%. Target overnight dryback: depends on steering strategy. How to weigh (scale under slab, commercial substrate sensors like Grodan GroSens, Aroya Teros)
- **Cube-to-slab propagation** — Seeds in 1-inch cubes → transplant to 4-inch cubes when roots emerge → transplant to slabs when roots penetrate cube sides. Cube placement on slab. Drip stake placement. First-watering-after-transplant protocol
- **Slab management** — Cut slab drainage slits (bottom, off-center), slab wrapping (keep light out, retain moisture), slab tilting for drainage, multi-plant-per-slab configurations, slab replacement between grows
- **Environmental health** — Rockwool fiber handling (wear gloves, mask during dry handling), used rockwool disposal (not compostable, landfill or recycling programs), environmental concerns and alternatives

### Stage-by-Stage Config (ROCKWOOL_STAGES)
- 12 stages with shot-based irrigation parameters per stage
- Dryback targets per stage with steering mode transitions
- Slab weight tracking targets per stage
- Cube-to-slab transplant timing

## Impact
- Affected code: `api/app/grows/grow_type_configs/rockwool.py` (new), `__init__.py` (register)
- Affected specs: `grow-type-configs`
