## 1. API Changes
- [x] 1.1 Add `last_water_change_at` computed field to BucketResponse schema (query latest journal entry with event_type in ["water_change", "flushing"])
- [x] 1.2 Add `POST /journal/quick` endpoint that accepts bucket_id + event_type + optional sensor readings in one call
- [x] 1.3 Ensure journal query for latest water change is indexed efficiently (bucket_id + event_type + created_at)

## 2. Bucket Card Quick Actions
- [x] 2.1 Add "Water Change" button (RefreshCw icon) to bucket card action row
- [x] 2.2 Add "Feed" button (FlaskConical icon) to bucket card action row
- [x] 2.3 Water Change button opens minimal dialog: pH, EC, PPM, water temp, notes → creates journal entry + sensor reading via /journal/quick
- [x] 2.4 Feed button opens dialog: same fields → creates journal entry (event_type: "feeding") + sensor reading via /journal/quick

## 3. Days-Since Badge
- [x] 3.1 Display "X days since water change" on each bucket card using `last_water_change_at`
- [x] 3.2 Color coding: green (≤7 days), yellow (8-10 days), red (>10 days or never)
- [x] 3.3 Show "No water change" with muted style if no water change recorded

## 4. Quick Log Integration
- [x] 4.1 Quick Log Feeding already creates a journal entry (event_type: "feeding") alongside sensor readings (verified in quick_log_routes.py)
- [x] 4.2 Add "Water Change" option to Quick Log (not just "Feeding" and "Reading")
- [x] 4.3 Quick Log Water Change: bucket selector + pH + EC + notes → creates journal entry + reading

## 5. Overview Tab Enhancement
- [x] 5.1 Add "Bucket Status" summary card to Overview tab showing each bucket's last water change date
- [x] 5.2 Highlight any buckets overdue for water change in the summary

## 6. Testing
- [x] 6.1 Unit test: `last_water_change_at` computation from journal entries
- [x] 6.2 Unit test: quick journal endpoint creates both entry and reading
- [x] 6.3 E2E test: water change flow from bucket card
