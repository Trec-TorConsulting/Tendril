## Context
Growers perform water changes every 7-14 days (hydro) or feed daily/weekly. These are the highest-frequency actions but they're hidden behind a Journal tab requiring 5+ clicks. The current bucket card only surfaces "Log Reading" (raw sensor values) which doesn't map to the grower's mental model of "I just did something to my plant."

## Goals / Non-Goals
- Goals: One-click water change from bucket card; at-a-glance "days since" visibility; unified action that logs both the event and readings
- Non-Goals: Changing the journal model; adding reservoir-level tracking (separate future proposal); automated water change detection via sensors

## Decisions
- Decision: Combined action endpoint (`POST /journal/quick`) that creates both a JournalEntry AND a SensorReading in one transaction
  - Rationale: Users currently must log the event (journal) and the readings (sensor) separately. This is the #1 friction point.
- Decision: Derive `last_water_change_at` from journal entries rather than adding a dedicated column
  - Rationale: Single source of truth (journal), no data sync issues
  - Trade-off: Slightly slower query (mitigate with index on bucket_id + event_type + created_at DESC)
- Decision: Days-since thresholds are hardcoded (7/10 days) initially, not per-grow-type configurable
  - Rationale: Ship simple first; DWC and RDWC typically need changes every 7-14 days, soil/coco less often. Can make configurable later.
- Alternatives considered:
  - Add `last_water_change_at` column to Bucket table → rejected (denormalized, needs triggers to stay in sync)
  - Only improve Quick Log → rejected (doesn't solve visibility on bucket cards)

## Risks / Trade-offs
- Hardcoded 7/10 day thresholds won't fit all grow types → acceptable for v1, make configurable later
- Additional query per bucket for `last_water_change_at` → batch query all buckets' latest events in one DB call

## Open Questions
- Should the water change dialog offer a "full flush" toggle that uses event_type "flushing" vs "water_change"?
- Should feed logging support selecting from configured nutrient schedules (from Feeding tab)?
