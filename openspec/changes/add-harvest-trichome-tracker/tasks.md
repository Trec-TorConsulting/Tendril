## 1. Backend — trichome observations
- [ ] 1.1 Add `trichome_observations` table + model (tenant_id RLS, grow_cycle_id FK, nullable bucket_id, observed_at, clear_pct, cloudy_pct, amber_pct, note, photo_ref, timestamps; index on grow_cycle_id+observed_at).
- [ ] 1.2 Add Alembic migration with RLS policy.
- [ ] 1.3 Add store methods: create/list/get/delete observations for a grow; validate percentages sum to ~100.
- [ ] 1.4 Add CRUD routes (create observation, list observations) guarded by grow permissions; wire photo upload through existing media flow.

## 2. Backend — deterministic harvest window estimator
- [ ] 2.1 Implement a pure `estimate_harvest_window(grow, strain, observations)` returning earliest/optimal/latest dates + confidence + rationale, using flower start + strain flower-weeks (grow-type default fallback) adjusted by trichome trend against a documented quality-first target profile.
- [ ] 2.2 Add an endpoint `GET /v1/grows/{id}/harvest-window` returning the estimate.

## 3. Backend — optional AI narrative (cached)
- [ ] 3.1 Reuse `harvest_predict` for a narrative; cache keyed by (grow_id, latest_observation_id); Ollama first, Gemini fallback; regenerate only when new observation data exists.

## 4. Backend — ripening checklist
- [ ] 4.1 Define stage-gated ripening checklist items (flush window, terpene-preservation environment, mold vigilance, dark period); surface actionable items via the task system.

## 5. Frontend
- [ ] 5.1 Add a trichome logging form on the grow detail page (percent sliders/inputs + optional photo + note).
- [ ] 5.2 Add a trichome progression chart (clear/cloudy/amber over time).
- [ ] 5.3 Add a harvest-window card showing the earliest/optimal/latest range, confidence, and rationale; never a single hard date.
- [ ] 5.4 Add the ripening checklist, shown in flowering/ripening stages.

## 6. Testing
- [ ] 6.1 Unit tests for `estimate_harvest_window` (sparse data widens range/low confidence; rising cloudy/amber narrows and shifts; strain vs grow-type fallback).
- [ ] 6.2 Validate percentage-sum constraint on observations.
- [ ] 6.3 Test narrative cache regenerates only on new observation.
- [ ] 6.4 Migration + RLS test for trichome_observations.
- [ ] 6.5 Web component tests for the log form, chart, and harvest-window card.

## 7. Validation
- [ ] 7.1 Run `openspec validate add-harvest-trichome-tracker --strict --no-interactive`.
- [ ] 7.2 Regenerate API types; run lint + API + web tests.
