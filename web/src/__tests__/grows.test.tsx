import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/grows",
  useParams: () => ({ id: "test-id" }),
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

const { mockGrows, mockTents, mockGrowTypes } = vi.hoisted(() => {
  const mockGrows = [
    {
      id: "g1",
      tent_id: "t1",
      name: "Spring DWC",
      grow_type: "dwc",
      status: "active",
      stage: "vegetative",
      started_at: "2025-03-01T00:00:00Z",
      ended_at: null,
      notes: null,
      settings: null,
    },
    {
      id: "g2",
      tent_id: "t1",
      name: "Soil Run",
      grow_type: "soil",
      status: "completed",
      stage: "curing",
      started_at: "2025-01-01T00:00:00Z",
      ended_at: "2025-04-01T00:00:00Z",
      notes: null,
      settings: null,
    },
  ];

  const mockTents = [{ id: "t1", name: "Main Tent", environment_type: "indoor", latitude: null, longitude: null, settings: null }];
  const mockGrowTypes = [{ id: "dwc", name: "Deep Water Culture (DWC)", category: "hydroponic", description: "..." }];
  return { mockGrows, mockTents, mockGrowTypes };
});

vi.mock("@/lib/api", () => ({
  listGrows: vi.fn(() => Promise.resolve(mockGrows)),
  listTents: vi.fn(() => Promise.resolve(mockTents)),
  listGrowTypes: vi.fn(() => Promise.resolve(mockGrowTypes)),
  createGrow: vi.fn(() => Promise.resolve(mockGrows[0])),
  deleteGrow: vi.fn(() => Promise.resolve()),
}));

describe("GrowsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders grows list", async () => {
    const { default: GrowsPage } = await import("@/app/dashboard/grows/page");
    render(<GrowsPage />);
    await waitFor(() => {
      expect(screen.getByText("Grows")).toBeInTheDocument();
    });
  });

  it("shows filter buttons", async () => {
    const { default: GrowsPage } = await import("@/app/dashboard/grows/page");
    render(<GrowsPage />);
    await waitFor(() => {
      expect(screen.getByText("Active")).toBeInTheDocument();
      expect(screen.getByText("Completed")).toBeInTheDocument();
      expect(screen.getByText("Archived")).toBeInTheDocument();
    });
  });

  it("shows New Grow button", async () => {
    const { default: GrowsPage } = await import("@/app/dashboard/grows/page");
    render(<GrowsPage />);
    await waitFor(() => {
      expect(screen.getAllByText("New Grow").length).toBeGreaterThanOrEqual(1);
    });
  });
});
