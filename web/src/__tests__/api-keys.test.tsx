import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/api-keys",
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

const { mockKeys } = vi.hoisted(() => {
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
  return { mockKeys };
});

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

  it("renders page title", async () => {
    render(<ApiKeysPage />);
    await waitFor(() => {
      expect(screen.getByText("API Keys")).toBeInTheDocument();
    });
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
    await waitFor(() => {
      expect(screen.getByText("Generate Key")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText("Generate Key"));
    await waitFor(() => {
      expect(screen.getByText("Generate API Key")).toBeInTheDocument();
    });
  });

  it("shows key actions", async () => {
    render(<ApiKeysPage />);
    await waitFor(() => {
      expect(screen.getByText("Home Assistant")).toBeInTheDocument();
    });
  });

  it("shows expiry info", async () => {
    render(<ApiKeysPage />);
    await waitFor(() => {
      expect(screen.getByText(/Expires:/)).toBeInTheDocument();
    });
  });
});
