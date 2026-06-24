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

vi.mock("@/components/ui/sidebar", async () =>
  (await import("./helpers/sidebar-mock")).sidebarModuleMock());

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
