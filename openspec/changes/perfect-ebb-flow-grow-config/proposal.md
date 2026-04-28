# Change: Perfect Ebb & Flow (Flood and Drain) Grow Configuration

## Why
Ebb & Flow is the most versatile active hydro system — it works with many growing media (hydroton, rockwool, perlite, coco, even soil) and supports various container configurations (individual pots on a flood table, or media-filled flood trays). Its unique concerns are **flood/drain cycle optimization** (frequency and duration change by stage, media, and plant size), **tray engineering** (level surfaces, drainage, overflow prevention), **media selection** (each media changes flood frequency dramatically), and **timer reliability** (timer failure = either flooding or drought). No config exists yet.

## What Changes

### Core Ebb & Flow-Specific Sections
- **Flood cycle engineering** — Cycle frequency by stage AND media type (hydroton floods 4-6x/day, rockwool 2-3x/day, perlite 3-4x/day). Flood duration (time to fill + soak time). Drain time monitoring. Night cycle adjustments (reduce or skip floods)
- **Media selection guide** — Detailed comparison: hydroton (fast drain, frequent floods), rockwool cubes (high retention, fewer floods), perlite/vermiculite mix (moderate), coco in pots (high retention). Each media gets its own flood frequency table per stage
- **Tray engineering** — Level surface requirements (even 1/8" slope causes uneven flooding), tray sizing, overflow fitting height, drain fitting placement, flood height calculation (water level should reach 2/3 up the media but never touch stems)
- **Reservoir management** — Smaller relative to DWC (flood table drains back). Reservoir sizing by tray volume. pH/EC monitoring during drain-back (reading most accurate 30 min after last flood). Reservoir change schedule
- **Timer and pump configuration** — Mechanical vs digital timer selection, pump sizing per tray volume (fill time should be 5-10 minutes), backup timer, failsafe (what happens if timer sticks ON = overflow, if sticks OFF = drought)
- **Multi-tray configurations** — Multiple flood tables from single reservoir, manifold plumbing, sequential vs simultaneous flooding, pump sizing for multi-tray

### Stage-by-Stage Config (EBB_FLOW_STAGES)
- 12 stages with **media-specific flood cycle tables** per stage (the key differentiator)
- Flood frequency ramp: seedlings (1-2x/day) → late veg (4-6x/day) → flower (3-5x/day)
- Night cycle recommendations per stage

### Equipment, Troubleshooting, Quick Reference
- Equipment: flood trays, overflow/drain fittings, pump, timer, growing media options, individual pots or tray fill
- Troubleshooting: Flooding Issues, Drainage Problems, Timer Failures, Media-Specific Issues, Salt Buildup
- Quick reference: flood frequency by media × stage matrix, tray sizing table

## Impact
- Affected code: `api/app/grows/grow_type_configs/ebb_flow.py` (new), `__init__.py` (register)
- Affected specs: `grow-type-configs`
