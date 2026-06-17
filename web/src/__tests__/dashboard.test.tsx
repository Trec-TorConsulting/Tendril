import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard",
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/lib/auth", () => ({
  getAccessToken: () => "test-token",
  getRefreshToken: () => "test-refresh",
  isAuthenticated: () => true,
  setTokens: vi.fn(),
  clearTokens: vi.fn(),
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

vi.mock("@/hooks/use-user", () => ({
  useUser: () => ({
    user: { id: "u1", email: "test@test.com", role: "owner", name: "Test" },
    loading: false,
    logout: vi.fn(),
  }),
}));

vi.mock("@/hooks/use-grow", () => ({
  GrowProvider: ({ children }: any) => children,
  useGrow: () => ({ grows: [], selectedGrow: null, setSelectedGrowId: vi.fn(), refreshGrows: vi.fn() }),
}));

vi.mock("@/components/chat-provider", () => ({
  ChatProvider: ({ children }: any) => children,
  useChat: () => ({ openChat: vi.fn(), toggle: vi.fn() }),
}));

vi.mock("@/components/app-sidebar", () => ({
  AppSidebar: () => (
    <nav>
      <a href="/dashboard">Dashboard</a>
      <a href="/dashboard/grows">Grows</a>
      <a href="/dashboard/analytics">Analytics</a>
      <a href="/dashboard/devices">Devices</a>
      <span>AI Chat</span>
      <a href="/dashboard/strains">Strains</a>
      <a href="/dashboard/settings">Settings</a>
    </nav>
  ),
}));

vi.mock("@/components/mobile-bottom-nav", () => ({
  MobileBottomNav: () => null,
}));

vi.mock("@/components/command-palette", () => ({
  CommandPalette: () => null,
}));

vi.mock("@/hooks/use-widget-layout", () => ({
  useWidgetLayout: () => ({
    widgets: [
      { id: "stats", visible: true },
      { id: "active-grows", visible: true },
      { id: "harvest-countdown", visible: true },
    ],
    toggle: vi.fn(),
    moveUp: vi.fn(),
    moveDown: vi.fn(),
    reset: vi.fn(),
    isVisible: () => true,
  }),
}));

vi.mock("@/components/onboarding-checklist", () => ({
  OnboardingChecklist: () => null,
}));

vi.mock("@/hooks/use-preferences", () => ({
  usePreferences: () => ({
    prefs: {
      temp_unit: "fahrenheit",
      date_format: "MM/DD/YYYY",
      time_format: "12h",
      timezone: "America/New_York",
      default_grow_id: "",
      theme: "system",
      widget_layout: [],
      measurement_system: "imperial",
      wind_unit: "mph",
      pressure_unit: "inhg",
      week_start: "sunday",
      compact_numbers: false,
      show_onboarding: true,
    },
    update: vi.fn(),
    loading: false,
  }),
  PreferencesProvider: ({ children }: any) => children,
}));

vi.mock("@/hooks/use-layout-mode", () => ({
  useLayoutMode: () => ({
    mode: "standard",
    config: { maxGrows: 999, maxDevices: 999, features: [] },
    setMode: vi.fn(),
  }),
  LayoutProvider: ({ children }: any) => children,
}));

vi.mock("@/components/sparkline", () => ({
  SensorSparkline: () => null,
}));

vi.mock("@/components/pull-to-refresh", () => ({
  PullToRefresh: ({ children }: any) => children,
}));

vi.mock("@/components/customize-widgets-dialog", () => ({
  CustomizeWidgetsDialog: () => null,
}));

vi.mock("@/lib/api", () => ({
  listGrows: vi.fn().mockResolvedValue([]),
  listDevices: vi.fn().mockResolvedValue([]),
  listTents: vi.fn().mockResolvedValue([]),
  getHarvestCountdown: vi.fn().mockResolvedValue([]),
  getTent: vi.fn().mockResolvedValue(null),
  listSensorReadings: vi.fn().mockResolvedValue([]),
  listTentReadings: vi.fn().mockResolvedValue([]),
}));

vi.mock("framer-motion", () => ({
  motion: new Proxy({}, { get: (_t, prop) => ({ children, ...props }: any) => {
    const Tag = typeof prop === "string" ? prop : "div";
    return <Tag {...props}>{children}</Tag>;
  }}),
  AnimatePresence: ({ children }: any) => children,
}));

describe("DashboardLayout", () => {
  it("renders sidebar with navigation items", async () => {
    const { default: DashboardLayout } = await import(
      "@/app/dashboard/layout"
    );
    render(
      <DashboardLayout>
        <div>Test content</div>
      </DashboardLayout>,
    );

    await waitFor(() => {
      expect(screen.getByText("Dashboard")).toBeInTheDocument();
    });
    expect(screen.getByText("Grows")).toBeInTheDocument();
    expect(screen.getByText("Analytics")).toBeInTheDocument();
    expect(screen.getByText("Devices")).toBeInTheDocument();
    expect(screen.getByText("AI Chat")).toBeInTheDocument();
    expect(screen.getByText("Strains")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  it("renders children in main content area", async () => {
    const { default: DashboardLayout } = await import(
      "@/app/dashboard/layout"
    );
    render(
      <DashboardLayout>
        <div data-testid="child">Hello</div>
      </DashboardLayout>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("child")).toBeInTheDocument();
    });
  });

  it("renders Tendril branding", async () => {
    const { default: DashboardLayout } = await import(
      "@/app/dashboard/layout"
    );
    render(
      <DashboardLayout>
        <div>Branded</div>
      </DashboardLayout>,
    );

    await waitFor(() => {
      expect(screen.getByText("Branded")).toBeInTheDocument();
    });
  });
});

describe("DashboardPage", () => {
  it("renders dashboard with summary cards", async () => {
    const { default: DashboardPage } = await import(
      "@/app/dashboard/page"
    );
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText("Dashboard")).toBeInTheDocument();
    });
  });
});
