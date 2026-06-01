"use client";

import { useCallback, useEffect, useRef } from "react";
import { Group, Rect, Text, Circle, Line, Arrow } from "react-konva";
import { Transformer } from "react-konva";
import type Konva from "konva";
import type { FieldElement } from "../types";
import { useCanvasStore } from "../hooks/use-canvas-state";
import { useSnapGrid } from "../hooks/use-snap-grid";

// ─── Element colors by type ──────────────────────────────────────────────────

const TYPE_FILLS: Record<string, { fill: string; stroke: string }> = {
  raised_bed:      { fill: "#86efac", stroke: "#16a34a" },
  ground_row:      { fill: "#bbf7d0", stroke: "#22c55e" },
  plant_marker:    { fill: "#4ade80", stroke: "#15803d" },
  companion_zone:  { fill: "#fef08a", stroke: "#ca8a04" },
  cover_crop:      { fill: "#a7f3d0", stroke: "#059669" },
  container:       { fill: "#d6d3d1", stroke: "#78716c" },
  tree:            { fill: "#86efac", stroke: "#166534" },
  shrub:           { fill: "#6ee7b7", stroke: "#047857" },
  trellis:         { fill: "#e7e5e4", stroke: "#57534e" },
  greenhouse:      { fill: "#e0f2fe", stroke: "#0284c7" },
  hoop_house:      { fill: "#dbeafe", stroke: "#2563eb" },
  shed:            { fill: "#fde68a", stroke: "#b45309" },
  fence:           { fill: "#d6d3d1", stroke: "#44403c" },
  compost_bin:     { fill: "#a3a3a3", stroke: "#525252" },
  water_spigot:    { fill: "#67e8f9", stroke: "#0891b2" },
  rain_barrel:     { fill: "#a5f3fc", stroke: "#0e7490" },
  water_tank:      { fill: "#a5f3fc", stroke: "#155e75" },
  sprinkler_head:  { fill: "#22d3ee", stroke: "#0891b2" },
  irrigation_valve:{ fill: "#06b6d4", stroke: "#0e7490" },
  path:            { fill: "#d6d3d1", stroke: "#78716c" },
  grow_light:      { fill: "#fde047", stroke: "#a16207" },
  sensor:          { fill: "#c4b5fd", stroke: "#7c3aed" },
  power_outlet:    { fill: "#fbbf24", stroke: "#92400e" },
  camera:          { fill: "#a78bfa", stroke: "#5b21b6" },
  bench:           { fill: "#e7e5e4", stroke: "#57534e" },
  pond:            { fill: "#7dd3fc", stroke: "#0369a1" },
  rock:            { fill: "#a8a29e", stroke: "#57534e" },
  garden_art:      { fill: "#f9a8d4", stroke: "#be185d" },
  text_label:      { fill: "transparent", stroke: "transparent" },
};

const DEFAULT_STYLE = { fill: "#e5e7eb", stroke: "#6b7280" };

// ─── Component ───────────────────────────────────────────────────────────────

interface Props {
  element: FieldElement;
  isSelected: boolean;
  isLocked: boolean;
}

