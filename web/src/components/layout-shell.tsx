"use client";

import { useIsMobile } from "@/hooks/use-mobile";
import { useLayoutMode } from "@/hooks/use-layout-mode";
import { MobileBottomNav } from "@/components/mobile-bottom-nav";
import { AppSidebar } from "@/components/app-sidebar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { CommandPalette } from "@/components/command-palette";
import { cn } from "@/lib/utils";
import type { UserData } from "@/hooks/use-user";

interface LayoutShellProps {
  children: React.ReactNode;
  user: UserData | null;
  onLogout: () => void;
}

export function LayoutShell({ children, user, onLogout }: LayoutShellProps) {
  const isMobile = useIsMobile();
  const { config } = useLayoutMode();

  return (
    <SidebarProvider>
      {!isMobile && <AppSidebar user={user} onLogout={onLogout} />}
      {isMobile ? (
        <div className={cn("flex min-h-dvh flex-col overflow-x-hidden", densityClass(config.density))}>
          <main className="flex flex-1 flex-col pb-16">{children}</main>
          <MobileBottomNav />
        </div>
      ) : (
        <SidebarInset>
          <main
            className={cn("flex flex-1 flex-col", densityClass(config.density))}
          >
            {children}
          </main>
        </SidebarInset>
      )}
      <CommandPalette />
    </SidebarProvider>
  );
}

function densityClass(density: "relaxed" | "normal" | "compact") {
  switch (density) {
    case "relaxed":
      return "text-base gap-6";
    case "compact":
      return "text-sm gap-2";
    default:
      return "text-sm gap-4";
  }
}
