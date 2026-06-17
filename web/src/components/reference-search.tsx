"use client";

import { useEffect, useMemo, useState } from "react";
import { searchReferenceStrains, searchNutrients } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

interface StrainSuggestion {
  id: string;
  name: string;
  breeder: string | null;
  genetics: string | null;
}

interface NutrientSuggestion {
  id: string;
  barcode: string;
  name: string;
  brand: string | null;
  npk: string | null;
  nutrients: Record<string, unknown> | null;
}

interface ReferenceStrainSearchProps {
  onSelect: (strain: StrainSuggestion) => void;
  placeholder?: string;
  className?: string;
}

export function ReferenceStrainSearch({ onSelect, placeholder = "Search global strain database...", className }: ReferenceStrainSearchProps) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  const { data } = useApiSWR<StrainSuggestion[]>(
    debouncedQuery.length >= 2 ? ["reference-strains", debouncedQuery] : null,
    (token) => searchReferenceStrains(token, debouncedQuery),
  );
  const results = useMemo(() => data ?? [], [data]);

  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setOpen(false);
      return;
    }
    setOpen(results.length > 0);
  }, [debouncedQuery, results.length]);

  return (
    <div className={`relative ${className || ""}`}>
      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => results.length > 0 && setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 200)}
          placeholder={placeholder}
          className="pl-9"
        />
      </div>
      {open && results.length > 0 && (
        <div className="absolute z-50 mt-1 w-full max-h-72 overflow-y-auto rounded-md border bg-popover p-1 shadow-lg">
          {results.map((s) => (
            <button
              key={s.id}
              type="button"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => { onSelect(s); setQuery(s.name); setOpen(false); }}
              className="flex w-full cursor-pointer items-start gap-2 rounded-sm px-2 py-1.5 text-left text-sm hover:bg-muted"
            >
              <div>
                <p className="font-medium">{s.name}</p>
                <p className="text-xs text-muted-foreground">
                  {[s.breeder, s.genetics].filter(Boolean).join(" · ") || "Unknown breeder"}
                </p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

interface NutrientSearchProps {
  onSelect: (nutrient: NutrientSuggestion) => void;
  placeholder?: string;
  className?: string;
}

export function NutrientSearch({ onSelect, placeholder = "Search nutrients by name or brand...", className }: NutrientSearchProps) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  const { data } = useApiSWR<NutrientSuggestion[]>(
    debouncedQuery.length >= 2 ? ["nutrients", "search", debouncedQuery] : null,
    (token) => searchNutrients(token, debouncedQuery),
  );
  const results = useMemo(() => data ?? [], [data]);

  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setOpen(false);
      return;
    }
    setOpen(results.length > 0);
  }, [debouncedQuery, results.length]);

  return (
    <div className={`relative ${className || ""}`}>
      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => results.length > 0 && setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 200)}
          placeholder={placeholder}
          className="pl-9"
        />
      </div>
      {open && results.length > 0 && (
        <div className="absolute z-50 mt-1 w-full max-h-72 overflow-y-auto rounded-md border bg-popover p-1 shadow-lg">
          {results.map((n) => (
            <button
              key={n.id}
              type="button"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => { onSelect(n); setQuery(n.name); setOpen(false); }}
              className="flex w-full cursor-pointer items-start gap-2 rounded-sm px-2 py-1.5 text-left text-sm hover:bg-muted"
            >
              <div className="min-w-0 flex-1">
                <p className="font-medium">{n.name}</p>
                <p className="text-xs text-muted-foreground">
                  {[n.brand, n.npk ? `NPK: ${n.npk}` : null].filter(Boolean).join(" · ")}
                </p>
                {typeof n.nutrients?.description === "string" && (
                  <p className="text-xs text-muted-foreground/70 line-clamp-1">
                    {n.nutrients.description}
                  </p>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
