# Change: Perfect DWC (Deep Water Culture) Grow Configuration

## Why
DWC is the foundational grow type and the most actively used configuration. The existing 1262-line config covers 12 stages with environment variants, equipment, quick reference, and troubleshooting — but it was built for hobbyist-scale single-bucket setups. It lacks scale guidance (1 plant → commercial farm), autoflower vs photoperiod differentiation, water source handling, advanced techniques (crop steering, CO2, foliar), commercial compliance, and detailed monitoring threshold definitions for automation integration.

This is the gold-standard template that every other grow type config (Phases 2-12) will follow. Getting DWC perfect establishes the architecture, depth, and quality bar for all 12 grow types.

## What Changes

### Config Additions (grow_type_configs/dwc.py)
- **Scale profiles** — Solo bucket, small tent (2-8), multi-tent (9-24), commercial room (25-100+), warehouse scale (100+). Each scale tier defines: reservoir management strategy, monitoring approach, labor requirements, cost tracking, equipment differences
- **Photoperiod vs autoflower variants** — Stage durations, light schedules, training suitability, yield expectations, and schedule flexibility differences
- **Water source guidance** — RO water, tap water (chlorine/chloramine treatment), well water, softened water. Starting water chemistry targets and CalMag adjustment tables
- **Advanced techniques section** — CO2 supplementation (ppfd/CO2 correlation tables), crop steering (generative vs vegetative), foliar feeding schedule, beneficial microbe programs (Hydroguard + alternatives), silica supplementation timing
- **Monitoring thresholds** — Alert vs warning vs critical thresholds for every sensor reading, response time requirements, escalation rules. These connect directly to automation rules
- **Commercial compliance fields** — Batch tracking hooks, seed-to-sale integration points, testing requirements, regulatory fields, chain of custody
- **Harvest decision matrix** — Trichome ratios by desired effect (energetic/balanced/sedative), flush timing by plant condition, environmental manipulation for color/terpene enhancement
- **Post-harvest detail** — Drying room specs (60°F/60% humidity), cure schedules, Boveda vs Grove bag guidance, long-term storage
- **Photo logging guidance** — What to photograph at each stage, comparison photo timing, problem documentation protocol
- **Nutrient brand alternatives** — GH Flora Trio (current), plus FloraNova, MaxiGro/MaxiBloom, Jack's 321, Athena, Advanced Nutrients mappings

### Profile Additions (grow_types.py DWC entry)
- **scale_tiers** — Array of scale definitions with equipment, monitoring, and labor differences
- **strain_adjustments** — Auto vs photo differences in stage durations and nutrient strength
- **water_source_profiles** — RO, tap, well water starting points

### API Additions
- `GET /v1/grow-types/{id}/config?scale=commercial&strain_type=auto` — Optional query params to filter config for scale and strain type
- `GET /v1/grow-types/{id}/thresholds` — Alert/warning/critical thresholds for automation integration
- `GET /v1/grow-types/{id}/equipment?scale=small_tent` — Scale-filtered equipment list

### Test Coverage
- Unit tests for DWC config completeness (all stages present, all required fields populated)
- API tests for new query parameter filtering
- Threshold validation tests (warning < alert < critical)

## Impact
- Affected specs: `grow-type-configs` (new capability spec), `grow-assistant-core` (AI context enhancement)
- Affected code: `api/app/grows/grow_type_configs/dwc.py`, `api/app/grows/grow_types.py`, `api/app/grows/grow_type_routes.py`, `api/app/ai/context.py`
- No breaking changes — all additions are backwards-compatible
- Sets the architectural template for Phases 2-12 (RDWC, NFT, Ebb & Flow, Drip, Aeroponics, Kratky, Coco, Rockwool, Soil, Outdoor Soil, Outdoor Container)
