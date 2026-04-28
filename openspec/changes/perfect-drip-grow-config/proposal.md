# Change: Perfect Drip / Top Feed Grow Configuration

## Why
Drip/Top Feed is the commercial indoor workhorse — the most common system in licensed cannabis facilities. Its unique concerns are **emitter management** (clog detection, uniform distribution), **runoff ratio monitoring** (10-20% runoff target, input EC vs runoff EC delta as the primary health indicator), **drain-to-waste vs recirculating** decision (DTW simpler but wasteful, recirc saves water but risks pathogen buildup), **media-dependent irrigation scheduling** (coco, rockwool, perlite, or mixed — each requires different frequency, volume, and dryback targets), and **crop steering via irrigation strategy** (generative vs vegetative steering through shot timing and dryback %). No config exists yet.

## What Changes

### Core Drip-Specific Sections
- **Emitter management** — Emitter types (drip stakes, drip rings, blumats, pressure-compensating), clog detection methods, cleaning protocol (H2O2 flush, acid wash), flow rate verification per emitter, spare emitter strategy
- **Runoff management** — The primary diagnostic tool in drip. Input EC vs runoff EC delta interpretation (runoff EC much higher = salt buildup, need flush; runoff EC lower = plant is hungry). Target runoff percentage (10-20%). Runoff pH vs input pH interpretation. Drain-to-waste collection and disposal
- **Drain-to-waste vs recirculating** — Full decision guide: DTW (simpler, no pathogen risk, more waste, higher water/nutrient cost) vs recirculating (saves 30-40% water, requires UV/ozone sterilization, pathogen risk, EC/pH management more complex). System requirements for each
- **Media-specific irrigation profiles** — Coco (high frequency, never dry, CalMag), rockwool (precision shots, dryback steering), perlite (fast drain, frequent irrigation), mixed media blends. Each gets its own irrigation schedule by stage
- **Crop steering** — Advanced technique unique to drip/rockwool. Generative steering (larger dryback, higher EC, stress signals to push flowering/ripening) vs vegetative steering (lower dryback, lower EC, more frequent irrigations to push growth). Shot timing, volume, and dryback % targets by strategy
- **Irrigation scheduling** — First shot timing (when substrate EC starts rising = plant is transpiring), last shot timing (allow adequate dryback before lights off), shot count ramp through stages, P1-P2-P3 shot strategies (first irrigations restore overnight dryback, mid-day maintains, late shots set up for morning)
- **Scale considerations** — Hand watering (1-10 plants), simple timer + manifold (10-50), commercial controller with substrate sensors (50+), fully automated precision irrigation systems

### Stage-by-Stage Config (DRIP_STAGES)
- 12 stages with media-specific irrigation schedules
- Runoff monitoring targets per stage
- Crop steering phase-appropriate strategies (vegetative in veg, transition to generative in flower)

## Impact
- Affected code: `api/app/grows/grow_type_configs/drip.py` (new), `__init__.py` (register)
- Affected specs: `grow-type-configs`
