## 1. Backend
- [x] 1.1 Create `GET /v1/analytics/compare` endpoint — accept grow_ids[], metrics[], date_range
- [x] 1.2 Return normalized time-series data (day-in-grow as X axis, not calendar date)
- [x] 1.3 Include final yield, quality scores, environment averages per grow

## 2. Comparison UI
- [x] 2.1 Create `/dashboard/analytics/compare` page
- [x] 2.2 Add grow multi-select (pick 2-4 grows to compare)
- [x] 2.3 Add metric selector (pH, EC, temp, humidity, VPD, yield)
- [x] 2.4 Render overlay line charts (one color per grow, shared X axis = day-in-grow)
- [x] 2.5 Add summary stats table (avg pH, avg EC, total yield, grow duration)
- [x] 2.6 Highlight differences and best-performing grow per metric

## 3. Season-over-Season
- [x] 3.1 Auto-detect comparable grows (same strain + same grow type)
- [x] 3.2 Add "Compare with previous" button on grow detail page (via comparable endpoint)
- [x] 3.3 Show improvement/regression indicators (↑ yield +12%, ↓ avg EC -0.3)
- [x] 3.4 Add to analytics page as a "Compare" tab
