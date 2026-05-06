"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { getAccessToken } from "@/lib/auth";
import { useUser } from "@/hooks/use-user";
import { GrowProvider } from "@/hooks/use-grow";
import { ConfirmProvider } from "@/components/confirm-dialog";
import { LayoutProvider } from "@/hooks/use-layout-mode";
import { PreferencesProvider } from "@/hooks/use-preferences";
import { LayoutShell } from "@/components/layout-shell";
import { ChatProvider } from "@/components/chat-provider";
import { OnboardingGate } from "@/components/onboarding-gate";
import { UpgradePrompt } from "@/components/upgrade-prompt";

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
    <GrowProvider defaultGrowId={user?.preferences?.default_grow_id}>
      <ConfirmProvider>
      <ChatProvider>
      <PreferencesProvider>
      <LayoutProvider>
        <LayoutShell user={user} onLogout={logout}>
          <OnboardingGate>
            <UpgradePrompt />
            {children}
          </OnboardingGate>
        </LayoutShell>
      </LayoutProvider>
      </PreferencesProvider>
      </ChatProvider>
      </ConfirmProvider>
    </GrowProvider>
  );
}
