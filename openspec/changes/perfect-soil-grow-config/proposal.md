# Change: Perfect Indoor Soil Grow Configuration

## Why
Indoor soil is the most beginner-friendly and most forgiving grow method, but it has deep complexity for advanced growers pursuing living soil, organic methods, and terroir. Its unique concerns are **wet/dry cycle management** (soil must dry between waterings — opposite of coco/hydro), **organic vs synthetic feeding** (two completely different nutrient approaches), **living soil biology** (mycorrhizae, beneficial bacteria, soil food web), **compost tea and top dressing** (slow-release organic amendment techniques), **pot sizing and root zone management** (root-bound plants, air pruning), and **pest management in the media** (fungus gnats, root aphids — soil-specific pests). No config exists yet.

## What Changes

### Core Soil-Specific Sections
- **Organic vs synthetic decision** — Two fundamentally different approaches: Organic/living soil (feed the soil, the soil feeds the plant — amendments, compost tea, top dressing, no pH adjustment needed if soil is healthy) vs Synthetic (feed the plant directly, pH adjustment required, faster response, less forgiving). Each gets its own nutrient schedule, pH management protocol, and feeding philosophy
- **Living soil deep dive** — Building a living soil: base recipe (peat/coco, comite, perlite, worm castings), amendments (kelp meal, bone meal, neem meal, glacial rock dust, gypsum), cover crop (clover, alfalfa), mulch layer, no-till method. Soil food web education: mycorrhizae, beneficial bacteria, protozoa, nematodes, fungi networks
- **Wet/dry cycle management** — THE fundamental soil skill. How to know when to water (pot weight method, finger test, moisture meter), why overwatering is the #1 beginner mistake, how soil structure affects drainage, watering technique (slow, even, around perimeter), water volume per pot size
- **Compost tea and top dressing** — Compost tea: aerobic vs anaerobic, brewing protocol (compost + molasses + air pump + 24-48h), application frequency and timing, what it adds (beneficial microbes, not nutrients). Top dressing: amendment application on soil surface, slow-release feeding, timing by stage, layering technique
- **Pot sizing and root management** — Soil needs larger pots than hydro (roots grow less efficiently). Sizing guide: autos (3-5 gal), photos (5-15 gal), mother plants (15-30 gal). Transplant shock prevention. Air pruning via fabric pots. Root-bound signs and intervention
- **Soil-specific pest management** — Fungus gnats (sand top layer, sticky traps, Mosquito Bits/BTI, neem drench), root aphids (systemic treatment, beneficial nematodes), thrips in soil (soil drench + foliar spray). Beneficial predators: predatory mites, rove beetles, nematodes
- **pH management in soil** — Organic: soil self-buffers if properly built (6.0-7.0 natural range, minimal pH adjustment needed). Synthetic: pH to 6.0-6.5 every watering. Why soil pH range is higher than hydro (nutrient availability chart differs in soil). Lime for pH up, sulfur for pH down (slow-acting soil amendments)
- **Super soil / water-only grows** — Pre-amended soil that requires only plain water throughout the grow. Recipe, layering technique (hot soil on bottom, lighter on top), how the plant roots "reach" for nutrients as they grow down

### Stage-by-Stage Config (SOIL_STAGES)
- 12 stages with DUAL feeding schedules (organic AND synthetic tracks)
- Wet/dry cycle guidance per stage (seedlings dry faster, large plants need more water)
- Top dressing and compost tea schedules for organic track
- Synthetic nutrient schedule with pH targets for synthetic track

## Impact
- Affected code: `api/app/grows/grow_type_configs/soil.py` (new), `__init__.py` (register)
- Affected specs: `grow-type-configs`
