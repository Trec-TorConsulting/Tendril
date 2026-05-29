# Change: Perfect Outdoor Soil Grow Configuration

## Why
Outdoor soil is the most environmentally complex grow method — the grower fights AND cooperates with nature. It has more external variables than any other type: **weather** (frost, rain, wind, heat), **natural photoperiod** (no light schedule control — the sun decides when flower starts), **companion planting** (leveraging plant relationships for pest control and soil health), **soil amendments and building** (in-ground soil requires testing and building over seasons), **growing degree days** (heat unit accumulation for maturity prediction), **hardiness zones** (location determines what and when you can grow), **pest and animal pressure** (deer, rabbits, caterpillars, spider mites, powdery mildew), and **seasonal planning** (germination indoors → hardening off → transplant after last frost → harvest before first frost). The outdoor modules (plot grid, soil tests, pest scouting, weather, yields, companion plants) already exist as API routes. This config provides the grow type configuration that ties them together with stage-by-stage guidance. Related: `add-outdoor-soil-experience` covers the full outdoor module buildout.

## What Changes

### Core Outdoor Soil-Specific Sections
- **Weather integration** — How weather affects every decision. Temperature management: frost protection (row covers, cold frames, bringing in at night), heat stress (shade cloth, mulching, deep watering). Rain management: when to supplement vs skip irrigation, overwatering from extended rain, nutrient leaching after heavy rain. Wind: windbreak planning, staking tall plants, desiccation risk. Lightning/storm: physical protection
- **Natural photoperiod management** — Outdoor growers don't control light. Photoperiod-dependent strains flower when daylight drops below ~14 hours (varies by latitude). Light dep technique (covering plants with tarps to force early flower). Autoflower advantages outdoors (no photoperiod dependency). Latitude-based flower trigger date calculator. Supplemental lighting to prevent early flower (extending photoperiod with outdoor lights)
- **Companion planting integration** — Which plants to grow alongside cannabis: basil (repels aphids, thrips), marigold (nematode deterrent), lavender (attracts pollinators, repels pests), clover (nitrogen fixation cover crop), dill (attracts beneficial predators). Harmful neighbors to avoid. Spacing considerations. Trap cropping strategy
- **In-ground soil building** — Different from container soil: you're building a permanent soil ecosystem over seasons. Soil testing (N-P-K, pH, CEC, micronutrients), amendment based on test results, cover cropping between grows (crimson clover, winter rye, daikon radish), composting, mulch layering, no-till permanent beds, biochar, humic/fulvic acids
- **Growing degree days (GDD)** — Heat unit accumulation: daily GDD = ((max temp + min temp) / 2) - base temp. Base temperature for cannabis: 50°F / 10°C. Accumulated GDD predicts maturity. Stage transitions triggered by GDD thresholds (not calendar dates). Integration with weather data for automatic tracking
- **Hardiness zones** — USDA zone auto-detection from latitude/longitude. Determines: last frost date, first frost date, growing season length, compatible companion plants, planting window. Zone-specific adjustment to stage timelines
- **Pest and wildlife pressure** — Outdoor-specific threats: deer (fencing, deer repellent, elevated beds), rabbits (chicken wire barriers), caterpillars (BT spray, manual removal), spider mites (predatory mites, neem oil), powdery mildew (airflow, defoliation, potassium bicarbonate), budrot/botrytis (moisture management, defoliation for airflow). Integrated Pest Management (IPM) protocol for outdoor
- **Seasonal planning** — The grow follows the SEASON, not the grower's schedule. Indoor seed start → hardening off (7-10 days gradual outdoor exposure) → transplant after last frost → vegetative growth (long days) → natural flower trigger → harvest before first frost. Calendar-based planning by hardiness zone. Succession planting for extended harvest
- **Moon phase / biodynamic planting** — Optional: planting by lunar calendar (plant above-ground crops during waxing moon, root crops during waning). Not required but supported for biodynamic growers
- **Irrigation planning for outdoor** — Drip vs soaker vs hand watering. Watering depth vs frequency (deep and infrequent encourages deep roots). Rain-skip logic. Mulch to retain moisture. Morning watering (avoid nighttime moisture = PM risk). Water source: well, municipal, rainwater collection

### Stage-by-Stage Config (OUTDOOR_SOIL_STAGES)
- 12 stages with GDD-based triggers for transitions (not calendar dates)
- Weather integration per stage (frost protection in early stages, heat management in veg, moisture management in flower)
- Companion planting schedule per stage (what to plant when)
- In-ground vs raised bed variants

## Impact
- Affected code: `api/app/grows/grow_type_configs/outdoor_soil.py` (new), `__init__.py` (register)
- Affected specs: `grow-type-configs`
- Related change: `add-outdoor-soil-experience` (covers full outdoor module API/frontend — 129 tasks)
