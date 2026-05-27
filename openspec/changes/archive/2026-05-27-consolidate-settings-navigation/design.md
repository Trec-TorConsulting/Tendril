## Context
Users report settings are hard to find. Currently 12+ locations house configuration, with inconsistent sidebar grouping. The mental model mismatch (e.g., Notifications under "Automation", Billing accessible from two places) creates friction for routine tasks.

## Goals / Non-Goals
- Goals: Reduce settings locations to 4 logical groups; every setting reachable within 2 clicks from sidebar; remove duplication
- Non-Goals: Changing any API behavior; redesigning settings forms themselves; adding new settings

## Decisions
- Decision: Group by domain concern, not by technical level
  - "Your Account" = things about YOU (profile, password, billing, team)
  - "Automation" = things that RUN automatically (rules, schedules, notification channels)
  - "Connections" = things that CONNECT externally (devices, integrations)
  - "Library" = reference data (strains, grow types, reference docs)
- Decision: Keep existing URL paths where possible, add redirects for any that move
  - Avoids breaking bookmarks or shared links
- Decision: Single settings index page acts as hub with search
  - Users who don't know where something lives can find it quickly
- Alternatives considered:
  - Single mega-settings page with all sections as tabs → rejected (too overwhelming, 12+ tabs)
  - Keep current structure but add search → rejected (doesn't fix navigation confusion)

## Risks / Trade-offs
- Users with muscle memory for current locations will need to re-learn → mitigate with redirects and toast notifications
- Mobile bottom nav has limited slots → mitigate by making settings a gear icon leading to hub page

## Open Questions
- Should "Audit Trail" remain a top-level page or move under Account?
- Should "Grow Types" be under Library or under a "Growing" group alongside Strains?
