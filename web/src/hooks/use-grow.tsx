"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { getAccessToken } from "@/lib/auth";
import { listGrows, type GrowResponse } from "@/lib/api";

interface GrowContextValue {
  grows: GrowResponse[];
  selectedGrow: GrowResponse | null;
  setSelectedGrowId: (id: string) => void;
  refreshGrows: () => Promise<void>;
  loading: boolean;
}

const GrowContext = createContext<GrowContextValue>({
  grows: [],
  selectedGrow: null,
  setSelectedGrowId: () => {},
  refreshGrows: async () => {},
  loading: true,
});

export function useGrow() {
  return useContext(GrowContext);
}

export function GrowProvider({ children, defaultGrowId }: { children: ReactNode; defaultGrowId?: string }) {
  const [grows, setGrows] = useState<GrowResponse[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [loading, setLoading] = useState(true);

  const refreshGrows = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const data = await listGrows(token);
      setGrows(data);
      // Auto-select: honor default_grow_id preference, then first active, then first
      if (!selectedId || !data.find((g) => g.id === selectedId)) {
        const preferred = defaultGrowId ? data.find((g) => g.id === defaultGrowId) : null;
        if (preferred) setSelectedId(preferred.id);
        else {
          const active = data.find((g) => g.status === "active");
          if (active) setSelectedId(active.id);
          else if (data.length > 0) setSelectedId(data[0].id);
        }
      }
    } finally {
      setLoading(false);
    }
  }, [selectedId, defaultGrowId]);

  useEffect(() => {
    refreshGrows();
  }, [refreshGrows]);

  const selectedGrow = grows.find((g) => g.id === selectedId) || null;

  return (
    <GrowContext.Provider
      value={{
        grows,
        selectedGrow,
        setSelectedGrowId: setSelectedId,
        refreshGrows,
        loading,
      }}
    >
      {children}
    </GrowContext.Provider>
  );
}
