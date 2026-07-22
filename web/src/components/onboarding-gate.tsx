"use client";

import { useState } from "react";
import { useGrow } from "@/hooks/use-grow";
import { useUser } from "@/hooks/use-user";
import { OnboardingWizard } from "@/components/onboarding-wizard";

export function OnboardingGate({ children }: { children: React.ReactNode }) {
  const { grows, loading } = useGrow();
  const { user } = useUser();
  const [dismissed, setDismissed] = useState(false);

  // Only show the wizard to genuinely new users. The server-side
  // `show_onboarding` preference is the durable source of truth — it persists
  // across browsers and devices, so completing the wizard once (which sets it
  // to false) prevents it from ever re-triggering. We additionally require that
  // the user has no grows yet, and keep a per-browser "seen" flag as a fast
  // guard so it never flashes twice within a session (and lets e2e bypass it).
  const showOnboardingPref = user?.preferences?.show_onboarding;
  const shouldShowWizard =
    !loading &&
    user != null &&
    !dismissed &&
    grows.length === 0 &&
    showOnboardingPref !== false &&
    !hasSeenOnboarding();

  if (shouldShowWizard) {
    return (
      <OnboardingWizard
        onComplete={() => {
          markOnboardingSeen();
          setDismissed(true);
        }}
      />
    );
  }

  return <>{children}</>;
}

const ONBOARDING_KEY = "tendril_onboarding_seen";

function hasSeenOnboarding(): boolean {
  if (typeof window === "undefined") return false;
  return localStorage.getItem(ONBOARDING_KEY) === "true";
}

function markOnboardingSeen() {
  try {
    localStorage.setItem(ONBOARDING_KEY, "true");
  } catch { /* ignore */ }
}
