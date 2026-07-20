import { describe, expect, it } from "vitest";
import { computeTopSectionOrder } from "@/hooks/use-dashboard-priority";
import type { TaskItem } from "@/lib/api";

function task(overrides: Partial<TaskItem>): TaskItem {
  return {
    id: "task-1",
    title: "Task",
    description: null,
    status: "pending",
    priority: "medium",
    category: "maintenance",
    source: "automation",
    assigned_to: null,
    created_by: "user-1",
    grow_cycle_id: "grow-1",
    tent_id: null,
    bucket_id: null,
    due_date: null,
    completed_at: null,
    recurring: null,
    recurring_interval_days: null,
    routine: null,
    estimated_minutes: null,
    created_at: new Date().toISOString(),
    ...overrides,
  };
}

describe("computeTopSectionOrder", () => {
  it("prioritizes health above AI when critical alert tasks exist", () => {
    const order = computeTopSectionOrder({
      tasks: [task({ category: "alert_response", priority: "urgent" })],
      growStage: "flowering",
    });

    expect(order).toEqual(["next", "health", "ai"]);
  });

  it("prioritizes AI before health during flowering when no critical alerts", () => {
    const order = computeTopSectionOrder({
      tasks: [task({ category: "maintenance", priority: "medium" })],
      growStage: "flowering",
    });

    expect(order).toEqual(["next", "ai", "health"]);
  });

  it("uses default order outside flower window", () => {
    const order = computeTopSectionOrder({
      tasks: [task({ category: "maintenance", priority: "medium" })],
      growStage: "vegetative",
    });

    expect(order).toEqual(["next", "health", "ai"]);
  });
});
