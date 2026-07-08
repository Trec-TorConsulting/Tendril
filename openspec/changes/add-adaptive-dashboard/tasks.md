## 1. Priority computation
- [ ] 1.1 Create `web/src/hooks/use-dashboard-priority.ts` that takes the already-fetched dashboard data (grow, stage, tasks, alerts, coaching events, sensor trends, harvest countdown) and returns an ordered list of section keys with a computed priority score.
- [ ] 1.2 Define the deterministic priority rules: active critical alert > urgent task > important/critical coaching > stage-relevant guidance > standard cards. Document the rule table in the hook.
- [ ] 1.3 Add stage-relevance weighting: e.g., harvest countdown/trichome guidance boosted in flowering/ripening/harvesting; de-boosted in seedling/veg.

## 2. Next Best Action
- [ ] 2.1 Create `web/src/components/next-best-action.tsx` that selects the single highest-priority actionable item and renders it with a clear label and a one-tap action (navigate/complete/acknowledge).
- [ ] 2.2 Handle the empty case (nothing urgent) with a calm positive state ("All good — next check in Xh").

## 3. Dashboard integration
- [ ] 3.1 In `web/src/app/dashboard/page.tsx`, render `NextBestAction` at the top and reorder existing sections using the ordered keys from `use-dashboard-priority`.
- [ ] 3.2 Ensure ordering operates within the current persona layout (density/tabs unchanged) and falls back to the existing fixed order when the priority list is empty.
- [ ] 3.3 Preserve existing animations/stagger; avoid layout thrash on data refresh (stable keys, memoized order).

## 4. Testing
- [ ] 4.1 Unit tests for `use-dashboard-priority` covering: critical alert wins; urgent task over coaching; stage weighting (harvest boosted in flower, hidden/deboosted in veg); empty fallback.
- [ ] 4.2 Component test for `next-best-action` selection + empty state.
- [ ] 4.3 Dashboard test asserting sections reorder when a critical alert is present.

## 5. Validation
- [ ] 5.1 Run `openspec validate add-adaptive-dashboard --strict --no-interactive`.
- [ ] 5.2 Run `npm run lint` and `npm test` (web); ensure pass.
