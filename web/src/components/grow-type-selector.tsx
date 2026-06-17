"use client";

import { useMemo } from "react";
import { listGrowTypes, type GrowTypeSummary } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";

interface GrowTypeSelectorProps {
  value: string;
  onChange: (id: string) => void;
}

export function GrowTypeSelector({ value, onChange }: GrowTypeSelectorProps) {
  const { data } = useApiSWR<GrowTypeSummary[]>(["grow-types", "selector"], (token) => listGrowTypes(token));
  const types = data ?? [];

  const categories = useMemo(() => [...new Set(types.map((t) => t.category))], [types]);

  return (
    <div className="space-y-3">
      {categories.map((cat) => (
        <div key={cat}>
          <p className="mb-1 text-xs font-medium uppercase text-neutral-500">{cat}</p>
          <div className="flex flex-wrap gap-2">
            {types
              .filter((t) => t.category === cat)
              .map((t) => (
                <button
                  key={t.id}
                  type="button"
                  className={`rounded-md border px-3 py-1.5 text-sm ${
                    value === t.id
                      ? "border-green-600 bg-green-900/30 text-green-400"
                      : "border-neutral-700 bg-neutral-800 text-neutral-300 hover:border-neutral-600"
                  }`}
                  onClick={() => onChange(t.id)}
                  title={t.description}
                >
                  {t.name}
                </button>
              ))}
          </div>
        </div>
      ))}
    </div>
  );
}
