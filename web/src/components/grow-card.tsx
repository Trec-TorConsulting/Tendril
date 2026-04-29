"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sprout, Timer } from "lucide-react";
import type { GrowResponse } from "@/lib/api";

interface GrowCardProps {
  grow: GrowResponse;
  variant?: "compact" | "standard" | "expanded";
  countdown?: { days_remaining: number } | null;
}

export function GrowCard({ grow, variant = "standard", countdown }: GrowCardProps) {
  if (variant === "compact") {
    return (
      <Link href={`/dashboard/grows/${grow.id}`}>
        <Card className="hover:border-primary/50 transition-colors">
          <CardContent className="flex items-center gap-3 p-3">
            <Sprout className="size-4 text-green-500 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{grow.name}</p>
              <p className="text-xs text-muted-foreground capitalize">{grow.stage}</p>
            </div>
            <Badge variant="outline" className="text-[10px] shrink-0">
              {grow.status}
            </Badge>
          </CardContent>
        </Card>
      </Link>
    );
  }

  if (variant === "expanded") {
    return (
      <Link href={`/dashboard/grows/${grow.id}`}>
        <Card className="hover:border-primary/50 transition-colors">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">{grow.name}</CardTitle>
              <Badge variant={grow.status === "active" ? "default" : "secondary"}>
                {grow.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span className="capitalize">{grow.stage}</span>
              <span>{grow.grow_type}</span>
            </div>
            {countdown && countdown.days_remaining > 0 && (
              <div className="flex items-center gap-2 text-sm">
                <Timer className="size-4 text-orange-500" />
                <span>{countdown.days_remaining} days remaining</span>
              </div>
            )}
            {grow.notes && (
              <p className="text-xs text-muted-foreground line-clamp-2">{grow.notes}</p>
            )}
          </CardContent>
        </Card>
      </Link>
    );
  }

  // standard
  return (
    <Link href={`/dashboard/grows/${grow.id}`}>
      <Card className="hover:border-primary/50 transition-colors">
        <CardContent className="flex items-center gap-3 p-4">
          <div className="flex size-10 items-center justify-center rounded-lg bg-green-500/10">
            <Sprout className="size-5 text-green-500" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{grow.name}</p>
            <p className="text-xs text-muted-foreground capitalize">{grow.stage} · {grow.grow_type}</p>
          </div>
          <div className="text-right shrink-0">
            <Badge variant={grow.status === "active" ? "default" : "secondary"} className="text-[10px]">
              {grow.status}
            </Badge>
            {countdown && countdown.days_remaining > 0 && (
              <p className="text-[10px] text-muted-foreground mt-0.5">{countdown.days_remaining}d</p>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
