import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/strains",
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

const { mockStrains } = vi.hoisted(() => {
  const mockStrains = [
    { id: "s1", name: "Blue Dream", breeder: "DJ Short", genetics: "Blueberry x Haze", flowering_days: 65, thc_pct: 21, cbd_pct: null, notes: null },
    { id: "s2", name: "OG Kush", breeder: null, genetics: null, flowering_days: 56, thc_pct: 23, cbd_pct: null, notes: null },
  ];
  return { mockStrains };
});

vi.mock("@/lib/api", () => ({
  listStrains: vi.fn(() => Promise.resolve(mockStrains)),
  createStrain: vi.fn(() => Promise.resolve(mockStrains[0])),
  deleteStrain: vi.fn(() => Promise.resolve()),
  getStrainLeaderboard: vi.fn(() => Promise.resolve([])),
}));

describe("StrainsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders strains heading", async () => {
    const { default: StrainsPage } = await import("@/app/dashboard/strains/page");
    render(<StrainsPage />);
    await waitFor(() => {
      expect(screen.getByText("Strains")).toBeInTheDocument();
    });
  });

  it("shows Add Strain button", async () => {
    const { default: StrainsPage } = await import("@/app/dashboard/strains/page");
    render(<StrainsPage />);
    await waitFor(() => {
      expect(screen.getByText("Add Strain")).toBeInTheDocument();
    });
  });

  it("shows library and leaderboard tabs", async () => {
    const { default: StrainsPage } = await import("@/app/dashboard/strains/page");
    render(<StrainsPage />);
    await waitFor(() => {
      expect(screen.getByText("Library")).toBeInTheDocument();
      expect(screen.getByText("Leaderboard")).toBeInTheDocument();
    });
  });
});
