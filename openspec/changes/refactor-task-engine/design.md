# Design: Refactor Task Engine

## Architecture

### Routine Grouping
Tasks are grouped into routines — logical bundles of related work that happen together:

| Routine | When | Typical Duration | Description |
|---------|------|-----------------|-------------|
| `morning` | Lights-on + 30 min (or 7 AM local) | 5-15 min | Quick visual, pH/EC, environment check |
| `evening` | Lights-off - 30 min (or 7 PM local) | 5 min | Temp check, spot issues, IPM spray timing |
| `weekly` | User-configured day (default: Saturday 9 AM) | 30-60 min | Reservoir change, deep clean, calibration |
| `biweekly` | Every 14 days | 15-30 min | Filter checks, amendment applications |
| `monthly` | 1st of month | 1-2 hrs | Equipment audit, carbon filter, air stones |
| `on_demand` | As needed (event-driven) | Varies | AI tasks, alert responses, stage transitions |

### Time-of-Day Awareness
Instead of hard-coding 9 AM UTC, the system uses:
1. **User timezone** from tenant settings (stored as `timezone` on tenant)
2. **Light schedule** from grow environment config (if available)
3. **Routine time mapping**: morning routine → lights_on + 30min; evening → lights_off - 30min
4. **Fallback**: 7 AM / 7 PM local time if no light schedule configured

### Grow-Type Task Accuracy Matrix

| Task | DWC | RDWC | NFT | Ebb/Flow | Drip | Aero | Kratky | Coco | Rockwool | Soil | Outdoor |
|------|-----|------|-----|----------|------|------|--------|------|----------|------|---------|
| pH check | 1x/day | 1x/day | 1x/day | 1x/day | 1x/day | 1x/day | 1x/week | 1x/day | 1x/day | 2x/week | 1x/week |
| EC check | 1x/day | 1x/day | 1x/day | 1x/day | 1x/day | 1x/day | 1x/week | 1x/day | 1x/day | N/A | N/A |
| Water temp | 1x/day | 1x/day | 1x/day | N/A | N/A | 1x/day | N/A | N/A | N/A | N/A | N/A |
| Reservoir change | 7 days | 7 days | 7 days | 7 days | 7 days | 5 days | Never* | N/A | N/A | N/A | N/A |
| Watering | N/A | N/A | N/A | Auto | Auto | Auto | N/A | 1-5x/day† | 2-6x/day† | Dry-back | Rain-dep |
| IPM spray | 3 days | 3 days | 3 days | 3 days | 3 days | 3 days | 7 days | 3 days | 3 days | 5 days | 5 days |
| Equipment check | 7 days | 7 days | 3 days‡ | 7 days | 7 days | 2 days‡ | N/A | 7 days | 7 days | N/A | N/A |
| Meter calibration | 14 days | 14 days | 14 days | 14 days | 14 days | 14 days | 30 days | 14 days | 14 days | 30 days | 30 days |

\* Kratky: top-off only when roots drying, never full change
† Coco/Rockwool: frequency increases with plant size and in flower
‡ NFT/Aero: pump/nozzle failure is lethal — more frequent checks

### Conditional Task Suppression
Tasks can be suppressed when automation handles them:

```python
AUTOMATION_SUPPRESSIONS = {
    "auto_ph_dosing": ["ph_check"],          # Auto-doser handles pH
    "auto_ec_dosing": ["ec_check"],          # Auto-doser handles EC
    "auto_irrigation": ["watering"],          # Timer/sensor handles watering
    "chiller_heater": ["water_temp"],         # Chiller maintains temp
    "inline_monitor": ["ph_check", "ec_check"],  # Continuous monitoring
}
```

When suppressed, a weekly "Verify automation" task replaces daily manual checks.

### Estimated Duration Per Task
Each template includes `estimated_minutes`:
- Quick checks (pH, EC, temp, visual): 2-3 min
- Inspections (roots, pests, trichomes): 5-10 min
- Maintenance (res change, flush & fill): 30-60 min
- Equipment (calibration, filter change): 15-30 min

### Progressive Disclosure
Task descriptions have two layers:
- `brief`: 1-2 sentence actionable checklist (shown by default)
- `detail`: Full educational context (shown on expand or first occurrence)

```python
{
    "brief": "Test pH → target 5.8-6.2. Adjust with pH Down if above 6.3.",
    "detail": "pH swings are the #1 issue in DWC. Roots submerged 24/7 means..."
}
```

### Database Changes (Additive)
Add two columns to `tasks` table:
- `routine: String(20) | None` — morning, evening, weekly, biweekly, monthly, on_demand
- `estimated_minutes: Integer | None` — estimated time to complete

### New Task Categories Added
- `ipm_spray` — Preventive pest management rotation
- `equipment_check` — Pump, fan, filter inspection
- `meter_calibration` — pH/EC probe calibration
- `photo_documentation` — Weekly progress photos
- `nutrient_prep` — Pre-mix nutrients before res change day
- `deep_clean` — Between-grow sanitization
- `carbon_filter` — Filter replacement reminder
- `air_stone` — Air stone replacement
- `light_check` — Light distance/intensity verification

## Implementation Strategy
1. Add migration for `routine` and `estimated_minutes` columns
2. Rewrite `TASK_TEMPLATES` with accurate intervals, routines, durations, and brief/detail descriptions
3. Update `generate_tasks_for_grow()` to use timezone-aware scheduling and routine grouping
4. Add automation suppression check
5. Update frontend to display routine badges and duration
6. Add new CATEGORY_LABELS for new categories
