"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  getPlotGrid,
  upsertPlotGrid,
  batchUpdateCells,
  listCompanionPlants,
  suggestCompanions,
  type PlotGridResponse,
  type PlotCellResponse,
  type BucketResponse,
  type DeviceResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import {
  Grid3X3,
  Flower2,
  Sprout,
  Radio,
  Droplets,
  Footprints,
  Plus,
  RotateCcw,
  Maximize2,
  Minimize2,
  Settings2,
  MousePointer2,
  Paintbrush,
  Eraser,
  Undo2,
  Save,
} from "lucide-react";

// Cell type colors & icons
const CELL_CONFIG: Record<string, { bg: string; border: string; hoverRing: string; icon: typeof Sprout; label: string }> = {
  empty:      { bg: "bg-stone-100 dark:bg-stone-800",     border: "border-stone-300 dark:border-stone-600", hoverRing: "ring-stone-400",  icon: Plus,       label: "Empty" },
  plant:      { bg: "bg-green-100 dark:bg-green-900/40",  border: "border-green-500",                       hoverRing: "ring-green-400",  icon: Sprout,     label: "Plant" },
  companion:  { bg: "bg-yellow-100 dark:bg-yellow-900/40", border: "border-yellow-500",                     hoverRing: "ring-yellow-400", icon: Flower2,    label: "Companion" },
  sensor:     { bg: "bg-blue-100 dark:bg-blue-900/40",    border: "border-blue-500",                        hoverRing: "ring-blue-400",   icon: Radio,      label: "Sensor" },
  irrigation: { bg: "bg-cyan-100 dark:bg-cyan-900/40",    border: "border-cyan-500",                        hoverRing: "ring-cyan-400",   icon: Droplets,   label: "Irrigation" },
  path:       { bg: "bg-stone-300 dark:bg-stone-700",     border: "border-stone-500",                       hoverRing: "ring-stone-500",  icon: Footprints, label: "Path" },
};

type ToolMode = "select" | "paint" | "erase";

interface Props {
  growId: string;
  buckets: BucketResponse[];
  devices: DeviceResponse[];
  onBucketCreated?: () => void;
}

