# Change: Add Contextual Prompts (Right Question at the Right Time)

## Why
This is the literal "ask the right questions at the right time" ask. Tendril collects data but rarely *asks the user* for the input it needs to be smart — e.g., "Did you flip to 12/12?", "Log today's runoff pH?", "Are trichomes cloudy or amber yet?". These questions are stage- and time-dependent and, when missing, degrade every downstream feature (alerts, coaching, harvest prediction). A lightweight, rules-driven prompt/nudge system asks for the right input at the right moment and feeds the existing quick-log flow.

## What Changes
- Add a **contextual prompt engine**: deterministic rules that produce eligible prompts for a grow based on stage, elapsed time in stage/week, and missing/stale data (e.g., no runoff pH logged in N days, entering flower without a light-schedule confirmation).
- Surface prompts as **lightweight in-app nudges** (dismissible cards / quick-log prompts), not push, to keep them low-friction.
- Wire prompt answers into the existing **quick-log** flow and data model so answering a prompt persists real data (journal entry, reading, stage confirmation).
- Track prompt state (shown, answered, snoozed, dismissed) so prompts don't repeat and can be re-surfaced after a snooze interval.
- Prompts are **deterministic (no LLM)** for speed and predictability; AI coaching (separate change) handles free-form guidance.

## Impact
- Affected specs:
  - contextual-prompts (NEW capability)
- Affected code (expected):
  - api/app/ (new prompt-eligibility endpoint + prompt-state store)
  - api/app/scheduler/ or on-demand evaluation
  - web/src/components/ (nudge component), web/src/app/dashboard/quick-log/**
- Data model impact:
  - NEW table for prompt state per grow (prompt_key, status, shown_at, answered_at, snoozed_until) — new tables approved
- Security impact:
  - tenant-scoped via RLS
- Breaking changes:
  - none; additive
