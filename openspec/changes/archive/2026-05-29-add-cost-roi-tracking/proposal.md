# Change: Add Cost/ROI Tracking Per Grow

## Why
AGRIVI and FarmKeep both provide cost tracking as a core feature. Every commercial cannabis grower needs to know their cost-per-gram and ROI. Currently Tendril tracks what's growing but not what it costs. This is essential for commercial viability and was identified as the #2 feature gap in competitive analysis.

## What Changes

### New: Expense Tracking
- `POST /v1/grows/{id}/expenses` — Log an expense (nutrients, electricity, equipment, labor, rent, etc.)
- `GET /v1/grows/{id}/expenses` — List expenses with category filtering
- Categories: nutrients, electricity, water, equipment, labor, rent, supplies, other
- Recurring expenses (electricity, rent) with automatic pro-rating per grow

### New: Harvest Value Tracking
- Extend harvest yield model with value fields: price per gram (dry), total value
- Track by quality grade (A, B, trim, waste)

### New: ROI Dashboard
- Cost-per-gram calculation (total expenses / total dry yield)
- ROI percentage ((harvest value - total cost) / total cost × 100)
- Cost breakdown by category (pie chart)
- Grow-over-grow cost comparison
- Projected ROI based on current spending rate + expected yield

## Impact
- Affected code: New expense routes, extend harvest yield model, new dashboard component
- New spec: `cost-roi-tracking`
