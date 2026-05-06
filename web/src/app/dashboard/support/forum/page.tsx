"use client";

import { useEffect, useState } from "react";
import { listForumCategories, listForumThreads, type ForumCategory, type ForumThread } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Pin, CheckCircle, ArrowUp } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";

export default function ForumPage() {
  const searchParams = useSearchParams();
  const categorySlug = searchParams.get("category");
  const [categories, setCategories] = useState<ForumCategory[]>([]);
  const [threads, setThreads] = useState<ForumThread[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [cats, threadResult] = await Promise.all([
          listForumCategories(),
          listForumThreads({ category_slug: categorySlug || undefined }),
        ]);
        setCategories(cats);
        setThreads(threadResult.threads);
      } catch {
        toast.error("Failed to load forum");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [categorySlug]);

  return (
    <>
      <PageHeader
        title="Community Forum"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Support", href: "/dashboard/support" },
          { label: "Forum" },
        ]}
        action={
          <Link href="/dashboard/support/forum/new">
            <Button size="sm">New Thread</Button>
          </Link>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* Category chips */}
        <div className="flex flex-wrap gap-2">
          <Link href="/dashboard/support/forum">
            <Badge variant={!categorySlug ? "default" : "outline"} className="cursor-pointer">All</Badge>
          </Link>
          {categories.map((cat) => (
            <Link key={cat.id} href={`/dashboard/support/forum?category=${cat.slug}`}>
              <Badge variant={categorySlug === cat.slug ? "default" : "outline"} className="cursor-pointer">
                {cat.name} ({cat.thread_count})
              </Badge>
            </Link>
          ))}
        </div>

        {/* Threads */}
        {loading ? (
          <div className="space-y-2">
            {[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} className="h-16 w-full" />)}
          </div>
        ) : threads.length === 0 ? (
          <div className="py-12 text-center">
            <p className="text-muted-foreground">No threads yet. Be the first to start a discussion!</p>
          </div>
        ) : (
          <div className="space-y-2">
            {threads.map((thread) => (
              <Link key={thread.id} href={`/dashboard/support/forum/${thread.id}`}>
                <Card className="transition-colors hover:border-primary">
                  <CardContent className="flex items-center gap-4 py-3">
                    {/* Upvotes */}
                    <div className="flex flex-col items-center text-xs text-muted-foreground">
                      <ArrowUp className="size-4" />
                      <span>{thread.upvotes}</span>
                    </div>

                    {/* Title + meta */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        {thread.is_pinned && <Pin className="size-3 text-primary" />}
                        {thread.has_solution && <CheckCircle className="size-3 text-green-500" />}
                        <p className="font-medium text-sm truncate">{thread.title}</p>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                        <span>{thread.reply_count} replies</span>
                        <span>·</span>
                        <span>{thread.view_count} views</span>
                        <span>·</span>
                        <span>{new Date(thread.last_activity_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    {/* Status */}
                    {thread.status !== "open" && (
                      <Badge variant="secondary" className="text-xs">{thread.status}</Badge>
                    )}
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
