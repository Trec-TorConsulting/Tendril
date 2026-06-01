"use client";

import { create } from "zustand";
import type {
  CanvasData,
  Connector,
  FieldElement,
  LayerConfig,
  ToolMode,
  PaletteItem,
} from "../types";
import { DEFAULT_LAYERS as LAYERS } from "../types";

// ─── History (Undo/Redo) ─────────────────────────────────────────────────────

interface HistoryEntry {
  elements: FieldElement[];
  connectors: Connector[];
}

const MAX_HISTORY = 50;

// ─── Store Interface ─────────────────────────────────────────────────────────

interface CanvasStore {
  // Viewport
  stageX: number;
  stageY: number;
  scale: number;

  // Data
  elements: FieldElement[];
  connectors: Connector[];
  layers: LayerConfig[];

  // Selection & Tool
  selectedIds: Set<string>;
  tool: ToolMode;
  activeLayerId: string;

  // Grid snap
  snapEnabled: boolean;
  snapSize: number;
  showGrid: boolean;

  // Placement mode (drag from palette)
  placingItem: PaletteItem | null;

  // Dirty flag for auto-save
  dirty: boolean;

  // History
  _history: HistoryEntry[];
  _historyIndex: number;

  // ─── Actions ─────────────────────────────────────────────────────────────

  // Viewport
  setViewport: (x: number, y: number, scale: number) => void;

  // Elements
  addElement: (item: PaletteItem, x: number, y: number) => string;
  updateElement: (id: string, updates: Partial<FieldElement>) => void;
  removeElements: (ids: string[]) => void;
  duplicateElements: (ids: string[]) => void;

  // Connectors
  addConnector: (connector: Omit<Connector, "id">) => string;
  updateConnector: (id: string, updates: Partial<Connector>) => void;
  removeConnectors: (ids: string[]) => void;

  // Layers
  setLayerVisibility: (layerId: string, visible: boolean) => void;
  setLayerLocked: (layerId: string, locked: boolean) => void;
  setActiveLayer: (layerId: string) => void;
  reorderLayers: (layers: LayerConfig[]) => void;

  // Selection
  select: (ids: string[]) => void;
  addToSelection: (ids: string[]) => void;
  clearSelection: () => void;

  // Tool
  setTool: (tool: ToolMode) => void;

  // Grid
  toggleSnap: () => void;
  setSnapSize: (size: number) => void;
  toggleGrid: () => void;

  // Placement
  setPlacingItem: (item: PaletteItem | null) => void;

  // History
  undo: () => void;
  redo: () => void;
  _pushHistory: () => void;

  // Persistence
  loadCanvas: (data: CanvasData) => void;
  getCanvasData: () => CanvasData;
  markClean: () => void;
}

// ─── ID Generation ───────────────────────────────────────────────────────────

function genId(): string {
  return crypto.randomUUID();
}

// ─── Store ───────────────────────────────────────────────────────────────────

