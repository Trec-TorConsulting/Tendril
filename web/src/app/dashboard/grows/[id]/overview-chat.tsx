"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { getAiChatWsUrl } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Send, Bot, User, CheckCircle2, MessageSquare } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { cn } from "@/lib/utils";

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

interface OverviewChatProps {
  growId: string;
}

export function OverviewChat({ growId }: OverviewChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [connected, setConnected] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const connect = useCallback(() => {
    const token = getAccessToken();
    if (!token) return;

    const ws = new WebSocket(getAiChatWsUrl());
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ token, grow_id: growId }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "ping") {
        ws.send(JSON.stringify({ type: "pong" }));
        return;
      }

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
        return;
      }

      if (data.type === "action_event") {
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
        setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${data.message}` }]);
        setStreaming(false);
      }
    };

    ws.onclose = () => {
      setConnected(false);
    };

    return () => ws.close();
  }, [growId]);

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

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-sm font-medium">
            <MessageSquare className="size-4" /> AI Chat
          </CardTitle>
          <Badge variant={connected ? "default" : "outline"} className="text-[10px] px-1.5 py-0">
            {connected ? "Connected" : "Connecting…"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col p-0 min-h-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-2 min-h-0" style={{ maxHeight: "320px" }}>
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <Bot className="size-8 text-muted-foreground/40" />
              <p className="mt-2 text-xs text-muted-foreground">
                Ask about your grow…
              </p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                "mb-2 flex gap-2",
                msg.role === "user" && "flex-row-reverse",
                msg.role === "action" && "justify-center"
              )}
            >
              {msg.role === "action" ? (
                <div className="flex items-center gap-1.5 rounded-md border border-primary/20 bg-primary/5 px-2 py-1 text-[10px] text-primary">
                  <CheckCircle2 className="size-3" />
                  <span>{msg.content}</span>
                </div>
              ) : (
                <>
                  <div className={cn(
                    "flex size-6 shrink-0 items-center justify-center rounded-full",
                    msg.role === "user" ? "bg-primary/20" : "bg-muted"
                  )}>
                    {msg.role === "user" ? (
                      <User className="size-3 text-primary" />
                    ) : (
                      <Bot className="size-3 text-muted-foreground" />
                    )}
                  </div>
                  <div
                    className={cn(
                      "max-w-[85%] rounded-lg px-3 py-1.5 text-xs",
                      msg.role === "user"
                        ? "bg-primary/10 text-primary"
                        : "bg-muted"
                    )}
                  >
                    {msg.role === "user" ? (
                      <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
                    ) : (
                      <div className="prose prose-xs dark:prose-invert max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0 [&_p]:text-xs [&_li]:text-xs">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          ))}
          {streaming && (
            <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
              <div className="size-1.5 animate-pulse rounded-full bg-primary" />
              Thinking…
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t px-3 py-2">
          <div className="flex gap-2">
            <Input
              placeholder="Ask about your grow…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              disabled={!connected}
              className="h-8 text-xs"
            />
            <Button size="sm" className="h-8 px-2.5" onClick={sendMessage} disabled={!connected || !input.trim()}>
              <Send className="size-3.5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
