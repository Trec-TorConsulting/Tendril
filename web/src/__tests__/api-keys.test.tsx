import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/api-keys",
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

const mockKeys = [
  {
    id: "k1",
    name: "Home Assistant",
    key_prefix: "tnd_abcd1234",
    scopes: "read,write",
    last_used: "2025-06-10T10:00:00Z",
    expires_at: "2025-09-10T10:00:00Z",
    revoked: false,
    created_at: "2025-06-01T10:00:00Z",
  },
];

vi.mock("@/lib/api", () => ({
  listApiKeys: vi.fn().mockResolvedValue(mockKeys),
  createApiKey: vi.fn().mockResolvedValue({
    ...mockKeys[0],
    id: "k2",
    name: "New Key",
    key: "tnd_test1234567890abcdef",
  }),
  revokeApiKey: vi.fn().mockResolvedValue(undefined),
}));

import ApiKeysPage from "@/app/dashboard/api-keys/page";

describe("ApiKeysPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders page title", () => {
    render(<ApiKeysPage />);
    expect(screen.getByText("API Keys")).toBeInTheDocument();
  });

  it("shows existing keys", async () => {
    render(<ApiKeysPage />);
    await waitFor(() => {
      expect(screen.getByText("Home Assistant")).toBeInTheDocument();
      expect(screen.getByText(/tnd_abcd1234/)).toBeInTheDocument();
    });
  });

  it("shows scopes", async () => {
    render(<ApiKeysPage />);
    await waitFor(() => {
      expect(screen.getByText(/read,write/)).toBeInTheDocument();
    });
  });

  it("opens create modal", async () => {
    render(<ApiKeysPage />);
    fireEvent.click(screen.getByText("+ Generate Key"));
    await waitFor(() => {
      expect(screen.getByText("Generate API Key")).toBeInTheDocument();
    });
  });

  it("shows revoke button", async () => {
    render(<ApiKeysPage />);
    await waitFor(() => {
      expect(screen.getByText("Revoke")).toBeInTheDocument();
    });
  });

  it("shows expiry info", async () => {
    render(<ApiKeysPage />);
    await waitFor(() => {
      expect(screen.getByText(/Expires:/)).toBeInTheDocument();
    });
  });
});
