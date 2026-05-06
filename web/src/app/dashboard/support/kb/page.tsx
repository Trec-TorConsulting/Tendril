"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { listKBCategories, listKBArticles, searchKBArticles, type KBCategory, type KBArticle } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Search } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

export default function KnowledgeBasePage() {
  const searchParams = useSearchParams();
  const categorySlug = searchParams.get("category");
  const [categories, setCategories] = useState<KBCategory[]>([]);
  const [articles, setArticles] = useState<KBArticle[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<KBArticle[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [cats, arts] = await Promise.all([
          listKBCategories(),
          listKBArticles({ category_slug: categorySlug || undefined }),
        ]);
        setCategories(cats);
        setArticles(arts.articles);
      } catch {
        toast.error("Failed to load knowledge base");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [categorySlug]);

  const handleSearch = useCallback(async () => {
    if (searchQuery.length < 2) {
      setSearchResults(null);
      return;
    }
    try {
      const results = await searchKBArticles(searchQuery);
      setSearchResults(results);
    } catch {
      toast.error("Search failed");
    }
  }, [searchQuery]);

  useEffect(() => {
    const timeout = setTimeout(handleSearch, 300);
    return () => clearTimeout(timeout);
  }, [handleSearch]);

  const displayArticles = searchResults ?? articles;

  return (
    <>
      <PageHeader
        title="Knowledge Base"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Support", href: "/dashboard/support" },
          { label: "Knowledge Base" },
        ]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* Search */}
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search articles..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-[240px_1fr]">
          {/* Category sidebar */}
          <nav className="space-y-1">
            <Link href="/dashboard/support/kb">
              <div className={`rounded-md px-3 py-2 text-sm transition-colors hover:bg-muted ${!categorySlug ? "bg-muted font-medium" : ""}`}>
                All Articles
              </div>
            </Link>
            {categories.map((cat) => (
              <Link key={cat.id} href={`/dashboard/support/kb?category=${cat.slug}`}>
                <div className={`rounded-md px-3 py-2 text-sm transition-colors hover:bg-muted ${categorySlug === cat.slug ? "bg-muted font-medium" : ""}`}>
                  {cat.name}
                  <span className="ml-2 text-xs text-muted-foreground">({cat.article_count})</span>
                </div>
              </Link>
            ))}
          </nav>

          {/* Articles */}
          <div className="space-y-3">
            {loading ? (
              [1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-16 w-full" />)
            ) : displayArticles.length === 0 ? (
              <p className="text-muted-foreground">No articles found.</p>
            ) : (
              displayArticles.map((article) => (
                <Link key={article.id} href={`/dashboard/support/kb/${article.slug}`}>
                  <Card className="transition-colors hover:border-primary">
                    <CardHeader className="py-3">
                      <CardTitle className="text-sm font-medium">{article.title}</CardTitle>
                      <div className="flex items-center gap-2">
                        {article.tags?.map((tag) => (
                          <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
                        ))}
                        <span className="text-xs text-muted-foreground">{article.views} views</span>
                      </div>
                    </CardHeader>
                  </Card>
                </Link>
              ))
            )}
          </div>
        </div>
      </div>
    </>
  );
}
