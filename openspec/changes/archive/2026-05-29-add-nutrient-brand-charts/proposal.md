# Change: Add Nutrient Brand Feed Charts

## Why
Every nutrient brand publishes feeding schedules for their product lines. New growers constantly ask "what week X looks like for Brand Y". Pre-built charts let Tendril AI give brand-specific feeding advice like "For Fox Farm Ocean Forest in Week 3, use Big Bloom at 15ml/gal + Grow Big at 10ml/gal".

## What Changes
- Seed database with feed charts for top 10 nutrient brands
- API endpoint to list available brands and their charts
- AI context includes active brand chart when generating feeding advice
- Users can select a nutrient brand per grow

## Impact
- Affected specs: `integrations-framework`
- Depends on: existing feeding/grow models (no external API needed)
- No breaking changes

## Brands to Include (Initial)
1. **Fox Farm** — Trio (Grow Big, Big Bloom, Tiger Bloom) + Dirty Dozen
2. **General Hydroponics** — Flora Series (Micro, Gro, Bloom) + FloraNova
3. **Advanced Nutrients** — pH Perfect Sensi Grow/Bloom, Big Bud, Overdrive
4. **Botanicare** — Pure Blend Pro, Cal-Mag Plus
5. **Canna** — Terra, Coco, Aqua lines
6. **Athena** — Pro Line (Core, Bloom, Fade, CleansE)
7. **Jack's** — 321 (3-2-1 formula)
8. **Nectar for the Gods** — Roman regiment (Herculean, Medusa's, Zeus)
9. **Emerald Harvest** — Grow, Micro, Bloom + Cal-Mag
10. **Mills** — Basis A+B, Start, C4, Ultimate PK

## Data Source
- Manually transcribed from manufacturer PDF feed charts
- No API needed — static data seeded into DB
- Effort: LOW (data entry, no code complexity)
