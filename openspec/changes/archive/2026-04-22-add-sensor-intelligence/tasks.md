## 1. Sensor Trend Drift Detection
- [x] 1.1 Add drift analysis function — compare current reading to 24h rolling average
- [x] 1.2 Generate `drift` alert when pH deviates > 0.3 or EC > 0.2 from rolling average
- [x] 1.3 Add trend direction indicator (↑ rising, ↓ falling, → stable) to bucket cards and detail view
- [x] 1.4 Store drift alerts in alerts table with bucket context
- [ ] 1.5 Add drift alert to push notification triggers (if PWA push is enabled)

## 2. Per-Bucket VPD Calculation
- [x] 2.1 Implement leaf VPD formula: VPD = (SVPleaf - VPair) where SVP is from temp/humidity
- [x] 2.2 Calculate VPD from ambient temp + ambient humidity (from ESP32 DHT22 or tent sensors)
- [x] 2.3 Display VPD in bucket detail view with optimal range indicator per growth stage
- [x] 2.4 Add VPD to bucket card (condensed display)
- [x] 2.5 Generate alert when VPD is outside optimal range for current growth stage
- [x] 2.6 Add VPD trend line to sensor history chart in detail view

## 3. Nutrient Calculator
- [x] 3.1 Add `POST /api/nutrient-calc` endpoint — takes current EC/PPM + target EC/PPM + reservoir volume → returns ml to add
- [x] 3.2 Create nutrient calculator UI panel (accessible from bucket detail or toolbar)
- [x] 3.3 Support common nutrient lines (General Hydroponics Flora series, Fox Farm, Advanced Nutrients) with preset ratios
- [x] 3.4 Allow custom nutrient ratio input
- [x] 3.5 Log calculated doses to bucket journal automatically

## 4. Reservoir Flush Countdown
- [x] 4.1 Add configurable flush interval per growth stage (e.g., seedling=10d, veg=7d, flower=5d)
- [x] 4.2 Display countdown timer on bucket card (days until next flush due)
- [x] 4.3 Generate warning alert 1 day before flush is due, critical alert when overdue
- [x] 4.4 Add flush countdown to daily health check context (AI mentions overdue flushes)
- [x] 4.5 Configure flush intervals in tent settings

## 5. Harvest Yield Tracking
- [x] 5.1 Add `yields` table (bucket_id, wet_weight_g, dry_weight_g, notes, created_at)
- [x] 5.2 Add `POST /api/buckets/{id}/yield` endpoint
- [x] 5.3 Add yield entry UI when bucket status is changed to "harvested"
- [x] 5.4 Calculate and display grams-per-plant
- [x] 5.5 Calculate grams-per-watt (if light wattage configured in tent settings)
- [x] 5.6 Show yield summary in bucket detail view (for harvested buckets)
- [x] 5.7 Add yield history to grow journal

## 6. Testing
- [x] 6.1 Test drift detection with mock sensor data (rising pH over 24h)
- [x] 6.2 Test VPD calculation accuracy against known values
- [x] 6.3 Test nutrient calculator math
- [x] 6.4 Test flush countdown alerts (due, overdue)
- [x] 6.5 Test yield tracking CRUD
