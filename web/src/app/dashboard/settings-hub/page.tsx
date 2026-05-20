"use client";

import { useState } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { Input } from "@/components/ui/input";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  User,
  Lock,
  Users,
  CreditCard,
  KeyRound,
  ClipboardList,
  LifeBuoy,
  Bot,
  Clock,
  Bell,
  Cpu,
  Plug,
  Dna,
  BookOpen,
  Search,
} from "lucide-react";
import { useUser } from "@/hooks/use-user";

interface SettingsCard {
  title: string;
  description: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  category: "account" | "automation" | "connections" | "library";
  keywords: string[];
  ownerOnly?: boolean;
}

const SETTINGS_CARDS: SettingsCard[] = [
  {
    title: "Profile & Preferences",
    description: "Display name, units, timezone, theme, layout mode",
    href: "/dashboard/settings",
    icon: User,
    category: "account",
    keywords: ["profile", "name", "email", "units", "temperature", "metric", "imperial", "theme", "dark", "light", "timezone", "layout", "display"],
  },
  {
    title: "Security",
    description: "Change password and manage authentication",
    href: "/dashboard/settings/security",
    icon: Lock,
    category: "account",
    keywords: ["security", "password", "authentication", "login"],
  },
  {
    title: "Team",
    description: "Invite members, assign roles, manage access",
    href: "/dashboard/settings/team",
    icon: Users,
    category: "account",
    keywords: ["team", "members", "invite", "roles", "access", "permissions"],
    ownerOnly: true,
  },
  {
    title: "Billing",
    description: "Subscription plan, invoices, payment methods",
    href: "/dashboard/billing",
    icon: CreditCard,
    category: "account",
    keywords: ["billing", "subscription", "plan", "invoice", "payment", "upgrade", "cancel"],
  },
  {
    title: "API Keys",
    description: "Generate and manage developer access tokens",
    href: "/dashboard/api-keys",
    icon: KeyRound,
    category: "account",
    keywords: ["api", "keys", "tokens", "developer", "access"],
  },
  {
    title: "Audit Trail",
    description: "Review account activity and change history",
    href: "/dashboard/audit",
    icon: ClipboardList,
    category: "account",
    keywords: ["audit", "trail", "history", "activity", "log", "changes"],
    ownerOnly: true,
  },
  {
    title: "Support",
    description: "Forum, support tickets, and knowledge base",
    href: "/dashboard/support",
    icon: LifeBuoy,
    category: "account",
    keywords: ["support", "help", "tickets", "forum", "knowledge", "base", "kb"],
  },
  {
    title: "Automation Rules",
    description: "If-then rules, alert triggers, and conditions",
    href: "/dashboard/automation",
    icon: Bot,
    category: "automation",
    keywords: ["automation", "rules", "triggers", "alerts", "conditions", "if-then"],
  },
  {
    title: "Schedules",
    description: "Light, fan, HVAC, and pump timing schedules",
    href: "/dashboard/schedules",
    icon: Clock,
    category: "automation",
    keywords: ["schedules", "timers", "light", "fan", "hvac", "pump", "cron"],
  },
  {
    title: "Notifications",
    description: "Alert channels, delivery preferences, and event routing",
    href: "/dashboard/notifications",
    icon: Bell,
    category: "automation",
    keywords: ["notifications", "alerts", "email", "sms", "discord", "slack", "push", "channels"],
  },
  {
    title: "Devices",
    description: "Register, pair, and manage IoT sensors and cameras",
    href: "/dashboard/devices",
    icon: Cpu,
    category: "connections",
    keywords: ["devices", "sensors", "iot", "esp32", "cameras", "pairing", "mqtt"],
  },
  {
    title: "Integrations",
    description: "Connect external services like Home Assistant, Pulse, Ecowitt",
    href: "/dashboard/integrations",
    icon: Plug,
    category: "connections",
    keywords: ["integrations", "home assistant", "pulse", "ecowitt", "mqtt", "webhook", "vivosun"],
  },
  {
    title: "Strains",
    description: "Strain library with genetics, flowering times, and terpenes",
    href: "/dashboard/strains",
    icon: Dna,
    category: "library",
    keywords: ["strains", "genetics", "flowering", "terpenes", "thc", "cbd", "breeder"],
  },
  {
    title: "Reference",
    description: "Growing guides, nutrient charts, and reference material",
    href: "/dashboard/reference",
    icon: BookOpen,
    category: "library",
    keywords: ["reference", "guides", "charts", "nutrients", "deficiency", "ph"],
  },
];

const CATEGORY_LABELS: Record<string, string> = {
  account: "Account",
  automation: "Automation",
  connections: "Connections",
  library: "Library",
};

export default function SettingsHubPage() {
  const [search, setSearch] = useState("");
  const { user } = useUser();
  const isOwner = user?.role === "owner";

  const filtered = SETTINGS_CARDS.filter((card) => {
    if (card.ownerOnly && !isOwner) return false;
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      card.title.toLowerCase().includes(q) ||
      card.description.toLowerCase().includes(q) ||
      card.keywords.some((k) => k.includes(q))
    );
  });

  const grouped = Object.entries(CATEGORY_LABELS).map(([key, label]) => ({
    key,
    label,
    cards: filtered.filter((c) => c.category === key),
  })).filter((g) => g.cards.length > 0);

  return (
    <>
      <PageHeader title="Settings" description="Find and manage all your account, automation, and system settings" />
      <div className="p-4 space-y-6">
        {/* Search */}
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Search settings... (e.g., notifications, password, theme)"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Grouped cards */}
        {grouped.map((group) => (
          <div key={group.key} className="space-y-3">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
              {group.label}
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {group.cards.map((card) => (
                <Link key={card.href} href={card.href} className="group">
                  <Card className="h-full transition-colors group-hover:border-primary/50 group-hover:bg-accent/50">
                    <CardHeader className="flex flex-row items-start gap-3 p-4">
                      <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <card.icon className="size-5" />
                      </div>
                      <div className="min-w-0">
                        <CardTitle className="text-sm">{card.title}</CardTitle>
                        <CardDescription className="text-xs mt-0.5">
                          {card.description}
                        </CardDescription>
                      </div>
                    </CardHeader>
                  </Card>
                </Link>
              ))}
            </div>
          </div>
        ))}

        {filtered.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            <Search className="size-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No settings found for &ldquo;{search}&rdquo;</p>
          </div>
        )}
      </div>
    </>
  );
}
