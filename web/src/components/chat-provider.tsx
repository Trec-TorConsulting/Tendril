"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { getAccessToken } from "@/lib/auth";
import { getAiChatWsUrl } from "@/lib/api";
import { useGrow } from "@/hooks/use-grow";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Send,
  Bot,
  User,
  CheckCircle2,
  MessageSquare,
  X,
  Trash2,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { cn } from "@/lib/utils";

// ── Types ──────────────────────────────────────────────────
interface ChatMessage {
  role: "user" | "assistant" | "action";
  content: string;
  tool?: string;
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
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const connectedGrowRef = useRef<string | undefined>(undefined);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when drawer opens
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [open]);

  // Connect / reconnect when grow changes
  const connect = useCallback(() => {
    const token = getAccessToken();
    if (!token) return;

    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    const ws = new WebSocket(getAiChatWsUrl());
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ token, grow_id: selectedGrow?.id || undefined }));
      connectedGrowRef.current = selectedGrow?.id;
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "ready") {
        setConnected(true);
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
        setMessages((prev) => [
          ...prev,
          { role: "action", content: data.result, tool: data.tool },
        ]);
        return;
      }

      if (data.type === "done") {
        setStreaming(false);
        return;
      }

      if (data.type === "error") {
        setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${data.message}` }]);
        setStreaming(false);
      }
    };

    ws.onclose = () => {
      setConnected(false);
    };

    return () => ws.close();
  }, [selectedGrow?.id]);

  // Reconnect when grow changes
  useEffect(() => {
    if (selectedGrow?.id !== connectedGrowRef.current) {
      const cleanup = connect();
      return () => cleanup?.();
    }
  }, [selectedGrow?.id, connect]);

  // Initial connection
  useEffect(() => {
    const cleanup = connect();
    return () => cleanup?.();
  }, [connect]);

  const sendMessage = () => {
    if (!input.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    setMessages((prev) => [...prev, { role: "user", content: input }]);
    wsRef.current.send(JSON.stringify({ message: input }));
    setInput("");
  };

  const clearMessages = () => {
    setMessages([]);
  };

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

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-3">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Bot className="size-10 text-muted-foreground/40" />
              <p className="mt-3 text-sm text-muted-foreground">
                Ask Tendril anything about your grow.
              </p>
              <p className="mt-1 text-xs text-muted-foreground/60">
                Chat persists as you navigate. Switch grows from the sidebar selector.
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
