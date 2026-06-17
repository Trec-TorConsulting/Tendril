"use client";

import { useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getAccessToken, clearTokens } from "@/lib/auth";
import { getMe, logout as apiLogout } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";

export interface UserPreferences {
  temp_unit?: "fahrenheit" | "celsius";
  date_format?: "MM/DD/YYYY" | "DD/MM/YYYY" | "YYYY-MM-DD";
  time_format?: "12h" | "24h";
  timezone?: string;
  default_grow_id?: string;
  theme?: "light" | "dark" | "system";
  widget_layout?: string[];
  measurement_system?: "imperial" | "metric";
  wind_unit?: "kmh" | "mph" | "ms";
  pressure_unit?: "hpa" | "inhg";
  week_start?: "sunday" | "monday";
  compact_numbers?: boolean;
  show_onboarding?: boolean;
}

export interface UserData {
  id: string;
  email: string;
  display_name: string | null;
  role: string;
  tenant_id: string;
  is_platform_admin: boolean;
  is_support: boolean;
  layout_mode: string;
  preferences?: UserPreferences;
}

export function useUser() {
  const router = useRouter();
  const {
    data,
    error,
    isLoading,
    mutate,
  } = useApiSWR<UserData>(getAccessToken() ? ["user", "me"] : null, (token) => getMe(token));

  const refresh = useCallback(async () => {
    await mutate();
  }, [mutate]);

  useEffect(() => {
    if (!error) return;
    clearTokens();
    router.push("/login");
  }, [error, router]);

  const logout = useCallback(async () => {
    try { await apiLogout(); } catch { /* ignore */ }
    clearTokens();
    mutate(undefined, { revalidate: false });
    router.push("/login");
  }, [mutate, router]);

  return { user: data ?? null, loading: isLoading, logout, refresh };
}
