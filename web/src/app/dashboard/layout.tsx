"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { getAccessToken } from "@/lib/auth";
import { useUser } from "@/hooks/use-user";
import { GrowProvider } from "@/hooks/use-grow";
import { ConfirmProvider } from "@/components/confirm-dialog";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { MobileBottomNav } from "@/components/mobile-bottom-nav";
import { CommandPalette } from "@/components/command-palette";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, loading, logout } = useUser();

  useEffect(() => {
    if (!getAccessToken()) {
      router.push("/login");
    }
  }, [router]);

  if (loading) {
    return (
      <div className="flex min-h-dvh items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="size-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <GrowProvider>
      <ConfirmProvider>
      <SidebarProvider>
        <AppSidebar user={user} onLogout={logout} />
        <SidebarInset>
          <main className="flex flex-1 flex-col pb-16 md:pb-0">
            {children}
          </main>
        </SidebarInset>
        <MobileBottomNav />
        <CommandPalette />
      </SidebarProvider>
      </ConfirmProvider>
    </GrowProvider>
  );
}
