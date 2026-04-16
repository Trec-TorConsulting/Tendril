"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { getGrowType } from "@/lib/api";

/**
 * Hook to get grow-type-specific terminology (e.g., "reservoir" vs "pot").
 * Returns the terminology map and a lookup function.
 */
export function useGrowTerminology(growType: string | null) {
  const [terminology, setTerminology] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!growType) return;
    const load = async () => {
      const token = getAccessToken();
      if (!token) return;
      try {
        const profile = await getGrowType(token, growType);
        if (profile.terminology && typeof profile.terminology === "object") {
          setTerminology(profile.terminology as Record<string, string>);
        }
      } catch {
        // Fallback to default terminology
      }
    };
    load();
  }, [growType]);

  const term = (key: string, fallback?: string): string => {
    return terminology[key] ?? fallback ?? key;
  };

  return { terminology, term };
}
