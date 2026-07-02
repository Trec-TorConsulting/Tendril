# Design: Harvest & Trichome Tracker

## Context
`/v1/ai/insights` already supports `harvest_predict`. Grows have a stage, `started_at`, and stage timing; strains may expose flower-weeks/lineage. Media/photos flow through existing MinIO storage.

## Goals
- Evidence-based harvest window that improves as trichome data accrues.
- Deterministic estimate (no LLM) for the number; AI narrative optional and cached.
- Quality-first: never nudge toward early harvest for yield.

## Decisions

### Trichome observation model
New table `trichome_observations`:
- `id`, `tenant_id` (RLS), `grow_cycle_id` (FK), `bucket_id` (nullable), `observed_at`, `clear_pct`, `cloudy_pct`, `amber_pct` (ints summing ~100), `note` (nullable), `photo_ref` (nullable), timestamps.
- Index on `(grow_cycle_id, observed_at)`.

### Deterministic harvest window
Estimate combines:
- Baseline: flower start + strain flower-weeks (fallback to a grow-type default when strain unknown).
- Adjustment from trichome trend: as cloudy% rises toward target and amber% appears, narrow and shift the window. Define a documented target profile (e.g., mostly cloudy with a small amber fraction for balanced effect) consistent with quality-first guidance.
- Output: a date range (`earliest`, `optimal`, `latest`) + confidence, with rationale text.

Keep the estimator pure and unit-tested; no LLM.

### AI narrative (optional)
Reuse `harvest_predict` for a human-readable narrative; cache keyed by `(grow_id, latest_observation_id)` so it only regenerates when new data arrives. Ollama first, Gemini fallback.

### Ripening checklist
Static, stage-gated checklist items surfaced in flowering/ripening (flush window, environment/terpene preservation, humidity/mold vigilance, dark period). Reuse the task system where an item is actionable.

### Surfacing
- Grow detail page: trichome log + chart + harvest window card + checklist.
- Adaptive dashboard: harvest window card boosted in flower/ripening (via the adaptive-dashboard change).

## Risks
- **Overconfidence** with sparse data → show confidence + widen range when few observations; never present a single hard date.
- **Quality drift** → estimator and narrative both enforce quality-first (no early-harvest-for-yield).
