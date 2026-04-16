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

vi.mock("@/lib/api", () => ({
  listCustomGrowTypes: vi.fn().mockResolvedValue(mockCustomTypes),
  listGrowTypes: vi.fn().mockResolvedValue(mockBuiltIn),
  createCustomGrowType: vi.fn().mockResolvedValue({ id: "gt2", ...mockCustomTypes[0] }),
  deleteCustomGrowType: vi.fn().mockResolvedValue(undefined),
  submitGrowTypeForReview: vi.fn().mockResolvedValue({ status: "submitted" }),
}));

import GrowTypesPage from "@/app/dashboard/grow-types/page";

describe("GrowTypesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders custom grow types list", async () => {
    render(<GrowTypesPage />);
    await waitFor(() => {
      expect(screen.getByText("My Custom DWC")).toBeInTheDocument();
    });
  });

  it("shows page title", async () => {
    render(<GrowTypesPage />);
    expect(screen.getByText("Custom Grow Types")).toBeInTheDocument();
  });

  it("opens create modal", async () => {
    render(<GrowTypesPage />);
    fireEvent.click(screen.getByText("+ New Grow Type"));
    await waitFor(() => {
      expect(screen.getByText("New Custom Grow Type")).toBeInTheDocument();
    });
  });

  it("shows submit and delete buttons", async () => {
    render(<GrowTypesPage />);
    await waitFor(() => {
      expect(screen.getByText("Submit")).toBeInTheDocument();
      expect(screen.getByText("Delete")).toBeInTheDocument();
    });
  });

  it("shows category and base type info", async () => {
    render(<GrowTypesPage />);
    await waitFor(() => {
      expect(screen.getByText(/hydroponic/i)).toBeInTheDocument();
      expect(screen.getByText(/based on dwc/i)).toBeInTheDocument();
    });
  });
});
