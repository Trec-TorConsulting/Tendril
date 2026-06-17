"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { listGrows, type GrowResponse } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";

interface GrowContextValue {
  grows: GrowResponse[];
  grow: GrowResponse | null;
  selectedGrow: GrowResponse | null;
  setSelectedGrowId: (id: string) => void;
  refreshGrows: () => Promise<void>;
  loading: boolean;
}

const GrowContext = createContext<GrowContextValue>({
  grows: [],
  grow: null,
  selectedGrow: null,
  setSelectedGrowId: () => {},
  refreshGrows: async () => {},
  loading: true,
});

export function useGrow() {
  return useContext(GrowContext);
}

export function GrowProvider({ children, defaultGrowId }: { children: ReactNode; defaultGrowId?: string }) {
  const [selectedId, setSelectedId] = useState<string>("");
  const {
    data,
    isLoading,
    mutate,
  } = useApiSWR<GrowResponse[]>(["grow", "list"], (token) => listGrows(token));
  const grows = data ?? [];

  const refreshGrows = useCallback(async () => {
    await mutate();
  }, [mutate]);

  useEffect(() => {
    // Auto-select: honor default_grow_id preference, then first active, then first
    if (!selectedId || !grows.find((g) => g.id === selectedId)) {
      const preferred = defaultGrowId ? grows.find((g) => g.id === defaultGrowId) : null;
      if (preferred) setSelectedId(preferred.id);
      else {
        const active = grows.find((g) => g.status === "active");
        if (active) setSelectedId(active.id);
        else if (grows.length > 0) setSelectedId(grows[0].id);
      }
    }
  }, [selectedId, grows, defaultGrowId]);

  const selectedGrow = grows.find((g) => g.id === selectedId) || null;

  return (
    <GrowContext.Provider
      value={{
        grows,
        grow: selectedGrow,
        selectedGrow,
        setSelectedGrowId: setSelectedId,
        refreshGrows,
        loading: isLoading,
      }}
    >
      {children}
    </GrowContext.Provider>
  );
}
