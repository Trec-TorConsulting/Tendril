# Design: Stage-Aware and Strain-Aware Alerting

## Context
`api/app/automation/engine.py` currently evaluates threshold, composite, trend, and critical rules against static thresholds. `critical_alerts_defaults.py` seeds grow-type-specific defaults but has no stage dimension. `openspec/project.md` documents stage-specific ideal ranges (water temp, pH, humidity, VPD, EC, DO) that are authoritative science defaults.

## Goals
- Resolve effective thresholds dynamically by `(grow_type, stage, metric)` at evaluation time.
- Allow per-grow overrides without forking the engine.
- Keep evaluation cheap (runs on the 30s–60s scheduler loop).
- Zero behavior change when no stage/override data is present.

## Decisions

### Threshold resolution order (highest precedence first)
1. Per-grow override for `(metric, stage)` if present.
2. Per-grow override for `(metric)` (stage-agnostic) if present.
3. Stage-keyed science default for `(grow_type, stage, metric)`.
4. Existing static grow-type default (current behavior — fallback).

This ordering guarantees backward compatibility: with no overrides and no stage match, step 4 preserves today's behavior.

### Stage bucketing
Map the grow lifecycle to threshold stages: `seedling`, `vegetative`, `transition`, `flowering`, `late_flowering`, `ripening`. `late_flowering` is derived (flower + week ≥ N, using `_current_grow_week()` from `api/app/ai/context.py`) since the DB stage enum stops at `flowering`/`ripening`. Keep the derivation in one helper so it is testable and reused.

### Data model
New table `grow_threshold_overrides`:
- `id`, `tenant_id` (RLS), `grow_cycle_id` (FK), `metric` (str), `stage` (nullable str — null = all stages), `caution_low`, `caution_high`, `critical_low`, `critical_high` (nullable floats), `created_at`, `updated_at`.
- Unique on `(grow_cycle_id, metric, stage)`.

Science defaults stay in code (`critical_alerts_defaults.py`) extended to a `STAGE_THRESHOLDS[grow_type][stage][metric]` structure — not in the DB, so they version with the code and match `project.md`.

### Alert message contract
Alert payloads gain: `stage`, `effective_range`, `metric_value`, and a `recommendation` string. The recommendation is a templated, quality-first sentence (no LLM call required for the alert itself — keeps alerting fast and deterministic). Optional AI enrichment is out of scope here (covered by proactive-ai-coaching).

### Strain adjustment (optional, additive)
When a grow's dominant strain has a known `flower_weeks` / lineage bias, adjust only harvest-window hints and late-flower onset week. Sensor ranges remain stage-driven. If no strain data, skip.

### Suppression interaction
On stage transition, clear cooldowns for rules whose effective threshold changed, so a newly-relevant alert can fire immediately rather than waiting out a stale cooldown.

## Risks
- **False sense of precision** in derived `late_flowering`: mitigate by making the week cutoff configurable and documented.
- **Migration**: new table only; no destructive change.
