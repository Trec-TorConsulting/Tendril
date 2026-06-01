"use client";

import { useCallback, useRef } from "react";
import { Stage, Layer, Line, Rect } from "react-konva";
import type Konva from "konva";
import { useCanvasStore } from "./hooks/use-canvas-state";
import { useSnapGrid } from "./hooks/use-snap-grid";
import { BaseElement } from "./elements/base-element";
import { ConnectorLine } from "./connectors/connector-line";

interface Props {
  width: number;
  height: number;
}

export function CanvasStage({ width, height }: Props) {
  const stageRef = useRef<Konva.Stage>(null);
  const {
    stageX,
    stageY,
    scale,
    setViewport,
    elements,
    connectors,
    layers,
    selectedIds,
    tool,
    placingItem,
    showGrid,
    snapSize,
    select,
    clearSelection,
    addElement,
    setPlacingItem,
  } = useCanvasStore();

  const { snapPoint } = useSnapGrid();

  // ─── Zoom via scroll wheel ─────────────────────────────────────────────────

  const handleWheel = useCallback(
    (e: Konva.KonvaEventObject<WheelEvent>) => {
      e.evt.preventDefault();
      const stage = stageRef.current;
      if (!stage) return;

      const scaleBy = 1.08;
      const oldScale = scale;
      const pointer = stage.getPointerPosition();
      if (!pointer) return;

      const newScale =
        e.evt.deltaY < 0
          ? Math.min(oldScale * scaleBy, 4)
          : Math.max(oldScale / scaleBy, 0.2);

      const mousePointTo = {
        x: (pointer.x - stageX) / oldScale,
        y: (pointer.y - stageY) / oldScale,
      };

      setViewport(
        pointer.x - mousePointTo.x * newScale,
        pointer.y - mousePointTo.y * newScale,
        newScale
      );
    },
    [scale, stageX, stageY, setViewport]
  );

  // ─── Pan via drag (when pan tool or middle mouse) ──────────────────────────

  const handleDragEnd = useCallback(
    (e: Konva.KonvaEventObject<DragEvent>) => {
      if (e.target !== stageRef.current) return;
      setViewport(e.target.x(), e.target.y(), scale);
    },
    [scale, setViewport]
  );

  // ─── Click on stage background ─────────────────────────────────────────────

  const handleStageClick = useCallback(
    (e: Konva.KonvaEventObject<MouseEvent>) => {
      // Only handle clicks on the stage itself (not on elements)
      if (e.target !== stageRef.current) return;

      if (placingItem) {
        const stage = stageRef.current;
        if (!stage) return;
        const pointer = stage.getPointerPosition();
        if (!pointer) return;

        const pos = snapPoint(
          (pointer.x - stageX) / scale - placingItem.defaultWidth / 2,
          (pointer.y - stageY) / scale - placingItem.defaultHeight / 2
        );
        addElement(placingItem, pos.x, pos.y);
        // Keep placing mode active (click again to place another)
        return;
      }

      clearSelection();
    },
    [placingItem, clearSelection, stageX, stageY, scale, snapPoint, addElement]
  );

  // ─── Right-click to cancel placement ───────────────────────────────────────

  const handleContextMenu = useCallback(
    (e: Konva.KonvaEventObject<PointerEvent>) => {
      e.evt.preventDefault();
      if (placingItem) {
        setPlacingItem(null);
      }
    },
    [placingItem, setPlacingItem]
  );

  // ─── Render grid lines ─────────────────────────────────────────────────────

  const renderGrid = () => {
    if (!showGrid) return null;
    const lines: React.ReactElement[] = [];
    const gridSize = snapSize;

    // Compute visible area in canvas coordinates
    const startX = Math.floor(-stageX / scale / gridSize) * gridSize - gridSize;
    const startY = Math.floor(-stageY / scale / gridSize) * gridSize - gridSize;
    const endX = startX + (width / scale + gridSize * 2);
    const endY = startY + (height / scale + gridSize * 2);

    for (let x = startX; x < endX; x += gridSize) {
      lines.push(
        <Line
          key={`gv-${x}`}
          points={[x, startY, x, endY]}
          stroke="#e5e7eb"
          strokeWidth={0.5 / scale}
          listening={false}
        />
      );
    }
    for (let y = startY; y < endY; y += gridSize) {
      lines.push(
        <Line
          key={`gh-${y}`}
          points={[startX, y, endX, y]}
          stroke="#e5e7eb"
          strokeWidth={0.5 / scale}
          listening={false}
        />
      );
    }
    return lines;
  };

  // ─── Render elements per layer ─────────────────────────────────────────────

  const visibleLayers = layers.filter((l) => l.visible).sort((a, b) => a.order - b.order);

  return (
    <Stage
      ref={stageRef}
      width={width}
      height={height}
      x={stageX}
      y={stageY}
      scaleX={scale}
      scaleY={scale}
      draggable={tool === "pan"}
      onWheel={handleWheel}
      onDragEnd={handleDragEnd}
      onClick={handleStageClick}
      onTap={handleStageClick as unknown as (evt: Konva.KonvaEventObject<TouchEvent>) => void}
      onContextMenu={handleContextMenu}
      style={{ cursor: placingItem ? "crosshair" : tool === "pan" ? "grab" : "default" }}
    >
      {/* Grid layer (always bottom) */}
      <Layer listening={false}>{renderGrid()}</Layer>

      {/* Element layers */}
      {visibleLayers.map((layer) => (
        <Layer key={layer.id}>
          {elements
            .filter((el) => el.layerId === layer.id && el.visible)
            .map((el) => (
              <BaseElement
                key={el.id}
                element={el}
                isSelected={selectedIds.has(el.id)}
                isLocked={layer.locked || el.locked}
              />
            ))}
        </Layer>
      ))}

      {/* Connectors layer (on top) */}
      <Layer>
        {connectors
          .filter((c) => {
            const layer = layers.find((l) => l.id === c.layerId);
            return layer?.visible !== false;
          })
          .map((c) => (
            <ConnectorLine key={c.id} connector={c} />
          ))}
      </Layer>
    </Stage>
  );
}
