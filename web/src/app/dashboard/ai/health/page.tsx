"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { listGrows, runHealthCheck, type GrowResponse } from "@/lib/api";
import { HealthCheckForm } from "@/components/health-check-form";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Heart, AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface HealthResult {
  score: number | null;
  issues: string[];
  actions: string[];
  raw_analysis: string;
}

export default function HealthPage() {
  const [grows, setGrows] = useState<GrowResponse[]>([]);
  const [selectedGrow, setSelectedGrow] = useState<GrowResponse | null>(null);
  const [result, setResult] = useState<HealthResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      const token = getAccessToken();
      if (!token) return;
      setGrows(await listGrows(token, { status: "active" }));
    };
    load();
  }, []);

  const handleSubmit = useCallback(
    async (observations: Record<string, string>) => {
      if (!selectedGrow) return;
      const token = getAccessToken();
      if (!token) return;

      setLoading(true);
      setError("");
      setResult(null);

      try {
        const res = await runHealthCheck(token, {
          grow_id: selectedGrow.id,
          observations,
        });
        setResult(res);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Health check failed");
      } finally {
        setLoading(false);
      }
    },
    [selectedGrow],
  );

  return (
    <>
      <PageHeader
        title="Health Check"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "AI", href: "/dashboard/ai" },
          { label: "Health Check" },
        ]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* Grow selector */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Heart className="size-4" />
              Select Grow
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Label className="mb-2 block">Choose a grow to assess</Label>
            <Select
              value={selectedGrow?.id || ""}
              onValueChange={(val) => {
                const g = grows.find((g) => g.id === val);
                setSelectedGrow(g || null);
                setResult(null);
              }}
            >
              <SelectTrigger className="w-full sm:w-72">
                <SelectValue placeholder="Choose a grow…" />
              </SelectTrigger>
              <SelectContent>
                {grows.map((g) => (
                  <SelectItem key={g.id} value={g.id}>
                    {g.name} ({g.grow_type})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        {/* Health check form */}
        {selectedGrow && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Observations</CardTitle>
            </CardHeader>
            <CardContent>
              <HealthCheckForm growType={selectedGrow.grow_type} onSubmit={handleSubmit} />
              {loading && (
                <div className="mt-3 flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="size-4 animate-spin" />
                  Running health check…
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Results */}
        {result && (
          <div className="grid gap-4 lg:grid-cols-3">
            {/* Score */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Health Score</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-baseline gap-2">
                  <span
                    className={cn(
                      "text-4xl font-bold",
                      (result.score ?? 0) >= 80
                        ? "text-primary"
                        : (result.score ?? 0) >= 50
                          ? "text-yellow-500"
                          : "text-destructive"
                    )}
                  >
                    {result.score ?? "N/A"}
                  </span>
                  <span className="text-muted-foreground">/ 100</span>
                </div>
              </CardContent>
            </Card>

            {/* Issues */}
            {result.issues.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <AlertTriangle className="size-4 text-destructive" />
                    Issues Found
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {result.issues.map((issue, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <Badge variant="destructive" className="mt-0.5 size-1.5 rounded-full p-0" />
                        {issue}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Actions */}
            {result.actions.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <CheckCircle2 className="size-4 text-primary" />
                    Recommended Actions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {result.actions.map((action, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary" />
                        {action}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </>
  );
}
