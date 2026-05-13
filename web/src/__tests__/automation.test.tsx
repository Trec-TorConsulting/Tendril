import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/automation",
  useParams: () => ({}),
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/lib/auth", () => ({
  getAccessToken: () => "test-token",
}));

vi.mock("@/components/confirm-dialog", () => ({
  useConfirm: () => vi.fn().mockResolvedValue(true),
  ConfirmProvider: ({ children }: { children: React.ReactNode }) => children,
}));

vi.mock("@/components/ui/sidebar", () => ({
  Sidebar: ({ children }: any) => children,
  SidebarContent: ({ children }: any) => children,
  SidebarFooter: ({ children }: any) => children,
  SidebarGroup: ({ children }: any) => children,
  SidebarGroupAction: ({ children }: any) => children,
  SidebarGroupContent: ({ children }: any) => children,
  SidebarGroupLabel: ({ children }: any) => children,
  SidebarHeader: ({ children }: any) => children,
  SidebarInput: (props: any) => null,
  SidebarInset: ({ children }: any) => children,
  SidebarMenu: ({ children }: any) => children,
  SidebarMenuAction: ({ children }: any) => children,
  SidebarMenuBadge: ({ children }: any) => children,
  SidebarMenuButton: ({ children }: any) => children,
  SidebarMenuItem: ({ children }: any) => children,
  SidebarMenuSkeleton: () => null,
  SidebarMenuSub: ({ children }: any) => children,
  SidebarMenuSubButton: ({ children }: any) => children,
  SidebarMenuSubItem: ({ children }: any) => children,
  SidebarProvider: ({ children }: any) => children,
  SidebarRail: () => null,
  SidebarSeparator: () => null,
  SidebarTrigger: ({ children }: any) => children,
  useSidebar: () => ({
    state: "expanded",
    open: true,
    setOpen: vi.fn(),
    openMobile: false,
    setOpenMobile: vi.fn(),
    isMobile: false,
    toggleSidebar: vi.fn(),
  }),
}));

const { mockRules, mockAlerts } = vi.hoisted(() => {
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
  return { mockRules, mockAlerts };
});

vi.mock("@/lib/api", () => ({
  listAutomationRules: vi.fn().mockResolvedValue(mockRules),
  listAlerts: vi.fn().mockResolvedValue(mockAlerts),
  createAutomationRule: vi.fn().mockResolvedValue({ ...mockRules[0], id: "r2", name: "New" }),
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
    await waitFor(() => {
      expect(screen.getByText("Automation")).toBeDefined();
    });
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

  it("renders new rule button", async () => {
    render(<AutomationPage />);
    await waitFor(() => {
      expect(screen.getByText("New Rule")).toBeDefined();
    });
  });

  it("shows alerts count badge", async () => {
    render(<AutomationPage />);
    await waitFor(() => {
      expect(screen.getByText(/Alerts \(1\)/)).toBeDefined();
    });
  });

  it("opens create rule modal", async () => {
    render(<AutomationPage />);
    await waitFor(() => {
      expect(screen.getByText("New Rule")).toBeDefined();
    });
    fireEvent.click(screen.getAllByText("New Rule")[0]);
    await waitFor(() => {
      expect(screen.getByText("New Automation Rule")).toBeDefined();
    });
  });
});
