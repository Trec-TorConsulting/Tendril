## Context
The grow-assistant frontend is a single `index.html` file (~4,800 lines) containing all HTML, CSS, and JS. It started as a camera-monitoring + chat tool and grew to include 15+ major features. The UI pattern (tent tabs → 7 sub-tabs → modals/overlays) doesn't scale and buries key features. This redesign restructures the frontend into a modular, navigable app without introducing framework dependencies.

## Goals
- Every major feature reachable in ≤ 2 clicks from any screen
- Active grows show live data (not empty until archived)
- Mobile-first responsive layout (PWA standalone mode is primary target)
- Split monolith HTML into modular JS files loaded via `<script>` tags
- Consistent card-based design language across all views
- Keep vanilla JS/CSS — no React, Vue, or build tools required
- Light and dark mode with system preference detection and manual toggle
- Camera snapshot remains the hero/largest element on the Dashboard
- Use Chart.js (~60KB) for all charts — better visuals, less custom code

## Non-Goals
- Backend API redesign (existing endpoints stay, minor additions only)
- Framework adoption (no React/Vue/Svelte)
- SSR or code bundling (no webpack/vite/esbuild)
- Authentication (separate spec exists)
- New features beyond what's already built

## Decisions

### Decision: Hash-based routing instead of full SPA router
Use `window.location.hash` for view switching (`#dashboard`, `#grows`, `#buckets/b1`, etc.) with a simple router function. No history API pushState needed — hash routing works offline in PWA, requires no server config, and survives page refreshes.

**Alternatives considered:**
- History API pushState — requires server-side catch-all route, complicates offline caching
- URL params — no back-button support, poor UX
- Keep current tab switching — doesn't scale, already proven inadequate

### Decision: Modular JS files instead of single HTML
Split into separate JS files loaded via `<script>` tags in order. No ES modules (avoids CORS issues with service worker caching). Files share global state via a `window.App` namespace.

**File structure:**
```
app/static/
├── index.html          # Shell: nav, view containers, <script> tags
├── css/
│   └── app.css         # All styles (extracted from HTML)
├── js/
│   ├── state.js        # Global state, API helper, router, toast
│   ├── dashboard.js    # Dashboard view
│   ├── grows.js        # Grow manager view
│   ├── buckets.js      # Bucket list + detail views
│   ├── strains.js      # Strain library view
│   ├── feeding.js      # Feeding schedule planner
│   ├── analytics.js    # Analytics / charts / export
│   ├── settings.js     # Settings modal + PWA controls
│   ├── chat.js         # Chat panel (slide-out)
│   └── health.js       # Health checks + alerts
├── sw.js               # Service worker (exists)
├── manifest.json       # PWA manifest (exists)
├── icon-192.png        # (exists)
└── icon-512.png        # (exists)
```

**Alternatives considered:**
- ES modules with import/export — CORS issues with file:// and some SW scenarios
- Bundler (vite) — adds build step, increases image size, violates "no build tools" constraint
- Keep single file — already at 4,800 lines, unmaintainable

### Decision: Bottom navigation bar for mobile
Primary nav uses a fixed bottom bar (5 icons) on mobile and a left sidebar on wider screens. This matches native mobile app patterns and works well in PWA standalone mode.

**Navigation items (5):**
1. 🏠 Dashboard — score card, environment, alerts, recent activity
2. 🌱 Grows — active/archived grows, start/archive/compare
3. 🪣 Buckets — grid of all buckets, click → tabbed detail
4. 📊 Analytics — crop steering, sensor trends, score history, CSV export
5. 💬 Chat — AI assistant (slides in from right)

**Secondary nav (accessible from views):**
- 🌿 Strains — accessible from Grows and Bucket detail
- 🍽️ Feeding — accessible from Bucket detail and Grows
- ⚙️ Settings — header icon
- 🏥 Health — accessible from Dashboard

### Decision: Active grows show live bucket data
Modify `GET /api/grows/{id}` to return live bucket data (sensors, journal, photos) when the grow is active, instead of only returning the archived snapshot. Uses the grow's `start_date` and tent's current buckets to query live data. Archive snapshot behavior unchanged for completed grows.

### Decision: Tent selection via settings, not top-level tabs
Multi-tent support moves from top-level tabs to a tent selector in the header or settings. Most users have 1-2 tents — making tents the primary navigation wastes space. All views filter by the currently selected tent.

## Risks / Trade-offs
- **Risk**: Existing `index.html.bak` and `mockup.html` may reference old patterns → Mitigation: Keep old `index.html` as `index.html.v1` backup during transition
- **Risk**: Service worker cache invalidation when file structure changes → Mitigation: Bump `CACHE_VERSION` in sw.js, add new JS/CSS files to `APP_SHELL`
- **Risk**: Multiple JS files increase HTTP requests → Mitigation: Only 10 small files, all cached by SW after first load. Acceptable for a LAN-deployed app
- **Trade-off**: No hot module reload during development → Acceptable given no build step requirement

### Decision: Chart.js for data visualization
Use Chart.js (CDN or bundled ~60KB) for sensor charts, score history, and analytics. Replaces hand-drawn canvas charts.

**Alternatives considered:**
- Hand-drawn canvas — current approach, works but tedious, limited interactivity
- D3.js — overkill for this use case, steep learning curve
- uPlot — smaller but less documentation, fewer chart types

### Decision: Light and dark mode
Offer both light and dark themes with automatic detection via `prefers-color-scheme` media query. Manual toggle in settings, persisted in localStorage. CSS custom properties (`--bg`, `--surface`, `--card`, etc.) already exist — add complementary light-mode values.

### Decision: Camera as dashboard hero
Camera snapshot stays the largest element on the Dashboard view, spanning full width above the info cards. This preserves the visual-first monitoring workflow that defines the app.

## Open Questions
- None — all decisions are scoped to restructuring existing features with no new functionality
