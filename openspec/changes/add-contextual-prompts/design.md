# Design: Contextual Prompts

## Context
Tendril has a quick-log flow (`web/src/app/dashboard/quick-log`), stage tracking, and `_current_grow_week()`. There is no mechanism to *ask* the user for missing input at the right time.

## Goals
- Deterministic, cheap (no LLM), predictable prompts.
- Answering a prompt writes real data via existing endpoints.
- No nagging: state tracking + snooze.

## Decisions

### Prompt definition
Prompts are declared as data (a `PROMPT_RULES` registry), each with:
- `key` (stable id), `applies(grow, data) -> bool` predicate, `question`, `answer_type` (confirm | numeric-reading | choice | free-note), `target` (what answering writes: journal entry / reading / stage confirmation), `stages` filter, `cooldown`/`snooze_default`.

Examples:
- `confirm_flip_12_12` — stage flowering, no light-schedule confirmation logged.
- `log_runoff_ph` — coco/soil grow, no runoff pH reading in ≥ 3 days.
- `trichome_check` — late flower/ripening, weekly.
- `confirm_stage_advance` — week past typical stage duration without a stage change.

### Evaluation
Eligibility computed on-demand when the client requests prompts for a grow (fast, no scheduler needed), plus optional precompute. Returns the top N eligible prompts not currently snoozed/answered.

### Answering
Each prompt maps to a concrete write via existing quick-log/journal/reading endpoints. Answering records `answered_at` and performs the write in one action.

### State model
New table `grow_prompt_state`:
- `id`, `tenant_id` (RLS), `grow_cycle_id` (FK), `prompt_key`, `status` (eligible/shown/answered/snoozed/dismissed), `shown_at`, `answered_at`, `snoozed_until`, timestamps.
- Unique on `(grow_cycle_id, prompt_key)`; upsert on state change.

### Surfacing
Lightweight dismissible nudge cards on the dashboard and in quick-log. No push (keeps them non-intrusive; important guidance goes through proactive coaching instead).

## Risks
- **Prompt spam** → cap concurrent prompts (e.g., max 2), snooze support, per-prompt cooldown.
- **Stale eligibility** → recompute on each fetch; state upsert prevents duplicates.
