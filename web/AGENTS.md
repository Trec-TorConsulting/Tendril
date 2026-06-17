<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# Tendril Web — Agent Guide

Next.js **16** + React **19** + TypeScript + Tailwind **v4** + Base UI + shadcn. Multi-tenant PWA dashboard for the Tendril API.

> Cross-references: [`api/AGENTS.md`](../api/AGENTS.md) for the backend, [`AGENTS.md`](../AGENTS.md) and [`openspec/AGENTS.md`](../openspec/AGENTS.md) for spec workflow.

## Stack

| Concern | Choice |
|---|---|
| Framework | Next.js 16 (App Router, Turbopack, `output: "standalone"`) |
| UI primitives | `@base-ui/react` (Select, Dialog, Tooltip, etc.) |
| Component library | shadcn (style `base-nova`, neutral base) in `src/components/ui/` |
| Styling | Tailwind v4 (CSS-only config in `globals.css`), `tw-animate-css` |
| State / data | SWR (`@/lib/swr`), Zustand for local UI state |
| Forms | React Hook Form + Zod resolvers |
| Charts | Recharts (+ Konva for the field canvas) |
| Auth | httpOnly cookies + CSRF token header (no localStorage) |
| Offline | Service worker + IndexedDB queue (`@/lib/offline-queue`) + Background Sync |
| Tests | Vitest + Testing Library (unit), Playwright (e2e) |

## Layout

```
web/
  src/
    app/                    # App Router
      (auth)/               # Sign-in / sign-up — route group, no layout shell
      (marketing)/          # Public landing — separate layout
      dashboard/            # Authenticated app — wraps everything in AppSWRProvider
      platform/             # Platform-admin pages
      api/                  # Next route handlers (proxy/edge work only — real API is FastAPI)
      layout.tsx            # Root layout (theme, fonts, providers, service worker)
      globals.css           # Tailwind v4 entry + theme tokens (CSS variables)
    components/
      ui/                   # shadcn primitives (button, card, dialog, select, …)
      <feature>/            # Feature-scoped composites
      *.tsx                 # Top-level shared (app-sidebar, page-header, …)
    hooks/                  # use-* React hooks
    lib/
      api.ts                # apiFetch — central HTTP client
      api-types.ts          # GENERATED from FastAPI OpenAPI — never hand-edit
      auth.ts               # CSRF + cookie sentinel helpers
      swr.tsx               # AppSWRProvider + useApiSWR + useEvictCache
      offline-queue.ts      # IndexedDB-backed mutation queue
      units.ts / vpd.ts / humidity-thresholds.ts / nutrient-brands.ts / terminology.ts
    test/                   # Vitest setup (jsdom)
    __tests__/              # Unit tests
  e2e/                      # Playwright suites (01-auth.spec.ts … 12-layout-system.spec.ts)
  public/
  components.json           # shadcn CLI config
  next.config.ts            # output: standalone; ignoreBuildErrors: true (CI runs tsc separately)
  eslint.config.mjs         # Most rules downgraded to warnings (incremental cleanup)
  vitest.config.ts          # jsdom, @/* alias = src/*
  playwright.config.ts      # 3 engines × 6 viewports + PWA standalone
  Dockerfile
```

`@/*` is the path alias for `src/*` (configured in `tsconfig.json` + `vitest.config.ts`).

## Commands

All from `web/`.

```bash
npm ci --legacy-peer-deps   # install (CI flag also required locally — React 19 peer deps)

npm run dev                 # Next dev server on :3000 (Turbopack)
npm run build               # Standalone production build
npm run start               # Run the built server

npm run lint                # ESLint (blocking CI gate)
npm run type-check          # tsc --noEmit (separate from build — see "Pitfalls")

npm test                    # vitest watch
npm run test:run            # vitest one-shot (for CI / pre-commit)

npm run gen:types           # Regenerate src/lib/api-types.ts from FastAPI OpenAPI
npm run verify:types        # Diff regenerated vs committed (CI uses this exact command)

npm run qa                  # Full Playwright matrix (slow)
npm run qa:chromium         # Chromium projects only
npm run qa:mobile           # Mobile viewports only
npm run qa:report           # Open last HTML report

# From repo root:
./scripts/run-qa.sh         # Friendly QA wrapper — checks services, runs Playwright
```

## Conventions

### Server vs Client Components
- Default to Server Components. Add `"use client"` only when you need hooks, state, browser APIs, or event handlers.
- Don't import server-only modules (anything reading env vars, hitting the DB, or pulling Node-only packages) into client components.
- Files using `useApiSWR`, `useState`, `useEffect`, etc., are client components.

### Route groups
- `(auth)` and `(marketing)` are parenthesised — they do **not** add URL segments. They exist so each can have a different `layout.tsx` (no sidebar, etc.).
- Authenticated routes live under `dashboard/` and inherit `dashboard/layout.tsx` (mounts `AppSWRProvider`, sidebar, theme, etc.).

### API access
- All HTTP goes through `apiFetch` in [`src/lib/api.ts`](src/lib/api.ts).
  - Sets `credentials: "include"` so httpOnly auth cookies travel automatically.
  - Adds `X-CSRF-Token` header on POST/PUT/PATCH/DELETE.
  - Retries safe methods on `502/503/504/408/429` with exponential backoff.
  - Auto-refreshes on `401` and replays the request once.
  - 15s default timeout via `AbortController`.
