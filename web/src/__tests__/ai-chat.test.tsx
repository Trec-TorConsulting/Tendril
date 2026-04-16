import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/ai",
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

const mockGrows = [
  {
    id: "g1",
    tent_id: "t1",
    name: "Spring DWC",
    grow_type: "dwc",
    status: "active",
    stage: "vegetative",
    started_at: "2025-03-01T00:00:00Z",
    ended_at: null,
    notes: null,
  },
];

// Mock WebSocket
class MockWebSocket {
  static OPEN = 1;
  readyState = 1;
  onopen: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  send = vi.fn();
  close = vi.fn();
  constructor() {
    setTimeout(() => this.onopen?.(), 0);
  }
}

vi.stubGlobal("WebSocket", MockWebSocket);

vi.mock("@/lib/api", () => ({
  listGrows: vi.fn().mockResolvedValue(mockGrows),
  getAiChatWsUrl: vi.fn().mockReturnValue("ws://test/v1/ai/chat"),
}));

import AiChatPage from "@/app/dashboard/ai/page";

describe("AiChatPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders AI Chat heading", async () => {
    render(<AiChatPage />);
    expect(screen.getByText("AI Chat")).toBeDefined();
  });

  it("renders grow selector with options", async () => {
    render(<AiChatPage />);
    await waitFor(() => {
      expect(screen.getByText("No grow context")).toBeDefined();
    });
  });

  it("renders input field and send button", () => {
    render(<AiChatPage />);
    expect(screen.getByPlaceholderText("Ask about your grow…")).toBeDefined();
    expect(screen.getByText("Send")).toBeDefined();
  });

  it("shows help text when no messages", () => {
    render(<AiChatPage />);
    expect(screen.getByText(/Ask Tendril anything/)).toBeDefined();
  });
});
