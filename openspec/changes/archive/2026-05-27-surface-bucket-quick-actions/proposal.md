# Change: Surface Common Actions on Bucket Cards

## Why
The most frequent tasks growers perform (water change, feeding, flush) require navigating to a separate tab (Journal) and going through a multi-step form. Bucket cards currently only show "Log Reading" (sensor numbers) and "Edit" — neither of which maps to the action a grower is actually thinking: "I just changed my water" or "I just fed."

## What Changes
- Add "Water Change" and "Feed" quick-action buttons directly on each bucket card
- Show "days since last water change" badge on each bucket card (derived from journal entries)
- Quick Log Feeding tab should automatically create a journal entry alongside the sensor reading
- Overview tab should show at-a-glance status: last water change per bucket, upcoming tasks
- Bucket cards should visually signal when a water change is overdue (color coding)

## Impact
- Affected specs: `bucket-monitoring`
- Affected code: `web/src/app/dashboard/grows/[id]/buckets-tab.tsx`, `web/src/components/quick-log/feeding-log-form.tsx`, `api/app/grows/bucket_routes.py` (add computed field), `api/app/grows/journal_routes.py`
- API addition: `last_water_change_at` computed field in BucketResponse
