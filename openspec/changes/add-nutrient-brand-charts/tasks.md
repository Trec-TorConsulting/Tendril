## 1. Data Model
- [ ] 1.1 Create `NutrientBrand` table (id, name, website, logo_url)
- [ ] 1.2 Create `NutrientProduct` table (id, brand_id, name, npk_ratio)
- [ ] 1.3 Create `FeedChart` table (id, brand_id, name, medium_type, grow_type)
- [ ] 1.4 Create `FeedChartWeek` table (id, chart_id, week_number, stage, products: JSON with ml_per_gal)
- [ ] 1.5 Create Alembic migration

## 2. Seed Data
- [ ] 2.1 Transcribe Fox Farm Trio chart
- [ ] 2.2 Transcribe General Hydroponics Flora Series chart
- [ ] 2.3 Transcribe Advanced Nutrients Sensi chart
- [ ] 2.4 Transcribe remaining 7 brands
- [ ] 2.5 Create seed script to load charts into DB

## 3. API
- [ ] 3.1 `GET /v1/nutrients/brands` — list available brands
- [ ] 3.2 `GET /v1/nutrients/brands/{id}/charts` — list charts for a brand
- [ ] 3.3 `GET /v1/nutrients/charts/{id}` — full chart with all weeks
- [ ] 3.4 Add brand/chart selection to grow model

## 4. AI Integration
- [ ] 4.1 Include active brand chart in AI feeding advice context
- [ ] 4.2 AI generates brand-specific product/dose recommendations

## 5. Frontend
- [ ] 5.1 Brand selector in grow settings
- [ ] 5.2 Feed chart viewer showing week-by-week schedule
