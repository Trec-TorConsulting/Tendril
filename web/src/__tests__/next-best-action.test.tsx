import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { NextBestAction } from "@/components/next-best-action";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: ReactNode; href: string }) => <a href={href}>{children}</a>,
}));

describe("NextBestAction", () => {
  it("prioritizes critical alert tasks", () => {
    render(
      <NextBestAction
        growId="grow-1"
        growStage="vegetative"
        healthScore={90}
        tasks={[
          {
            id: "task-1",
            title: "Fix pH drift now",
            description: "pH is above threshold",
            status: "pending",
            category: "alert_response",
            priority: "urgent",
            source: "automation",
            assigned_to: null,
            created_by: "user-1",
            grow_cycle_id: "grow-1",
            tent_id: null,
            bucket_id: null,
            created_at: new Date().toISOString(),
            due_date: null,
            completed_at: null,
            recurring: null,
            routine: null,
            estimated_minutes: null,
          },
        ]}
      />,
    );

    expect(screen.getByText("Fix pH drift now")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Resolve" })).toHaveAttribute("href", "/dashboard/tasks");
  });

  it("suggests harvest guidance during flowering", () => {
    render(
      <NextBestAction
        growId="grow-2"
        growStage="flowering"
        healthScore={88}
        tasks={[]}
      />,
    );

    expect(screen.getByText("Review harvest guidance")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Review" })).toHaveAttribute("href", "/dashboard/grows/grow-2");
  });
});
