"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { getAiChatWsUrl, listGrows, type GrowResponse } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Send, Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export default function AiChatPage() {
  const [grows, setGrows] = useState<GrowResponse[]>([]);
  const [selectedGrow, setSelectedGrow] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [connected, setConnected] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const load = async () => {
      const token = getAccessToken();
      if (!token) return;
      setGrows(await listGrows(token, { status: "active" }));
    };
    load();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const connect = useCallback(() => {
    const token = getAccessToken();
    if (!token) return;

    const ws = new WebSocket(getAiChatWsUrl());
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ token, grow_id: selectedGrow || undefined }));
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
  }, [selectedGrow]);

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
    <>
      <PageHeader
        title="AI Chat"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "AI Chat" }]}
        actions={
          <div className="flex items-center gap-2">
            <Badge variant={connected ? "default" : "outline"} className="text-xs">
              {connected ? "Connected" : "Connecting…"}
            </Badge>
            <Select value={selectedGrow} onValueChange={(v) => setSelectedGrow(v ?? "")}>
              <SelectTrigger className="h-8 w-40 text-xs">
                <SelectValue placeholder="No grow context" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value=" ">No grow context</SelectItem>
                {grows.map((g) => (
                  <SelectItem key={g.id} value={g.id}>
                    {g.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        }
      />
      <div className="flex flex-1 flex-col p-4 lg:p-6">
        {/* Messages */}
        <Card className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-4">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Bot className="size-10 text-muted-foreground/50" />
                <p className="mt-3 text-sm text-muted-foreground">
                  Ask Tendril anything about your grow. Select a grow for context-aware responses.
                </p>
              </div>
            )}
            {messages.map((msg, i) => (
              <div
                key={i}
                className={cn(
                  "mb-3 flex gap-3",
                  msg.role === "user" && "flex-row-reverse"
                )}
              >
                <div className={cn(
                  "flex size-7 shrink-0 items-center justify-center rounded-full",
                  msg.role === "user" ? "bg-primary/20" : "bg-muted"
                )}>
                  {msg.role === "user" ? (
                    <User className="size-3.5 text-primary" />
                  ) : (
                    <Bot className="size-3.5 text-muted-foreground" />
                  )}
                </div>
                <div
                  className={cn(
                    "max-w-[80%] rounded-lg px-4 py-2 text-sm",
                    msg.role === "user"
                      ? "bg-primary/10 text-primary"
                      : "bg-muted"
                  )}
                >
                  <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
                </div>
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
                placeholder="Ask about your grow…"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                disabled={!connected}
                className="flex-1"
              />
              <Button size="icon" onClick={sendMessage} disabled={!connected || streaming}>
                <Send className="size-4" />
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </>
  );
}
