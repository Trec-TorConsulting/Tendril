# Change: Add Proactive AI Coaching

## Why
Tendril's AI is context-rich but **reactive-only** — it never speaks first. The scheduler already runs periodic jobs and the context builder ([api/app/ai/context.py](api/app/ai/context.py)) already assembles everything needed for good advice. By evaluating each active grow on meaningful state/stage transitions and sensor drift, the platform can deliver timely, quality-first coaching *before* problems become emergencies (e.g., warm water + falling dissolved oxygen → root-health nudge). This turns Tendril from a dashboard you check into an assistant that guides you.

## What Changes
- Add a scheduler job that periodically evaluates each active grow for **coaching triggers**: stage transitions, sustained sensor drift, entering a new grow week, and pre-emergency composite conditions.
- On a trigger, generate a concise, quality-first coaching message using the existing AI stack (**Ollama first, Gemini fallback**), with **aggressive caching** and de-duplication so the same advice is not repeated.
- Deliver coaching **in-app (notification/card) always, plus web push on important events**, respecting existing per-tenant notification preferences and severity filtering ([api/app/notifications/service.py](api/app/notifications/service.py)).
- Apply cooldown/de-duplication per `(grow, coaching_topic)` so users are not spammed; important/critical coaching may bypass the soft cooldown.
- Store coaching events so they can be shown in an in-app feed and acknowledged/dismissed.
- Respect a per-tenant/per-grow toggle to disable proactive coaching entirely.

## Impact
- Affected specs:
  - grow-assistant-core (ADDED — proactive coaching requirements)
- Affected code (expected):
  - api/app/scheduler/tasks.py (new coaching evaluation job)
  - api/app/ai/context.py (reuse existing prompt builders; add a coaching prompt)
  - api/app/ai/routes.py (endpoint to list/ack coaching events)
  - api/app/notifications/service.py (dispatch coaching notifications)
  - web/src/components/ (coaching feed/card), web/src/app/dashboard/**
- Data model impact:
  - NEW table for coaching events (topic, message, severity, grow_id, generated_at, acknowledged_at) — new tables approved
- Security impact:
  - tenant-scoped via RLS; respects notification preferences and consent toggle
- Breaking changes:
  - none; additive and default-on for in-app, push only for important events
