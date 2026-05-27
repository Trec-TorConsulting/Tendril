## 1. Data Model
- [x] 1.1 `NutrientProduct` model in `grows/models.py` (barcode, name, brand, npk, nutrients JSON, image_url, source)
- [x] 1.2 `FeedingSchedule` model with nutrients JSON array (name, brand, ml_per_gallon, strength_pct)
- [x] 1.3 Models migrated and live

## 2. Seed Data
- [x] 2.1 `reference/feed_charts.py` — General Hydroponics Flora Series (full week-by-week chart)
- [x] 2.2 `reference/feed_charts.py` — Advanced Nutrients pH Perfect Sensi (full chart)
- [x] 2.3 `reference/feed_charts.py` — Fox Farm Dirty Dozen (full chart)
- [x] 2.4 `reference/nutrient_knowledge.py` — DIY recipes (Masterblend Tomato, Jack's 3-2-1)
- [x] 2.5 `reference/nutrient_sync.py` — sync service loads charts into reference data

## 3. API
- [x] 3.1 `GET /v1/reference/nutrients` — search by name/brand
- [x] 3.2 `GET /v1/reference/nutrients/barcode/{barcode}` — barcode lookup
- [x] 3.3 Feed chart data served as part of reference nutrient endpoints
- [x] 3.4 Nutrient brand selection on grow via feeding schedules

## 4. AI Integration
- [x] 4.1 Feed charts included in AI context for feeding advice
- [x] 4.2 Brand-specific product/dose recommendations generated

## 5. Frontend
- [x] 5.1 `NutrientSearch` component (reference-search.tsx) — autocomplete brand/product selector
- [x] 5.2 Reference page with dedicated nutrient browsing tab
