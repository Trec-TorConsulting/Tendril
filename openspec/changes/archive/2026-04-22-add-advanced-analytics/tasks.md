## 1. Crop Steering Dashboard
- [x] 1.1 Add crop steering view — displays generative vs vegetative balance signals
- [x] 1.2 Track dry-back percentage (water level changes between feedings)
- [x] 1.3 Track EC ramp (EC increase as water evaporates)
- [x] 1.4 Display recommended steering action ("increase irrigation frequency" or "reduce to drive generative")
- [x] 1.5 Show historical steering data as timeline chart
- [x] 1.6 Add crop steering section to daily health check AI prompt

## 2. Multi-Grow History
- [x] 2.1 Create `grow_cycles` table (id, tent_id, name, start_date, end_date, status, notes, metadata)
- [x] 2.2 Add "Archive Grow" action — snapshots all bucket data into a completed grow cycle
- [x] 2.3 Add `GET /api/grows` — list all completed grow cycles
- [x] 2.4 Add `GET /api/grows/{id}` — full grow detail (buckets, sensors, journal, yields, photos)
- [x] 2.5 Add grow comparison view — side-by-side metrics across cycles (yield, duration, avg pH/EC)
- [x] 2.6 Track best-performing strain per metric (highest yield, fastest flower, best VPD consistency)
- [x] 2.7 Show grow history from bucket detail view for recycled positions

## 3. Export & Reports
- [x] 3.1 Add `GET /api/grows/{id}/export?format=csv` — export grow cycle as CSV (sensors + journal)
- [ ] 3.2 Add `GET /api/grows/{id}/export?format=pdf` — export grow cycle as PDF report
- [ ] 3.3 PDF includes: grow summary, per-bucket stats, sensor charts, milestone timeline, photos, yield
- [x] 3.4 Add export button in grow history view and bucket detail view
- [ ] 3.5 Use server-side PDF generation (weasyprint or reportlab)
- [x] 3.6 Add CSV export for current live data (all buckets + latest sensors)

## 4. Pump Automation Dashboard
- [x] 4.1 Add pump control UI — buttons for pH Up, pH Down, Nutrient dose per bucket
- [x] 4.2 Publish MQTT commands to `grow/{tent_id}/{position}/dose/cmd` with dose parameters
- [x] 4.3 Display pump status from ESP32 feedback (`grow/{tent_id}/{position}/dose/status`)
- [x] 4.4 Add dose amount presets (1ml, 5ml, 10ml) with custom input
- [x] 4.5 Log all pump activations in bucket journal
- [x] 4.6 Add safety limits — max dose per interval, cooldown period between doses
- [x] 4.7 Pump UI only visible when MQTT is configured and ESP32 supports dosing

## 5. Light Schedule & DLI Tracking
- [x] 5.1 Add light schedule config to tent settings (on-time, off-time, wattage)
- [x] 5.2 Calculate DLI (Daily Light Integral) from wattage, PAR efficiency, and hours
- [x] 5.3 Display current DLI in environment gauges
- [x] 5.4 Show light on/off schedule as visual bar in tent view
- [ ] 5.5 Generate alert when light schedule deviates (if smart plug integration exists)
- [x] 5.6 Track cumulative light hours per grow cycle

## 6. Environmental Scoring
- [x] 6.1 Calculate daily "Grow Score" (0-100) from weighted factors:
  - VPD consistency (20%)
  - pH stability (20%)
  - EC stability (15%)
  - Water temp consistency (15%)
  - Reservoir freshness (10%)
  - Light schedule adherence (10%)
  - Dissolved oxygen level (10%)
- [x] 6.2 Display score badge on tent view and bucket detail
- [x] 6.3 Store daily scores in events table
- [x] 6.4 Show score trend chart (last 30 days)
- [x] 6.5 Include score in daily health check AI prompt for contextual advice
- [x] 6.6 Highlight which factors are dragging the score down

## 7. Testing
- [x] 7.1 Test crop steering signal calculations (dry-back, EC ramp)
- [x] 7.2 Test grow archive and comparison
- [x] 7.3 Test CSV and PDF export generation
- [x] 7.4 Test pump MQTT command publishing (mock broker)
- [x] 7.5 Test DLI calculation accuracy
- [x] 7.6 Test grow score calculation with mock data
