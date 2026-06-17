"use client";

import { useMemo } from "react";
import { getGrowType } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";

/**
 * Hook to get grow-type-specific terminology (e.g., "reservoir" vs "pot").
 * Returns the terminology map and a lookup function.
 */
export function useGrowTerminology(growType: string | null) {
  const { data } = useApiSWR(
    growType ? ["grow-type", "terminology", growType] : null,
    (token) => getGrowType(token, growType as string),
  );

  const terminology = useMemo(() => {
    if (data?.terminology && typeof data.terminology === "object") {
      return data.terminology as Record<string, string>;
    }
    return {};
  }, [data]);

  const term = (key: string, fallback?: string): string => {
    return terminology[key] ?? fallback ?? key;
  };

  return { terminology, term };
}
