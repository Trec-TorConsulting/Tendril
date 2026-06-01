/** Field Canvas type definitions */

// ─── Element Types ───────────────────────────────────────────────────────────

export type ElementType =
  | "raised_bed"
  | "ground_row"
  | "plant_marker"
  | "companion_zone"
  | "cover_crop"
  | "container"
  | "tree"
  | "shrub"
  | "trellis"
  | "greenhouse"
  | "hoop_house"
  | "shed"
  | "fence"
  | "compost_bin"
  | "water_spigot"
  | "rain_barrel"
  | "water_tank"
  | "drip_line"
  | "sprinkler_head"
  | "soaker_hose"
  | "irrigation_valve"
  | "path"
  | "grow_light"
  | "sensor"
  | "power_outlet"
  | "camera"
  | "bench"
  | "pond"
  | "rock"
  | "garden_art"
  | "text_label";

export type ToolMode = "select" | "pan" | "connect";

export type AnchorPosition = "top" | "right" | "bottom" | "left";

export type LineType = "straight" | "elbow" | "curve";

export type FlowDirection = "forward" | "reverse" | "none";

// ─── Layers ──────────────────────────────────────────────────────────────────

export interface LayerConfig {
  id: string;
  name: string;
  visible: boolean;
  locked: boolean;
  color: string;
  order: number;
}

export const DEFAULT_LAYERS: LayerConfig[] = [
  { id: "ground", name: "Ground", visible: true, locked: false, color: "#78716c", order: 0 },
  { id: "planting", name: "Planting", visible: true, locked: false, color: "#16a34a", order: 1 },
  { id: "irrigation", name: "Irrigation", visible: true, locked: false, color: "#0891b2", order: 2 },
  { id: "structures", name: "Structures", visible: true, locked: false, color: "#d97706", order: 3 },
  { id: "sensors", name: "Sensors", visible: true, locked: false, color: "#7c3aed", order: 4 },
];

// ─── Elements ────────────────────────────────────────────────────────────────

export interface FieldElement {
  id: string;
  type: ElementType;
  layerId: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  props: Record<string, unknown>;
  locked: boolean;
  visible: boolean;
  /** For polyline-based elements (fence, path) */
  points?: number[];
}

// ─── Connectors ──────────────────────────────────────────────────────────────

export interface Connector {
  id: string;
  layerId: string;
  fromId: string;
  fromAnchor: AnchorPosition;
  toId: string;
  toAnchor: AnchorPosition;
  flowDirection: FlowDirection;
  lineType: LineType;
  label?: string;
  props: Record<string, unknown>;
}

// ─── Canvas State ────────────────────────────────────────────────────────────

export interface CanvasData {
  elements: FieldElement[];
  connectors: Connector[];
  layers: LayerConfig[];
  viewport: {
    x: number;
    y: number;
    scale: number;
  };
}

// ─── Palette Item Definition ─────────────────────────────────────────────────

export type PaletteCategory =
  | "beds"
  | "trees"
  | "water"
  | "infrastructure"
  | "other";

export interface PaletteItem {
  type: ElementType;
  label: string;
  category: PaletteCategory;
  icon: string; // lucide icon name
  defaultWidth: number;
  defaultHeight: number;
  defaultLayer: string;
  defaultProps?: Record<string, unknown>;
}

// ─── Palette Registry ────────────────────────────────────────────────────────

