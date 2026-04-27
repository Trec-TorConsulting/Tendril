# Change: Add Premium Outdoor Soil Growing Experience

## Why
Outdoor soil growers have fundamentally different workflows than indoor hydro growers. The current "bucket" paradigm was designed for DWC/hydro setups and doesn't map to outdoor growing. Outdoor growers need garden bed layouts, planting maps, weather integration, soil health tracking, companion planting, and harvest forecasting — not reservoir management. This redesign gives outdoor soil the same first-class treatment that indoor hydro already has.

## What Changes

### New: Garden Plot Designer (Interactive Grid)
- Visual drag-and-drop garden bed layout editor
- Users create beds/raised-beds on a 2D plot grid (rows × columns)
- Each cell can hold a plant/strain, companion plant, or be marked empty/path
- Sensor devices are placed on the grid so users see which sensor covers which zone
- Plant spacing recommendations based on strain metadata
- Exportable/printable garden map

### New: Soil Health Dashboard
- Soil test log: pH, N-P-K, organic matter %, CEC, calcium, magnesium, sulfur
- Soil amendment tracker with application history and calendar reminders
- Cover crop planner (off-season soil regeneration)
- Soil temperature monitoring with planting-readiness indicators
- Composting tracker (batch age, temperature, turn schedule)

### New: Outdoor Intelligence Suite
- **Sun Map**: Track daily sun hours per zone (manual + calculated from lat/lng + date)
- **Frost Calendar**: First/last frost dates based on location, freeze alerts from weather API
- **Rain Tracker**: Cumulative rainfall log (auto from weather + manual gauge readings)
- **Wind Exposure**: Wind speed/direction tracking for windbreak planning
- **Moon Phase Calendar**: Lunar planting guidance (biodynamic support)
- **Growing Degree Days (GDD)**: Accumulated heat units for maturity prediction
- **Hardiness Zone**: Auto-detect from lat/lng, recommend compatible strains

### New: Companion Planting System
- Built-in companion planting database (beneficial/harmful pairings)
- Visual indicators on plot grid (green = good neighbor, red = bad neighbor)
- Auto-suggest companions based on planted strains
- Pest-deterrent plant recommendations

### New: Pest & Disease Field Scout
- Visual pest/disease identification guide with photos
- Field scout log: GPS-tagged observations with photo upload
- IPM (Integrated Pest Management) action tracker
- Beneficial insect tracking (ladybugs, predator mites, etc.)
- Treatment application log with re-entry intervals

### New: Harvest Forecasting & Yield Tracking
- Growing Degree Day model for maturity estimation
- Per-plant yield logging (wet weight, dry weight, trim weight)
- Yield-per-square-foot analytics across seasons
- Harvest window calculator based on trichome stage + weather forecast
- Season-over-season comparison dashboards
- Cost tracking (inputs vs. yield for ROI calculation)

### New: Irrigation Planner
- Drip/soaker layout mapped to plot grid
- Smart irrigation skip when rain forecast exceeds threshold
- Watering zone management (sensors per zone)
- Soil moisture history with optimal range overlays
- Water usage tracking and efficiency metrics

### New: Season Planner & Timeline
- Visual Gantt-style timeline: germination → transplant → veg → flower → harvest
- Succession planting scheduler
- Task automation tied to growth stage transitions
- Historical season comparison (this year vs. last year)
- Printable season calendar export

### Modified: Terminology Engine
- When `grow_type` is `outdoor_soil`, replace "Bucket" → "Plant/Bed", "Tent" → "Garden", "Position" → "Plot Location"
- UI labels, empty states, and help text adapt to outdoor vocabulary

### Modified: Bucket Model → Plant/Bed Model
- For outdoor_soil grows, "buckets" represent individual plants or bed sections
- Add fields: `grid_row`, `grid_col`, `plant_spacing_in`, `companion_plants`, `sun_zone`
- Position becomes grid coordinates instead of sequential number

## Impact
- Affected specs: `bucket-monitoring`, `environment-monitoring`, `grow-assistant-core`
- New spec: `outdoor-soil-experience`
- Affected code:
  - **API**: New routes for plot grid, soil tests, companion planting, pest scouting, irrigation, GDD calculations
  - **Models**: Extended Bucket model, new SoilTest/CompanionPlant/PestScout/IrrigationZone models
  - **Frontend**: New plot designer component, soil dashboard, outdoor intelligence tabs, pest scout UI
  - **Scheduler**: Frost alerts, rain-skip logic, GDD accumulation, moon phase tasks
  - **MQTT Worker**: Soil sensor data enrichment with zone context
  - **Grow Type Profile**: Extended outdoor_soil unique_fields and automations
