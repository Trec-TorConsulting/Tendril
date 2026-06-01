"use client";

import { useMemo } from "react";
import { Arrow, Line, Text, Group } from "react-konva";
import type { Connector, FieldElement } from "../types";
import { useCanvasStore } from "../hooks/use-canvas-state";

/**
 * Get the absolute position of an anchor on an element.
 */
function getAnchorPos(
  el: FieldElement,
  anchor: "top" | "right" | "bottom" | "left"
): { x: number; y: number } {
  const cx = el.x + el.width / 2;
  const cy = el.y + el.height / 2;

  switch (anchor) {
    case "top":
      return { x: cx, y: el.y };
    case "bottom":
      return { x: cx, y: el.y + el.height };
    case "left":
      return { x: el.x, y: cy };
    case "right":
      return { x: el.x + el.width, y: cy };
  }
}

interface Props {
  connector: Connector;
}

export function ConnectorLine({ connector }: Props) {
  const elements = useCanvasStore((s) => s.elements);
  const selectedIds = useCanvasStore((s) => s.selectedIds);

  const fromEl = elements.find((e) => e.id === connector.fromId);
  const toEl = elements.find((e) => e.id === connector.toId);

  const points = useMemo(() => {
    if (!fromEl || !toEl) return null;

    const from = getAnchorPos(fromEl, connector.fromAnchor);
    const to = getAnchorPos(toEl, connector.toAnchor);

    if (connector.lineType === "straight") {
      return [from.x, from.y, to.x, to.y];
    }

    if (connector.lineType === "elbow") {
      // Orthogonal path: go halfway then turn
      const midX = (from.x + to.x) / 2;
      return [from.x, from.y, midX, from.y, midX, to.y, to.x, to.y];
    }

    // Curve: use midpoints as control-like segments
    const midX = (from.x + to.x) / 2;
    const midY = (from.y + to.y) / 2;
    return [from.x, from.y, midX, from.y, midX, midY, midX, to.y, to.x, to.y];
  }, [fromEl, toEl, connector.fromAnchor, connector.toAnchor, connector.lineType]);

  if (!points || !fromEl || !toEl) return null;

  const isSelected = selectedIds.has(connector.id);
  const strokeColor = connector.flowDirection === "none" ? "#6b7280" : "#0891b2";

  return (
    <Group>
      {connector.flowDirection !== "none" ? (
        <Arrow
          points={points}
          stroke={strokeColor}
          strokeWidth={isSelected ? 3 : 2}
          fill={strokeColor}
          pointerLength={8}
          pointerWidth={6}
          lineCap="round"
          lineJoin="round"
          dash={connector.lineType === "elbow" ? undefined : [8, 4]}
          tension={connector.lineType === "curve" ? 0.3 : 0}
        />
      ) : (
        <Line
          points={points}
          stroke={strokeColor}
          strokeWidth={isSelected ? 3 : 2}
          lineCap="round"
          lineJoin="round"
          dash={[6, 4]}
          tension={connector.lineType === "curve" ? 0.3 : 0}
        />
      )}
      {connector.label && (
        <Text
          x={(points[0] + points[points.length - 2]) / 2 - 20}
          y={(points[1] + points[points.length - 1]) / 2 - 8}
          text={connector.label}
          fontSize={10}
          fill="#374151"
          padding={2}
        />
      )}
    </Group>
  );
}
