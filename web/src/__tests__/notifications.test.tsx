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

const mockChannels = [
  {
    id: "ch1",
    channel_type: "discord",
    name: "Dev Alerts",
    config: { webhook_url: "https://discord.com/api/webhooks/test" },
    enabled: true,
  },
];

vi.mock("@/lib/api", () => ({
  listChannels: vi.fn().mockResolvedValue(mockChannels),
  createChannel: vi.fn().mockResolvedValue({ id: "ch2", ...mockChannels[0], name: "New" }),
  updateChannel: vi.fn().mockResolvedValue({ ...mockChannels[0], enabled: false }),
  deleteChannel: vi.fn().mockResolvedValue(undefined),
  testChannel: vi.fn().mockResolvedValue({ status: "sent" }),
  pushSubscribe: vi.fn().mockResolvedValue({ status: "subscribed" }),
  pushUnsubscribe: vi.fn().mockResolvedValue(undefined),
}));

import NotificationsPage from "@/app/dashboard/notifications/page";

describe("NotificationsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders notifications heading", async () => {
    render(<NotificationsPage />);
    expect(screen.getByText("Notifications")).toBeDefined();
  });

  it("renders channel list", async () => {
    render(<NotificationsPage />);
    await waitFor(() => {
      expect(screen.getByText("Dev Alerts")).toBeDefined();
    });
  });

  it("renders push notifications section", () => {
    render(<NotificationsPage />);
    expect(screen.getByText("Push Notifications")).toBeDefined();
  });

  it("renders add channel button", () => {
    render(<NotificationsPage />);
    expect(screen.getByText("Add Channel")).toBeDefined();
  });

  it("opens create channel modal", async () => {
    render(<NotificationsPage />);
    fireEvent.click(screen.getByText("Add Channel"));
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