export const useCanvasStore = create<CanvasStore>((set, get) => ({
  // Initial state
  stageX: 0,
  stageY: 0,
  scale: 1,

  elements: [],
  connectors: [],
  layers: [...LAYERS],

  selectedIds: new Set(),
  tool: "select",
  activeLayerId: "planting",

  snapEnabled: true,
  snapSize: 24,
  showGrid: true,

  placingItem: null,
  dirty: false,

  _history: [],
  _historyIndex: -1,

  // ─── Viewport ──────────────────────────────────────────────────────────────

  setViewport: (x, y, scale) => set({ stageX: x, stageY: y, scale }),

  // ─── Elements ──────────────────────────────────────────────────────────────

  addElement: (item, x, y) => {
    const state = get();
    state._pushHistory();
    const id = genId();
    const element: FieldElement = {
      id,
      type: item.type,
      layerId: item.defaultLayer,
      x,
      y,
      width: item.defaultWidth,
      height: item.defaultHeight,
      rotation: 0,
      props: { ...item.defaultProps },
      locked: false,
      visible: true,
    };
    set({ elements: [...state.elements, element], dirty: true });
    return id;
  },

  updateElement: (id, updates) => {
    const state = get();
    state._pushHistory();
    set({
      elements: state.elements.map((el) => (el.id === id ? { ...el, ...updates } : el)),
      dirty: true,
    });
  },

  removeElements: (ids) => {
    const state = get();
    state._pushHistory();
    const idSet = new Set(ids);
    set({
      elements: state.elements.filter((el) => !idSet.has(el.id)),
      connectors: state.connectors.filter(
        (c) => !idSet.has(c.fromId) && !idSet.has(c.toId)
      ),
      selectedIds: new Set(),
      dirty: true,
    });
  },

  duplicateElements: (ids) => {
    const state = get();
    state._pushHistory();
    const idSet = new Set(ids);
    const dupes = state.elements
      .filter((el) => idSet.has(el.id))
      .map((el) => ({
        ...el,
        id: genId(),
        x: el.x + 20,
        y: el.y + 20,
      }));
    const newIds = new Set(dupes.map((d) => d.id));
    set({
      elements: [...state.elements, ...dupes],
      selectedIds: newIds,
      dirty: true,
    });
  },

  // ─── Connectors ────────────────────────────────────────────────────────────

  addConnector: (connector) => {
    const state = get();
    state._pushHistory();
    const id = genId();
    set({
      connectors: [...state.connectors, { ...connector, id }],
      dirty: true,
    });
    return id;
  },

  updateConnector: (id, updates) => {
    const state = get();
    state._pushHistory();
    set({
      connectors: state.connectors.map((c) => (c.id === id ? { ...c, ...updates } : c)),
      dirty: true,
    });
  },

  removeConnectors: (ids) => {
    const state = get();
    state._pushHistory();
    const idSet = new Set(ids);
    set({
      connectors: state.connectors.filter((c) => !idSet.has(c.id)),
      dirty: true,
    });
  },

  // ─── Layers ────────────────────────────────────────────────────────────────

  setLayerVisibility: (layerId, visible) =>
    set((s) => ({
      layers: s.layers.map((l) => (l.id === layerId ? { ...l, visible } : l)),
    })),

  setLayerLocked: (layerId, locked) =>
    set((s) => ({
      layers: s.layers.map((l) => (l.id === layerId ? { ...l, locked } : l)),
    })),

  setActiveLayer: (layerId) => set({ activeLayerId: layerId }),

  reorderLayers: (layers) => set({ layers }),

  // ─── Selection ─────────────────────────────────────────────────────────────

  select: (ids) => set({ selectedIds: new Set(ids) }),
  addToSelection: (ids) =>
    set((s) => {
      const next = new Set(s.selectedIds);
      ids.forEach((id) => next.add(id));
      return { selectedIds: next };
    }),
  clearSelection: () => set({ selectedIds: new Set() }),

  // ─── Tool ──────────────────────────────────────────────────────────────────

  setTool: (tool) => set({ tool, placingItem: null }),

  // ─── Grid ──────────────────────────────────────────────────────────────────

  toggleSnap: () => set((s) => ({ snapEnabled: !s.snapEnabled })),
  setSnapSize: (size) => set({ snapSize: size }),
  toggleGrid: () => set((s) => ({ showGrid: !s.showGrid })),

  // ─── Placement ─────────────────────────────────────────────────────────────

  setPlacingItem: (item) => set({ placingItem: item, tool: "select" }),

  // ─── History ───────────────────────────────────────────────────────────────

  _pushHistory: () => {
    const state = get();
    const entry: HistoryEntry = {
      elements: structuredClone(state.elements),
      connectors: structuredClone(state.connectors),
    };
    // Truncate any redo entries
    const history = state._history.slice(0, state._historyIndex + 1);
    history.push(entry);
    if (history.length > MAX_HISTORY) history.shift();
    set({ _history: history, _historyIndex: history.length - 1 });
  },

  undo: () => {
    const state = get();
    if (state._historyIndex < 0) return;
    const entry = state._history[state._historyIndex];
    set({
      elements: entry.elements,
      connectors: entry.connectors,
      _historyIndex: state._historyIndex - 1,
      dirty: true,
    });
  },

  redo: () => {
    const state = get();
    if (state._historyIndex >= state._history.length - 1) return;
    const nextIndex = state._historyIndex + 1;
    // If there's a next entry after the one we're restoring, use it
    if (nextIndex + 1 < state._history.length) {
      const entry = state._history[nextIndex + 1];
      set({
        elements: entry.elements,
        connectors: entry.connectors,
        _historyIndex: nextIndex,
        dirty: true,
      });
    }
  },

  // ─── Persistence ───────────────────────────────────────────────────────────

  loadCanvas: (data) =>
    set({
      elements: data.elements,
      connectors: data.connectors,
      layers: data.layers.length > 0 ? data.layers : [...LAYERS],
      stageX: data.viewport.x,
      stageY: data.viewport.y,
      scale: data.viewport.scale,
      dirty: false,
      _history: [],
      _historyIndex: -1,
    }),

  getCanvasData: (): CanvasData => {
    const state = get();
    return {
      elements: state.elements,
      connectors: state.connectors,
      layers: state.layers,
      viewport: { x: state.stageX, y: state.stageY, scale: state.scale },
    };
  },

  markClean: () => set({ dirty: false }),
}));
