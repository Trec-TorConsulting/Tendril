# Outdoor Soil Experience — Technical Design

## Architecture Overview

The outdoor soil experience layers on top of the existing grow/bucket/tent architecture rather than replacing it. Outdoor-specific features are activated when `grow_type === "outdoor_soil"` and `tent.environment_type === "outdoor"`.

## Data Model Extensions

### PlotGrid (new table)
```
plot_grids
  id: UUID (PK)
  tenant_id: UUID (FK tenants, RLS)
  grow_cycle_id: UUID (FK grow_cycles, unique)
  rows: int (1-50)
  cols: int (1-50)
  cell_size_inches: int (default 12)
  orientation: str ("north"|"south"|"east"|"west")
  notes: text
  created_at, updated_at: timestamptz
```

### PlotCell (new table)
```
plot_cells
  id: UUID (PK)
  tenant_id: UUID (FK tenants, RLS)
  plot_grid_id: UUID (FK plot_grids)
  row: int
  col: int
  cell_type: str ("plant"|"companion"|"path"|"empty"|"sensor"|"irrigation")
  bucket_id: UUID (FK buckets, nullable) — links to plant
  companion_plant: str (nullable) — e.g., "basil", "marigold"
  device_id: str (nullable) — sensor placed here
  irrigation_zone: str (nullable)
  sun_zone: str ("full_sun"|"partial_sun"|"partial_shade"|"full_shade")
  notes: text
  UNIQUE(plot_grid_id, row, col)
```

### SoilTest (new table)
```
soil_tests
  id: UUID (PK)
  tenant_id: UUID (FK tenants, RLS)
  grow_cycle_id: UUID (FK grow_cycles)
  tested_at: timestamptz
  ph: float
  nitrogen_ppm: float
  phosphorus_ppm: float
  potassium_ppm: float
  organic_matter_pct: float
  cec: float (cation exchange capacity)
  calcium_ppm: float
  magnesium_ppm: float
  sulfur_ppm: float
  notes: text
  source: str ("lab"|"home_kit"|"sensor")
```

### SoilAmendment (new table)
```
soil_amendments
  id: UUID (PK)
  tenant_id: UUID (FK tenants, RLS)
  grow_cycle_id: UUID (FK grow_cycles)
  applied_at: timestamptz
  amendment_type: str ("compost"|"worm_castings"|"bone_meal"|"blood_meal"|"kelp"|"lime"|"sulfur"|"gypsum"|"cover_crop"|"mulch"|"custom")
  product_name: str
  quantity: str (e.g., "2 cups per plant", "1 inch top dress")
  area_applied: str (nullable, e.g., "beds 1-3")
  cost: float (nullable)
  notes: text
```

### PestScoutEntry (new table)
```
pest_scout_entries
  id: UUID (PK)
  tenant_id: UUID (FK tenants, RLS)
  grow_cycle_id: UUID (FK grow_cycles)
  scouted_at: timestamptz
  pest_type: str ("insect"|"disease"|"animal"|"beneficial"|"unknown")
  species: str (e.g., "aphid", "powdery_mildew", "deer")
  severity: str ("low"|"medium"|"high"|"critical")
  grid_row: int (nullable) — where spotted
  grid_col: int (nullable)
  photo_url: str (nullable)
  treatment_applied: str (nullable)
  treatment_type: str ("organic"|"synthetic"|"biological"|"physical"|"none")
  notes: text
```

### WeatherLog (new table)
```
weather_logs
  id: UUID (PK)
  tenant_id: UUID (FK tenants, RLS)
  tent_id: UUID (FK tents)
  logged_at: timestamptz
  source: str ("api"|"manual"|"sensor")
  temp_high_f: float
  temp_low_f: float
  rainfall_in: float
  humidity_pct: float
  wind_speed_mph: float
  wind_direction: str
  uv_index: float
  gdd_contribution: float (calculated)
  notes: text
```

### HarvestYield (new table)
```
harvest_yields
  id: UUID (PK)
  tenant_id: UUID (FK tenants, RLS)
  bucket_id: UUID (FK buckets) — per-plant
  harvested_at: timestamptz
  wet_weight_oz: float
  dry_weight_oz: float
  trim_weight_oz: float
  quality_rating: int (1-10)
  trichome_stage: str ("clear"|"cloudy"|"amber"|"mixed")
  notes: text
```

### Extend Existing Bucket Model
Add nullable columns for outdoor grid placement:
```
buckets (ALTER)
  grid_row: int (nullable)
  grid_col: int (nullable)
  plant_spacing_in: int (nullable)
  companion_plants: jsonb (nullable) — ["basil", "marigold"]
  sun_zone: str (nullable)
  planting_method: str (nullable) — "direct_seed"|"transplant"|"clone"
  transplant_date: date (nullable)
```

## API Routes

