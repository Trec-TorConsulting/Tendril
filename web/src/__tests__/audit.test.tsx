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
}));

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

vi.mock("@/lib/api", () => ({
  listAuditLogs: vi.fn().mockResolvedValue(mockAuditPage),
}));

import AuditPage from "@/app/dashboard/audit/page";

describe("AuditPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders audit trail title", () => {
    render(<AuditPage />);
    expect(screen.getByText("Audit Trail")).toBeInTheDocument();
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

  it("shows filter controls", () => {
    render(<AuditPage />);
    expect(screen.getByText("All Actions")).toBeInTheDocument();
  });

  it("shows expandable details links", async () => {
    render(<AuditPage />);
    await waitFor(() => {
      const showButtons = screen.getAllByText("Show");
      expect(showButtons.length).toBe(2);
    });
  });
});
