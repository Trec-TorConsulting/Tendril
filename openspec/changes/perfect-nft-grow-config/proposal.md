# Change: Perfect NFT (Nutrient Film Technique) Grow Configuration

## Why
NFT is fundamentally different from reservoir-based hydro. Plants grow in sloped channels with a thin, continuously flowing nutrient film. The defining characteristic is **zero buffer time** — pump failure means roots dry in minutes, making system reliability and redundancy the #1 concern. Unique requirements include channel slope engineering, root mat management (roots can block flow), and multi-channel balancing. No stage-by-stage config exists yet.

## What Changes

### Core NFT-Specific Sections
- **Channel engineering** — Slope angle (1:30 to 1:40 recommended), channel width by plant size, channel material (PVC, corrugated, commercial NFT rail), length limits (salt accumulation at end), optimal plant spacing per channel
- **Flow rate management** — Thin film target (2-4mm depth), flow rate per channel (1-2 L/min), return to reservoir engineering, pump sizing for multi-channel, flow uniformity verification
- **Root mat management** — Root mass blocking flow (the #1 NFT-specific problem), channel cleaning between grows, root training to prevent blockage, signs of flow restriction, when to trim roots
- **Pump failure protocol** — NFT's critical vulnerability. Roots dry in 2-5 minutes without flow. Backup pump requirements, battery backup for pump, alarm system, response time SLA
- **Salt accumulation** — Plants at end of channel receive higher EC (nutrients concentrate along the channel). Channel length limits, flushing schedule, bi-directional flow option, EC monitoring at inlet vs outlet
- **Propagation-to-channel transfer** — Seedlings started in rockwool cubes, transferred to channel when root system is established. Timing, technique, spacing considerations
- **Commercial NFT systems** — Multi-tier vertical NFT, A-frame NFT, automated planting/harvesting systems, conveyor NFT

### Stage-by-Stage Config (NFT_STAGES)
- 12 stages with NFT-specific reservoir/flow parameters per stage
- Propagation phase (seedlings in rockwool cubes before channel placement)
- Channel placement timing and technique
- Flow rate adjustments through growth stages (increase as root mass grows)

### Equipment, Troubleshooting, Quick Reference
- NFT-specific equipment (channels, end caps, reservoir, pump with backup, flow restrictors, slope leveling tools)
- Troubleshooting: Flow Issues, Root Blockage, Salt Buildup, Pump Failure, Channel Leaks
- Quick reference with flow rate tables and channel sizing

## Impact
- Affected code: `api/app/grows/grow_type_configs/nft.py` (new), `__init__.py` (register)
- Affected specs: `grow-type-configs`
