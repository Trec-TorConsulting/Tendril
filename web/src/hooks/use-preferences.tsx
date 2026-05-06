"use client";

import { createContext, useCallback, useContext, useMemo } from "react";
import { useUser, type UserPreferences } from "@/hooks/use-user";
import { getAccessToken } from "@/lib/auth";
import { updateProfile } from "@/lib/api";

/** Default preferences applied when user has no overrides */
const DEFAULTS: Required<UserPreferences> = {
  temp_unit: "fahrenheit",
  date_format: "MM/DD/YYYY",
  time_format: "12h",
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  default_grow_id: "",
  theme: "system",
  widget_layout: [],
  measurement_system: "imperial",
  wind_unit: "mph",
  pressure_unit: "inhg",
  week_start: "sunday",
  compact_numbers: false,
  show_onboarding: true,
};

interface PreferencesContextValue {
  /** Resolved preferences (user overrides merged with defaults) */
  prefs: Required<UserPreferences>;
  /** Update one or more preference keys. Pass null to reset a key to default. */
  update: (patch: Partial<UserPreferences>) => Promise<void>;
  /** Whether user data is still loading */
  loading: boolean;
}

const PreferencesContext = createContext<PreferencesContextValue | null>(null);

export function PreferencesProvider({ children }: { children: React.ReactNode }) {
  const { user, loading, refresh } = useUser();

  const prefs = useMemo<Required<UserPreferences>>(() => {
    const raw = user?.preferences ?? {};
    return { ...DEFAULTS, ...raw } as Required<UserPreferences>;
  }, [user?.preferences]);

  const update = useCallback(
    async (patch: Partial<UserPreferences>) => {
      const token = getAccessToken();
      if (!token) return;
      await updateProfile(token, { preferences: patch as Record<string, unknown> });
      await refresh();
    },
    [refresh],
  );

  const value = useMemo(
    () => ({ prefs, update, loading }),
    [prefs, update, loading],
  );

  return (
    <PreferencesContext.Provider value={value}>
      {children}
    </PreferencesContext.Provider>
  );
}

export function usePreferences() {
  const ctx = useContext(PreferencesContext);
  if (!ctx) {
    throw new Error("usePreferences must be used within PreferencesProvider");
  }
  return ctx;
}
