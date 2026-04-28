import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

const { mockOpenChat, mockReplace } = vi.hoisted(() => {
  const mockOpenChat = vi.fn();
  const mockReplace = vi.fn();
  return { mockOpenChat, mockReplace };
});

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: mockReplace }),
  usePathname: () => "/dashboard/ai",
  useParams: () => ({}),
}));

vi.mock("@/components/chat-provider", () => ({
  useChat: () => ({ openChat: mockOpenChat, toggle: vi.fn() }),
  ChatProvider: ({ children }: any) => children,
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

  it("redirects to dashboard", async () => {
    render(<AiChatPage />);
    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith("/dashboard");
    });
  });

  it("renders nothing", () => {
    const { container } = render(<AiChatPage />);
    expect(container.innerHTML).toBe("");
  });
});
