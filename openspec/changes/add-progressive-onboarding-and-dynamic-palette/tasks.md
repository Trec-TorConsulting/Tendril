## 1. Progressive onboarding
- [ ] 1.1 Model onboarding as a progression of milestones (account created → tent → grow → device → first log → first health check) rather than a one-time wizard.
- [ ] 1.2 Persist onboarding progress (reuse profile/preferences; optionally a profile field) so it survives sessions and devices.
- [ ] 1.3 Update `onboarding-checklist.tsx` to reflect completed milestones dynamically and always show the single next recommended step.
- [ ] 1.4 In `use-layout-mode.tsx`, advance layout complexity as milestones complete (e.g., beginner → home → standard), while allowing manual override in settings.
- [ ] 1.5 Re-surface the checklist/next step contextually after inactivity instead of only on first login.

## 2. Dynamic command palette — ranking
- [ ] 2.1 Track page/action recency and frequency (localStorage) and rank palette results by a combined recency+frequency score, keeping exact-match search behavior.
- [ ] 2.2 Boost the currently selected grow's related entities (its tent, devices, strains) toward the top.

## 3. Dynamic command palette — contextual actions
- [ ] 3.1 Add a contextual-action rules module that, given the selected grow's stage/state, suggests relevant actions (e.g., "Run health check", "Log trichomes" in flower/ripening, "Confirm 12/12 flip" when applicable), reusing existing endpoints/routes.
- [ ] 3.2 Surface a "Suggested" section at the top of the palette with these actions.

## 4. Testing
- [ ] 4.1 Unit tests for milestone progression and layout advancement (with manual override respected).
- [ ] 4.2 Tests for palette ranking (recency/frequency ordering; selected-grow boosting).
- [ ] 4.3 Tests for contextual action suggestions by stage (harvest actions in flower, hidden in veg).
- [ ] 4.4 Component tests for the updated checklist and palette suggested section.

## 5. Validation
- [ ] 5.1 Run `openspec validate add-progressive-onboarding-and-dynamic-palette --strict --no-interactive`.
- [ ] 5.2 Run `npm run lint` and `npm test` (web); ensure pass.
