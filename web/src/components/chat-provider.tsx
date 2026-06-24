"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { getAccessToken } from "@/lib/auth";
import {
  approveAiAction,
  getAiChatWsUrl,
  getConversation,
  listAiActions,
  listConversations,
  rejectAiAction,
  type ConversationMessageResponse,
} from "@/lib/api";
import { AiActionQueue } from "@/components/ai-action-queue";
import { useGrow } from "@/hooks/use-grow";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useApiSWR } from "@/lib/swr";
import {
  Send,
  Bot,
  User,
  CheckCircle2,
  MessageSquare,
  X,
  Trash2,
  TriangleAlert,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

// ── Types ──────────────────────────────────────────────────
interface ChatMessage {
  role: "user" | "assistant" | "action";
  content: string;
  tool?: string;
}

function formatActionLifecycleMessage(data: Record<string, unknown>) {
  const message = typeof data.message === "string" ? data.message : null;
  if (message) {
    return message;
  }

  const phase = typeof data.phase === "string" ? data.phase : "updated";
  const tool = typeof data.tool === "string" ? data.tool.replace(/_/g, " ") : "tool";
  return `${tool}: ${phase}`;
}

const CONVERSATION_SCOPE_GLOBAL = "global";
const CONVERSATION_STORAGE_KEY = "tendril.ai.drawer.conversations";
const NEW_CONVERSATION_SENTINEL = "__new__";

function getConversationScope(growId?: string) {
  return growId || CONVERSATION_SCOPE_GLOBAL;
}

function readConversationMap(): Record<string, string> {
  if (typeof window === "undefined") {
    return {};
  }

  try {
    const raw = window.localStorage.getItem(CONVERSATION_STORAGE_KEY);
    if (!raw) {
      return {};
    }
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") {
      return {};
    }
    return Object.fromEntries(
      Object.entries(parsed).filter((entry): entry is [string, string] => typeof entry[1] === "string"),
    );
  } catch {
    return {};
  }
}

function writeConversationMap(nextMap: Record<string, string>) {
  if (typeof window === "undefined") {
    return;
  }

  try {
    window.localStorage.setItem(CONVERSATION_STORAGE_KEY, JSON.stringify(nextMap));
  } catch {
    // Ignore storage failures; in-memory state still allows resume within the session.
  }
}

function mapConversationMessages(messages: ConversationMessageResponse[]): ChatMessage[] {
  return messages.flatMap((message) => {
    if (message.role === "user" || message.role === "assistant") {
      return [{ role: message.role, content: message.content }];
    }
    return [];
  });
}

interface ChatContextValue {
  open: boolean;
  toggle: () => void;
  openChat: () => void;
  closeChat: () => void;
}

// ── Context ────────────────────────────────────────────────
const ChatContext = createContext<ChatContextValue>({
  open: false,
  toggle: () => {},
  openChat: () => {},
  closeChat: () => {},
});

export function useChat() {
  return useContext(ChatContext);
}

// ── Provider + Drawer ──────────────────────────────────────
export function ChatProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);

  const toggle = useCallback(() => setOpen((v) => !v), []);
  const openChat = useCallback(() => setOpen(true), []);
  const closeChat = useCallback(() => setOpen(false), []);

  return (
    <ChatContext.Provider value={{ open, toggle, openChat, closeChat }}>
      {children}
      <ChatDrawer open={open} onClose={closeChat} />
    </ChatContext.Provider>
  );
}

