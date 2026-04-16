"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAccessToken, clearTokens } from "@/lib/auth";
import { getMe } from "@/lib/api";

export interface UserData {
  id: string;
  email: string;
  display_name: string | null;
  role: string;
  tenant_id: string;
  is_platform_admin: boolean;
  is_support: boolean;
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

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
    router.push("/login");
  }, [router]);

  return { user, loading, logout, refresh };
}