export function BaseElement({ element, isSelected, isLocked }: Props) {
  const groupRef = useRef<Konva.Group>(null);
  const trRef = useRef<Konva.Transformer>(null);

  const { select, addToSelection, updateElement, tool } = useCanvasStore();
  const { snapPoint } = useSnapGrid();

  // Attach transformer when selected
  useEffect(() => {
    if (isSelected && trRef.current && groupRef.current) {
      trRef.current.nodes([groupRef.current]);
      trRef.current.getLayer()?.batchDraw();
    }
  }, [isSelected]);

  // ─── Handlers ──────────────────────────────────────────────────────────────

  const handleClick = useCallback(
    (e: Konva.KonvaEventObject<MouseEvent>) => {
      if (tool !== "select" || isLocked) return;
      e.cancelBubble = true;
      if (e.evt.shiftKey) {
        addToSelection([element.id]);
      } else {
        select([element.id]);
      }
    },
    [tool, isLocked, element.id, select, addToSelection]
  );

  const handleDragEnd = useCallback(
    (e: Konva.KonvaEventObject<DragEvent>) => {
      const pos = snapPoint(e.target.x(), e.target.y());
      updateElement(element.id, { x: pos.x, y: pos.y });
    },
    [element.id, updateElement, snapPoint]
  );

  const handleTransformEnd = useCallback(() => {
    const node = groupRef.current;
    if (!node) return;

    const scaleX = node.scaleX();
    const scaleY = node.scaleY();

    // Reset scale and update width/height
    node.scaleX(1);
    node.scaleY(1);

    updateElement(element.id, {
      x: node.x(),
      y: node.y(),
      width: Math.max(10, element.width * scaleX),
      height: Math.max(10, element.height * scaleY),
      rotation: node.rotation(),
    });
  }, [element, updateElement]);

  // ─── Shape Rendering ───────────────────────────────────────────────────────

  const style = TYPE_FILLS[element.type] || DEFAULT_STYLE;

  const renderShape = () => {
    const { type, width, height, props } = element;

    // Circular elements
    if (["plant_marker", "tree", "shrub", "sprinkler_head", "irrigation_valve", "sensor", "camera", "power_outlet", "grow_light"].includes(type)) {
      const radius = Math.min(width, height) / 2;
      return (
        <>
          <Circle
            x={width / 2}
            y={height / 2}
            radius={radius}
            fill={style.fill}
            stroke={style.stroke}
            strokeWidth={2}
          />
          {type === "tree" && (
            <Rect
              x={width / 2 - 4}
              y={height / 2 + radius * 0.5}
              width={8}
              height={radius * 0.6}
              fill="#92400e"
              cornerRadius={2}
            />
          )}
        </>
      );
    }

    // Text label
    if (type === "text_label") {
      return (
        <Text
          text={(props?.text as string) || "Label"}
          fontSize={14}
          fill="#1f2937"
          width={width}
          height={height}
          align="center"
          verticalAlign="middle"
        />
      );
    }

    // Pond (ellipse-like)
    if (type === "pond") {
      return (
        <Circle
          x={width / 2}
          y={height / 2}
          radiusX={width / 2}
          radiusY={height / 2}
          fill={style.fill}
          stroke={style.stroke}
          strokeWidth={2}
        />
      );
    }

    // Default: rectangle
    return (
      <Rect
        width={width}
        height={height}
        fill={style.fill}
        stroke={style.stroke}
        strokeWidth={2}
        cornerRadius={type === "path" ? height / 4 : 4}
      />
    );
  };

  // ─── Label ─────────────────────────────────────────────────────────────────

  const label =
    element.type === "text_label"
      ? ""
      : (element.props?.label as string) ||
        element.type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <>
      <Group
        ref={groupRef}
        x={element.x}
        y={element.y}
        rotation={element.rotation}
        draggable={tool === "select" && !isLocked}
        onClick={handleClick}
        onTap={handleClick as unknown as (evt: Konva.KonvaEventObject<TouchEvent>) => void}
        onDragEnd={handleDragEnd}
        onTransformEnd={handleTransformEnd}
      >
        {renderShape()}
        {label && element.width > 40 && (
          <Text
            text={label}
            fontSize={11}
            fill="#374151"
            width={element.width}
            height={element.height}
            align="center"
            verticalAlign="middle"
            listening={false}
          />
        )}
      </Group>

      {isSelected && !isLocked && (
        <Transformer
          ref={trRef}
          rotateEnabled={true}
          anchorSize={14}
          anchorCornerRadius={3}
          anchorStroke="#2563eb"
          anchorFill="#dbeafe"
          anchorStrokeWidth={2}
          borderStroke="#2563eb"
          borderStrokeWidth={1.5}
          borderDash={[4, 4]}
          padding={4}
          enabledAnchors={[
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "middle-left",
            "middle-right",
            "top-center",
            "bottom-center",
          ]}
          boundBoxFunc={(oldBox, newBox) => {
            if (newBox.width < 10 || newBox.height < 10) return oldBox;
            return newBox;
          }}
        />
      )}
    </>
  );
}
