# Design: redesign-field-canvas

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  FieldTab                                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │  FieldCanvas (main orchestrator)                  │  │
│  │  ┌──────────┐  ┌─────────────────────────────┐   │  │
│  │  │ Palette  │  │  Konva Stage                 │   │  │
│  │  │ Sidebar  │  │  ┌─────────────────────────┐ │   │  │
│  │  │          │  │  │ Layer: Ground            │ │   │  │
│  │  │ [Beds]   │  │  │ Layer: Planting          │ │   │  │
│  │  │ [Water]  │  │  │ Layer: Irrigation        │ │   │  │
│  │  │ [Struct] │  │  │ Layer: Structures        │ │   │  │
│  │  │ [Infra]  │  │  │ Layer: Sensors           │ │   │  │
│  │  │ [Other]  │  │  └─────────────────────────┘ │   │  │
│  │  └──────────┘  └─────────────────────────────────┘   │  │
│  │  ┌───────────────────────────────────────────────┐   │  │
│  │  │ Toolbar: Select|Pan|Connect|Snap|Zoom|Layers │   │  │
│  │  └───────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Component Tree

```
web/src/components/field-canvas/
├── index.tsx                    # Main FieldCanvas export
├── canvas-stage.tsx             # Konva Stage + Layer management
├── palette-sidebar.tsx          # Categorized item palette
├── toolbar.tsx                  # Tool selection bar
├── layers-panel.tsx             # Layer visibility toggles
├── properties-panel.tsx         # Selected element properties
├── connectors/
│   ├── connector-line.tsx       # Arrow/line between elements
│   └── anchor-points.tsx        # Connection anchor dots on shapes
├── elements/
│   ├── base-element.tsx         # Shared drag/transform/select behavior
│   ├── raised-bed.tsx           # Rectangular bed with size label
│   ├── ground-row.tsx           # Long thin planting row
│   ├── plant-marker.tsx         # Individual plant icon
│   ├── tree-shape.tsx           # Circle/canopy shape
│   ├── structure-shape.tsx      # Generic rectangle (shed, greenhouse)
│   ├── fence-line.tsx           # Multi-point line shape
│   ├── path-shape.tsx           # Variable-width path
│   ├── water-source.tsx         # Spigot/barrel/tank icon
│   ├── sensor-marker.tsx        # Sensor icon with type badge
│   ├── irrigation-head.tsx      # Sprinkler/valve icon
│   ├── text-label.tsx           # Free text annotation
│   └── generic-icon.tsx         # Fallback for misc items
├── hooks/
│   ├── use-canvas-state.ts      # Zustand store for canvas state
│   ├── use-snap-grid.ts         # Grid snapping logic
│   ├── use-keyboard.ts          # Keyboard shortcuts
│   ├── use-history.ts           # Undo/redo stack
│   └── use-persistence.ts      # Auto-save debounce + API calls
└── types.ts                     # All canvas type definitions
```

## Data Model

### Frontend State (Zustand store)

```typescript
interface CanvasState {
  // Viewport
  stageX: number;
  stageY: number;
  scale: number;

  // Elements
  elements: FieldElement[];
  connectors: Connector[];
  layers: LayerConfig[];

  // Selection
  selectedIds: Set<string>;
  tool: 'select' | 'pan' | 'connect';

  // Settings
  snapEnabled: boolean;
  snapSize: number; // px
  showGrid: boolean;
}

interface FieldElement {
  id: string;
  type: string;           // e.g. "raised_bed", "tree", "sensor"
  layerId: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  props: Record<string, unknown>; // Type-specific (plant name, sensor id, etc.)
  locked: boolean;
  visible: boolean;
}

interface Connector {
  id: string;
  layerId: string;
  fromId: string;
  fromAnchor: 'top' | 'right' | 'bottom' | 'left';
  toId: string;
  toAnchor: 'top' | 'right' | 'bottom' | 'left';
  flowDirection: 'forward' | 'reverse' | 'none';
  lineType: 'straight' | 'elbow' | 'curve';
  label?: string;
  props: Record<string, unknown>; // e.g. { pipeType: "drip", diameter: "0.5in" }
}

interface LayerConfig {
  id: string;
  name: string;
  visible: boolean;
  locked: boolean;
  color: string; // Theme color for layer badge
  order: number;
}
```

### Database Schema

