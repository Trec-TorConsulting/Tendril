import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/audit",
  useParams: () => ({}),
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

vi.mock("@/components/ui/sidebar", async () =>
  (await import("./helpers/sidebar-mock")).sidebarModuleMock());

const { mockAuditPage } = vi.hoisted(() => {
  const mockAuditPage = {
    items: [
      {
        id: "al1",
        user_id: "u1",
        action: "create",
        resource_type: "tent",
        resource_id: "tent-abc-123",
        before_value: null,
        after_value: { name: "New Tent" },
        ip_address: "192.168.1.10",
        created_at: "2025-06-01T10:00:00Z",
      },
      {
        id: "al2",
        user_id: "u1",
        action: "update",
        resource_type: "grow",
        resource_id: "grow-def-456",
        before_value: { status: "active" },
        after_value: { status: "harvested" },
        ip_address: "192.168.1.10",
        created_at: "2025-06-01T11:00:00Z",
      },
    ],
    total: 2,
    page: 1,
    page_size: 50,
  };
  return { mockAuditPage };
});

vi.mock("@/lib/api", () => ({
  listAuditLogs: vi.fn().mockResolvedValue(mockAuditPage),
}));

import AuditPage from "@/app/dashboard/audit/page";

describe("AuditPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders audit trail title", async () => {
    render(<AuditPage />);
    await waitFor(() => {
      expect(screen.getByText("Audit Trail")).toBeInTheDocument();
    });
  });

  it("shows audit entries", async () => {
    render(<AuditPage />);
    await waitFor(() => {
      expect(screen.getByText("tent")).toBeInTheDocument();
      expect(screen.getByText("grow")).toBeInTheDocument();
    });
  });

  it("shows action badges", async () => {
    render(<AuditPage />);
    await waitFor(() => {
      expect(screen.getByText("create")).toBeInTheDocument();
      expect(screen.getByText("update")).toBeInTheDocument();
    });
  });

  it("shows filter controls", async () => {
    render(<AuditPage />);
    await waitFor(() => {
      expect(screen.getByText("Action")).toBeInTheDocument();
    });
  });

  it("shows details column", async () => {
    render(<AuditPage />);
    await waitFor(() => {
      expect(screen.getByText("Details")).toBeInTheDocument();
    });
  });
});
