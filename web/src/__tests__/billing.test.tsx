import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/billing",
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

vi.mock("@/lib/api", () => ({
  getBillingStatus: vi.fn().mockResolvedValue({
    plan: "free",
    plan_name: "Seedling (Free)",
    stripe_customer_id: null,
    stripe_subscription_id: null,
    portal_url: null,
  }),
  createCheckout: vi.fn().mockResolvedValue({ checkout_url: "https://checkout.stripe.com/test" }),
  createPortalSession: vi.fn().mockResolvedValue({ portal_url: "https://billing.stripe.com/test" }),
}));

import BillingPage from "@/app/dashboard/billing/page";

describe("BillingPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders billing heading", async () => {
    render(<BillingPage />);
    await waitFor(() => {
      expect(screen.getByText("Billing")).toBeDefined();
    });
  });

  it("shows current plan", async () => {
    render(<BillingPage />);
    await waitFor(() => {
      expect(screen.getByText("Seedling (Free)")).toBeDefined();
    });
  });

  it("shows plan options", async () => {
    render(<BillingPage />);
    await waitFor(() => {
      expect(screen.getByText("Hobby")).toBeDefined();
      expect(screen.getByText("Pro")).toBeDefined();
      expect(screen.getByText("Commercial")).toBeDefined();
    });
  });

  it("shows current plan indicator", async () => {
    render(<BillingPage />);
    await waitFor(() => {
      expect(screen.getByText("Current Plan")).toBeDefined();
    });
  });
});
