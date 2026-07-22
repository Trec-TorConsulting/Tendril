"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
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
import { AppSWRProvider } from "@/lib/swr";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, loading, logout } = useUser();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!getAccessToken()) {
      router.push("/login");
    }
  }, [router]);

  // Auth depends on browser cookies that don't exist during SSR, so the server
  // and the first client paint must render the same thing to avoid a hydration
  // mismatch. Show a stable loading state until we've mounted on the client.
  if (!mounted || loading) {
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
    <AppSWRProvider>
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
    </AppSWRProvider>
  );
}
