# Change: Perfect Coco Coir Grow Configuration

## Why
Coco coir is the bridge between hydro and soil — a soilless media that requires hydroponic-style nutrient management but with the physical growing experience of potted plants. Its defining characteristics are **mandatory CalMag supplementation** (coco's cation exchange sites lock out calcium/magnesium), **every watering is a feeding** (never plain water in coco), **high-frequency fertigation** (multiple times daily in flower), **dryback monitoring** (the primary steering tool), and **buffering/pre-treatment** requirements (raw coco must be rinsed and buffered before use). Coco is currently the fastest-growing method category in cannabis cultivation. No config exists yet.

## What Changes

### Core Coco-Specific Sections
- **CalMag science** — Why coco locks out Ca/Mg (cation exchange capacity), how to buffer new coco (soak in CalMag solution 24h), ongoing CalMag requirements (1-2 ml/gal at every feeding), symptoms of CalMag deficiency in coco (brown spots, stunted growth), LED lights increase demand, RO water makes it worse
- **Coco preparation and buffering** — New coco MUST be rinsed (remove salt, dust, shipping chemicals) and buffered (soak in CalMag + nutrient solution). Pre-buffered coco brands vs raw. Coco brick rehydration. Mixing ratios: straight coco vs coco/perlite (70/30 most common) vs coco/perlite/hydroton
- **Fertigation frequency** — The key to coco: more frequent = better (within reason). Seedlings (1x/day), early veg (1-2x/day), late veg (2-3x/day), flower (3-6x/day). The "feed until runoff" rule. Why high-frequency low-volume beats low-frequency high-volume
- **Dryback monitoring** — The primary crop steering tool in coco. Pot weight tracking (hand feel or scale). Target dryback %: vegetative (5-10%), generative/flower (10-20%). Never let coco dry completely (anaerobic conditions, salt concentration, hydrophobic surface)
- **Runoff management** — Input vs runoff EC as the #1 diagnostic. Target 10-20% runoff. Runoff EC interpretation: rising = salt accumulation (increase runoff % or flush), dropping = hungry plant (increase EC). pH stability in coco (coco is naturally pH-stable around 5.8-6.2)
- **Pot sizing and transplanting** — Start in small pots (solo cup), transplant to 1-gal, final pot (3-7 gal depending on plant size). Why fabric pots are preferred (air pruning). When to transplant (roots visible at drain holes). Transplant shock prevention in coco
- **Reuse and recycling** — Coco can be reused 2-3 grows if properly cleaned (enzyme treatment, re-buffer). Composting spent coco. Environmental sustainability angle

### Stage-by-Stage Config (COCO_STAGES)
- 12 stages with coco-specific fertigation frequency per stage
- Dryback targets per stage (vegetative vs generative steering)
- CalMag dosing per stage
- Pot-up schedule (transplant timing)

## Impact
- Affected code: `api/app/grows/grow_type_configs/coco.py` (new), `__init__.py` (register)
- Affected specs: `grow-type-configs`
