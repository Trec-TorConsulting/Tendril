# Proposal: redesign-tendril-ui

## Summary
Full UI/UX design system overhaul of the Tendril web frontend to be mobile-first, modern, and highly usable. The current UI is functional but desktop-adapted with critical mobile navigation gaps, non-interactive cards, no form validation, and dark-mode only.

## Motivation
- Mobile is the primary usage mode — users log readings, check health, and chat with AI from their phone while tending grows
- Current bottom nav "More" tab dead-ends at Tents; 10+ sections unreachable without hamburger sidebar
- Cards are not tappable — users must find small icon buttons for actions
- `window.confirm()` breaks the dark theme aesthetic on mobile
- No light mode despite `next-themes` being installed
- No form validation — errors only surface after failed API calls
- Grow detail page has 8 sub-tabs and 15+ dialog states in one component

## Scope

### Phase 1: Navigation & Shell (this change)
- **4-tab bottom nav + center FAB** for quick actions (Log Reading, Health Check, Quick Photo, Log Ambient)
- **"More" tab opens a sheet** with remaining navigation items (not direct navigation)
- **Light/dark theme toggle** with system preference auto-detection
- **Clickable cards** — entire card surface navigates to detail view
- **Custom AlertDialog** replacing all `window.confirm()` calls
- **Subtle animations** via framer-motion (page transitions, tap feedback)

### Phase 2: Page-by-page redesign (future change)
- Dashboard hero card with active grow snapshot
- Grow detail page refactor (scrollable pill tabs, condensed layout)
- Form validation with react-hook-form + zod
- Loading skeletons on all pages
- Empty state polish

### Phase 3: Polish (future change)
- Gesture support (swipe to complete tasks, pull to refresh)
- Onboarding flow for new users
- Customizable dashboard widgets

## Design Decisions

### Bottom Nav: 4 tabs + center FAB
Inspired by productivity apps. The FAB provides instant access to the 3 most common mobile actions (log reading, health check, chat) without navigating away from the current page.

```
┌──────────────────────────────────────┐
│  Home    Grows    [+]    AI    More  │
└──────────────────────────────────────┘
```

### Theme: System-aware light/dark
Use `next-themes` (already installed) with `attribute="class"` and `defaultTheme="system"`. Green primary accent works in both modes.

### Card Interaction: Navigate on tap
Entire card surface is a `<Link>` or clickable div. Destructive actions (delete) remain in dropdown menus to prevent accidental triggers.

### Animations: Subtle via framer-motion
- Page enter/exit: fade + slight translateY
- Card tap: scale spring (0.98 → 1.0)
- FAB expand: spring animation for menu items
- Sheet/dialog: smooth enter/exit

## Dependencies Added
- `framer-motion` — animation library
- (react-hook-form + zod deferred to Phase 2)

## Risk
- Low risk: all changes are frontend-only, no API or DB changes
- Rollback: git revert to previous commit

## Status
- [x] Approved
