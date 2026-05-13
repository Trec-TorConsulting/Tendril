import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

const { mockOpenChat } = vi.hoisted(() => {
  const mockOpenChat = vi.fn();
  return { mockOpenChat };
});

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  usePathname: () => "/dashboard/ai",
  useParams: () => ({}),
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("@/components/chat-provider", () => ({
  useChat: () => ({ openChat: mockOpenChat, toggle: vi.fn() }),
  ChatProvider: ({ children }: any) => children,
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

import AiChatPage from "@/app/dashboard/ai/page";

describe("AiChatPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls openChat on mount", async () => {
    render(<AiChatPage />);
    await waitFor(() => {
      expect(mockOpenChat).toHaveBeenCalled();
    });
  });

  it("renders AI Chat heading", async () => {
    render(<AiChatPage />);
    await waitFor(() => {
      expect(screen.getByText("Chat")).toBeInTheDocument();
    });
  });

  it("renders side panel message", () => {
    render(<AiChatPage />);
    expect(screen.getByText(/side panel/)).toBeInTheDocument();
  });
});
