import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ChatProvider, useChat } from "@/components/chat-provider";

const listConversationsMock = vi.fn();
const getConversationMock = vi.fn();
const useApiSWRMock = vi.fn();
const getAccessTokenMock = vi.fn();

vi.mock("@/hooks/use-grow", () => ({
  useGrow: () => ({
    selectedGrow: { id: "grow-1", name: "Flower Tent" },
  }),
}));

vi.mock("@/lib/auth", () => ({
  getAccessToken: () => getAccessTokenMock(),
}));

vi.mock("@/lib/swr", () => ({
  useApiSWR: (...args: unknown[]) => useApiSWRMock(...args),
}));

vi.mock("@/lib/api", () => ({
  getAiChatWsUrl: () => "ws://localhost:8000/v1/ai/chat",
  listConversations: (...args: unknown[]) => listConversationsMock(...args),
  getConversation: (...args: unknown[]) => getConversationMock(...args),
  listAiActions: vi.fn(),
  approveAiAction: vi.fn(),
  rejectAiAction: vi.fn(),
}));

vi.mock("@/components/ai-action-queue", () => ({
  AiActionQueue: () => <div>Action queue mock</div>,
}));

class MockWebSocket {
  static instances: MockWebSocket[] = [];

  readyState = MockWebSocket.OPEN;
  sent: string[] = [];
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(public readonly url: string) {
    MockWebSocket.instances.push(this);
  }

  send(payload: string) {
    this.sent.push(payload);
  }

  close() {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.({} as CloseEvent);
  }

  static reset() {
    MockWebSocket.instances = [];
  }

  static readonly OPEN = 1;
  static readonly CLOSED = 3;
}

function ChatHarness() {
  const { openChat } = useChat();

  return <button onClick={openChat}>Open chat</button>;
}

describe("ChatProvider conversation resume", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    MockWebSocket.reset();
    window.localStorage.clear();
    Element.prototype.scrollIntoView = vi.fn();
    getAccessTokenMock.mockReturnValue("cookie");
    useApiSWRMock.mockReturnValue({
      data: { items: [] },
      error: null,
      isLoading: false,
      isValidating: false,
      mutate: vi.fn(),
    });
    listConversationsMock.mockResolvedValue([
      {
        id: "conv-1",
        grow_cycle_id: "grow-1",
        title: "Humidity follow-up",
        message_count: 2,
        created_at: "2026-06-24T00:00:00Z",
        updated_at: "2026-06-24T00:10:00Z",
      },
    ]);
    getConversationMock.mockResolvedValue({
      id: "conv-1",
      grow_cycle_id: "grow-1",
      title: "Humidity follow-up",
      message_count: 2,
      created_at: "2026-06-24T00:00:00Z",
      updated_at: "2026-06-24T00:10:00Z",
      messages: [
        {
          id: "msg-1",
          role: "user",
          content: "What should I do about humidity?",
          metadata_json: null,
          created_at: "2026-06-24T00:00:01Z",
        },
        {
          id: "msg-2",
          role: "assistant",
          content: "Increase airflow before lights out.",
          metadata_json: null,
          created_at: "2026-06-24T00:00:03Z",
        },
      ],
    });

    vi.stubGlobal("WebSocket", MockWebSocket as unknown as typeof WebSocket);
  });

  it("reuses the latest grow conversation in the websocket handshake", async () => {
    const user = userEvent.setup();

    render(
      <ChatProvider>
        <ChatHarness />
      </ChatProvider>,
    );

    await user.click(screen.getByRole("button", { name: "Open chat" }));

    await waitFor(() => {
      expect(listConversationsMock).toHaveBeenCalledWith("cookie", "grow-1");
      expect(getConversationMock).toHaveBeenCalledWith("cookie", "conv-1");
    });

    expect(await screen.findByText("Increase airflow before lights out.")).toBeInTheDocument();

    await waitFor(() => {
      expect(MockWebSocket.instances).toHaveLength(1);
    });

    await act(async () => {
      MockWebSocket.instances[0].onopen?.(new Event("open"));
    });

    expect(JSON.parse(MockWebSocket.instances[0].sent[0])).toEqual({
      token: "cookie",
      grow_id: "grow-1",
      conversation_id: "conv-1",
    });
  });

  it("starts a fresh thread after clear chat", async () => {
    const user = userEvent.setup();

    render(
      <ChatProvider>
        <ChatHarness />
      </ChatProvider>,
    );

    await user.click(screen.getByRole("button", { name: "Open chat" }));

    expect(await screen.findByText("Increase airflow before lights out.")).toBeInTheDocument();

    await waitFor(() => {
      expect(MockWebSocket.instances).toHaveLength(1);
    });

    await act(async () => {
      MockWebSocket.instances[0].onopen?.(new Event("open"));
    });

    await user.click(screen.getByTitle("Clear chat"));

    await waitFor(() => {
      expect(MockWebSocket.instances).toHaveLength(2);
    });

    await act(async () => {
      MockWebSocket.instances[1].onopen?.(new Event("open"));
    });

    expect(MockWebSocket.instances[1].sent[0]).toContain('"grow_id":"grow-1"');
    expect(MockWebSocket.instances[1].sent[0]).not.toContain("conversation_id");
    expect(screen.queryByText("Increase airflow before lights out.")).not.toBeInTheDocument();
  });

  it("responds to keepalive pings and renders structured action events", async () => {
    const user = userEvent.setup();

    render(
      <ChatProvider>
        <ChatHarness />
      </ChatProvider>,
    );

    await user.click(screen.getByRole("button", { name: "Open chat" }));

    await waitFor(() => {
      expect(MockWebSocket.instances).toHaveLength(1);
    });

    await act(async () => {
      MockWebSocket.instances[0].onopen?.(new Event("open"));
      MockWebSocket.instances[0].onmessage?.(
        {
          data: JSON.stringify({ type: "ping", ts: "2026-06-24T00:00:10Z" }),
        } as MessageEvent,
      );
      MockWebSocket.instances[0].onmessage?.(
        {
          data: JSON.stringify({
            type: "action_event",
            phase: "executing",
            tool: "update_grow_stage",
            message: "Running tool: update grow stage",
          }),
        } as MessageEvent,
      );
      MockWebSocket.instances[0].onmessage?.(
        {
          data: JSON.stringify({
            type: "action",
            tool: "update_grow_stage",
            result: "legacy completion",
          }),
        } as MessageEvent,
      );
    });

    expect(MockWebSocket.instances[0].sent).toContain(JSON.stringify({ type: "pong" }));
    expect(screen.getByText("Running tool: update grow stage")).toBeInTheDocument();
    expect(screen.queryByText("legacy completion")).not.toBeInTheDocument();
  });
});
