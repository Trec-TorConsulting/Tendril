import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/grow-types",
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

const { mockCustomTypes, mockBuiltIn } = vi.hoisted(() => {
  const mockCustomTypes = [
    {
      id: "gt1",
      slug: "my-dwc",
      name: "My Custom DWC",
      category: "hydroponic",
      description: "Custom DWC variant",
      base_type: "dwc",
      profile: { ph_range: { min: 5.5, max: 6.5 } },
      submitted_for_review: false,
      approved: false,
    },
  ];

  const mockBuiltIn = [
    { id: "dwc", name: "Deep Water Culture", category: "hydroponic" },
    { id: "nft", name: "NFT", category: "hydroponic" },
  ];
  return { mockCustomTypes, mockBuiltIn };
});

vi.mock("@/lib/api", () => ({
  listCustomGrowTypes: vi.fn().mockResolvedValue(mockCustomTypes),
  listGrowTypes: vi.fn().mockResolvedValue(mockBuiltIn),
  createCustomGrowType: vi.fn().mockResolvedValue({ ...mockCustomTypes[0], id: "gt2" }),
  deleteCustomGrowType: vi.fn().mockResolvedValue(undefined),
  submitGrowTypeForReview: vi.fn().mockResolvedValue({ status: "submitted" }),
}));

import GrowTypesPage from "@/app/dashboard/grow-types/page";

describe("GrowTypesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows page title", async () => {
    render(<GrowTypesPage />);
    await waitFor(() => {
      expect(screen.getByText("Grow Types")).toBeInTheDocument();
    });
  });

  it("shows built-in types in default tab", async () => {
    render(<GrowTypesPage />);
    await waitFor(() => {
      expect(screen.getByText("Deep Water Culture")).toBeInTheDocument();
    });
  });

  it("shows custom tab with count", async () => {
    render(<GrowTypesPage />);
    await waitFor(() => {
      expect(screen.getByText(/My Custom \(1\)/)).toBeInTheDocument();
    });
  });

  it("opens create modal", async () => {
    render(<GrowTypesPage />);
    await waitFor(() => {
      expect(screen.getByText("Custom Grow Type")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText("Custom Grow Type"));
    await waitFor(() => {
      expect(screen.getByText("New Custom Grow Type")).toBeInTheDocument();
    });
  });

  it("shows built-in category", async () => {
    render(<GrowTypesPage />);
    await waitFor(() => {
      expect(screen.getAllByText(/hydroponic/i).length).toBeGreaterThanOrEqual(1);
    });
  });
});
