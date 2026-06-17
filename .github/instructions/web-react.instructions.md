---
description: Tendril web (Next.js + React + Base UI) conventions — auto-attached to TSX/TS files under web/src.
applyTo: "web/src/**/*.{ts,tsx}"
---

# Tendril Web — Per-file rules

Read [`web/AGENTS.md`](../../web/AGENTS.md) first. The Next.js APIs in this workspace differ from public docs; check `web/node_modules/next/dist/docs/` before guessing.

## API client
- All API calls go through `web/src/lib/api-types.ts` (generated from FastAPI OpenAPI). **Never** hand-write request/response types that duplicate it.
- After any backend route change, regenerate: `cd web && npm run gen:types`. Commit the diff in the same PR.

## Base UI Select gotchas
- `@base-ui/react` `Select` items render in a Portal — they don't mount until the dropdown opens.
- `SelectValue` cannot resolve the label on first render when the value is a UUID. **Don't use `<SelectValue>` for ID-valued selects.** Render the label manually:
  ```tsx
  <SelectTrigger>
    <span>{selectedItem?.name ?? "Placeholder"}</span>
  </SelectTrigger>
  ```
- `SelectValue` ignores JSX children. Only the `placeholder` prop renders for the empty state.

## Server vs Client components
- Default to Server Components. Add `"use client"` only when the component needs hooks, state, browser APIs, or event handlers.
- Don't import server-only modules (e.g. anything reading env vars or hitting the DB directly) into a client component.

## Styling
- Tailwind v4 — utility classes only, no separate CSS modules for new work.
- Use the design-token classes from `globals.css` (e.g. `bg-surface`, `text-muted`) rather than raw Tailwind colors where a token exists.

## Tests
- Unit: `vitest` (`npm test`). Component tests live next to the component.
- E2E: Playwright in `web/e2e/`. Run with `./scripts/run-qa.sh` from repo root.

## Lint
- `npm run lint` is the blocking CI gate. ESLint config is `eslint.config.mjs`.