```sql
-- Replace plot_grids with field_canvas
CREATE TABLE field_canvases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    grow_cycle_id UUID NOT NULL REFERENCES grow_cycles(id),
    name VARCHAR(255) DEFAULT 'Main Field',
    canvas_data JSONB NOT NULL DEFAULT '{}',  -- Full CanvasState
    thumbnail_key VARCHAR(1024),              -- S3 key for preview image
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (grow_cycle_id)  -- One canvas per grow for now
);

-- RLS policy
ALTER TABLE field_canvases ENABLE ROW LEVEL SECURITY;
CREATE POLICY field_canvases_tenant ON field_canvases
    USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

The entire canvas state is stored as a single JSONB document. This is deliberate:
- Canvas edits are frequent (debounced auto-save every 2s of inactivity)
- No need to query individual elements server-side
- Simple upsert semantics
- Element-level queries (if needed later) can use JSONB operators

### API Endpoints

```
GET    /v1/grows/{grow_id}/field-canvas       → FieldCanvasResponse | 404
PUT    /v1/grows/{grow_id}/field-canvas       → Upsert full canvas
DELETE /v1/grows/{grow_id}/field-canvas       → Delete canvas
POST   /v1/grows/{grow_id}/field-canvas/thumbnail  → Upload PNG thumbnail
```

## Interaction Model

### Adding Elements
1. User opens palette sidebar (collapsible)
2. Clicks an item → cursor becomes placement mode
3. Click on canvas to place at default size
4. **OR** drag from palette directly onto canvas (ghost preview follows cursor)
5. After placement, element is selected with resize handles

### Selecting & Transforming
- Click to select, Shift+Click for multi-select
- Drag selection box for area select
- Selected elements show: resize handles, rotation handle, anchor points
- Delete key removes selected
- Ctrl+D duplicates selected

### Connecting Elements
1. Switch to Connect tool (or hover anchor point in Select mode)
2. Click source anchor → drag to target anchor
3. Arrow appears with flow direction indicator
4. Click connector to edit: line type, label, flow direction

### Pan & Zoom
- Scroll wheel to zoom (centered on cursor)
- Middle-click drag or Space+drag to pan
- Pinch-to-zoom on touch devices
- Minimap in corner (optional, v2)

### Grid Snap
- Toggle via toolbar button or `G` key
- Configurable snap increment (6", 12", 24")
- Visual grid overlay when enabled
- Elements snap to nearest grid point on release

### Layers
- 5 default layers: Ground, Planting, Irrigation, Structures, Sensors
- Layer panel shows visibility toggles (eye icon) and lock toggles
- Active layer highlighted — new elements go to active layer
- Locked layers prevent selection/editing
- User can reorder layers (drag in panel)

### Undo/Redo
- Ctrl+Z / Ctrl+Shift+Z
- History stack of canvas state snapshots (max 50)
- Each action (move, add, delete, connect, property change) creates a snapshot

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| V | Select tool |
| H | Pan tool |
| C | Connect tool |
| G | Toggle grid snap |
| Del/Backspace | Delete selected |
| Ctrl+D | Duplicate |
| Ctrl+Z | Undo |
| Ctrl+Shift+Z | Redo |
| Ctrl+A | Select all (active layer) |
| Ctrl+S | Force save |
| +/- | Zoom in/out |
| 0 | Fit to screen |

## Mobile Experience

On viewports < 768px:
- Canvas renders read-only (pan + zoom only)
- Tap element to see properties popover
- No palette sidebar, no editing tools
- "Edit on desktop" banner at top
- Layers panel available as bottom sheet (toggle visibility only)

## Migration Strategy

- Old `plot_grids` / `plot_cells` tables remain (not deleted)
- One-time frontend migration: if grow has plot_grid but no field_canvas, show a banner "Upgrade to new Field Designer" with a button
- Clicking it converts the old grid into canvas elements (each cell → appropriate element type)
- After conversion, old grid data stays but is no longer displayed

## Performance Considerations

- Konva uses HTML5 Canvas (not DOM nodes) — handles 500+ elements smoothly
- Debounced auto-save (2s after last change) to avoid API spam
- Canvas viewport culling — off-screen elements don't render
- Thumbnail generation: client-side via `stage.toDataURL()` on save
- Initial load: single API call returns full JSONB, no pagination needed

## Dependencies to Add

```json
{
  "konva": "^9.3.0",
  "react-konva": "^18.2.0",
  "zustand": "^5.0.0"
}
```

Note: The project already uses zustand-like patterns via React state. Zustand adds ~2KB gzipped and gives us proper undo/redo middleware and devtools.
