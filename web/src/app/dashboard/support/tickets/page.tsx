"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { listMyTickets, type SupportTicket } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import { Plus } from "lucide-react";
import { toast } from "sonner";

export default function TicketsPage() {
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    async function load() {
      const token = getAccessToken();
      if (!token) return;
      try {
        const result = await listMyTickets(token);
        setTickets(result.tickets);
        setTotal(result.total);
      } catch {
        toast.error("Failed to load tickets");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const priorityColor = (p: string) => {
    switch (p) {
      case "urgent": return "destructive";
      case "high": return "default";
      case "medium": return "secondary";
      default: return "outline";
    }
  };

  return (
    <>
      <PageHeader
        title="My Tickets"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Support", href: "/dashboard/support" },
          { label: "Tickets" },
        ]}
        action={
          <Link href="/dashboard/support/tickets/new">
            <Button size="sm"><Plus className="mr-1 size-4" /> New Ticket</Button>
          </Link>
        }
      />
      <div className="flex flex-1 flex-col gap-4 p-4 lg:p-6">
        {loading ? (
          <div className="space-y-2">
            {[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} className="h-14 w-full" />)}
          </div>
        ) : tickets.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-12 text-center">
            <p className="text-muted-foreground">You haven&apos;t submitted any tickets yet.</p>
            <Link href="/dashboard/support/tickets/new">
              <Button>Create Your First Ticket</Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-2">
            {tickets.map((ticket) => (
              <Link key={ticket.id} href={`/dashboard/support/tickets/${ticket.id}`}>
                <div className="flex items-center justify-between rounded-lg border p-4 transition-colors hover:bg-muted/50">
                  <div className="space-y-1">
                    <p className="font-medium">{ticket.subject}</p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>{ticket.category}</span>
                      <span>·</span>
                      <span>{new Date(ticket.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={priorityColor(ticket.priority) as "default" | "secondary" | "destructive" | "outline"}>{ticket.priority}</Badge>
                    <Badge variant="secondary">{ticket.status.replace(/_/g, " ")}</Badge>
                  </div>
                </div>
              </Link>
            ))}
            {total > tickets.length && (
              <p className="text-center text-sm text-muted-foreground">Showing {tickets.length} of {total} tickets</p>
            )}
          </div>
        )}
      </div>
    </>
  );
}
