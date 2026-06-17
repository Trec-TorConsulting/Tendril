"use client";

import { useState } from "react";
import { getBillingStatus, createCheckout, createPortalSession, getPublicPlans, type BillingStatus, type PublicBillingPlan } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";
import { getAccessToken } from "@/lib/auth";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CreditCard, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

const WALLET_ICONS: Record<string, { label: string; icon: string }> = {
  apple_pay: { label: "Apple Pay", icon: "" },
  google_pay: { label: "Google Pay", icon: "G Pay" },
  link: { label: "Link", icon: "⚡" },
  paypal: { label: "PayPal", icon: "PP" },
  venmo: { label: "Venmo", icon: "V" },
  cash_app: { label: "Cash App", icon: "$" },
  card: { label: "Card", icon: "💳" },
};

function formatPrice(cents: number, annual: number | null, isAnnual: boolean): string {
  if (cents === 0) return "Free";
  if (isAnnual && annual != null) {
    return `$${(annual / 100).toFixed(2)}/yr`;
  }
  return `$${(cents / 100).toFixed(2)}/mo`;
}

function formatLimit(value: number | null): string {
  if (value == null) return "Unlimited";
  return value.toLocaleString();
}

function planFeatures(plan: PublicBillingPlan): string[] {
  const features: string[] = [];
  features.push(`${formatLimit(plan.max_grows)} grow${plan.max_grows !== 1 ? "s" : ""}`);
  features.push(`${formatLimit(plan.max_devices)} device${plan.max_devices !== 1 ? "s" : ""}`);
  if (plan.max_journal_entries_month != null) {
    features.push(`${formatLimit(plan.max_journal_entries_month)} journal entries/mo`);
  } else {
    features.push("Unlimited journals");
  }
  if (plan.max_ai_analyses_month != null) {
    features.push(`${formatLimit(plan.max_ai_analyses_month)} AI analyses/mo`);
  } else {
    features.push("Unlimited AI");
  }
  if (plan.max_storage_gb != null) {
    features.push(`${plan.max_storage_gb} GB storage`);
  } else {
    features.push("Unlimited storage");
  }
  if (plan.max_automations != null) {
    features.push(`${plan.max_automations} automations`);
  } else if (plan.max_automations == null && plan.base_price_cents > 0) {
    features.push("Unlimited automations");
  }
  if (plan.max_integrations != null) {
    features.push(`${plan.max_integrations} integrations`);
  } else if (plan.max_integrations == null && plan.base_price_cents > 0) {
    features.push("Unlimited integrations");
  }
  if (plan.max_team_members != null && plan.max_team_members > 1) {
    features.push(`${plan.max_team_members} team members`);
  } else if (plan.max_team_members == null && plan.base_price_cents >= 7999) {
    features.push("Unlimited team members");
  }
  if (plan.included_support_tier !== "community") {
    features.push(`${plan.included_support_tier.charAt(0).toUpperCase()}${plan.included_support_tier.slice(1)} support`);
  }
  return features;
}

export default function BillingPage() {
  const [annualBilling, setAnnualBilling] = useState(false);

  const { data, isLoading: loading } = useApiSWR(
    ["billing"],
    async (token) => {
      const [publicPlans, billingStatus] = await Promise.all([
        getPublicPlans(),
        getBillingStatus(token),
      ]);
      return {
        plans: publicPlans.sort((a, b) => a.sort_order - b.sort_order),
        status: billingStatus,
      };
    },
  );

  const plans = data?.plans ?? [];
  const status = data?.status ?? null;

  const handleUpgrade = async (plan: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const { checkout_url } = await createCheckout(token, plan);
      window.location.assign(checkout_url);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to start checkout");
    }
  };

  const handlePortal = async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const { portal_url } = await createPortalSession(token);
      window.location.assign(portal_url);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to open billing portal");
    }
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
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl font-bold text-primary">{status?.plan_name}</span>
                  {status?.stripe_subscription_id && (
                    <Button variant="outline" size="sm" onClick={handlePortal}>
                      Manage Subscription
                    </Button>
                  )}
                </div>
                {/* Supported Payment Methods */}
                {status?.supported_methods && status.supported_methods.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">Accepted payment methods</p>
                    <div className="flex flex-wrap gap-2">
                      {status.supported_methods.map((method) => {
                        const info = WALLET_ICONS[method];
                        return (
                          <div
                            key={method}
                            className="flex items-center gap-1.5 rounded-md border border-neutral-700 bg-neutral-900 px-3 py-1.5 text-sm"
                          >
                            {info?.icon && <span className="text-base">{info.icon}</span>}
                            <span className="text-neutral-200">{info?.label || method}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Plan Grid */}
        {plans.length > 0 && (
          <>
            {/* Annual Toggle */}
            {plans.some((p) => p.annual_price_cents != null) && (
              <div className="flex items-center justify-center gap-3">
                <span className={cn("text-sm", !annualBilling && "font-medium text-foreground")}>Monthly</span>
                <button
                  type="button"
                  role="switch"
                  aria-checked={annualBilling}
                  onClick={() => setAnnualBilling(!annualBilling)}
                  className={cn(
                    "relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors",
                    annualBilling ? "bg-primary" : "bg-muted-foreground/30"
                  )}
                >
                  <span
                    className={cn(
                      "pointer-events-none inline-block size-5 rounded-full bg-white shadow-sm transition-transform",
                      annualBilling ? "translate-x-5" : "translate-x-0"
                    )}
                  />
                </button>
                <span className={cn("text-sm", annualBilling && "font-medium text-foreground")}>
                  Annual <Badge variant="secondary" className="ml-1 text-xs">Save ~17%</Badge>
                </span>
              </div>
            )}

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {plans.map((plan) => {
                const isCurrent = status?.plan === plan.slug;
                const isPopular = plan.slug === "pro";
                const isContact = plan.slug === "dedicated";
                const features = planFeatures(plan);
                return (
                  <Card
                    key={plan.id}
                    className={cn(
                      isCurrent && "border-primary",
                      isPopular && "ring-2 ring-primary/50"
                    )}
                  >
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-base">{plan.name}</CardTitle>
                        {isPopular && (
                          <Badge variant="default" className="text-xs">Popular</Badge>
                        )}
                      </div>
                      <CardDescription>{plan.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-2xl font-bold">
                        {formatPrice(plan.base_price_cents, plan.annual_price_cents, annualBilling)}
                      </p>
                      <ul className="space-y-1 text-sm text-muted-foreground">
                        {features.map((f) => (
                          <li key={f} className="flex items-center gap-2">
                            <Check className="size-3 text-primary" />
                            {f}
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                    <CardFooter>
                      {isCurrent ? (
                        <Badge variant="default" className="gap-1">
                          <Check className="size-3" />
                          Current Plan
                        </Badge>
                      ) : isContact ? (
                        <Button size="sm" variant="outline" className="w-full" asChild>
                          <a href="mailto:info@tendrilgrow.com">Contact Sales</a>
                        </Button>
                      ) : plan.base_price_cents === 0 ? (
                        <span className="text-sm text-muted-foreground">Free tier</span>
                      ) : (
                        <Button size="sm" className="w-full" onClick={() => handleUpgrade(plan.slug)}>
                          {status?.plan === "free" ? "Upgrade" : "Switch"}
                        </Button>
                      )}
                    </CardFooter>
                  </Card>
                );
              })}
            </div>
          </>
        )}
      </div>
    </>
  );
}
