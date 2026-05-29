# Change: Perfect Kratky (Passive Hydro) Grow Configuration

## Why
Kratky already has a 1340-line config — the second most complete after DWC. However, like DWC, it needs the same enhancements: scale profiles, auto/photo differentiation, water source handling, monitoring thresholds, and advanced technique sections. Additionally, Kratky has unique concepts that need deeper coverage: **Modified Kratky** (top-offs for cannabis — deviates from pure Kratky), **container selection** (opaque, sealed, proper sizing is critical since there's no reservoir change), **air root vs water root zone management**, and **the progression from pure passive to modified approach for cannabis**.

## What Changes

### Kratky-Specific Enhancements (what makes Kratky unique)
- **Pure Kratky vs Modified Kratky** — Pure: fill once, never touch. Modified: strategic top-offs when water level drops critically. Cannabis almost always needs Modified Kratky. Detailed decision guide on when to top off, how much, and what concentration
- **Container selection deep dive** — Container material (food-safe plastic, painted mason jars, 5-gal buckets), color (MUST be opaque — #1 failure is algae from light), seal quality (lid must be tight), sizing by plant size (undersized = early depletion, oversized = waste). Container-to-plant sizing calculator
- **Air root zone management** — The fundamental Kratky mechanism. Water roots absorb nutrients, air roots absorb oxygen. The air gap GROWS as the plant drinks. Illustrated progression of water level through a grow. Why overfilling kills: it drowns the air roots. Visual guide to healthy air gap progression
- **Top-off protocol (Modified Kratky)** — When to top off (water level below 25% of original), what concentration (half-strength nutrients), how high to fill (NEVER above the air root line — only to bottom of water roots), frequency expectations by stage
- **EC/pH drift management** — In Kratky, you can't do reservoir changes. pH naturally drifts up, EC drops as plant consumes. Acceptable drift ranges by stage. When drift indicates a problem vs normal behavior. Emergency intervention thresholds
- **Nutrient front-loading** — Since you can't easily change nutrients, initial mix is critical. Higher starting EC than DWC. Slow-release nutrient options. Nutrient ratio adjustments for Kratky (more CalMag upfront)
- **Multiple container management** — Running many Kratky containers (common at scale). Individual tracking importance (each container is its own ecosystem). Stagger planting for continuous harvest

### Enhancements Matching DWC Gold Standard
- Scale profiles (single jar → grow room full of Kratky containers)
- Auto/photo differentiation (autos are ideal for Kratky due to shorter cycle)
- Water source profiles
- Monitoring thresholds
- Nutrient brand alternatives
- Harvest decision matrix
- Photo documentation protocol

## Impact
- Affected code: `api/app/grows/grow_type_configs/kratky.py` (modify), `api/app/grows/grow_types.py` (enhance profile)
- Affected specs: `grow-type-configs`
