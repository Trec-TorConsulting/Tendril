## 1. Backend — coaching events model
- [ ] 1.1 Add `coaching_events` table + model in a new `api/app/coaching/models.py` (or under notifications): tenant_id RLS, grow_cycle_id FK, topic, severity enum (info/important/critical), message, generated_at, acknowledged_at, dismissed_at; index on (tenant_id, grow_cycle_id, generated_at).
- [ ] 1.2 Add Alembic migration with RLS policy.
- [ ] 1.3 Add store methods: create event, list events for grow/tenant, acknowledge, dismiss, and `last_coached_at(grow, topic)`.

## 2. Backend — trigger evaluation
- [ ] 2.1 Implement a deterministic trigger evaluator: stage transition, new grow-week crossing, sustained sensor drift (≥ N consecutive readings toward/past caution), and pre-emergency composite conditions. Each yields a stable `coaching_topic` + severity.
- [ ] 2.2 Reuse composite/trend logic patterns from `api/app/automation/engine.py` at softer, earlier thresholds.

## 3. Backend — message generation with caching
- [ ] 3.1 Add `build_coaching_prompt(grow, topic, context)` in `api/app/ai/context.py` reusing existing context assembly and quality-first guardrails.
- [ ] 3.2 Generate with Ollama first, Gemini fallback; low temperature.
- [ ] 3.3 Cache generated message keyed by (grow_id, topic, input_hash); reuse fresh cached message without an LLM call.
- [ ] 3.4 De-duplicate: skip emitting if a `(grow, topic)` event exists within the topic cooldown, unless severity is critical.

## 4. Backend — scheduler job + delivery
- [ ] 4.1 Add a scheduler job in `api/app/scheduler/tasks.py` running every 30 minutes over active grows, skipping grows with proactive coaching disabled.
- [ ] 4.2 On fired trigger: persist a coaching event (in-app) and, for important/critical severity, dispatch web push via `api/app/notifications/service.py` honoring per-tenant prefs.
- [ ] 4.3 Add a `proactive_coaching_enabled` preference (tenant default true) with optional per-grow override; enforce disable toggle (except critical safety events).

## 5. Backend — API
- [ ] 5.1 Add endpoints to list coaching events for a grow, acknowledge, and dismiss (under `api/app/ai/routes.py` or new coaching router), tenant-scoped.

## 6. Frontend
- [ ] 6.1 Add a coaching feed/card component that lists recent coaching events with severity, message, timestamp, and acknowledge/dismiss actions.
- [ ] 6.2 Surface unacknowledged important/critical coaching prominently on the dashboard home.
- [ ] 6.3 Add a settings toggle for proactive coaching (tenant + per-grow).

## 7. Testing
- [ ] 7.1 Unit tests for each trigger type firing/not firing.
- [ ] 7.2 Test de-duplication and cooldown (including critical bypass).
- [ ] 7.3 Test caching prevents redundant LLM calls (mock provider).
- [ ] 7.4 Test delivery split: in-app always, push only for important/critical, and disable toggle honored.
- [ ] 7.5 Migration + RLS test for coaching_events.
- [ ] 7.6 Web component tests for the coaching feed and settings toggle.

## 8. Validation
- [ ] 8.1 Run `openspec validate add-proactive-ai-coaching --strict --no-interactive`.
- [ ] 8.2 Regenerate API types; run lint + API + web tests.