### Plot Grid (`/v1/grows/{grow_id}/plot`)
- `GET` — Get plot grid with all cells
- `PUT` — Create or update grid dimensions
- `PATCH /cells` — Batch update cells (drag-and-drop saves)
- `DELETE` — Remove grid

### Soil Tests (`/v1/grows/{grow_id}/soil-tests`)
- `POST` — Log soil test
- `GET` — List tests (chronological)
- `GET /latest` — Most recent test
- `DELETE /{id}` — Remove test

### Soil Amendments (`/v1/grows/{grow_id}/amendments`)
- `POST` — Log amendment
- `GET` — List amendments
- `DELETE /{id}` — Remove

### Pest Scouting (`/v1/grows/{grow_id}/pest-scouts`)
- `POST` — Log scouting entry (with optional photo)
- `GET` — List entries (filterable by type/severity)
- `DELETE /{id}` — Remove

### Weather (`/v1/tents/{tent_id}/weather`)
- `GET /current` — Current conditions from OpenWeather API
- `GET /forecast` — 7-day forecast
- `GET /history` — Historical weather logs
- `POST /manual` — Manual weather/rain gauge entry
- `GET /gdd` — Growing Degree Days accumulator
- `GET /frost-dates` — First/last frost estimates
- `GET /moon` — Current moon phase + upcoming phases

### Harvest Yields (`/v1/grows/{grow_id}/yields`)
- `POST` — Log harvest
- `GET` — List all yields
- `GET /summary` — Aggregate stats (total yield, avg per plant, per sq ft)
- `GET /seasons` — Season-over-season comparison

### Companion Plants (`/v1/companion-plants`)
- `GET` — Full companion planting database
- `GET /check?plant=X&neighbor=Y` — Check compatibility
- `GET /suggest?plant=X` — Suggest good companions

## Frontend Components

### PlotDesigner (`components/outdoor/plot-designer.tsx`)
- CSS Grid-based interactive layout
- Click cell → assign plant, companion, sensor, path
- Drag to resize beds
- Color coding: green (plant), yellow (companion), gray (path), blue (sensor), cyan (irrigation)
- Companion compatibility overlay (green/red borders)
- Sensor coverage radius visualization
- Zoom/pan for large plots
- Mobile-friendly touch interactions

### SoilDashboard (`components/outdoor/soil-dashboard.tsx`)
- Soil test history chart (pH, NPK trends over time)
- Amendment timeline (visual log)
- Soil health score (calculated from latest test)
- Recommendations based on test results
- Next amendment reminder

### OutdoorIntelligence (`components/outdoor/intelligence.tsx`)
- Weather widget (current + 7-day)
- GDD progress bar (current vs. target for strain maturity)
- Frost risk indicator
- Rain accumulator (weekly/monthly)
- Sun hours tracker
- Moon phase display
- Hardiness zone badge

### PestScout (`components/outdoor/pest-scout.tsx`)
- Log new observation (photo + location on grid)
- Pest/disease identification cards
- IPM action recommendations
- Treatment log with reentry tracking

### HarvestTracker (`components/outdoor/harvest-tracker.tsx`)
- Per-plant yield entry
- Running totals dashboard
- Yield-per-sqft calculation
- Season comparison charts
- Cost/ROI calculator

### SeasonTimeline (`components/outdoor/season-timeline.tsx`)
- Gantt-style horizontal timeline
- Stage milestones with actual vs. expected dates
- Weather overlay (frost/rain events)
- GDD progression overlay

## Scheduler Enhancements

### New Scheduled Tasks
- **Daily weather log**: Fetch and store weather data from OpenWeather API
- **GDD accumulation**: Calculate daily GDD contribution → `(high + low) / 2 - base_temp`
- **Frost alert**: Check forecast for temps below 32°F → push notification
- **Rain skip**: When >0.5" rain forecast, suppress watering reminders
- **Moon phase update**: Calculate and cache lunar phase daily

### Task Generator Extensions
Add outdoor_soil-specific tasks to existing `task_generator.py`:
- Soil test reminder (every 30 days)
- Companion planting check (at transplant)
- Pest scouting reminder (every 3 days in veg/flower)
- Harvest window check (when GDD approaches target)

## Terminology Mapping

When `grow_type === "outdoor_soil"`, the UI adapts all labels:

| Default Term | Outdoor Soil Term |
|---|---|
| Bucket | Plant / Bed Section |
| Tent | Garden |
| Position | Plot Location |
| Volume (gallons) | Bed Size (sq ft) |
| Reservoir | Soil |
| Add Bucket | Add Plant |
| Buckets Tab | Garden Plot |

This is driven by the existing `terminology` field in the grow type profile.

## Migration Strategy
- New tables only (no existing table modifications that break backward compat)
- Bucket model extensions are all nullable columns (safe ALTER)
- Frontend conditionally renders outdoor components when `grow_type === "outdoor_soil"`
- Existing indoor grows are completely unaffected