// ── Drawer ─────────────────────────────────────────────────
function ChatDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { selectedGrow } = useGrow();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [connected, setConnected] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [decisionActionId, setDecisionActionId] = useState<string | null>(null);
  const [conversationMap, setConversationMap] = useState<Record<string, string>>(() => readConversationMap());
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [conversationHistoryLoading, setConversationHistoryLoading] = useState(false);
  const [conversationHistoryReady, setConversationHistoryReady] = useState(false);
  const [conversationHistoryError, setConversationHistoryError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const activeConversationIdRef = useRef<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const retryCount = useRef(0);
  const intentionalClose = useRef(false);
  const authFailed = useRef(false);
  const [connectionNonce, setConnectionNonce] = useState(0);
  const activeScope = useMemo(() => getConversationScope(selectedGrow?.id), [selectedGrow?.id]);

  const persistConversationId = useCallback((scope: string, conversationId: string | null) => {
    setConversationMap((current) => {
      const nextValue = conversationId ?? undefined;
      if ((current[scope] ?? undefined) === nextValue) {
        return current;
      }

      const next = { ...current };
      if (conversationId) {
        next[scope] = conversationId;
      } else {
        delete next[scope];
      }
      writeConversationMap(next);
      return next;
    });
  }, []);

  useEffect(() => {
    activeConversationIdRef.current = activeConversationId;
  }, [activeConversationId]);

  const actionKey = useMemo(
    () => (open ? (["ai-actions", selectedGrow?.id ?? "all"] as const) : null),
    [open, selectedGrow?.id],
  );
  const {
    data: actionData,
    error: actionError,
    isLoading: actionLoading,
    isValidating: actionRefreshing,
    mutate: mutateActions,
  } = useApiSWR(
    actionKey,
    (token) => listAiActions(token, { growCycleId: selectedGrow?.id, pageSize: 12 }),
    {
      refreshInterval: open ? 15_000 : 0,
    },
  );
  const actions = actionData?.items ?? [];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when drawer opens
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [open]);

  useEffect(() => {
    if (!open) {
      return;
    }

    const token = getAccessToken();
    if (!token) {
      queueMicrotask(() => {
        activeConversationIdRef.current = null;
        setActiveConversationId(null);
        setMessages([]);
        setConversationHistoryLoading(false);
        setConversationHistoryReady(false);
        setConversationHistoryError(null);
      });
      return;
    }
    const authToken = token;

    let cancelled = false;
    const rememberedConversationId = conversationMap[activeScope] ?? null;

    async function loadConversationHistory() {
      setConversationHistoryReady(false);
      setConversationHistoryLoading(true);
      setConversationHistoryError(null);

      try {
        let conversationId = rememberedConversationId;

        if (conversationId === NEW_CONVERSATION_SENTINEL) {
          if (!cancelled) {
            activeConversationIdRef.current = null;
            setActiveConversationId(null);
            setMessages([]);
          }
          return;
        }

        if (!conversationId) {
          const conversations = await listConversations(authToken, selectedGrow?.id ?? undefined);
          conversationId = conversations[0]?.id ?? null;
          if (conversationId) {
            persistConversationId(activeScope, conversationId);
          }
        }

        if (!conversationId) {
          if (!cancelled) {
            activeConversationIdRef.current = null;
            setActiveConversationId(null);
            setMessages([]);
          }
          return;
        }

        const resolvedConversationId = conversationId;

        const conversation = await getConversation(authToken, resolvedConversationId);

        if (!cancelled) {
          activeConversationIdRef.current = conversation.id;
          setActiveConversationId(conversation.id);
          setMessages(mapConversationMessages(conversation.messages));
          persistConversationId(activeScope, conversation.id);
        }
      } catch (error) {
        if (!cancelled) {
          activeConversationIdRef.current = null;
          setActiveConversationId(null);
          setMessages([]);
          setConversationHistoryError(
            error instanceof Error ? error.message : "Failed to load conversation history.",
          );
          persistConversationId(activeScope, null);
        }
      } finally {
        if (!cancelled) {
          setConversationHistoryLoading(false);
          setConversationHistoryReady(true);
        }
      }
    }

    void loadConversationHistory();

    return () => {
      cancelled = true;
    };
  }, [activeScope, conversationMap, open, persistConversationId, selectedGrow?.id]);

  // WebSocket — connects when drawer opens, auto-reconnects on drop (not on auth failure)
  useEffect(() => {
    if (!open) {
      // Drawer closed — disconnect cleanly
      intentionalClose.current = true;
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      return;
    }

    if (conversationHistoryLoading || !conversationHistoryReady) {
      return;
    }

    intentionalClose.current = false;
    authFailed.current = false;

    function connect() {
      const token = getAccessToken();
      if (!token) {
        authFailed.current = true;
        setConnected(false);
        return;
      }

      // Close existing connection
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      const growId = selectedGrow?.id;
      const ws = new WebSocket(getAiChatWsUrl());
      wsRef.current = ws;

      ws.onopen = () => {
        ws.send(
          JSON.stringify({
            token,
            grow_id: growId || undefined,
            conversation_id: activeConversationIdRef.current || undefined,
          }),
        );
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "ping") {
          ws.send(JSON.stringify({ type: "pong" }));
          return;
        }

        if (data.type === "ready") {
          setConnected(true);
          retryCount.current = 0;
          return;
        }

        if (data.type === "conversation_id") {
          if (typeof data.id === "string") {
            activeConversationIdRef.current = data.id;
            setActiveConversationId(data.id);
            persistConversationId(activeScope, data.id);
          }
          return;
        }

        if (data.type === "chunk") {
          setStreaming(true);
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            if (last && last.role === "assistant") {
              return [...prev.slice(0, -1), { ...last, content: last.content + data.content }];
            }
            return [...prev, { role: "assistant", content: data.content }];
          });
          return;
        }

        if (data.type === "action") {
          void mutateActions();
          return;
        }

        if (data.type === "action_event") {
          void mutateActions();
          setMessages((prev) => [
            ...prev,
            {
              role: "action",
              content: formatActionLifecycleMessage(data),
              tool: typeof data.tool === "string" ? data.tool : undefined,
            },
          ]);
          return;
        }

        if (data.type === "done") {
          setStreaming(false);
          return;
        }

        if (data.type === "error") {
          // Stop reconnecting on auth errors
          if (data.message?.toLowerCase().includes("auth") || data.message?.toLowerCase().includes("token")) {
            authFailed.current = true;
          }
          setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${data.message}` }]);
          setStreaming(false);
        }
      };

      ws.onerror = () => {
        // Will trigger onclose, reconnect handled there
      };

      ws.onclose = () => {
        setConnected(false);
        if (wsRef.current === ws) {
          wsRef.current = null;
        }
        // Auto-reconnect with exponential backoff (max 30s), but NOT on auth failure
        if (!intentionalClose.current && !authFailed.current) {
          const delay = Math.min(2000 * 2 ** retryCount.current, 30000);
          retryCount.current += 1;
          reconnectTimer.current = setTimeout(connect, delay);
        }
      };
    }

    connect();

    return () => {
      intentionalClose.current = true;
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeScope, connectionNonce, conversationHistoryLoading, conversationHistoryReady, open, persistConversationId, selectedGrow?.id]);

  const sendMessage = () => {
    if (!input.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    setMessages((prev) => [...prev, { role: "user", content: input }]);
    wsRef.current.send(JSON.stringify({ message: input }));
    setInput("");
  };

  const clearMessages = () => {
    persistConversationId(activeScope, NEW_CONVERSATION_SENTINEL);
    activeConversationIdRef.current = null;
    setActiveConversationId(null);
    setMessages([]);
    if (wsRef.current) {
      intentionalClose.current = true;
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
    setConnectionNonce((current) => current + 1);
  };

  const handleApproveAction = useCallback(
    async (actionId: string, reason?: string) => {
      const token = getAccessToken();
      if (!token) {
        toast.error("You need to sign in again to approve actions.");
        return;
      }

      setDecisionActionId(actionId);
      try {
        await approveAiAction(token, actionId, reason);
        toast.success("Action approved");
        await mutateActions();
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "Failed to approve action");
      } finally {
        setDecisionActionId(null);
      }
    },
    [mutateActions],
  );

  const handleRejectAction = useCallback(
    async (actionId: string, reason?: string) => {
      const token = getAccessToken();
      if (!token) {
        toast.error("You need to sign in again to reject actions.");
        return;
      }

      setDecisionActionId(actionId);
      try {
        await rejectAiAction(token, actionId, reason);
        toast.success("Action rejected");
        await mutateActions();
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "Failed to reject action");
      } finally {
        setDecisionActionId(null);
      }
    },
    [mutateActions],
  );

  return (
    <>
      {/* Backdrop (mobile) */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/40 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Drawer panel */}
      <div
        className={cn(
          "fixed right-0 top-0 z-50 flex h-dvh w-full max-w-md flex-col border-l bg-background shadow-xl transition-transform duration-300 ease-in-out",
          open ? "translate-x-0" : "translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b px-4 py-3">
          <div className="flex items-center gap-2">
            <MessageSquare className="size-4 text-primary" />
            <span className="text-sm font-semibold">AI Chat</span>
            {selectedGrow && (
              <Badge variant="secondary" className="text-[10px] px-1.5">
                {selectedGrow.name}
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-1">
            <Badge variant={connected ? "default" : "outline"} className="text-[10px] px-1.5 py-0">
              {connected ? "Connected" : "Connecting…"}
            </Badge>
            {messages.length > 0 && (
              <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={clearMessages} title="Clear chat">
                <Trash2 className="size-3.5 text-muted-foreground" />
              </Button>
            )}
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={onClose}>
              <X className="size-4" />
            </Button>
          </div>
        </div>

        {selectedGrow ? (
          <AiActionQueue
            actions={actions}
            growName={selectedGrow.name}
            isLoading={actionLoading}
            isRefreshing={actionRefreshing}
            decisionActionId={decisionActionId}
            onApprove={handleApproveAction}
            onReject={handleRejectAction}
            onRefresh={() => {
              void mutateActions();
            }}
          />
        ) : null}

        {actionError ? (
          <div className="border-b px-4 py-3">
            <Alert variant="destructive">
              <TriangleAlert className="size-4" />
              <AlertTitle>Action queue unavailable</AlertTitle>
              <AlertDescription>
                {actionError instanceof Error ? actionError.message : "Failed to load AI action proposals."}
              </AlertDescription>
            </Alert>
          </div>
        ) : null}

        {conversationHistoryError ? (
          <div className="border-b px-4 py-3">
            <Alert variant="destructive">
              <TriangleAlert className="size-4" />
              <AlertTitle>Conversation unavailable</AlertTitle>
              <AlertDescription>{conversationHistoryError}</AlertDescription>
            </Alert>
          </div>
        ) : null}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-3">
          {conversationHistoryLoading ? (
            <div className="flex items-center gap-2 py-6 text-xs text-muted-foreground">
              <div className="size-2 animate-pulse rounded-full bg-primary" />
              Restoring your last conversation...
            </div>
          ) : null}
          {!conversationHistoryLoading && messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Bot className="size-10 text-muted-foreground/40" />
              <p className="mt-3 text-sm text-muted-foreground">
                Ask Tendril anything about your grow.
              </p>
              <p className="mt-1 text-xs text-muted-foreground/60">
                Chat resumes the latest thread for each grow. Switch grows from the sidebar selector.
              </p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                "mb-3 flex gap-3",
                msg.role === "user" && "flex-row-reverse",
                msg.role === "action" && "justify-center"
              )}
            >
              {msg.role === "action" ? (
                <div className="flex items-center gap-2 rounded-md border border-primary/20 bg-primary/5 px-3 py-1.5 text-xs text-primary">
                  <CheckCircle2 className="size-3.5" />
                  <span>{msg.content}</span>
                </div>
              ) : (
                <>
                  <div
                    className={cn(
                      "flex size-7 shrink-0 items-center justify-center rounded-full",
                      msg.role === "user" ? "bg-primary/20" : "bg-muted"
                    )}
                  >
                    {msg.role === "user" ? (
                      <User className="size-3.5 text-primary" />
                    ) : (
                      <Bot className="size-3.5 text-muted-foreground" />
                    )}
                  </div>
                  <div
                    className={cn(
                      "max-w-[80%] rounded-lg px-4 py-2 text-sm",
                      msg.role === "user" ? "bg-primary/10 text-primary" : "bg-muted"
                    )}
                  >
                    {msg.role === "user" ? (
                      <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
                    ) : (
                      <div className="prose prose-sm dark:prose-invert max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          ))}
          {streaming && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <div className="size-2 animate-pulse rounded-full bg-primary" />
              Thinking…
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t p-3">
          <div className="flex gap-2">
            <Input
              ref={inputRef}
              placeholder="Ask about your grow…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              disabled={!connected}
              className="h-9"
            />
            <Button size="sm" className="h-9 px-3" onClick={sendMessage} disabled={!connected || !input.trim()}>
              <Send className="size-4" />
            </Button>
          </div>
        </div>
      </div>
    </>
  );
}
