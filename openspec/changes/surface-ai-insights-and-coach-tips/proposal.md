# Change: Surface AI Insights and Coach Tips on the Dashboard

## Why
Tendril already ships three fully-built AI insight endpoints — `harvest_predict`, `nutrient_advice`, and `anomaly_scan` (see `/v1/ai/insights` and `runInsight` in `web/src/lib/api.ts`) — plus a `/v1/ai/coach-tip` endpoint. Today these have **no consumer on the main dashboard**: insights have no UI at all, and coach tips are buried on the grow-detail health sub-tab. Users land on the home dashboard and never see the intelligence the platform already produces. This is the highest-ROI, lowest-risk dynamism win: wire existing backend intelligence to the surface where users look.

## What Changes
- Add a **coach tip card** to the main dashboard home ([web/src/app/dashboard/page.tsx](web/src/app/dashboard/page.tsx)) that calls the existing `/v1/ai/coach-tip` for the selected grow, with aggressive client-side caching (TTL) matching the existing health-tab pattern.
- Add an **AI Insights panel** on the dashboard that surfaces the three existing insight types (harvest prediction, nutrient advice, anomaly scan) via the existing `runInsight` client, shown contextually (e.g., harvest prediction only when in flowering/ripening).
- Cache insight results aggressively on both client and server: reuse a server-side cache keyed by grow + insight type + input hash so repeated dashboard loads do not re-invoke the LLM.
- Respect AI provider preference: **Ollama first, Gemini fallback** (existing behavior), with cached results served without any LLM call when fresh.
- No new mutating behavior; this is additive read-only surfacing of existing endpoints.

## Impact
- Affected specs:
  - grow-assistant-core (MODIFIED — insight/coach surfacing requirements)
- Affected code (expected):
  - web/src/app/dashboard/page.tsx (new cards)
  - web/src/components/ (new `coach-tip-card.tsx`, `ai-insights-panel.tsx`)
  - web/src/lib/api.ts (reuse `getCoachTip`, `runInsight`)
  - api/app/ai/routes.py (add/confirm server-side caching for insights + coach tips)
  - api/app/ai/context.py (no prompt change required)
- Data model impact:
  - none required (server cache may reuse existing cache store / Redis)
- Security impact:
  - read-only; existing auth + tenant scoping applies
- Breaking changes:
  - none; additive
