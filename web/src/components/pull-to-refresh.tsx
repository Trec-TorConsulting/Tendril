"use client";

import { useCallback, useRef, useState, type ReactNode } from "react";
import { Loader2 } from "lucide-react";

const PULL_THRESHOLD = 80;

interface PullToRefreshProps {
  onRefresh: () => Promise<void>;
  children: ReactNode;
  className?: string;
}

/**
 * Wrap scrollable content to enable pull-to-refresh on touch devices.
 * Uses native touch events so iOS scroll is never blocked.
 */
export function PullToRefresh({ onRefresh, children, className }: PullToRefreshProps) {
  const [refreshing, setRefreshing] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const startYRef = useRef(0);
  const pullingRef = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    if (refreshing) return;
    // Only activate pull when scrolled to top
    const scrollTop = containerRef.current?.scrollTop ?? window.scrollY ?? document.documentElement.scrollTop;
    if (scrollTop <= 0) {
      startYRef.current = e.touches[0].clientY;
      pullingRef.current = true;
    }
  }, [refreshing]);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (!pullingRef.current || refreshing) return;
    const currentY = e.touches[0].clientY;
    const diff = currentY - startYRef.current;
    if (diff > 0) {
      // Apply resistance
      setPullDistance(Math.min(diff * 0.4, 120));
    } else {
      // User scrolling up — cancel pull tracking
      pullingRef.current = false;
      setPullDistance(0);
    }
  }, [refreshing]);

  const handleTouchEnd = useCallback(async () => {
    if (!pullingRef.current) return;
    pullingRef.current = false;
    if (pullDistance >= PULL_THRESHOLD && !refreshing) {
      setRefreshing(true);
      setPullDistance(0);
      try {
        await onRefresh();
      } finally {
        setRefreshing(false);
      }
    } else {
      setPullDistance(0);
    }
  }, [pullDistance, refreshing, onRefresh]);

  return (
    <div
      ref={containerRef}
      className={className}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* Refresh indicator */}
      <div
        className="flex items-center justify-center overflow-hidden transition-[height,opacity] duration-200"
        style={{
          height: refreshing ? 40 : pullDistance > 10 ? pullDistance * 0.5 : 0,
          opacity: refreshing ? 1 : Math.min(pullDistance / PULL_THRESHOLD, 1),
        }}
      >
        <Loader2
          className={`size-5 text-muted-foreground ${refreshing ? "animate-spin" : ""}`}
          style={{ transform: refreshing ? undefined : `rotate(${(pullDistance / PULL_THRESHOLD) * 180}deg)` }}
        />
      </div>
      <div
        style={{
          transform: refreshing ? undefined : pullDistance > 0 ? `translateY(${pullDistance * 0.3}px)` : undefined,
          transition: pullingRef.current ? "none" : "transform 0.2s ease-out",
        }}
      >
        {children}
      </div>
    </div>
  );
}
