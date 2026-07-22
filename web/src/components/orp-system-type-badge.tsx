"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { resolveOrpSystemType, type OrpSystemType } from "@/lib/orp-system-type";

interface OrpSystemTypeBadgeProps {
  value: unknown;
  className?: string;
}

function labelFor(systemType: OrpSystemType): string {
  return systemType === "live_beneficial" ? "ORP: Live" : "ORP: Sterile";
}

export function OrpSystemTypeBadge({ value, className }: OrpSystemTypeBadgeProps) {
  const systemType = resolveOrpSystemType(value);
  const isLive = systemType === "live_beneficial";

  return (
    <Badge
      variant="outline"
      className={cn(
        "gap-1.5 whitespace-nowrap",
        isLive
          ? "border-emerald-500/50 text-emerald-700 dark:text-emerald-300"
          : "border-cyan-500/50 text-cyan-700 dark:text-cyan-300",
        className,
      )}
      title={isLive ? "Live beneficial ORP thresholds" : "Sterile ORP thresholds"}
    >
      <span
        className={cn(
          "inline-block size-1.5 rounded-full",
          isLive ? "bg-emerald-500" : "bg-cyan-500",
        )}
        aria-hidden
      />
      {labelFor(systemType)}
    </Badge>
  );
}
