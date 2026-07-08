## 1. Backend — stage-keyed science defaults
- [ ] 1.1 In `api/app/automation/critical_alerts_defaults.py`, extend defaults to a `STAGE_THRESHOLDS[grow_type][stage][metric]` structure seeded from the ideal ranges in `openspec/project.md` (water temp, pH, humidity, VPD, EC, DO by stage).
- [ ] 1.2 Add a `derive_threshold_stage(grow)` helper that maps the grow lifecycle to threshold stages, deriving `late_flowering` from flower stage + current week (reuse `_current_grow_week` from `api/app/ai/context.py`). Make the late-flower week cutoff a module constant.

## 2. Backend — per-grow override model
- [ ] 2.1 Add `grow_threshold_overrides` table + SQLAlchemy model in `api/app/automation/models.py` (tenant_id RLS, grow_cycle_id FK, metric, nullable stage, caution_low/high, critical_low/high, timestamps; unique on grow_cycle_id+metric+stage).
- [ ] 2.2 Add Alembic migration for the new table with RLS policy matching other tenant tables.
- [ ] 2.3 Add store methods: create/get/list/update/delete overrides for a grow.
- [ ] 2.4 Add CRUD routes under `api/app/automation/routes.py` guarded by existing automation permissions.

## 3. Backend — threshold resolution in the engine
- [ ] 3.1 Add `resolve_threshold(grow, metric)` implementing precedence: per-grow (metric,stage) → per-grow (metric) → stage default (grow_type,stage,metric) → existing static default.
- [ ] 3.2 Wire `resolve_threshold` into `evaluate_critical_alerts` and threshold-rule evaluation in `api/app/automation/engine.py`.
- [ ] 3.3 Extend alert payload with `stage`, `effective_range`, `metric_value`, and a templated quality-first `recommendation` string (no LLM call).
- [ ] 3.4 On stage transition, clear cooldowns for rules whose effective threshold changed.

## 4. Optional strain adjustment
- [ ] 4.1 When a grow's dominant strain exposes `flower_weeks`/lineage bias, adjust late-flower onset week and harvest-window hints only (not sensor ranges). Skip when absent.

## 5. Frontend — override UI
- [ ] 5.1 Add a "Thresholds" section to `web/src/app/dashboard/automation/` showing the effective range per metric per stage for the selected grow, with the source (default vs override) labeled.
- [ ] 5.2 Allow editing an override per metric/stage and resetting to default.

## 6. Testing
- [ ] 6.1 Unit tests for `resolve_threshold` precedence (all four levels + fallback).
- [ ] 6.2 Unit tests for `derive_threshold_stage` including late-flower week cutoff.
- [ ] 6.3 Test that a stage transition clears cooldowns only for affected rules.
- [ ] 6.4 Test alert payload includes stage, effective range, and recommendation.
- [ ] 6.5 Migration test for the new table + RLS.
- [ ] 6.6 Web component test for the threshold override editor.

## 7. Validation
- [ ] 7.1 Run `openspec validate add-stage-aware-alerting --strict --no-interactive`.
- [ ] 7.2 Regenerate API types; run lint + API + web tests.
