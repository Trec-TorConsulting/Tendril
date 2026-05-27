## 1. Database & Migrations

- [x] 1.1 Create Alembic migration: `plot_grids` table
- [x] 1.2 Create Alembic migration: `plot_cells` table with unique(grid_id, row, col)
- [x] 1.3 Create Alembic migration: `soil_tests` table
- [x] 1.4 Create Alembic migration: `soil_amendments` table
- [x] 1.5 Create Alembic migration: `pest_scout_entries` table
- [x] 1.6 Create Alembic migration: `weather_logs` table
- [x] 1.7 Create Alembic migration: `harvest_yields` table
- [x] 1.8 Alter `buckets` table: add `grid_row`, `grid_col`, `plant_spacing_in`, `companion_plants`, `sun_zone`, `planting_method`, `transplant_date` (all nullable)
- [x] 1.9 Add RLS policies to all new tables (tenant_id based)
- [x] 1.10 Create SQLAlchemy models for all new tables in `tenants/models.py`
- [x] 1.11 Update Bucket model with new nullable columns

## 2. API — Plot Grid

- [x] 2.1 Create `api/app/outdoor/` module with `__init__.py`
- [x] 2.2 Plot grid routes: `PUT /grows/{id}/plot` (create/update grid)
- [x] 2.3 Plot grid routes: `GET /grows/{id}/plot` (get grid with cells)
- [x] 2.4 Plot grid routes: `PATCH /grows/{id}/plot/cells` (batch cell update)
- [x] 2.5 Plot grid routes: `DELETE /grows/{id}/plot` (remove grid)
- [x] 2.6 Pydantic schemas for PlotGrid and PlotCell requests/responses
- [x] 2.7 Mount outdoor router in `main.py`

## 3. API — Soil Health

- [x] 3.1 Soil test routes: `POST /grows/{id}/soil-tests` (log test)
- [x] 3.2 Soil test routes: `GET /grows/{id}/soil-tests` (list tests)
- [x] 3.3 Soil test routes: `GET /grows/{id}/soil-tests/latest` (most recent)
- [x] 3.4 Soil test routes: `DELETE /grows/{id}/soil-tests/{test_id}`
- [x] 3.5 Soil amendment routes: `POST /grows/{id}/amendments` (log amendment)
- [x] 3.6 Soil amendment routes: `GET /grows/{id}/amendments` (list)
- [x] 3.7 Soil amendment routes: `DELETE /grows/{id}/amendments/{id}`
- [x] 3.8 Pydantic schemas for SoilTest and SoilAmendment

## 4. API — Pest Scouting

- [x] 4.1 Pest scout routes: `POST /grows/{id}/pest-scouts` (log observation)
- [x] 4.2 Pest scout routes: `GET /grows/{id}/pest-scouts` (list, filterable)
- [x] 4.3 Pest scout routes: `DELETE /grows/{id}/pest-scouts/{id}`
- [x] 4.4 Pydantic schemas for PestScoutEntry

## 5. API — Weather & Intelligence

- [x] 5.1 Weather routes: `GET /tents/{id}/weather/current` (proxy OpenWeather)
- [x] 5.2 Weather routes: `GET /tents/{id}/weather/forecast` (7-day)
- [x] 5.3 Weather routes: `GET /tents/{id}/weather/history` (stored logs)
- [x] 5.4 Weather routes: `POST /tents/{id}/weather/manual` (rain gauge, etc.)
- [x] 5.5 GDD routes: `GET /grows/{id}/gdd` (accumulated growing degree days)
- [x] 5.6 Frost date routes: `GET /tents/{id}/weather/frost-dates`
- [x] 5.7 Moon phase routes: `GET /tents/{id}/weather/moon`
- [x] 5.8 Pydantic schemas for weather data

## 6. API — Companion Plants

- [x] 6.1 Create `api/app/outdoor/companions.py` with built-in companion database
- [x] 6.2 Routes: `GET /companion-plants` (full database)
- [x] 6.3 Routes: `GET /companion-plants/check` (compatibility check)
- [x] 6.4 Routes: `GET /companion-plants/suggest` (suggestions for a plant)

## 7. API — Harvest Yields

- [x] 7.1 Yield routes: `POST /grows/{id}/yields` (log harvest)
- [x] 7.2 Yield routes: `GET /grows/{id}/yields` (list)
- [x] 7.3 Yield routes: `GET /grows/{id}/yields/summary` (aggregated stats)
- [x] 7.4 Yield routes: `GET /grows/{id}/yields/seasons` (multi-season comparison)
- [x] 7.5 Pydantic schemas for HarvestYield

## 8. Scheduler Enhancements

- [x] 8.1 Daily weather log job: fetch and store OpenWeather data for outdoor tents
- [x] 8.2 Daily GDD accumulation job: calculate and store per grow
- [x] 8.3 Frost alert job: check forecast, send push notification if <32°F
- [x] 8.4 Rain-skip logic: suppress watering tasks when rain forecast >0.5"
- [x] 8.5 Moon phase daily update
- [x] 8.6 Add outdoor-specific tasks to `task_generator.py` (soil test, pest scout, companion check, harvest window)

## 9. Frontend — Plot Designer

