## 1. Backend — prompt registry + state
- [ ] 1.1 Create a `PROMPT_RULES` registry (data-driven) with at least: `confirm_flip_12_12`, `log_runoff_ph`, `trichome_check`, `confirm_stage_advance`. Each has key, applies() predicate, question, answer_type, target write, stages filter, snooze default.
- [ ] 1.2 Add `grow_prompt_state` table + model (tenant_id RLS, grow_cycle_id FK, prompt_key, status, shown_at, answered_at, snoozed_until, timestamps; unique on grow_cycle_id+prompt_key).
- [ ] 1.3 Add Alembic migration with RLS policy.
- [ ] 1.4 Add store methods: upsert state, list active prompts for grow, mark shown/answered/snoozed/dismissed.

## 2. Backend — eligibility + answering
- [ ] 2.1 Add `evaluate_prompts(grow, data)` returning top-N eligible prompts, excluding answered/snoozed/dismissed and capping concurrent prompts (e.g., max 2).
- [ ] 2.2 Add endpoint `GET /v1/grows/{id}/prompts` returning eligible prompts.
- [ ] 2.3 Add endpoint to answer a prompt: performs the mapped write (journal entry / reading / stage confirmation) via existing services and records `answered_at`.
- [ ] 2.4 Add endpoints to snooze and dismiss a prompt.

## 3. Frontend
- [ ] 3.1 Create a `contextual-prompt-card.tsx` nudge component rendering the question and the appropriate answer control (confirm button / numeric input / choice / note).
- [ ] 3.2 Wire answer submission into the existing quick-log flow so answering persists real data.
- [ ] 3.3 Surface up to N prompts on the dashboard home and within `web/src/app/dashboard/quick-log`, with dismiss and snooze actions.

## 4. Testing
- [ ] 4.1 Unit tests for each prompt predicate (eligible/not eligible by stage, elapsed time, missing/stale data).
- [ ] 4.2 Test concurrent-prompt cap and snooze/dismiss suppression.
- [ ] 4.3 Test that answering writes the correct data and records answered_at.
- [ ] 4.4 Migration + RLS test for grow_prompt_state.
- [ ] 4.5 Web component test for the prompt card answer flows.

## 5. Validation
- [ ] 5.1 Run `openspec validate add-contextual-prompts --strict --no-interactive`.
- [ ] 5.2 Regenerate API types; run lint + API + web tests.
