"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAccessToken, clearTokens } from "@/lib/auth";
import { getMe, logout as apiLogout } from "@/lib/api";

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
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const me = await getMe(token);
      setUser(me);
    } catch {
      clearTokens();
      router.push("/login");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const logout = useCallback(async () => {
    try { await apiLogout(); } catch { /* ignore */ }
    clearTokens();
    setUser(null);
    router.push("/login");
  }, [router]);

  return { user, loading, logout, refresh };
}