- [x] 9.1 Create `components/outdoor/plot-designer.tsx` — interactive CSS Grid layout
- [x] 9.2 Cell click handler: modal to assign type (plant, companion, sensor, path, irrigation)
- [x] 9.3 Plant assignment: strain picker, creates bucket linked to cell
- [x] 9.4 Companion plant picker with compatibility indicators
- [x] 9.5 Sensor device picker: assign device to grid zone
- [x] 9.6 Drag-to-select for bulk cell operations
- [x] 9.7 Grid legend and color coding
- [x] 9.8 Zoom/pan controls for large plots
- [x] 9.9 Mobile touch support (tap to select, pinch to zoom)
- [x] 9.10 Print/export garden map layout

## 10. Frontend — Soil Dashboard

- [x] 10.1 Create `components/outdoor/soil-dashboard.tsx`
- [x] 10.2 Soil test entry form (pH, NPK, organic matter, CEC, micros)
- [x] 10.3 Soil health trend charts (Recharts: pH, NPK over time)
- [x] 10.4 Amendment timeline (visual log with type icons)
- [x] 10.5 Amendment entry form (type, product, quantity, area, cost)
- [x] 10.6 Soil health score card (calculated from latest test)
- [x] 10.7 Recommendation engine: suggest amendments based on test results

## 11. Frontend — Outdoor Intelligence

- [x] 11.1 Create `components/outdoor/intelligence.tsx` — composite dashboard
- [x] 11.2 GDD progress bar with strain maturity target
- [x] 11.3 Frost risk indicator and frost date display
- [x] 11.4 Rain accumulator (weekly/monthly totals, chart)
- [x] 11.5 Manual rain gauge entry button
- [x] 11.6 Sun hours tracker per zone
- [x] 11.7 Moon phase display with calendar
- [x] 11.8 Wind exposure summary
- [x] 11.9 Hardiness zone badge (auto from lat/lng)

## 12. Frontend — Pest Scout

- [x] 12.1 Create `components/outdoor/pest-scout.tsx`
- [x] 12.2 New observation form (type, species, severity, photo upload, grid location)
- [x] 12.3 Scout log list with severity badges and photos
- [x] 12.4 Treatment log entry (type, product, re-entry interval)
- [x] 12.5 Beneficial insect tracking section
- [x] 12.6 IPM recommendations based on observations

## 13. Frontend — Harvest & Yields

- [x] 13.1 Create `components/outdoor/harvest-tracker.tsx`
- [x] 13.2 Per-plant harvest entry form (wet/dry/trim weight, quality, trichome stage)
- [x] 13.3 Yield totals dashboard (total, per-plant avg, per-sqft)
- [x] 13.4 Season-over-season comparison chart
- [x] 13.5 Cost/ROI calculator (inputs vs. yield value)

## 14. Frontend — Season Timeline

- [x] 14.1 Create `components/outdoor/season-timeline.tsx`
- [x] 14.2 Gantt-style horizontal timeline with stage bars
- [x] 14.3 Milestone markers (actual vs. expected)
- [x] 14.4 Weather event overlay (frost, rain, heatwave markers)
- [x] 14.5 GDD progression line overlay
- [x] 14.6 Season comparison mode (side-by-side)

## 15. Frontend — Irrigation Planner

- [x] 15.1 Create `components/outdoor/irrigation-planner.tsx`
- [x] 15.2 Zone definition overlay on plot grid
- [x] 15.3 Sensor-to-zone linking
- [x] 15.4 Water usage tracking dashboard
- [x] 15.5 Soil moisture history chart with optimal range bands

## 16. Frontend — Tab Integration

- [x] 16.1 Replace "Buckets" tab with "Garden Plot" when grow_type is outdoor_soil
- [x] 16.2 Add "Soil Health" tab for outdoor_soil grows
- [x] 16.3 Add "Field Scout" tab for outdoor_soil grows
- [x] 16.4 Add "Intelligence" tab (weather/GDD/frost/moon) for outdoor_soil grows
- [x] 16.5 Add "Irrigation" tab for outdoor_soil grows
- [x] 16.6 Enhance "Harvest" tab with yield tracker for outdoor_soil
- [x] 16.7 Add "Season" tab with timeline for outdoor_soil grows

## 17. Terminology Engine

- [x] 17.1 Create `lib/terminology.ts` utility that maps default terms → grow-type-specific terms
- [x] 17.2 Update grow detail page to use terminology engine for all labels
- [x] 17.3 Update empty states and placeholder text to use outdoor vocabulary
- [x] 17.4 Update bucket creation dialog to use outdoor terms when applicable

## 18. Grow Type Profile Update

- [x] 18.1 Extend `outdoor_soil` profile in `grow_types.py`: add new automations, update unique_fields
- [x] 18.2 Add GDD base temperatures per strain category
- [x] 18.3 Add hardiness zone lookup utility

## 19. Testing

- [x] 19.1 API tests: plot grid CRUD
- [x] 19.2 API tests: soil test and amendment CRUD
- [x] 19.3 API tests: pest scout CRUD
- [x] 19.4 API tests: weather routes
- [x] 19.5 API tests: companion plant compatibility
- [x] 19.6 API tests: harvest yield CRUD and analytics
- [x] 19.7 Frontend tests: plot designer interactions
- [x] 19.8 Frontend tests: soil dashboard rendering
- [x] 19.9 Frontend tests: terminology engine

## 20. Build & Deploy

- [x] 20.1 Run Alembic migration on cluster
- [x] 20.2 Build and push tendril-api image
- [x] 20.3 Build and push tendril-web image
- [x] 20.4 Rolling restart API + web deployments
- [x] 20.5 Verify outdoor soil grow flow end-to-end