- Response/request types come from [`src/lib/api-types.ts`](src/lib/api-types.ts) — **generated**, never hand-edited. Any backend route change requires `npm run gen:types` in the same PR.

### Data fetching (SWR)
- Wrap fetches with `useApiSWR(['cache', 'key'], (token) => apiCall(token))` from [`@/lib/swr`](src/lib/swr.tsx).
- The hook folds the current access token into the cache key — sign-out automatically evicts that user's cache.
- `AppSWRProvider` is mounted by `dashboard/layout.tsx`. Defaults: revalidate on focus, no retry on error, 5s dedupe.
- For sign-out flows, call `useEvictCache()` to clear everything.

### Auth state
- Tokens live in **httpOnly cookies**, set by the API. JS cannot read them (XSS defence).
- `getAccessToken()` is a legacy shim — returns the string `"cookie"` if authenticated, `null` otherwise. Do not introduce new code that expects a real JWT in JS.
- CSRF token is in a non-httpOnly cookie (`csrf_token=`) plus an in-memory cache, both managed by [`@/lib/auth`](src/lib/auth.ts). The API client wires it into the `X-CSRF-Token` header on unsafe methods.

### Styling
- Tailwind v4 — utility classes only. **No** `tailwind.config.js`; tokens live in `src/app/globals.css` via `@theme inline`.
- Use the design-token classes, not raw Tailwind colors:
  - `bg-background` / `text-foreground` / `text-muted-foreground`
  - `bg-card` / `bg-popover` / `bg-primary` / `text-primary-foreground`
  - `border-border` / `ring-ring` / `bg-destructive`
  - `bg-sidebar` / `text-sidebar-foreground`
- Theme is OKLCH-based with first-class dark mode (`.dark` class, controlled by `next-themes`).
- Class merging: `cn()` from `@/lib/utils` (clsx + tailwind-merge).

### UI components
- shadcn primitives in `src/components/ui/` are the building blocks. Re-style by editing the file in place — they're owned, not vendored.
- Composites use Base UI directly when shadcn doesn't cover the case. Lucide for icons (`iconLibrary: lucide`).
- Toaster: `sonner` (top-right, rich colors), mounted in root layout.

### Forms
- React Hook Form + `@hookform/resolvers` + Zod schemas. Schemas live next to the form they validate.
- Server validation errors come back as `ApiError` — surface via `toast.error(err.detail)`.

### PWA / Offline
- Service worker is registered by `ServiceWorkerRegistration` (mounted in root layout).
- Mutations that should survive an offline reload enqueue via `enqueue({ url, method, headers, body, description })` from [`@/lib/offline-queue`](src/lib/offline-queue.ts).
- Background Sync is opportunistic — never assume it fires; the next online navigation also drains the queue.
- `manifest.json` is in `public/`. `themeColor` (#16a34a) and `appleWebApp` are set in root layout.

### Base UI Select gotchas
The [`web-react.instructions.md`](../.github/instructions/web-react.instructions.md) covers this in detail. Summary:
- `Select.Item` mounts inside a Portal — it doesn't exist on first render.
- `<SelectValue>` cannot resolve a UUID-valued selection on first paint. Render the label manually: `<SelectTrigger><span>{selectedItem?.name ?? "Placeholder"}</span></SelectTrigger>`.
- `<SelectValue>` ignores JSX children — only `placeholder` works.

### Testing
- **Unit (vitest)**: jsdom, `globals: true`, setup in `src/test/setup.ts`. Tests live in `src/__tests__/` or next to the component.
- **E2E (Playwright)**: numbered suites in `e2e/`. The full matrix runs 3 browsers × 6 viewports + PWA mode. Local dev: `npm run qa:chromium` for speed.
- The full QA wrapper [`scripts/run-qa.sh`](../scripts/run-qa.sh) checks API + web are reachable before launching the suite.

## Pitfalls

- **`next.config.ts` has `typescript.ignoreBuildErrors: true`.** This is intentional — `next build` crashes from OOM during Docker cross-compile when type-checking. CI runs `npm run type-check` (`tsc --noEmit`) as a separate gate. Don't rely on `next build` to catch TS errors locally; run `npm run type-check`.
- **`--legacy-peer-deps` is required** to install. React 19 peer-dep conflicts with some libs.
- **ESLint is intentionally permissive** for now: `no-explicit-any`, `no-unused-vars`, several `react-hooks/*` rules, and `@next/next/no-img-element` are downgraded to warnings while we clean up. Don't add new violations; fix nearby ones when you touch a file.
- **No localStorage for auth.** If you find yourself reaching for `localStorage.getItem("token")`, you're working against the auth model. Use the cookie + `apiFetch`.
- **Don't bypass `apiFetch`** with raw `fetch()` for API calls — you'll lose CSRF, retries, 401 refresh, and timeout handling.
- **`useApiSWR` is the only sanctioned way** to do cached reads. Hand-rolling `useEffect` + `fetch` defeats the cache-eviction-on-signout contract.
- **Generated `api-types.ts` is large.** Diffs should be small and explainable. A huge diff means you regenerated against the wrong branch or stale Python env — see [`.github/prompts/regen-api-types.prompt.md`](../.github/prompts/regen-api-types.prompt.md).
- **Mobile-first.** The dashboard ships a `mobile-bottom-nav` + viewport `userScalable: false`. Test mobile breakpoints before desktop polish.
- **Route groups don't show in URLs.** Moving a page from `dashboard/` to `(auth)/` changes the layout, not the URL — confirm both behaviors.
