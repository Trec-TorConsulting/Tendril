# Tasks: redesign-field-canvas

## Phase 1: Foundation

- [ ] Install dependencies (`konva`, `react-konva`, `zustand`)
- [ ] Create `web/src/components/field-canvas/types.ts` with all interfaces
- [ ] Create Zustand store (`use-canvas-state.ts`) with elements, connectors, layers, viewport, tool state
- [ ] Implement undo/redo middleware in store (`use-history.ts`)
- [ ] Create `canvas-stage.tsx` — Konva Stage with zoom/pan, grid overlay, layer rendering
- [ ] Create `base-element.tsx` — draggable/selectable/resizable wrapper using Konva Transformer

## Phase 2: Element Shapes

- [ ] `raised-bed.tsx` — resizable rectangle with dimension label, fill color by layer
- [ ] `ground-row.tsx` — elongated rect with row count indicator
- [ ] `plant-marker.tsx` — circle icon with plant name tooltip
- [ ] `tree-shape.tsx` — circle (canopy) + small trunk rect, scalable
- [ ] `structure-shape.tsx` — labeled rectangle (shed, greenhouse, hoop house)
- [ ] `fence-line.tsx` — polyline with posts (multi-point)
- [ ] `path-shape.tsx` — thick polyline with variable width
- [ ] `water-source.tsx` — icon shapes (spigot, barrel, tank)
- [ ] `sensor-marker.tsx` — small badge icon with type indicator
- [ ] `irrigation-head.tsx` — sprinkler/valve icon with radius indicator
- [ ] `text-label.tsx` — editable text node on canvas
- [ ] `generic-icon.tsx` — fallback SVG icon renderer for misc items (compost, bench, light, etc.)

## Phase 3: Palette & Toolbar

- [ ] Create `palette-sidebar.tsx` — categorized collapsible item list with icons
- [ ] Implement drag-from-palette to canvas (ghost preview on cursor)
- [ ] Implement click-to-place mode from palette
- [ ] Create `toolbar.tsx` — tool buttons (Select, Pan, Connect), snap toggle, zoom controls
- [ ] Implement grid snap logic (`use-snap-grid.ts`) with configurable increment
- [ ] Create `layers-panel.tsx` — layer visibility/lock toggles, active layer selector, reorder

## Phase 4: Connectors

- [ ] Create `anchor-points.tsx` — show connection points on hover/select (top/right/bottom/left)
- [ ] Create `connector-line.tsx` — Konva Arrow/Line between two anchors
- [ ] Implement Connect tool interaction (click source anchor → drag → release on target)
- [ ] Support line types: straight, elbow (orthogonal), curve
- [ ] Add flow direction indicator (animated dots or arrowhead)
- [ ] Connector label support (text along line)

## Phase 5: Properties & Editing

- [ ] Create `properties-panel.tsx` — context panel for selected element properties
- [ ] Element-specific property forms (e.g. bed dimensions, plant link to bucket, sensor device link)
- [ ] Multi-select actions: align, distribute, group, delete
- [ ] Implement keyboard shortcuts (`use-keyboard.ts`)
- [ ] Right-click context menu (duplicate, delete, lock, move to layer, bring forward/back)

## Phase 6: Persistence & API

- [ ] Create Alembic migration: `field_canvases` table with JSONB, RLS policy
- [ ] Create `api/app/grows/field_canvas_routes.py` — CRUD endpoints
- [ ] Add route to grows router
- [ ] Implement `use-persistence.ts` — debounced auto-save (2s), loading state, conflict detection
- [ ] Thumbnail generation on save (`stage.toDataURL()` → upload to S3)

## Phase 7: Integration & Cleanup

- [ ] Update `field-tab.tsx` to mount `FieldCanvas` instead of `PlotDesigner`
- [ ] Migration banner: detect old plot_grid, offer conversion
- [ ] Implement old grid → canvas element conversion logic
- [ ] Remove `plot-designer.tsx` (keep API routes for backward compat)
- [ ] Mobile responsive: read-only canvas with pan/zoom, properties popover on tap
- [ ] Desktop breakpoint: full editing UI

## Phase 8: Polish & Testing

- [ ] Add loading skeleton for canvas
- [ ] Empty state with onboarding prompt ("Design your field — drag items from the palette")
- [ ] Vitest unit tests for store logic (add/remove/undo/redo/snap)
- [ ] Playwright e2e test: create canvas, add elements, save, reload, verify persistence
- [ ] Performance test: 200+ elements render < 16ms frame time
- [ ] Accessibility: keyboard navigation for palette, ARIA labels on toolbar buttons
