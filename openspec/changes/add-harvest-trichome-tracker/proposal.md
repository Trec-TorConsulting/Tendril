# Change: Add Harvest & Trichome Tracker

## Why
The `harvest_predict` insight exists but is not a tracked, first-class feature. Harvest timing is the highest-leverage quality decision a grower makes (per the cannabis quality philosophy in `openspec/project.md`: cannabinoid maturity, terpene preservation, never rush). Growers need to log trichome observations over time and see a live "optimal harvest window" estimate with a ripening checklist — turning a one-shot AI guess into an evidence-based, evolving prediction.

## What Changes
- Add **trichome logging**: users record trichome state observations (clear / cloudy / amber percentages, optionally a photo) over time for a grow.
- Add a **harvest window estimate** that combines flower start date, strain flower-weeks (when known), and logged trichome progression into a live "optimal harvest in ~N days" range, refined as more observations are logged.
- Add a **ripening checklist** surfaced in flowering/ripening stages (flush timing, environment for terpene preservation, dark period, etc.), quality-first.
- Reuse the existing `harvest_predict` insight for the AI-generated narrative, cached aggressively (Ollama first, Gemini fallback); the deterministic estimate does not require an LLM.
- Surface the tracker on the grow detail page and feed the adaptive dashboard's harvest guidance.

## Impact
- Affected specs:
  - harvest-tracking (NEW capability)
- Affected code (expected):
  - api/app/ (new trichome log model + harvest-estimate service + routes)
  - api/app/ai/routes.py, context.py (reuse harvest_predict, cached)
  - web/src/app/dashboard/grows/[id]/** (tracker UI), web/src/components/**
- Data model impact:
  - NEW table for trichome observations (grow_id, observed_at, clear/cloudy/amber %, note, photo ref) — new tables approved
- Security impact:
  - tenant-scoped via RLS; photo handling via existing media flow
- Breaking changes:
  - none; additive
