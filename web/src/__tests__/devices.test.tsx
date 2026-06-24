import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/devices",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

// Mock auth
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

// Mock API
const { mockDevices } = vi.hoisted(() => {
  const mockDevices = [
    {
      id: "uuid-1",
      device_id: "td-abc123",
      label: "Tent A Hub",
      tent_id: null,
      status: "online",
      last_seen: "2026-04-15T10:00:00Z",
      firmware_version: "1.0.0",
    },
    {
      id: "uuid-2",
      device_id: "td-def456",
      label: null,
      tent_id: null,
      status: "offline",
      last_seen: null,
      firmware_version: null,
    },
  ];
  return { mockDevices };
});

vi.mock("@/lib/api", () => ({
  listDevices: vi.fn(() => Promise.resolve(mockDevices)),
  listTents: vi.fn(() => Promise.resolve([])),
  registerDevice: vi.fn(() =>
    Promise.resolve({
      id: "uuid-3",
      device_id: "td-new789",
      psk: "super-secret-key-abc123",
      label: "New Hub",
      status: "unpaired",
    }),
  ),
  revokeDevice: vi.fn(() => Promise.resolve(mockDevices[0])),
  deleteDevice: vi.fn(() => Promise.resolve()),
  updateDevice: vi.fn(() => Promise.resolve(mockDevices[0])),
  getDeviceQrUrl: vi.fn((id: string) => `http://test/v1/devices/${id}/qr`),
  ApiError: class extends Error {
    status: number;
    detail: string;
    constructor(status: number, detail: string) {
      super(detail);
      this.status = status;
      this.detail = detail;
    }
  },
}));

describe("DevicesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders device list", async () => {
    const { default: DevicesPage } = await import(
      "@/app/dashboard/devices/page"
    );
    render(<DevicesPage />);

    await waitFor(() => {
      expect(screen.getByText("Tent A Hub")).toBeInTheDocument();
    });
    expect(screen.getByText("td-abc123")).toBeInTheDocument();
    expect(screen.getByText("online")).toBeInTheDocument();
    // td-def456 appears twice (label fallback + id), so use getAllByText
    expect(screen.getAllByText("td-def456").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("offline")).toBeInTheDocument();
  });

  it("renders heading and register button", async () => {
    const { default: DevicesPage } = await import(
      "@/app/dashboard/devices/page"
    );
    render(<DevicesPage />);

    await waitFor(() => {
      expect(screen.getByText("Devices")).toBeInTheDocument();
    });
    expect(screen.getByText("Register Device")).toBeInTheDocument();
  });

  it("shows firmware version when available", async () => {
    const { default: DevicesPage } = await import(
      "@/app/dashboard/devices/page"
    );
    render(<DevicesPage />);

    await waitFor(() => {
      expect(screen.getByText("FW: 1.0.0")).toBeInTheDocument();
    });
  });

  it("shows device action buttons", async () => {
    const { default: DevicesPage } = await import(
      "@/app/dashboard/devices/page"
    );
    render(<DevicesPage />);

    await waitFor(() => {
      expect(screen.getByText("Tent A Hub")).toBeInTheDocument();
    });
    expect(screen.getAllByRole("button").length).toBeGreaterThanOrEqual(2);
  });
});
