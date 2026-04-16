"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { getBillingStatus, createCheckout, createPortalSession, type BillingStatus } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CreditCard, Check } from "lucide-react";
import { cn } from "@/lib/utils";

const PLANS = [
  { key: "free", name: "Seedling", price: "Free", description: "Basic grow tracking" },
  { key: "grower", name: "Grower", price: "$14.99/mo", description: "IoT + automation + AI" },
  { key: "pro", name: "Pro", price: "$29.99/mo", description: "Advanced AI + reports" },
  { key: "commercial", name: "Commercial", price: "$79.99/mo", description: "Teams + audit + API" },
];

export default function BillingPage() {
  const [status, setStatus] = useState<BillingStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    setLoading(true);
    try {
      setStatus(await getBillingStatus(token));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleUpgrade = async (plan: string) => {
    const token = getAccessToken();
    if (!token) return;
    const { checkout_url } = await createCheckout(token, plan);
    window.location.href = checkout_url;
  };

  const handlePortal = async () => {
    const token = getAccessToken();
    if (!token) return;
    const { portal_url } = await createPortalSession(token);
    window.location.href = portal_url;
  };

  return (
    <>
      <PageHeader
        title="Billing"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Billing" }]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* Current Plan */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="size-5" />
              Current Plan
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-32" />
            ) : (
              <div className="flex items-center gap-3">
                <span className="text-2xl font-bold text-primary">{status?.plan_name}</span>
                {status?.stripe_subscription_id && (
                  <Button variant="outline" size="sm" onClick={handlePortal}>
                    Manage Subscription
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Plan Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {PLANS.map((plan) => {
            const isCurrent = status?.plan === plan.key;
            return (
              <Card
                key={plan.key}
                className={cn(isCurrent && "border-primary")}
              >
                <CardHeader>
                  <CardTitle className="text-base">{plan.name}</CardTitle>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold">{plan.price}</p>
                </CardContent>
                <CardFooter>
                  {isCurrent ? (
                    <Badge variant="default" className="gap-1">
                      <Check className="size-3" />
                      Current Plan
                    </Badge>
                  ) : plan.key === "free" ? (
                    <span className="text-sm text-muted-foreground">Free tier</span>
                  ) : (
                    <Button size="sm" className="w-full" onClick={() => handleUpgrade(plan.key)}>
                      {status?.plan === "free" ? "Upgrade" : "Switch"}
                    </Button>
                  )}
                </CardFooter>
              </Card>
            );
          })}
        </div>
      </div>
    </>
  );
}
