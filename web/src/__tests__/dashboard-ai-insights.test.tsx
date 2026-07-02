import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/swr", () => ({
  useApiSWR: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
  getCoachTip: vi.fn(),
  getAiInsight: vi.fn(),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: ReactNode; href: string }) => <a href={href}>{children}</a>,
}));

describe("DashboardAiInsights", () => {
  it("hides harvest card outside flower stages", async () => {
    const { useApiSWR } = await import("@/lib/swr");
    vi.mocked(useApiSWR).mockReturnValue({
      data: {
        coachTip: "Keep VPD stable today.",
        coachGeneratedAt: new Date().toISOString(),
        coachCached: true,
        insights: {
          harvest_predict: {
            result: { summary: "Harvest window in 17 days" },
            generatedAt: new Date().toISOString(),
            cached: true,
          },
          nutrient_advice: {
            result: { summary: "Reduce EC by 0.2" },
            generatedAt: new Date().toISOString(),
            cached: false,
          },
        },
      },
      isLoading: false,
      mutate: vi.fn(),
    } as never);

    const { DashboardAiInsights } = await import("@/components/dashboard-ai-insights");
    render(<DashboardAiInsights growId="grow-1" growStage="vegetative" hasSensorData />);

    expect(screen.getByText("AI Guidance")).toBeInTheDocument();
    expect(screen.getByText("Coach Tip")).toBeInTheDocument();
    expect(screen.queryByText("Harvest Outlook")).not.toBeInTheDocument();
    expect(screen.getByText("Nutrient Advice")).toBeInTheDocument();
  });

  it("shows harvest card during flowering stages", async () => {
    const { useApiSWR } = await import("@/lib/swr");
    vi.mocked(useApiSWR).mockReturnValue({
      data: {
        coachTip: "Watch humidity overnight.",
        coachGeneratedAt: new Date().toISOString(),
        coachCached: false,
        insights: {
          harvest_predict: {
            result: { summary: "Harvest window in 10 days" },
            generatedAt: new Date().toISOString(),
            cached: false,
          },
          nutrient_advice: {
            result: { summary: "Hold current feed ratio" },
            generatedAt: new Date().toISOString(),
            cached: true,
          },
          anomaly_scan: {
            result: { summary: "No anomalies" },
            generatedAt: new Date().toISOString(),
            cached: true,
          },
        },
      },
      isLoading: false,
      mutate: vi.fn(),
    } as never);

    const { DashboardAiInsights } = await import("@/components/dashboard-ai-insights");
    render(<DashboardAiInsights growId="grow-1" growStage="flowering" hasSensorData />);

    expect(screen.getByText("Harvest Outlook")).toBeInTheDocument();
    expect(screen.getByText("Anomaly Scan")).toBeInTheDocument();
  });
});
