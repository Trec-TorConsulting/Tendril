import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/automation",
  useParams: () => ({}),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/lib/auth", () => ({
  getAccessToken: () => "test-token",
}));

const mockRules = [
  {
    id: "r1",
    grow_cycle_id: null,
    name: "High pH Alert",
    sensor: "ph",
    condition: ">",
    threshold: 7.0,
    action: "alert",
    cooldown_minutes: 30,
    severity: "warning",
    enabled: true,
    last_triggered: null,
  },
];

const mockAlerts = [
  {
    id: "a1",
    alert_type: "ph_high",
    severity: "warning",
    message: "pH is above 7.0",
    sensor_value: 7.3,
    acknowledged: false,
    created_at: "2025-06-01T10:00:00Z",
  },
];

vi.mock("@/lib/api", () => ({
  listAutomationRules: vi.fn().mockResolvedValue(mockRules),
  listAlerts: vi.fn().mockResolvedValue(mockAlerts),
  createAutomationRule: vi.fn().mockResolvedValue({ id: "r2", ...mockRules[0], name: "New" }),
  updateAutomationRule: vi.fn().mockResolvedValue({ ...mockRules[0], enabled: false }),
  deleteAutomationRule: vi.fn().mockResolvedValue(undefined),
  acknowledgeAlert: vi.fn().mockResolvedValue({ status: "ok" }),
}));

import AutomationPage from "@/app/dashboard/automation/page";

describe("AutomationPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders automation heading", async () => {
    render(<AutomationPage />);
    expect(screen.getByText("Automation")).toBeDefined();
  });

  it("renders rules tab with rules list", async () => {
    render(<AutomationPage />);
    await waitFor(() => {
      expect(screen.getByText("High pH Alert")).toBeDefined();
    });
  });

  it("shows rule details", async () => {
    render(<AutomationPage />);
    await waitFor(() => {
      expect(screen.getByText(/ph > 7/)).toBeDefined();
    });
  });

  it("renders new rule button", () => {
    render(<AutomationPage />);
    expect(screen.getByText("New Rule")).toBeDefined();
  });

  it("shows alerts count badge", async () => {
    render(<AutomationPage />);
    await waitFor(() => {
      expect(screen.getByText(/Alerts \(1\)/)).toBeDefined();
    });
  });

  it("opens create rule modal", async () => {
    render(<AutomationPage />);
    fireEvent.click(screen.getByText("New Rule"));
    await waitFor(() => {
      expect(screen.getByText("New Automation Rule")).toBeDefined();
    });
  });
});
