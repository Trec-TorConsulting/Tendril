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

  it("renders structured nutrient adjustments instead of raw JSON", async () => {
    const { useApiSWR } = await import("@/lib/swr");
    vi.mocked(useApiSWR).mockReturnValue({
      data: {
        coachTip: "Hold steady.",
        coachGeneratedAt: new Date().toISOString(),
        coachCached: true,
        insights: {
          nutrient_advice: {
            result: {
              adjustments: [
                { nutrient: "POTASSIUM", action: "increase", amount: "+5% PK" },
                { nutrient: "CALCIUM", action: "maintain", amount: "standard" },
              ],
              reasoning: "Seedling stage needs light feeding.",
            },
            generatedAt: new Date().toISOString(),
            cached: true,
          },
        },
      },
      isLoading: false,
      mutate: vi.fn(),
    } as never);

    const { DashboardAiInsights } = await import("@/components/dashboard-ai-insights");
    const { container } = render(
      <DashboardAiInsights growId="grow-1" growStage="seedling" hasSensorData={false} />,
    );

    expect(screen.getByText("Potassium")).toBeInTheDocument();
    expect(screen.getByText("Calcium")).toBeInTheDocument();
    expect(screen.getByText("Seedling stage needs light feeding.")).toBeInTheDocument();
    expect(container.textContent).not.toContain("```");
    expect(container.textContent).not.toContain('"adjustments"');
  });

  it("cleans prose and drops raw JSON when the insight is an unparsed string", async () => {
    const { useApiSWR } = await import("@/lib/swr");
    const degraded =
      'Based on the provided information, here are some general recommendations: ```json { "adjustments": [ { "nutrient": "POTASSIUM", "action": "increase"';
    vi.mocked(useApiSWR).mockReturnValue({
      data: {
        coachTip: "Hold steady.",
        coachGeneratedAt: new Date().toISOString(),
        coachCached: true,
        insights: {
          nutrient_advice: {
            result: degraded,
            generatedAt: new Date().toISOString(),
            cached: true,
          },
        },
      },
      isLoading: false,
      mutate: vi.fn(),
    } as never);

    const { DashboardAiInsights } = await import("@/components/dashboard-ai-insights");
    const { container } = render(
      <DashboardAiInsights growId="grow-1" growStage="seedling" hasSensorData={false} />,
    );

    expect(screen.getByText(/here are some general recommendations/i)).toBeInTheDocument();
    expect(container.textContent).not.toContain("```");
    expect(container.textContent).not.toContain('"nutrient"');
  });
});
