import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/notifications",
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
  getRefreshToken: () => "test-refresh",
  isAuthenticated: () => true,
  setTokens: vi.fn(),
  clearTokens: vi.fn(),
}));

vi.mock("@/components/confirm-dialog", () => ({
  useConfirm: () => vi.fn().mockResolvedValue(true),
  ConfirmProvider: ({ children }: { children: React.ReactNode }) => children,
}));

vi.mock("@/components/ui/sidebar", async () =>
  (await import("./helpers/sidebar-mock")).sidebarModuleMock());

const { mockChannels, mockLogs } = vi.hoisted(() => {
  const mockChannels = [
    {
      id: "ch1",
      channel_type: "discord",
      name: "Dev Alerts",
      config: { webhook_url: "https://discord.com/api/webhooks/test" },
      enabled: true,
    },
  ];
  const mockLogs = [
    {
      id: "log-1",
      channel_type: "in_app",
      event_type: "ai_action_lifecycle",
      severity: "warning",
      subject: "Approval needed",
      body: "Review a pending integration action.",
      status: "sent",
      error: null,
      created_at: "2026-06-25T10:30:00Z",
    },
  ];
  return { mockChannels, mockLogs };
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
  listNotificationLogs: vi.fn().mockResolvedValue(mockLogs),
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

  it("renders ai lifecycle feed", async () => {
    render(<NotificationsPage />);
    await waitFor(() => {
      expect(screen.getByText("AI Lifecycle Feed")).toBeDefined();
      expect(screen.getByText("Approval needed")).toBeDefined();
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
