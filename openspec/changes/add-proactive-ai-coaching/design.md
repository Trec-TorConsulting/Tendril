# Design: Proactive AI Coaching

## Context
The scheduler (`api/app/scheduler/tasks.py`) already runs periodic jobs with leader election. The AI context builder assembles stage, sensors, trends, feeding schedule, strain, and quality philosophy. Notifications (`api/app/notifications/service.py`) already fan out in-app / push / email with per-tenant severity + event-type filtering and cooldown suppression.

## Goals
- Speak first, usefully, without spamming.
- Reuse existing AI + notification infrastructure; add orchestration only.
- Keep LLM cost bounded via triggers + caching + de-duplication.

## Decisions

### Trigger model (evaluated, not LLM-driven)
A cheap, deterministic pre-filter decides *whether* to coach; the LLM only writes the message. Triggers:
- **Stage transition** (grow.stage changed since last evaluation).
- **New grow week** crossing (`_current_grow_week` increments).
- **Sustained sensor drift** (a metric trending toward/past caution for ≥ N consecutive readings).
- **Pre-emergency composite** (e.g., water_temp rising AND DO falling) — reuse patterns from the composite alert engine but at a softer, earlier threshold.

Each trigger has a stable `coaching_topic` key used for de-duplication.

### Evaluation cadence
Run every 30 minutes (align with existing scheduler cadence). Skip grows with proactive coaching disabled. Only active grows.

### Message generation + caching
- On trigger fire, build a coaching prompt (new builder in `context.py`, reusing existing context assembly).
- Generate with Ollama first, Gemini fallback.
- **Cache** the generated message keyed by `(grow_id, coaching_topic, input_hash)`; if a fresh message exists for the same topic+inputs, reuse it (no LLM call).
- **De-duplicate**: do not emit a coaching event for a `(grow, topic)` already emitted within the topic's cooldown, unless severity is `critical`.

### Delivery
- Always create an in-app coaching event (persisted).
- For `important`/`critical` severity, also dispatch web push via existing notification service, honoring per-tenant prefs.
- Never bypass the tenant's disable toggle except for `critical` safety events (documented).

### Data model
New table `coaching_events`:
- `id`, `tenant_id` (RLS), `grow_cycle_id` (FK), `topic` (str), `severity` (enum: info/important/critical), `message` (text), `generated_at`, `acknowledged_at` (nullable), `dismissed_at` (nullable).
- Index on `(tenant_id, grow_cycle_id, generated_at)`.

New settings fields (reuse preferences store): `proactive_coaching_enabled` (per tenant, default true), optional per-grow override.

### Idempotency
Store `last_coached_at` per `(grow, topic)` (can be derived from `coaching_events`) to enforce cooldown without a separate table.

## Risks
- **Notification fatigue** → mitigated by trigger pre-filter, per-topic cooldown, in-app-default/push-only-important split.
- **LLM cost** → mitigated by deterministic triggers + aggressive caching + de-dup.
- **Bad advice** → messages are quality-first templated context; keep temperature low; include the same guardrails as chat.
