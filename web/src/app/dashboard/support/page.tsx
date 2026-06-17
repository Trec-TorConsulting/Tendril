"use client";

import { useEffect, useState } from "react";
import { listMyTickets, listKBCategories, type SupportTicket, type KBCategory } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { MessageSquare, Book, HelpCircle } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

export default function SupportPage() {
  const [hasShownError, setHasShownError] = useState(false);
  const { data: rawData, isLoading: loading, error } = useApiSWR(
    ["support", "home"],
    async (token) => {
      const [ticketResult, catResult] = await Promise.all([
        listMyTickets(token),
        listKBCategories(),
      ]);
      return {
        tickets: ticketResult.tickets.slice(0, 5),
        categories: catResult,
      };
    },
  );
  const tickets: SupportTicket[] = rawData?.tickets ?? [];
  const categories: KBCategory[] = rawData?.categories ?? [];

  useEffect(() => {
    if (error && !hasShownError) {
      toast.error("Failed to load support data");
      setHasShownError(true);
    }
  }, [error, hasShownError]);

  const statusColor = (status: string) => {
    switch (status) {
      case "open": return "default";
      case "resolved": case "closed": return "secondary";
      case "in_progress": return "outline";
      default: return "default";
    }
  };

  return (
    <>
      <PageHeader
        title="Support"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Support" }]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* Quick Actions */}
        <div className="grid gap-4 md:grid-cols-3">
          <Link href="/dashboard/support/tickets/new">
            <Card className="cursor-pointer transition-colors hover:border-primary">
              <CardHeader className="flex flex-row items-center gap-3 pb-2">
                <MessageSquare className="size-5 text-primary" />
                <CardTitle className="text-base">Submit a Ticket</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>Need help? Open a support ticket and we&apos;ll get back to you.</CardDescription>
              </CardContent>
            </Card>
          </Link>
          <Link href="/dashboard/support/kb">
            <Card className="cursor-pointer transition-colors hover:border-primary">
              <CardHeader className="flex flex-row items-center gap-3 pb-2">
                <Book className="size-5 text-primary" />
                <CardTitle className="text-base">Knowledge Base</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>Browse guides, tutorials, and troubleshooting articles.</CardDescription>
              </CardContent>
            </Card>
          </Link>
          <Link href="/dashboard/support/forum">
            <Card className="cursor-pointer transition-colors hover:border-primary">
              <CardHeader className="flex flex-row items-center gap-3 pb-2">
                <HelpCircle className="size-5 text-primary" />
                <CardTitle className="text-base">Community Forum</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>Ask questions, share tips, and connect with other growers.</CardDescription>
              </CardContent>
            </Card>
          </Link>
        </div>

        {/* Recent Tickets */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Recent Tickets</CardTitle>
            <Link href="/dashboard/support/tickets">
              <Button variant="outline" size="sm">View All</Button>
            </Link>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => <Skeleton key={i} className="h-10 w-full" />)}
              </div>
            ) : tickets.length === 0 ? (
              <p className="text-sm text-muted-foreground">No tickets yet. Need help? Submit a ticket above.</p>
            ) : (
              <div className="space-y-2">
                {tickets.map((ticket) => (
                  <Link key={ticket.id} href={`/dashboard/support/tickets/${ticket.id}`}>
                    <div className="flex items-center justify-between rounded-md border p-3 transition-colors hover:bg-muted/50">
                      <div>
                        <p className="text-sm font-medium">{ticket.subject}</p>
                        <p className="text-xs text-muted-foreground">{new Date(ticket.created_at).toLocaleDateString()}</p>
                      </div>
                      <Badge variant={statusColor(ticket.status) as "default" | "secondary" | "outline"}>{ticket.status.replace("_", " ")}</Badge>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* KB Categories */}
        {categories.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Browse Help Topics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                {categories.map((cat) => (
                  <Link key={cat.id} href={`/dashboard/support/kb?category=${cat.slug}`}>
                    <div className="flex items-center gap-3 rounded-md border p-3 transition-colors hover:bg-muted/50">
                      <div>
                        <p className="text-sm font-medium">{cat.name}</p>
                        <p className="text-xs text-muted-foreground">{cat.article_count} articles</p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}
