# Change: Add Progressive Onboarding and Dynamic Command Palette

## Why
Two experience surfaces are static today. Onboarding ([web/src/components/onboarding-wizard.tsx](web/src/components/onboarding-wizard.tsx)) is a fixed 4-step flow that sets a persona layout once and never adapts as the user demonstrates knowledge; the checklist ([onboarding-checklist.tsx](web/src/components/onboarding-checklist.tsx)) doesn't re-engage. The command palette ([web/src/components/command-palette.tsx](web/src/components/command-palette.tsx)) is dynamically populated but statically ordered — same pages in the same order, no recency/stage ranking, no contextual "next action" suggestions. Making both adaptive lets the app meet users where they are.

## What Changes
- **Progressive onboarding**: adapt the guided experience as the user completes real actions (create tent → grow → device → first log). Advance layout complexity as competence is demonstrated, and re-surface the right next step instead of a one-time fixed flow.
- **Dynamic command palette**: rank results by recency and frequency; add **contextual action suggestions** based on the selected grow's stage/state (e.g., "Run health check", "Log trichomes" surfaced when relevant), reusing existing endpoints.
- Keep both additive and non-breaking; users can still choose layout mode manually in settings.

## Impact
- Affected specs:
  - adaptive-experience (NEW capability)
- Affected code (expected):
  - web/src/components/onboarding-wizard.tsx, onboarding-checklist.tsx, onboarding-gate.tsx
  - web/src/components/command-palette.tsx
  - web/src/hooks/use-layout-mode.tsx (progressive advancement)
  - web/src/lib/ (recency/frequency tracking, contextual-action rules)
- Data model impact:
  - none required (client-side preferences/localStorage + existing profile fields); MAY persist onboarding progress to profile
- Security impact:
  - none new
- Breaking changes:
  - none; additive
