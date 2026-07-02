## 1. Backend — caching for existing insight/coach endpoints
- [ ] 1.1 In `api/app/ai/routes.py`, confirm `/v1/ai/coach-tip` and `/v1/ai/insights` responses. Add a server-side cache layer keyed by `(tenant_id, grow_id, insight_type, input_hash)` with a configurable TTL (default 6h for coach-tip, 24h for harvest_predict, 6h for nutrient_advice, 1h for anomaly_scan).
- [ ] 1.2 Serve a fresh cached result without invoking any LLM. On cache miss, run Ollama first, fall back to Gemini, then store the result in cache.
- [ ] 1.3 Add a `cached: bool` and `generated_at: datetime` field to the coach-tip and insight response models so the UI can show freshness.
- [ ] 1.4 Add a `force_refresh: bool = False` request field to bypass cache on explicit user refresh.

## 2. Frontend — coach tip card on dashboard home
- [ ] 2.1 Create `web/src/components/coach-tip-card.tsx` that calls `getCoachTip(token, growId)` via SWR, mirroring the caching pattern in `web/src/app/dashboard/grows/[id]/health-tab.tsx` (TTL cache in localStorage + interval refresh).
- [ ] 2.2 Show a loading skeleton, the tip text, a "generated Xh ago" freshness label, and a manual refresh button (sets `force_refresh`).
- [ ] 2.3 Render the card in `web/src/app/dashboard/page.tsx` for the selected grow, near the top of the content area.

## 3. Frontend — AI Insights panel on dashboard home
- [ ] 3.1 Create `web/src/components/ai-insights-panel.tsx` that calls `runInsight(token, growId, insightType)` via SWR for each relevant insight type.
- [ ] 3.2 Show `harvest_predict` only when the grow stage is `flowering`, `ripening`, or `harvesting`; show `nutrient_advice` in all growth stages; show `anomaly_scan` whenever recent sensor readings exist.
- [ ] 3.3 Render each insight as a compact card with a title, the AI result, freshness label, and refresh button.
- [ ] 3.4 Handle empty/error states gracefully (e.g., "No recent sensor data to analyze").
- [ ] 3.5 Render the panel in `web/src/app/dashboard/page.tsx`.

## 4. Testing
- [ ] 4.1 API: unit test that a fresh cache hit returns without invoking the LLM client (mock provider, assert not called).
- [ ] 4.2 API: unit test that `force_refresh=true` bypasses the cache.
- [ ] 4.3 Web: component test for `coach-tip-card.tsx` (loading, loaded, error, refresh).
- [ ] 4.4 Web: component test for `ai-insights-panel.tsx` stage-gating (harvest card hidden in veg, shown in flower).
- [ ] 4.5 Web: dashboard test asserting the coach tip card and insights panel render for a selected grow.

## 5. Validation
- [ ] 5.1 Run `openspec validate surface-ai-insights-and-coach-tips --strict --no-interactive` and resolve issues.
- [ ] 5.2 Regenerate API types (`cd web && npm run gen:types`) if response models changed; commit the diff.
- [ ] 5.3 Run `npm run lint`, `npm test` (web) and API tests; ensure all pass.