export const PALETTE_ITEMS: PaletteItem[] = [
  // Beds & Planting
  { type: "raised_bed", label: "Raised Bed (4×4)", category: "beds", icon: "square", defaultWidth: 120, defaultHeight: 120, defaultLayer: "planting", defaultProps: { sizeFt: "4×4" } },
  { type: "raised_bed", label: "Raised Bed (4×8)", category: "beds", icon: "rectangle-horizontal", defaultWidth: 240, defaultHeight: 120, defaultLayer: "planting", defaultProps: { sizeFt: "4×8" } },
  { type: "raised_bed", label: "Raised Bed (Custom)", category: "beds", icon: "rectangle-horizontal", defaultWidth: 160, defaultHeight: 100, defaultLayer: "planting", defaultProps: { sizeFt: "custom" } },
  { type: "ground_row", label: "In-Ground Row", category: "beds", icon: "rows-3", defaultWidth: 300, defaultHeight: 40, defaultLayer: "planting" },
  { type: "plant_marker", label: "Plant Marker", category: "beds", icon: "sprout", defaultWidth: 32, defaultHeight: 32, defaultLayer: "planting" },
  { type: "companion_zone", label: "Companion Zone", category: "beds", icon: "flower-2", defaultWidth: 100, defaultHeight: 100, defaultLayer: "planting" },
  { type: "cover_crop", label: "Cover Crop Area", category: "beds", icon: "leaf", defaultWidth: 150, defaultHeight: 100, defaultLayer: "planting" },
  { type: "container", label: "Container / Pot", category: "beds", icon: "cup-soda", defaultWidth: 48, defaultHeight: 48, defaultLayer: "planting" },

  // Trees & Structures
  { type: "tree", label: "Tree", category: "trees", icon: "tree-pine", defaultWidth: 64, defaultHeight: 64, defaultLayer: "planting" },
  { type: "shrub", label: "Shrub", category: "trees", icon: "shrub", defaultWidth: 48, defaultHeight: 40, defaultLayer: "planting" },
  { type: "trellis", label: "Trellis", category: "trees", icon: "grid-3x3", defaultWidth: 120, defaultHeight: 20, defaultLayer: "structures" },
  { type: "greenhouse", label: "Greenhouse", category: "trees", icon: "warehouse", defaultWidth: 200, defaultHeight: 150, defaultLayer: "structures" },
  { type: "hoop_house", label: "Hoop House", category: "trees", icon: "tent", defaultWidth: 180, defaultHeight: 100, defaultLayer: "structures" },
  { type: "shed", label: "Shed / Storage", category: "trees", icon: "home", defaultWidth: 100, defaultHeight: 80, defaultLayer: "structures" },
  { type: "fence", label: "Fence", category: "trees", icon: "fence", defaultWidth: 200, defaultHeight: 10, defaultLayer: "structures" },
  { type: "compost_bin", label: "Compost Bin", category: "trees", icon: "recycle", defaultWidth: 48, defaultHeight: 48, defaultLayer: "structures" },

  // Water & Irrigation
  { type: "water_spigot", label: "Water Spigot", category: "water", icon: "pipette", defaultWidth: 32, defaultHeight: 32, defaultLayer: "irrigation" },
  { type: "rain_barrel", label: "Rain Barrel", category: "water", icon: "cylinder", defaultWidth: 40, defaultHeight: 40, defaultLayer: "irrigation" },
  { type: "water_tank", label: "Water Tank", category: "water", icon: "database", defaultWidth: 60, defaultHeight: 60, defaultLayer: "irrigation" },
  { type: "sprinkler_head", label: "Sprinkler Head", category: "water", icon: "cloud-rain", defaultWidth: 28, defaultHeight: 28, defaultLayer: "irrigation" },
  { type: "irrigation_valve", label: "Irrigation Valve", category: "water", icon: "circle-dot", defaultWidth: 24, defaultHeight: 24, defaultLayer: "irrigation" },

  // Infrastructure
  { type: "path", label: "Walkway / Path", category: "infrastructure", icon: "footprints", defaultWidth: 200, defaultHeight: 40, defaultLayer: "ground" },
  { type: "grow_light", label: "Grow Light", category: "infrastructure", icon: "lightbulb", defaultWidth: 32, defaultHeight: 32, defaultLayer: "structures" },
  { type: "sensor", label: "Sensor", category: "infrastructure", icon: "radio", defaultWidth: 28, defaultHeight: 28, defaultLayer: "sensors" },
  { type: "power_outlet", label: "Power Outlet", category: "infrastructure", icon: "plug", defaultWidth: 24, defaultHeight: 24, defaultLayer: "structures" },
  { type: "camera", label: "Camera", category: "infrastructure", icon: "camera", defaultWidth: 28, defaultHeight: 28, defaultLayer: "sensors" },

  // Other / Decorative
  { type: "bench", label: "Bench / Seating", category: "other", icon: "armchair", defaultWidth: 80, defaultHeight: 36, defaultLayer: "structures" },
  { type: "pond", label: "Pond / Water Feature", category: "other", icon: "waves", defaultWidth: 100, defaultHeight: 80, defaultLayer: "ground" },
  { type: "rock", label: "Rock / Boulder", category: "other", icon: "mountain", defaultWidth: 40, defaultHeight: 36, defaultLayer: "ground" },
  { type: "garden_art", label: "Garden Art", category: "other", icon: "palette", defaultWidth: 32, defaultHeight: 32, defaultLayer: "structures" },
  { type: "text_label", label: "Text Label", category: "other", icon: "type", defaultWidth: 100, defaultHeight: 30, defaultLayer: "ground", defaultProps: { text: "Label" } },
];

// ─── API Response Types ──────────────────────────────────────────────────────

export interface FieldCanvasResponse {
  id: string;
  grow_cycle_id: string;
  name: string;
  canvas_data: CanvasData;
  thumbnail_key: string | null;
  created_at: string;
  updated_at: string;
}
