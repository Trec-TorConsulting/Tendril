"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getKBArticle, voteKBArticle, type KBArticle } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ThumbsUp, ThumbsDown } from "lucide-react";
import { toast } from "sonner";

export default function KBArticlePage() {
  const params = useParams();
  const slug = params.slug as string;
  const [article, setArticle] = useState<KBArticle | null>(null);
  const [loading, setLoading] = useState(true);
  const [voted, setVoted] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        setArticle(await getKBArticle(slug));
      } catch {
        toast.error("Article not found");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  const handleVote = async (helpful: boolean) => {
    if (voted) return;
    try {
      const result = await voteKBArticle(slug, helpful);
      setArticle((prev) => prev ? { ...prev, ...result } : prev);
      setVoted(true);
      toast.success("Thanks for your feedback!");
    } catch {
      toast.error("Failed to submit vote");
    }
  };

  if (loading) {
    return (
      <div className="p-4 lg:p-6 space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!article) {
    return <p className="p-6 text-muted-foreground">Article not found.</p>;
  }

  return (
    <>
      <PageHeader
        title={article.title}
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Support", href: "/dashboard/support" },
          { label: "Knowledge Base", href: "/dashboard/support/kb" },
          { label: article.title },
        ]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6 max-w-3xl">
        {/* Tags */}
        {article.tags && article.tags.length > 0 && (
          <div className="flex gap-2">
            {article.tags.map((tag) => (
              <Badge key={tag} variant="secondary">{tag}</Badge>
            ))}
          </div>
        )}

        {/* Article body */}
        <Card>
          <CardContent className="prose prose-sm dark:prose-invert max-w-none pt-6">
            {/* In production, render Markdown with a proper renderer */}
            <div className="whitespace-pre-wrap">{article.body_markdown}</div>
          </CardContent>
        </Card>

        {/* Helpfulness */}
        <Card>
          <CardContent className="flex items-center gap-4 py-4">
            <span className="text-sm text-muted-foreground">Was this article helpful?</span>
            <Button
              variant="outline"
              size="sm"
              disabled={voted}
              onClick={() => handleVote(true)}
              className="gap-1"
            >
              <ThumbsUp className="size-4" /> Yes ({article.helpful_yes})
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={voted}
              onClick={() => handleVote(false)}
              className="gap-1"
            >
              <ThumbsDown className="size-4" /> No ({article.helpful_no})
            </Button>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
