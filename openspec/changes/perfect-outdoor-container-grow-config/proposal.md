# Change: Perfect Outdoor Container Grow Configuration

## Why
Outdoor container growing is a hybrid method — it combines the environmental challenges of outdoor growing (weather, natural photoperiod, pests) with the root zone management of indoor growing (container sizing, drainage, watering frequency). Its unique concerns are **container heat management** (black pots in direct sun = root zone 120°F+ = root death), **root binding in containers** (outdoor plants get HUGE — 6-10+ feet — in containers that limit root growth), **mobility** (containers can be moved to shelter during storms, brought indoors for light dep, repositioned for sun exposure), **accelerated drying** (containers outdoors dry much faster than in-ground due to wind, sun, and limited soil volume), **wind vulnerability** (tall outdoor plants in lightweight containers = tipping over), and **pot material and color effects** (fabric vs plastic vs ceramic vs terracotta — each behaves differently in outdoor conditions). This is the counterpart to `outdoor_soil` — same environment, but in containers instead of in-ground. No config exists yet.

## What Changes

### Core Outdoor Container-Specific Sections
- **Container heat management** — THE #1 outdoor container challenge. Black plastic in sun = root zone 120°F+. Solutions: white/light-colored pots, pot sleeves/wraps (reflective), double-potting (pot inside pot with air gap), burying pots partially in ground, shade cloth on south-facing side of pots, mulch on soil surface. Temperature monitoring at root zone level (soil temp probe). Threshold: root activity slows above 85°F, root death starts above 95°F
- **Root binding and pot sizing** — Outdoor plants grow MUCH larger than indoor. Sizing guide: autos (5-10 gal, they don't need as much), photos (15-50+ gal for full outdoor size). Signs of root binding (slowed growth, wilting despite water, roots circling at bottom). Solutions: fabric pots (air pruning), root pruning, up-potting mid-season, Smart Pots / Air Pots. Why outdoor plants need larger containers than indoor equivalents (longer veg, more sun = more growth)
- **Container mobility strategy** — The killer advantage of outdoor containers. Move to shelter during: frost (bring inside overnight), hail, extreme wind, heavy rain (prevent overwatering). Move for light dep (bring inside or under tarp to force 12/12 early). Repositioning for sun exposure as sun angle changes seasonally. Moving to shade during heat waves. Logistics: pot dollies, hand trucks, wheeled platforms. Weight planning (a wet 30 gal pot = 150+ lbs)
- **Accelerated drying management** — Outdoor containers dry 2-3x faster than in-ground due to: wind evaporation from all sides, sun heating the pot walls, limited soil volume. Solutions: mulch top layer (3-4"), drip irrigation on timer, self-watering inserts for large pots, water retention amendments (perlite vs vermiculite trade-off), watering twice daily in peak summer. Monitoring: daily weight check or moisture sensor per pot
- **Wind protection** — Tall outdoor plants (6-10 feet) in containers = top-heavy and tip-prone. Solutions: wide-base pots (wider than tall), staking/trellising anchored to ground (not pot), grouping pots together for mutual wind protection, windbreak placement (fence, hedge, or screen), lowering center of gravity (wider, shorter containers vs tall narrow ones). Securing: ratchet straps to ground anchors for hurricane/severe wind
- **Pot material and color guide** — Each material behaves differently outdoors. Fabric (Smart Pots): best air pruning, dries fastest, lightweight, no heat buildup — the outdoor container standard. Plastic: cheapest, retains moisture, can overheat in sun. Ceramic/terracotta: heavy (stability), breathes slightly, cracks in frost. Air Pots: excellent air pruning, expensive. Color matters: dark colors absorb heat (bad in hot climates), light colors reflect (preferred outdoor)
- **Outdoor container nutrient management** — Containers leach nutrients via runoff AND rain washes nutrients through. Higher feeding frequency than in-ground. Slow-release amendments less effective (rain washes them through). Liquid feeding more reliable. CalMag demand higher in containers (rapid drying concentrates then dilutes salts)
- **Weather + container interaction** — Rain: containers overflow (ensure drainage holes clear, elevate on bricks). Frost: containers freeze faster than ground (insulate with bubble wrap or bring inside). Heat: see heat management section. Hail: containers are MOBILE — move under cover

### Stage-by-Stage Config (OUTDOOR_CONTAINER_STAGES)
- 12 stages with weather-integrated container-specific guidance
- Heat management protocol per stage (seedling more vulnerable, mature plants tolerate more)
- Pot size progression through stages (up-potting schedule)
- Drying rate adjustments by stage and season

## Impact
- Affected code: `api/app/grows/grow_type_configs/outdoor_container.py` (new), `__init__.py` (register)
- Affected specs: `grow-type-configs`
- Shares outdoor modules (weather, pest scouting, yields) with `outdoor_soil`
