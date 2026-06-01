# Proposal: redesign-field-canvas

## Summary

Replace the current CSS-grid-based Plot Designer with a modern, draw.io-style infinite canvas for outdoor field layout. Users drag pre-defined items (raised beds, irrigation lines, trees, sensors, etc.) onto a free-placement canvas with optional grid snapping, connectors with flow direction, toggleable layers, and zoom/pan controls.

## Motivation

The current `PlotDesigner` uses a fixed-dimension CSS grid with paint/erase tools. While functional, it feels dated and rigid:
- Cannot represent non-rectangular or free-form garden layouts
- No way to show irrigation flow or connections between elements
- No layering (irrigation lines overlap with planting zones)
- Limited item types (6 cell types)
- Not intuitive for first-time users

Outdoor gardens are inherently freeform. A draw.io-style canvas with a rich palette of pre-defined items is far more natural and powerful.

## Scope

- **Replaces entirely**: Current `PlotDesigner` component removed
- **Frontend only for Phase 1**: New canvas component with local state + existing API
- **API schema updates**: Extend `plot_grids` / `plot_cells` tables to store freeform elements, connectors, and layers
- **Desktop-first**: Full editing on desktop; mobile gets simplified read-only view with basic pan/zoom

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Canvas library | **react-konva** (Konva.js) | Built-in layers, drag/drop, transformers, touch support, custom shapes, arrows/lines. Mature & performant. |
| Placement model | Free with optional grid snap | Toggle-able snap grid (configurable spacing). Hold Shift to override. |
| Connectors | Directional arrows | Irrigation flow, electrical, etc. Attach to shape anchor points. |
| Layers | Multiple toggleable | Ground, Planting, Irrigation, Structures, Sensors |
| Data persistence | JSON blob per canvas | Store full canvas state as JSON (elements + connectors + layers + viewport) |
| Mobile | Read-only pan/zoom + tap info | Full editing requires desktop |

## Pre-defined Item Palette

Organized into categories in a collapsible sidebar:

### Beds & Planting
- Raised beds (4×4, 4×8, custom size)
- In-ground rows (variable length)
- Individual plant markers
- Companion planting zones
- Cover crop areas
- Container / pot

### Trees & Structures
- Trees / shrubs (fruit, shade, windbreak)
- Trellises / support structures
- Greenhouse / hoop house
- Shed / storage building
- Fencing / property boundaries
- Compost bin

### Water & Irrigation
- Water spigot / hose bib
- Rain barrel / water tank
- Drip line (connector)
- Sprinkler head
- Soaker hose (connector)
- Irrigation valve

### Infrastructure
- Walkways / paths (variable width)
- Outdoor grow lights
- Sensor locations (temp, soil, humidity)
- Power outlet
- Camera location

### Decorative / Other
- Bench / seating
- Pond / water feature
- Rock / boulder
- Garden art / marker
- Label / text annotation

## Non-Goals

- 3D visualization (future consideration)
- Real-time multiplayer editing
- Plant growth simulation on canvas
- Auto-layout / AI-suggested placement (future v2)

## Affected Areas

- `web/src/components/outdoor/plot-designer.tsx` → **removed**, replaced by new `field-canvas/` component tree
- `web/src/app/dashboard/grows/[id]/field-tab.tsx` → updated to mount new canvas
- `api/app/grows/plot_routes.py` → new endpoints for canvas persistence
- `api/app/grows/models.py` → new `FieldCanvas` / `FieldElement` models
- Database migration: new tables for canvas data
- `web/package.json` → add `react-konva`, `konva` dependencies

## Success Criteria

- User can design a complete outdoor garden layout in under 5 minutes
- All 17+ item types available in draggable palette
- Connectors show irrigation flow direction
- Layers can be toggled independently
- Canvas persists across sessions
- Loads in < 2s with 100+ elements
- Works on iPad/tablet in read-only mode
