"use client";

import { useRef, useState, type ReactNode } from "react";
import { motion, useMotionValue, useTransform, type PanInfo } from "framer-motion";
import { Loader2 } from "lucide-react";

const PULL_THRESHOLD = 80;

interface PullToRefreshProps {
  onRefresh: () => Promise<void>;
  children: ReactNode;
  className?: string;
}

/**
 * Wrap scrollable content to enable pull-to-refresh on touch devices.
 * Shows a spinner indicator when pulled down past the threshold.
 */
export function PullToRefresh({ onRefresh, children, className }: PullToRefreshProps) {
  const y = useMotionValue(0);
  const [refreshing, setRefreshing] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const spinOpacity = useTransform(y, [0, PULL_THRESHOLD], [0, 1]);
  const spinRotate = useTransform(y, [0, PULL_THRESHOLD], [0, 180]);

  const handleDragEnd = async (_: unknown, info: PanInfo) => {
    if (info.offset.y > PULL_THRESHOLD && !refreshing) {
      setRefreshing(true);
      try {
        await onRefresh();
      } finally {
        setRefreshing(false);
      }
    }
  };

  // Only allow pull when scroll is at the top
  const handleDragStart = () => {
    const el = containerRef.current;
    if (el && el.scrollTop > 0) {
      // Reset motion value to prevent drag when not at top
      y.set(0);
    }
  };

  return (
    <div ref={containerRef} className={className}>
      {/* Refresh indicator */}
      <motion.div
        className="flex items-center justify-center py-2"
        style={{ opacity: refreshing ? 1 : spinOpacity, height: refreshing ? 40 : 0 }}
      >
        <motion.div style={{ rotate: refreshing ? undefined : spinRotate }}>
          <Loader2 className={`size-5 text-muted-foreground ${refreshing ? "animate-spin" : ""}`} />
        </motion.div>
      </motion.div>
      <motion.div
        style={{ y: refreshing ? 0 : y }}
        drag={refreshing ? false : "y"}
        dragConstraints={{ top: 0, bottom: 120 }}
        dragElastic={0.4}
        dragSnapToOrigin
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        {children}
      </motion.div>
    </div>
  );
}