export function PlotDesigner({ growId, buckets, devices, onBucketCreated }: Props) {
  const [grid, setGrid] = useState<PlotGridResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [zoomed, setZoomed] = useState(false);

  // Creation form
  const [newRows, setNewRows] = useState(6);
  const [newCols, setNewCols] = useState(8);
  const [cellSize, setCellSize] = useState(12);
  const [sizeMode, setSizeMode] = useState<"grid" | "feet" | "sqft">("feet");
  const [lengthFt, setLengthFt] = useState(8);
  const [widthFt, setWidthFt] = useState(6);
  const [sqFt, setSqFt] = useState(48);

  // Resize dialog
  const [resizeOpen, setResizeOpen] = useState(false);
  const [resizeRows, setResizeRows] = useState(6);
  const [resizeCols, setResizeCols] = useState(8);
  const [resizeCellSize, setResizeCellSize] = useState(12);
  const [resizeSizeMode, setResizeSizeMode] = useState<"grid" | "feet" | "sqft">("feet");
  const [resizeLengthFt, setResizeLengthFt] = useState(8);
  const [resizeWidthFt, setResizeWidthFt] = useState(6);
  const [resizeSqFt, setResizeSqFt] = useState(48);
  const [resizing, setResizing] = useState(false);

  // Tool state
  const [tool, setTool] = useState<ToolMode>("select");
  const [brushType, setBrushType] = useState("plant");
  const [painting, setPainting] = useState(false);
  const paintedRef = useRef<Set<string>>(new Set());
  // Pending (unsaved) cell overrides from painting — key: "r,c"
  const [pendingCells, setPendingCells] = useState<Map<string, string>>(new Map());
  const [saving, setSaving] = useState(false);
  const [hoverCell, setHoverCell] = useState<string | null>(null);

  // Detail dialog
  const [selectedCell, setSelectedCell] = useState<{ row: number; col: number } | null>(null);
  const [cellDialog, setCellDialog] = useState(false);
  const [cellType, setCellType] = useState("empty");
  const [cellBucketId, setCellBucketId] = useState("");
  const [cellCompanion, setCellCompanion] = useState("");
  const [cellDeviceId, setCellDeviceId] = useState("");
  const [cellIrrigationZone, setCellIrrigationZone] = useState("");
  const [cellSunZone, setCellSunZone] = useState("");
  const [companions, setCompanions] = useState<string[]>([]);

  const refresh = useCallback(async () => {
    const token = await getAccessToken();
    if (!token) return;
    try {
      const data = await getPlotGrid(token, growId);
      setGrid(data);
    } catch {
      setGrid(null);
    } finally {
      setLoading(false);
    }
  }, [growId]);

  useEffect(() => {
    refresh();
    const token = getAccessToken();
    if (!token) return;
    listCompanionPlants(token)
      .then((data) => {
        setCompanions(data.filter((c) => c.plant !== "cannabis").map((c) => c.plant.replace(/_/g, " ")));
      })
      .catch(() => { /* ignore */ });
  }, [refresh]);

  // ── Creation form helpers ──
  const computedCreate = (() => {
    if (sizeMode === "grid") return { rows: newRows, cols: newCols };
    if (sizeMode === "feet") {
      const r = Math.max(1, Math.round((lengthFt * 12) / cellSize));
      const c = Math.max(1, Math.round((widthFt * 12) / cellSize));
      return { rows: r, cols: c };
    }
    const side = Math.sqrt(sqFt);
    const r = Math.max(1, Math.round((side * 12) / cellSize));
    return { rows: r, cols: r };
  })();

  const createSqFt = ((computedCreate.rows * cellSize * computedCreate.cols * cellSize) / 144).toFixed(1);

  const handleCreateGrid = async () => {
    const token = await getAccessToken();
    if (!token) return;
    setCreating(true);
    try {
      const data = await upsertPlotGrid(token, growId, { rows: computedCreate.rows, cols: computedCreate.cols, cell_size_inches: cellSize });
      setGrid(data);
    } finally {
      setCreating(false);
    }
  };

  // ── Resize helpers ──
  const computedResize = (() => {
    if (resizeSizeMode === "grid") return { rows: resizeRows, cols: resizeCols };
    if (resizeSizeMode === "feet") {
      const r = Math.max(1, Math.round((resizeLengthFt * 12) / resizeCellSize));
      const c = Math.max(1, Math.round((resizeWidthFt * 12) / resizeCellSize));
      return { rows: r, cols: c };
    }
    const side = Math.sqrt(resizeSqFt);
    const r = Math.max(1, Math.round((side * 12) / resizeCellSize));
    return { rows: r, cols: r };
  })();

  const resizeSqFtResult = ((computedResize.rows * resizeCellSize * computedResize.cols * resizeCellSize) / 144).toFixed(1);

  const handleOpenResize = () => {
    if (!grid) return;
    setResizeRows(grid.rows);
    setResizeCols(grid.cols);
    setResizeCellSize(grid.cell_size_inches);
    setResizeLengthFt(+((grid.cols * grid.cell_size_inches) / 12).toFixed(1));
    setResizeWidthFt(+((grid.rows * grid.cell_size_inches) / 12).toFixed(1));
    setResizeSqFt(+((grid.rows * grid.cell_size_inches * grid.cols * grid.cell_size_inches) / 144).toFixed(1));
    setResizeSizeMode("feet");
    setResizeOpen(true);
  };

  const handleResize = async () => {
    const token = await getAccessToken();
    if (!token) return;
    setResizing(true);
    try {
      const data = await upsertPlotGrid(token, growId, {
        rows: computedResize.rows,
        cols: computedResize.cols,
        cell_size_inches: resizeCellSize,
      });
      setGrid(data);
      setResizeOpen(false);
    } finally {
      setResizing(false);
    }
  };

  // ── Cell data helpers ──
  const getCellData = (row: number, col: number): PlotCellResponse | undefined => {
    return grid?.cells.find((c) => c.row === row && c.col === col);
  };

  /** Effective cell type considering pending paint overrides */
  const getEffectiveType = (row: number, col: number): string => {
    const key = `${row},${col}`;
    if (pendingCells.has(key)) return pendingCells.get(key)!;
    return getCellData(row, col)?.cell_type ?? "empty";
  };

  // ── Paint / erase logic ──
  const applyBrush = (row: number, col: number) => {
    const key = `${row},${col}`;
    if (paintedRef.current.has(key)) return; // already painted this stroke
    paintedRef.current.add(key);
    const newType = tool === "erase" ? "empty" : brushType;
    setPendingCells((prev) => {
      const next = new Map(prev);
      next.set(key, newType);
      return next;
    });
  };

  const handlePointerDown = (row: number, col: number) => {
    if (tool === "select") return;
    setPainting(true);
    paintedRef.current = new Set();
    applyBrush(row, col);
  };

  const handlePointerEnter = (row: number, col: number) => {
    setHoverCell(`${row},${col}`);
    if (painting && tool !== "select") {
      applyBrush(row, col);
    }
  };

  const handlePointerUp = () => {
    setPainting(false);
    paintedRef.current = new Set();
  };

  // Global pointer up to catch release outside grid
  useEffect(() => {
    const up = () => { setPainting(false); paintedRef.current = new Set(); };
    window.addEventListener("pointerup", up);
    return () => window.removeEventListener("pointerup", up);
  }, []);

  const handleUndo = () => {
    setPendingCells(new Map());
  };

  const handleSavePainted = async () => {
    if (pendingCells.size === 0) return;
    const token = await getAccessToken();
    if (!token) return;
    setSaving(true);
    try {
      const cells = Array.from(pendingCells.entries()).map(([key, cellT]) => {
        const [r, c] = key.split(",").map(Number);
        return { row: r, col: c, cell_type: cellT };
      });
      await batchUpdateCells(token, growId, cells);
      setPendingCells(new Map());
      await refresh();
    } finally {
      setSaving(false);
    }
  };

  // ── Detail dialog (double-click in select mode, or single click in select mode) ──
  const handleCellSelect = (row: number, col: number) => {
    if (tool !== "select") return;
    setSelectedCell({ row, col });
    const cell = getCellData(row, col);
    setCellType(cell?.cell_type ?? "empty");
    setCellBucketId(cell?.bucket_id ?? "");
    setCellCompanion(cell?.companion_plant ?? "");
    setCellDeviceId(cell?.device_id ?? "");
    setCellIrrigationZone(cell?.irrigation_zone ?? "");
    setCellSunZone(cell?.sun_zone ?? "");
    setCellDialog(true);
  };

  const handleCellSave = async () => {
    if (!selectedCell) return;
    const token = await getAccessToken();
    if (!token) return;
    try {
      await batchUpdateCells(token, growId, [{
        row: selectedCell.row,
        col: selectedCell.col,
        cell_type: cellType,
        bucket_id: cellType === "plant" && cellBucketId ? cellBucketId : null,
        companion_plant: cellType === "companion" && cellCompanion ? cellCompanion : null,
        device_id: cellType === "sensor" && cellDeviceId ? cellDeviceId : null,
        irrigation_zone: cellType === "irrigation" && cellIrrigationZone ? cellIrrigationZone : null,
        sun_zone: cellSunZone || null,
      }]);
      await refresh();
    } finally {
      setCellDialog(false);
      setSelectedCell(null);
    }
  };

  // ── Loading & creation ──
  if (loading) {
    return <div className="flex justify-center py-8"><div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" /></div>;
  }

  if (!grid) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Grid3X3 className="size-5" />
            Design Your Garden Plot
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Create an interactive grid to plan your garden layout. Place plants, companion plants, sensors, and irrigation lines.
          </p>
          <div>
            <Label>Size Input</Label>
            <div className="flex gap-1 mt-1">
              <Button size="sm" variant={sizeMode === "feet" ? "default" : "outline"} onClick={() => setSizeMode("feet")}>L × W (ft)</Button>
              <Button size="sm" variant={sizeMode === "sqft" ? "default" : "outline"} onClick={() => setSizeMode("sqft")}>Sq Ft</Button>
              <Button size="sm" variant={sizeMode === "grid" ? "default" : "outline"} onClick={() => setSizeMode("grid")}>Grid Cells</Button>
            </div>
          </div>
          {sizeMode === "feet" && (
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label>Length (ft)</Label>
                <Input type="number" min={1} max={200} step={0.5} value={lengthFt} onChange={(e) => setLengthFt(+e.target.value)} />
              </div>
              <div>
                <Label>Width (ft)</Label>
                <Input type="number" min={1} max={200} step={0.5} value={widthFt} onChange={(e) => setWidthFt(+e.target.value)} />
              </div>
              <div>
                <Label>Cell Size (in)</Label>
                <Input type="number" min={1} max={96} value={cellSize} onChange={(e) => setCellSize(+e.target.value)} />
              </div>
            </div>
          )}
          {sizeMode === "sqft" && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Total Square Feet</Label>
                <Input type="number" min={1} max={10000} step={1} value={sqFt} onChange={(e) => setSqFt(+e.target.value)} />
                <p className="text-xs text-muted-foreground mt-1">Creates a square grid</p>
              </div>
              <div>
                <Label>Cell Size (in)</Label>
                <Input type="number" min={1} max={96} value={cellSize} onChange={(e) => setCellSize(+e.target.value)} />
              </div>
            </div>
          )}
          {sizeMode === "grid" && (
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label>Rows</Label>
                <Input type="number" min={1} max={50} value={newRows} onChange={(e) => setNewRows(+e.target.value)} />
              </div>
              <div>
                <Label>Columns</Label>
                <Input type="number" min={1} max={50} value={newCols} onChange={(e) => setNewCols(+e.target.value)} />
              </div>
              <div>
                <Label>Cell Size (in)</Label>
                <Input type="number" min={1} max={96} value={cellSize} onChange={(e) => setCellSize(+e.target.value)} />
              </div>
            </div>
          )}
          <p className="text-xs text-muted-foreground">
            Grid: {computedCreate.rows} × {computedCreate.cols} cells · {createSqFt} sq ft ({(computedCreate.rows * cellSize / 12).toFixed(1)}&apos; × {(computedCreate.cols * cellSize / 12).toFixed(1)}&apos;)
          </p>
          <Button onClick={handleCreateGrid} disabled={creating}>
            {creating ? "Creating..." : "Create Garden Grid"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  // ── Render grid ──
  const totalSqFt = ((grid.rows * grid.cell_size_inches * grid.cols * grid.cell_size_inches) / 144).toFixed(1);
  const gridLengthFtDisplay = (grid.rows * grid.cell_size_inches / 12).toFixed(1);
  const gridWidthFtDisplay = (grid.cols * grid.cell_size_inches / 12).toFixed(1);
  const cellPx = zoomed ? 80 : 48;
  const brushCfg = CELL_CONFIG[brushType] ?? CELL_CONFIG.plant;

  return (
      <div className="space-y-3">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-3">
            <h3 className="text-sm font-medium">
              {gridLengthFtDisplay}&apos; × {gridWidthFtDisplay}&apos; · {totalSqFt} sq ft · {grid.rows}×{grid.cols} cells
            </h3>
            <Badge variant="outline">{grid.orientation.toUpperCase()}</Badge>
          </div>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="sm" onClick={handleOpenResize} title="Resize grid">
              <Settings2 className="size-4 mr-1" />
              Resize
            </Button>
            <Button variant="ghost" size="icon" onClick={() => setZoomed(!zoomed)} title={zoomed ? "Zoom out" : "Zoom in"}>
              {zoomed ? <Minimize2 className="size-4" /> : <Maximize2 className="size-4" />}
            </Button>
            <Button variant="ghost" size="icon" onClick={refresh} title="Refresh">
              <RotateCcw className="size-4" />
            </Button>
          </div>
        </div>

        {/* Toolbar */}
        <div className="flex flex-wrap items-center gap-2 rounded-lg border bg-muted/50 p-2">
          {/* Mode buttons */}
          <div className="flex items-center gap-1 border-r pr-2">
            <Button size="sm" variant={tool === "select" ? "default" : "ghost"} onClick={() => setTool("select")} className="gap-1.5" title="Click cells to edit details">
              <MousePointer2 className="size-4" />
              <span className="hidden sm:inline">Select</span>
            </Button>
            <Button size="sm" variant={tool === "paint" ? "default" : "ghost"} onClick={() => setTool("paint")} className="gap-1.5" title="Click & drag to paint cells">
              <Paintbrush className="size-4" />
              <span className="hidden sm:inline">Paint</span>
            </Button>
            <Button size="sm" variant={tool === "erase" ? "default" : "ghost"} onClick={() => setTool("erase")} className="gap-1.5" title="Click & drag to clear cells">
              <Eraser className="size-4" />
              <span className="hidden sm:inline">Erase</span>
            </Button>
          </div>

          {/* Brush type picker (only when paint mode) */}
          {tool === "paint" && (
            <div className="flex items-center gap-1 border-r pr-2">
              {Object.entries(CELL_CONFIG).filter(([t]) => t !== "empty").map(([type, cfg]) => {
                const Icon = cfg.icon;
                return (
                  <button
                    key={type}
                    onClick={() => setBrushType(type)}
                    title={`Paint ${cfg.label.toLowerCase()} cells`}
                    className={`flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors ${
                      brushType === type
                        ? `${cfg.bg} ${cfg.border} border-2 shadow-sm`
                        : "border border-transparent hover:bg-muted"
                    }`}
                  >
                    <Icon className="size-3.5" />
                    <span className="hidden md:inline">{cfg.label}</span>
                  </button>
                );
              })}
            </div>
          )}

          {/* Pending changes actions */}
          {pendingCells.size > 0 && (
            <div className="flex items-center gap-1 ml-auto">
              <Badge variant="secondary" className="tabular-nums">
                {pendingCells.size} unsaved
              </Badge>
              <Button size="sm" variant="ghost" onClick={handleUndo} title="Discard all painted changes">
                <Undo2 className="size-4 mr-1" />
                Undo
              </Button>
              <Button size="sm" onClick={handleSavePainted} disabled={saving}>
                <Save className="size-4 mr-1" />
                {saving ? "Saving..." : "Save"}
              </Button>
            </div>
          )}

          {pendingCells.size === 0 && tool !== "select" && (
            <p className="ml-auto text-xs text-muted-foreground">
              {tool === "paint" ? `Click & drag to paint ${brushCfg.label.toLowerCase()} cells` : "Click & drag to erase cells"}
            </p>
          )}
        </div>

        {/* Grid */}
        <div
          className={`overflow-auto rounded-lg border bg-background p-2 ${zoomed ? "max-h-[600px]" : "max-h-[400px]"} ${
            tool === "paint" ? "cursor-crosshair" : tool === "erase" ? "cursor-cell" : "cursor-pointer"
          }`}
          onPointerLeave={() => setHoverCell(null)}
        >
          <div
            className="grid gap-px select-none"
            style={{
              gridTemplateColumns: `repeat(${grid.cols}, ${cellPx}px)`,
              gridTemplateRows: `repeat(${grid.rows}, ${cellPx}px)`,
            }}
          >
            {Array.from({ length: grid.rows }, (_, r) =>
              Array.from({ length: grid.cols }, (_, c) => {
                const key = `${r},${c}`;
                const cell = getCellData(r, c);
                const effectiveType = getEffectiveType(r, c);
                const cfg = CELL_CONFIG[effectiveType] ?? CELL_CONFIG.empty;
                const Icon = cfg.icon;
                const bucket = cell?.bucket_id ? buckets.find((b) => b.id === cell.bucket_id) : null;
                const isPending = pendingCells.has(key);
                const isHover = hoverCell === key;
                const showBrushPreview = isHover && tool === "paint" && !isPending;
                const showErasePreview = isHover && tool === "erase" && !isPending;

                return (
                  <div
                    key={key}
                    className={`relative flex flex-col items-center justify-center rounded-sm border text-[9px] leading-tight transition-all touch-none ${cfg.bg} ${cfg.border} ${
                      isPending ? "ring-2 ring-primary ring-offset-1" : ""
                    } ${showBrushPreview ? `ring-2 ${brushCfg.hoverRing} ring-offset-1 opacity-80` : ""} ${
                      showErasePreview ? "ring-2 ring-red-400 ring-offset-1 opacity-60" : ""
                    } ${isHover && tool === "select" ? "ring-2 ring-primary/40" : ""}`}
                    onPointerDown={(e) => {
                      e.preventDefault();
                      if (tool === "select") {
                        handleCellSelect(r, c);
                      } else {
                        handlePointerDown(r, c);
                      }
                    }}
                    onPointerEnter={() => handlePointerEnter(r, c)}
                    onPointerUp={handlePointerUp}
                  >
                    <Icon className="size-3 text-muted-foreground" />
                    {effectiveType === "plant" && bucket && (
                      <span className="mt-0.5 max-w-full truncate px-0.5 font-medium">
                        {bucket.strain_name || bucket.label || `P${bucket.position}`}
                      </span>
                    )}
                    {effectiveType === "companion" && cell?.companion_plant && !isPending && (
                      <span className="mt-0.5 max-w-full truncate px-0.5">
                        {cell.companion_plant}
                      </span>
                    )}
                    {effectiveType === "sensor" && cell?.device_id && !isPending && (
                      <span className="mt-0.5 max-w-full truncate px-0.5">
                        {cell.device_id.slice(0, 8)}
                      </span>
                    )}
                    {/* Brush preview overlay */}
                    {showBrushPreview && (
                      <div className={`absolute inset-0 rounded-sm ${brushCfg.bg} opacity-50 pointer-events-none`} />
                    )}
                    {showErasePreview && (
                      <div className="absolute inset-0 rounded-sm bg-red-200 dark:bg-red-900/40 opacity-50 pointer-events-none" />
                    )}
                  </div>
                );
              }),
            )}
          </div>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
          {Object.entries(CELL_CONFIG).map(([type, cfg]) => {
            const Icon = cfg.icon;
            return (
              <div key={type} className="flex items-center gap-1">
                <div className={`size-4 rounded border ${cfg.bg} ${cfg.border}`}>
                  <Icon className="size-3 mx-auto mt-0.5" />
                </div>
                <span>{cfg.label}</span>
              </div>
            );
          })}
        </div>

        {/* Cell editor dialog */}
        <Dialog open={cellDialog} onOpenChange={setCellDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                Edit Cell ({selectedCell?.row}, {selectedCell?.col})
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Cell Type</Label>
                <Select value={cellType} onValueChange={(v) => setCellType(v ?? "empty")}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {Object.entries(CELL_CONFIG).map(([type, cfg]) => (
                      <SelectItem key={type} value={type}>{cfg.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {cellType === "plant" && (
                <div>
                  <Label>Link to Plant</Label>
                  <Select value={cellBucketId} onValueChange={(v) => setCellBucketId(v ?? "")}>
                    <SelectTrigger><SelectValue placeholder="Select plant..." /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Unassigned</SelectItem>
                      {buckets.map((b) => (
                        <SelectItem key={b.id} value={b.id}>
                          {b.strain_name || b.label || `Position ${b.position}`}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {cellType === "companion" && (
                <div>
                  <Label>Companion Plant</Label>
                  <Select value={cellCompanion} onValueChange={(v) => setCellCompanion(v ?? "")}>
                    <SelectTrigger><SelectValue placeholder="Select companion..." /></SelectTrigger>
                    <SelectContent>
                      {companions.map((c) => (
                        <SelectItem key={c} value={c}>
                          {c.charAt(0).toUpperCase() + c.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {cellType === "sensor" && (
                <div>
                  <Label>Device</Label>
                  <Select value={cellDeviceId} onValueChange={(v) => setCellDeviceId(v ?? "")}>
                    <SelectTrigger><SelectValue placeholder="Select device..." /></SelectTrigger>
                    <SelectContent>
                      {devices.map((d) => (
                        <SelectItem key={d.device_id} value={d.device_id}>
                          {d.label || d.device_id}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {cellType === "irrigation" && (
                <div>
                  <Label>Irrigation Zone</Label>
                  <Input value={cellIrrigationZone} onChange={(e) => setCellIrrigationZone(e.target.value)} placeholder="e.g., Zone A" />
                </div>
              )}

              <div>
                <Label>Sun Exposure</Label>
                <Select value={cellSunZone || "none"} onValueChange={(v) => setCellSunZone(v === "none" ? "" : v ?? "")}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Not set</SelectItem>
                    <SelectItem value="full_sun">Full Sun (6+ hrs)</SelectItem>
                    <SelectItem value="partial_sun">Partial Sun (4-6 hrs)</SelectItem>
                    <SelectItem value="partial_shade">Partial Shade (2-4 hrs)</SelectItem>
                    <SelectItem value="full_shade">Full Shade (&lt;2 hrs)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCellDialog(false)}>Cancel</Button>
              <Button onClick={handleCellSave}>Save</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Resize dialog */}
        <Dialog open={resizeOpen} onOpenChange={setResizeOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Resize Garden Grid</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Current: {grid.rows} × {grid.cols} cells ({totalSqFt} sq ft). Cells outside the new dimensions will be removed.
              </p>
              <div>
                <Label>Size Input</Label>
                <div className="flex gap-1 mt-1">
                  <Button size="sm" variant={resizeSizeMode === "feet" ? "default" : "outline"} onClick={() => setResizeSizeMode("feet")}>L × W (ft)</Button>
                  <Button size="sm" variant={resizeSizeMode === "sqft" ? "default" : "outline"} onClick={() => setResizeSizeMode("sqft")}>Sq Ft</Button>
                  <Button size="sm" variant={resizeSizeMode === "grid" ? "default" : "outline"} onClick={() => setResizeSizeMode("grid")}>Grid Cells</Button>
                </div>
              </div>
              {resizeSizeMode === "feet" && (
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label>Length (ft)</Label>
                    <Input type="number" min={1} max={200} step={0.5} value={resizeLengthFt} onChange={(e) => setResizeLengthFt(+e.target.value)} />
                  </div>
                  <div>
                    <Label>Width (ft)</Label>
                    <Input type="number" min={1} max={200} step={0.5} value={resizeWidthFt} onChange={(e) => setResizeWidthFt(+e.target.value)} />
                  </div>
                  <div>
                    <Label>Cell Size (in)</Label>
                    <Input type="number" min={1} max={96} value={resizeCellSize} onChange={(e) => setResizeCellSize(+e.target.value)} />
                  </div>
                </div>
              )}
              {resizeSizeMode === "sqft" && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Total Square Feet</Label>
                    <Input type="number" min={1} max={10000} step={1} value={resizeSqFt} onChange={(e) => setResizeSqFt(+e.target.value)} />
                    <p className="text-xs text-muted-foreground mt-1">Creates a square grid</p>
                  </div>
                  <div>
                    <Label>Cell Size (in)</Label>
                    <Input type="number" min={1} max={96} value={resizeCellSize} onChange={(e) => setResizeCellSize(+e.target.value)} />
                  </div>
                </div>
              )}
              {resizeSizeMode === "grid" && (
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label>Rows</Label>
                    <Input type="number" min={1} max={50} value={resizeRows} onChange={(e) => setResizeRows(+e.target.value)} />
                  </div>
                  <div>
                    <Label>Columns</Label>
                    <Input type="number" min={1} max={50} value={resizeCols} onChange={(e) => setResizeCols(+e.target.value)} />
                  </div>
                  <div>
                    <Label>Cell Size (in)</Label>
                    <Input type="number" min={1} max={96} value={resizeCellSize} onChange={(e) => setResizeCellSize(+e.target.value)} />
                  </div>
                </div>
              )}
              <p className="text-xs text-muted-foreground">
                New grid: {computedResize.rows} × {computedResize.cols} cells · {resizeSqFtResult} sq ft ({(computedResize.rows * resizeCellSize / 12).toFixed(1)}&apos; × {(computedResize.cols * resizeCellSize / 12).toFixed(1)}&apos;)
              </p>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setResizeOpen(false)}>Cancel</Button>
              <Button onClick={handleResize} disabled={resizing}>
                {resizing ? "Resizing..." : "Apply Resize"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
  );
}
