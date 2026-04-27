## 1. Grow Diary Timeline
- [x] 1.1 Add diary view — week-by-week vertical timeline for each bucket (Week 1, Week 2, ...)
- [x] 1.2 Each week row shows: growth stage, sensor averages (pH/EC/temp), photos, journal entries
- [x] 1.3 Add `GET /api/buckets/{id}/diary` endpoint — aggregates sensor + journal + snapshots by week
- [x] 1.4 Allow adding diary notes per week with optional photo upload
- [x] 1.5 Show milestone badges on the timeline (germinated, transplanted, flipped to flower, harvest)
- [x] 1.6 Navigate to diary from bucket detail view

## 2. Strain Library
- [x] 2.1 Create `strains` table (id, name, breeder, genetics, flowering_weeks, expected_yield_g, thc_pct, cbd_pct, description, created_at)
- [x] 2.2 Add `POST /api/strains` — create strain entry
- [x] 2.3 Add `GET /api/strains` — list all strains (with search)
- [x] 2.4 Add `GET /api/strains/{id}` — strain detail
- [x] 2.5 Add `PUT /api/strains/{id}` — update strain
- [x] 2.6 Add `DELETE /api/strains/{id}` — delete strain
- [x] 2.7 Add strain picker dropdown in bucket edit modal (auto-populates flowering time, expected yield)
- [x] 2.8 Pre-seed library with 20 popular strains (optional, can be toggled off)
- [x] 2.9 Track which strains have been grown (link strain → bucket history)

## 3. Growth Stage Auto-Advance
- [x] 3.1 Analyze sensor patterns + days elapsed to suggest stage transitions
- [x] 3.2 Germination → Seedling: when first sensor reading appears or user confirms sprout
- [x] 3.3 Seedling → Veg: after 7-14 days from germination
- [x] 3.4 Veg → Flower: when light schedule changes (if tracked) or user-configured flip day
- [x] 3.5 Show suggestion notification: "Bucket A1 has been in Veg for 28 days — advance to Flower?"
- [x] 3.6 Add auto-advance toggle in tent settings (default: suggestions only, not automatic)
- [x] 3.7 Log stage changes in bucket journal

## 4. Feeding Schedule Templates
- [x] 4.1 Create `feeding_schedules` table (id, name, nutrient_line, stages: JSON array of weekly doses)
- [x] 4.2 Pre-build templates for General Hydroponics Flora (3-part), Fox Farm Trio, Advanced Nutrients pH Perfect
- [x] 4.3 Add `GET /api/feeding-schedules` — list templates
- [x] 4.4 Add `POST /api/feeding-schedules` — create custom schedule
- [x] 4.5 Assign feeding schedule to bucket — show "this week's feeding" in bucket detail
- [x] 4.6 Show nutrient amounts based on current week number (from germ date)
- [ ] 4.7 Allow editing schedule amounts inline

## 5. Photo Comparison
- [x] 5.1 Add `GET /api/buckets/{id}/photos` — returns stored snapshots with timestamps
- [x] 5.2 Add photo compare UI — side-by-side slider with date selectors
- [x] 5.3 Pull photos from health check snapshots (already stored in health_snapshots table)
- [x] 5.4 Allow manual photo upload for a bucket (stored in DB or filesystem)
- [x] 5.5 Show "1 week ago vs today" quick compare button in bucket detail

## 6. Testing
- [x] 6.1 Test diary aggregation (weekly grouping of journal + sensors)
- [x] 6.2 Test strain CRUD and picker integration
- [x] 6.3 Test stage auto-advance suggestions
- [x] 6.4 Test feeding schedule template rendering per week
- [x] 6.5 Test photo comparison UI with mock images
