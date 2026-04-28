import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/notifications",
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

const { mockChannels } = vi.hoisted(() => {
  const mockChannels = [
    {
      id: "ch1",
      channel_type: "discord",
      name: "Dev Alerts",
      config: { webhook_url: "https://discord.com/api/webhooks/test" },
      enabled: true,
    },
  ];
  return { mockChannels };
});

vi.mock("@/lib/api", () => ({
  listChannels: vi.fn().mockResolvedValue(mockChannels),
  createChannel: vi.fn().mockResolvedValue({ ...mockChannels[0], id: "ch2", name: "New" }),
  updateChannel: vi.fn().mockResolvedValue({ ...mockChannels[0], enabled: false }),
  deleteChannel: vi.fn().mockResolvedValue(undefined),
  testChannel: vi.fn().mockResolvedValue({ status: "sent" }),
  pushSubscribe: vi.fn().mockResolvedValue({ status: "subscribed" }),
  pushUnsubscribe: vi.fn().mockResolvedValue(undefined),
  listNotificationPreferences: vi.fn().mockResolvedValue([]),
  createNotificationPreference: vi.fn().mockResolvedValue({}),
  deleteNotificationPreference: vi.fn().mockResolvedValue(undefined),
}));

import NotificationsPage from "@/app/dashboard/notifications/page";

describe("NotificationsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders notifications heading", async () => {
    render(<NotificationsPage />);
    await waitFor(() => {
      expect(screen.getByText("Notifications")).toBeDefined();
    });
  });

  it("renders channel list", async () => {
    render(<NotificationsPage />);
    await waitFor(() => {
      expect(screen.getByText("Dev Alerts")).toBeDefined();
    });
  });

  it("renders push notifications section", async () => {
    render(<NotificationsPage />);
    await waitFor(() => {
      expect(screen.getByText("Push Notifications")).toBeDefined();
    });
  });

  it("renders add channel button", async () => {
    render(<NotificationsPage />);
    await waitFor(() => {
      expect(screen.getAllByText("Add Channel").length).toBeGreaterThanOrEqual(1);
    });
  });

  it("opens create channel modal", async () => {
    render(<NotificationsPage />);
    await waitFor(() => {
      expect(screen.getAllByText("Add Channel").length).toBeGreaterThanOrEqual(1);
    });
    fireEvent.click(screen.getAllByText("Add Channel")[0]);
    await waitFor(() => {
      expect(screen.getByText("Add Notification Channel")).toBeDefined();
    });
  });

  it("shows channel type badge", async () => {
    render(<NotificationsPage />);
    await waitFor(() => {
      expect(screen.getByText("discord")).toBeDefined();
    });
  });
});
