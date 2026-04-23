"use client";

import { useState } from "react";
import { motion, useMotionValue, useTransform, type PanInfo } from "framer-motion";
import { CheckCircle2, Trash2 } from "lucide-react";

const SWIPE_THRESHOLD = 100;

interface SwipeableCardProps {
  children: React.ReactNode;
  onSwipeRight?: () => void;
  onSwipeLeft?: () => void;
  rightLabel?: string;
  leftLabel?: string;
}

/**
 * Wrap a card to enable swipe gestures on mobile.
 * Swipe right → primary action (e.g. complete), swipe left → destructive action (e.g. delete).
 */
export function SwipeableCard({
  children,
  onSwipeRight,
  onSwipeLeft,
  rightLabel = "Complete",
  leftLabel = "Delete",
}: SwipeableCardProps) {
  const x = useMotionValue(0);
  const [swiped, setSwiped] = useState(false);

  // Background reveal opacity (0 → 1 as user drags)
  const rightBg = useTransform(x, [0, SWIPE_THRESHOLD], [0, 1]);
  const leftBg = useTransform(x, [-SWIPE_THRESHOLD, 0], [1, 0]);

  const handleDragEnd = (_: unknown, info: PanInfo) => {
    if (swiped) return;
    if (info.offset.x > SWIPE_THRESHOLD && onSwipeRight) {
      setSwiped(true);
      onSwipeRight();
    } else if (info.offset.x < -SWIPE_THRESHOLD && onSwipeLeft) {
      setSwiped(true);
      onSwipeLeft();
    }
  };

  return (
    <div className="relative overflow-hidden rounded-xl">
      {/* Right-swipe background (green / complete) */}
      {onSwipeRight && (
        <motion.div
          className="absolute inset-0 flex items-center gap-2 rounded-xl bg-green-500/20 px-6 text-green-600 dark:text-green-400"
          style={{ opacity: rightBg }}
        >
          <CheckCircle2 className="size-5" />
          <span className="text-sm font-medium">{rightLabel}</span>
        </motion.div>
      )}
      {/* Left-swipe background (red / delete) */}
      {onSwipeLeft && (
        <motion.div
          className="absolute inset-0 flex items-center justify-end gap-2 rounded-xl bg-red-500/20 px-6 text-red-600 dark:text-red-400"
          style={{ opacity: leftBg }}
        >
          <span className="text-sm font-medium">{leftLabel}</span>
          <Trash2 className="size-5" />
        </motion.div>
      )}
      {/* Draggable card surface */}
      <motion.div
        style={{ x }}
        drag="x"
        dragConstraints={{ left: onSwipeLeft ? -160 : 0, right: onSwipeRight ? 160 : 0 }}
        dragElastic={0.2}
        dragSnapToOrigin
        onDragEnd={handleDragEnd}
        className="relative"
      >
        {children}
      </motion.div>
    </div>
  );
}
