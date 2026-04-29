"use client";

import { createContext, useCallback, useContext, useMemo } from "react";
import { useUser } from "@/hooks/use-user";
import {
  type LayoutMode,
  type LayoutModeConfig,
  LAYOUT_CONFIGS,
} from "@/lib/layout-config";
import { getAccessToken } from "@/lib/auth";
import { updateProfile } from "@/lib/api";

interface LayoutContextValue {
  mode: LayoutMode;
  config: LayoutModeConfig;
  setMode: (mode: LayoutMode) => Promise<void>;
}

const LayoutContext = createContext<LayoutContextValue | null>(null);

export function LayoutProvider({ children }: { children: React.ReactNode }) {
  const { user, refresh } = useUser();

  const mode: LayoutMode = (user?.layout_mode as LayoutMode) || "standard";
  const config = LAYOUT_CONFIGS[mode];

  const setMode = useCallback(
    async (newMode: LayoutMode) => {
      const token = getAccessToken();
      if (token) {
        await updateProfile(token, { layout_mode: newMode });
        await refresh();
      }
    },
    [refresh],
  );

  const value = useMemo(
    () => ({ mode, config, setMode }),
    [mode, config, setMode],
  );

  return (
    <LayoutContext.Provider value={value}>{children}</LayoutContext.Provider>
  );
}

export function useLayoutMode() {
  const ctx = useContext(LayoutContext);
  if (!ctx) {
    throw new Error("useLayoutMode must be used within LayoutProvider");
  }
  return ctx;
}
