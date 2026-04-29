"use client";

import { useState } from "react";
import { useGrow } from "@/hooks/use-grow";
import { useUser } from "@/hooks/use-user";
import { OnboardingWizard } from "@/components/onboarding-wizard";

export function OnboardingGate({ children }: { children: React.ReactNode }) {
  const { grows, loading } = useGrow();
  const { user } = useUser();
  const [dismissed, setDismissed] = useState(false);

  // Show wizard on first login: no grows and layout_mode is still default "standard"
  // (Once they've completed the wizard, layout_mode will be explicitly set)
  const shouldShowWizard =
    !loading &&
    !dismissed &&
    grows.length === 0 &&
    user?.layout_mode === "standard" &&
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
