import { useMemo } from "react";
import type { TaskItem } from "@/lib/api";

export type DashboardTopSection = "next" | "health" | "ai";

export function computeTopSectionOrder({
  tasks,
  growStage,
}: {
  tasks: TaskItem[];
  growStage?: string;
}): readonly DashboardTopSection[] {
  const hasCriticalAlert = tasks.some((task) => task.category === "alert_response" || task.priority === "urgent");
  const isFlowerWindow = growStage ? ["flowering", "ripening", "harvesting"].includes(growStage) : false;

  if (hasCriticalAlert) {
    return ["next", "health", "ai"] as const;
  }
  if (isFlowerWindow) {
    return ["next", "ai", "health"] as const;
  }
  return ["next", "health", "ai"] as const;
}

export function useDashboardPriority({
  tasks,
  growStage,
}: {
  tasks: TaskItem[];
  growStage?: string;
}) {
  const topSectionOrder = useMemo(
    () => computeTopSectionOrder({ tasks, growStage }),
    [tasks, growStage],
  );

  return { topSectionOrder };
}
