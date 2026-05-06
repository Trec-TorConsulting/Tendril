"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { searchReferenceStrains, searchNutrients } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Command, CommandEmpty, CommandGroup, CommandItem, CommandList } from "@/components/ui/command";
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
}

interface ReferenceStrainSearchProps {
  onSelect: (strain: StrainSuggestion) => void;
  placeholder?: string;
  className?: string;
}

export function ReferenceStrainSearch({ onSelect, placeholder = "Search global strain database...", className }: ReferenceStrainSearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<StrainSuggestion[]>([]);
  const [open, setOpen] = useState(false);

  const search = useCallback(async (q: string) => {
    if (q.length < 2) { setResults([]); return; }
    const token = getAccessToken();
    if (!token) return;
    try {
      const data = await searchReferenceStrains(token, q);
      setResults(data);
      setOpen(data.length > 0);
    } catch {
      setResults([]);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => search(query), 300);
    return () => clearTimeout(timer);
  }, [query, search]);

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
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-lg">
          <Command>
            <CommandList>
              <CommandGroup>
                {results.map((s) => (
                  <CommandItem
                    key={s.id}
                    value={s.name}
                    onSelect={() => { onSelect(s); setQuery(s.name); setOpen(false); }}
                    className="cursor-pointer"
                  >
                    <div>
                      <p className="text-sm font-medium">{s.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {[s.breeder, s.genetics].filter(Boolean).join(" · ") || "Unknown breeder"}
                      </p>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
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
  const [results, setResults] = useState<NutrientSuggestion[]>([]);
  const [open, setOpen] = useState(false);

  const search = useCallback(async (q: string) => {
    if (q.length < 2) { setResults([]); return; }
    const token = getAccessToken();
    if (!token) return;
    try {
      const data = await searchNutrients(token, q);
      setResults(data);
      setOpen(data.length > 0);
    } catch {
      setResults([]);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => search(query), 300);
    return () => clearTimeout(timer);
  }, [query, search]);

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
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-lg">
          <Command>
            <CommandList>
              <CommandGroup>
                {results.map((n) => (
                  <CommandItem
                    key={n.id}
                    value={n.name}
                    onSelect={() => { onSelect(n); setQuery(n.name); setOpen(false); }}
                    className="cursor-pointer"
                  >
                    <div>
                      <p className="text-sm font-medium">{n.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {[n.brand, n.npk ? `NPK: ${n.npk}` : null].filter(Boolean).join(" · ")}
                      </p>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </div>
      )}
    </div>
  );
}
