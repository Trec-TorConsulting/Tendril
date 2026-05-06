"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { getBillingStatus, createCheckout, createPortalSession, type BillingStatus } from "@/lib/api";
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

const PLANS = [
  {
    key: "free",
    name: "Seedling",
    price: "Free",
    description: "Get started with basic grow tracking",
    features: ["1 grow", "2 devices", "50 journal entries/mo", "10 AI analyses/mo", "1 GB storage"],
  },
  {
    key: "hobby",
    name: "Hobby",
    price: "$9.99/mo",
    description: "Hobbyist growers with IoT and automation",
    features: ["5 grows", "10 devices", "Unlimited journals", "50 AI analyses/mo", "10 GB storage", "5 automations", "3 integrations"],
    popular: false,
  },
  {
    key: "pro",
    name: "Pro",
    price: "$29.99/mo",
    description: "Serious growers with advanced AI + analytics",
    features: ["25 grows", "50 devices", "500 AI analyses/mo", "100 GB storage", "Unlimited automations", "10 integrations", "Priority support"],
    popular: true,
  },
  {
    key: "commercial",
    name: "Commercial",
    price: "$79.99/mo",
    description: "Teams with audit, API, and compliance",
    features: ["100 grows", "200 devices", "5 team members", "Unlimited AI", "500 GB storage", "API access", "Audit logs", "Custom grow types"],
  },
  {
    key: "enterprise",
    name: "Enterprise",
    price: "$249.99/mo",
    description: "Large operations with white-label + SLA",
    features: ["Unlimited grows", "Unlimited devices", "25 team members", "Unlimited everything", "White-label", "SSO/SAML", "Dedicated support", "Custom domain"],
  },
  {
    key: "dedicated",
    name: "Dedicated",
    price: "Custom",
    description: "Your own servers, your own domain",
    features: ["Dedicated infrastructure", "Custom domain", "Unlimited everything", "Priority SLA", "Custom integrations", "On-premise option"],
    contact: true,
  },
];

export default function BillingPage() {
  const [status, setStatus] = useState<BillingStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const token = getAccessToken();
      if (!token) return;
      try {
        const data = await getBillingStatus(token);
        if (!cancelled) setStatus(data);
      } catch (e) {
        if (!cancelled) toast.error(e instanceof Error ? e.message : "Failed to load billing status");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

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
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {PLANS.map((plan) => {
            const isCurrent = status?.plan === plan.key;
            return (
              <Card
                key={plan.key}
                className={cn(
                  isCurrent && "border-primary",
                  "popular" in plan && plan.popular && "ring-2 ring-primary/50"
                )}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{plan.name}</CardTitle>
                    {"popular" in plan && plan.popular && (
                      <Badge variant="default" className="text-xs">Popular</Badge>
                    )}
                  </div>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-2xl font-bold">{plan.price}</p>
                  {"features" in plan && (
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {plan.features.map((f) => (
                        <li key={f} className="flex items-center gap-2">
                          <Check className="size-3 text-primary" />
                          {f}
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
                <CardFooter>
                  {isCurrent ? (
                    <Badge variant="default" className="gap-1">
                      <Check className="size-3" />
                      Current Plan
                    </Badge>
                  ) : "contact" in plan && plan.contact ? (
                    <Button size="sm" variant="outline" className="w-full" asChild>
                      <a href="mailto:sales@tendril.dev">Contact Sales</a>
                    </Button>
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
