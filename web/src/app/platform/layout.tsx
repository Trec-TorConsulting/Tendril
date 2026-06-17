"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearTokens } from "@/lib/auth";
import { getMe, logout as apiLogout } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
} from "@/components/ui/sidebar";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Shield, BarChart3, Building2, Users, ArrowLeft, LogOut, ShieldAlert, CreditCard, Wallet, TrendingUp } from "lucide-react";

const PLATFORM_NAV = [
  { href: "/platform", label: "Overview", icon: BarChart3 },
  { href: "/platform/tenants", label: "Organizations", icon: Building2 },
  { href: "/platform/users", label: "Users", icon: Users },
  { href: "/platform/billing", label: "Billing Plans", icon: CreditCard },
  { href: "/platform/providers", label: "Providers", icon: Wallet },
  { href: "/platform/metrics", label: "Metrics", icon: TrendingUp },
];

export default function PlatformLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [authorized, setAuthorized] = useState<boolean | null>(null);
  const [userEmail, setUserEmail] = useState("");

  const { data: me, isLoading, error } = useApiSWR(["platform", "me"], (token) => getMe(token));

  useEffect(() => {
    if (isLoading) {
      setAuthorized(null);
      return;
    }
    if (error || !me) {
      router.push("/login");
      return;
    }
    if (!me.is_platform_admin && !me.is_support) {
      setAuthorized(false);
      return;
    }
    setUserEmail(me.email);
    setAuthorized(true);
  }, [isLoading, error, me, router]);

  if (authorized === null) {
    return (
      <div className="flex min-h-dvh items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="size-8 animate-spin rounded-full border-2 border-amber-500 border-t-transparent" />
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (authorized === false) {
    return (
      <div className="flex min-h-dvh items-center justify-center">
        <Card className="max-w-sm p-8 text-center">
          <ShieldAlert className="mx-auto size-12 text-destructive/50" />
          <h2 className="mt-4 text-xl font-bold">Access Denied</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Platform admin or support access required.
          </p>
          <Button className="mt-4" render={<Link href="/dashboard" />}>
            Return to Dashboard
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <SidebarProvider>
      <Sidebar collapsible="icon" className="border-r border-sidebar-border">
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="lg" render={<Link href="/platform" />}>
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-amber-500 text-white">
                  <Shield className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">Platform</span>
                  <span className="truncate text-xs text-muted-foreground">Admin Portal</span>
                </div>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>

        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu>
                {PLATFORM_NAV.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <SidebarMenuItem key={item.href}>
                      <SidebarMenuButton render={<Link href={item.href} />} isActive={isActive} tooltip={item.label}>
                        <item.icon className="size-4" />
                        <span>{item.label}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>

        <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton render={<Link href="/dashboard" />} tooltip="Back to App">
                <ArrowLeft className="size-4" />
                <span>Back to App</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <SidebarMenuButton
                tooltip="Log out"
                onClick={() => { apiLogout().catch(() => {}); clearTokens(); router.push("/login"); }}
                className="text-muted-foreground hover:text-destructive"
              >
                <LogOut className="size-4" />
                <span>Log out</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
          <p className="truncate px-2 pb-2 text-xs text-muted-foreground">{userEmail}</p>
        </SidebarFooter>

        <SidebarRail />
      </Sidebar>

      <SidebarInset>
        <header className="flex h-14 shrink-0 items-center gap-2 border-b border-border px-4 lg:px-6">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 !h-4" />
          <Badge variant="outline" className="text-amber-500 border-amber-500/30">
            Platform Admin
          </Badge>
        </header>
        <main className="flex flex-1 flex-col">
          {children}
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
