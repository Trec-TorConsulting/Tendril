import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/grow-types",
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
  getGrowType: vi.fn().mockResolvedValue(null),
  listGrowTypeReviewQueue: vi.fn().mockResolvedValue([]),
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
