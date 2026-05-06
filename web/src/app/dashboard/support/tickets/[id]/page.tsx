"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getAccessToken } from "@/lib/auth";
import { getTicket, addTicketMessage, closeTicket, rateTicket, type TicketDetail } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";

export default function TicketDetailPage() {
  const params = useParams();
  const ticketId = params.id as string;
  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [refreshCount, setRefreshCount] = useState(0);

  useEffect(() => {
    let cancelled = false;
    async function fetchTicket() {
      const token = getAccessToken();
      if (!token) return;
      try {
        const data = await getTicket(token, ticketId);
        if (!cancelled) setTicket(data);
      } catch {
        if (!cancelled) toast.error("Failed to load ticket");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchTicket();
    return () => { cancelled = true; };
  }, [ticketId, refreshCount]);

  const reload = () => setRefreshCount((c) => c + 1);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    const token = getAccessToken();
    if (!token) return;

    setSending(true);
    try {
      await addTicketMessage(token, ticketId, message);
      setMessage("");
      reload();
      toast.success("Message sent");
    } catch {
      toast.error("Failed to send message");
    } finally {
      setSending(false);
    }
  };

  const handleClose = async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await closeTicket(token, ticketId);
      reload();
      toast.success("Ticket closed");
    } catch {
      toast.error("Failed to close ticket");
    }
  };

  if (loading) {
    return (
      <>
        <PageHeader title="Ticket" breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Support", href: "/dashboard/support" }, { label: "Loading..." }]} />
        <div className="p-4 lg:p-6 space-y-4">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-40 w-full" />
        </div>
      </>
    );
  }

  if (!ticket) {
    return <p className="p-6 text-muted-foreground">Ticket not found.</p>;
  }

  const isClosed = ticket.status === "closed" || ticket.status === "resolved";

  return (
    <>
      <PageHeader
        title={ticket.subject}
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Support", href: "/dashboard/support" },
          { label: "Tickets", href: "/dashboard/support/tickets" },
          { label: ticket.subject },
        ]}
      />
      <div className="flex flex-1 flex-col gap-4 p-4 lg:p-6 max-w-3xl">
        {/* Status bar */}
        <div className="flex items-center gap-3">
          <Badge>{ticket.status.replace(/_/g, " ")}</Badge>
          <Badge variant="outline">{ticket.priority}</Badge>
          <Badge variant="secondary">{ticket.category}</Badge>
          {!isClosed && (
            <Button variant="outline" size="sm" className="ml-auto" onClick={handleClose}>
              Close Ticket
            </Button>
          )}
        </div>

        {/* Messages */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Conversation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {ticket.messages.map((msg) => (
              <div key={msg.id} className="rounded-lg border p-3">
                <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                  <span>{msg.author_id === ticket.messages[0]?.author_id ? "You" : "Support"}</span>
                  <span>{new Date(msg.created_at).toLocaleString()}</span>
                </div>
                <p className="text-sm whitespace-pre-wrap">{msg.body}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Reply form */}
        {!isClosed && (
          <Card>
            <CardContent className="pt-4">
              <form onSubmit={handleSendMessage} className="space-y-3">
                <textarea
                  className="flex min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm placeholder:text-muted-foreground"
                  placeholder="Type your reply..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                />
                <Button type="submit" disabled={sending || !message.trim()}>
                  {sending ? "Sending..." : "Send Reply"}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Rating (if closed) */}
        {isClosed && !ticket.satisfaction_rating && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">How was your experience?</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((r) => (
                  <Button
                    key={r}
                    variant="outline"
                    size="sm"
                    onClick={async () => {
                      const token = getAccessToken();
                      if (!token) return;
                      await rateTicket(token, ticketId, r);
                      reload();
                      toast.success("Thanks for your feedback!");
                    }}
                  >
                    {"⭐".repeat(r)}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}
