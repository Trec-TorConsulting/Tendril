"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { useChat } from "@/components/chat-provider";
import { getAccessToken } from "@/lib/auth";
import {
  listGrows,
  listTents,
  listStrains,
  listDevices,
  type GrowResponse,
  type TentResponse,
  type StrainResponse,
  type DeviceResponse,
} from "@/lib/api";
import {
  CommandDialog,
  Command,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandSeparator,
} from "@/components/ui/command";
import {
  LayoutDashboard,
  Warehouse,
  Sprout,
  FlaskConical,
  Cpu,
  BarChart3,
  MessageSquare,
  Stethoscope,
  Bot,
  Clock,
  Bell,
  CheckSquare,
  Dna,
  ClipboardList,
  KeyRound,
  CreditCard,
  Settings,
  Plus,
  Moon,
  Sun,
  Monitor,
  Search,
  ArrowRight,
} from "lucide-react";

// Static pages
const PAGES = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, keywords: "home overview" },
  { href: "/dashboard/tents", label: "Grow Spaces", icon: Warehouse, keywords: "tents rooms" },
  { href: "/dashboard/grows", label: "Grows", icon: Sprout, keywords: "cycles plants" },
  { href: "/dashboard/grow-types", label: "Grow Types", icon: FlaskConical, keywords: "hydro soil coco" },
  { href: "/dashboard/devices", label: "Devices", icon: Cpu, keywords: "sensors esp32 hardware" },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3, keywords: "charts data reports" },
  { href: "/dashboard/ai/health", label: "Health Check", icon: Stethoscope, keywords: "diagnosis plant health" },
  { href: "/dashboard/automation", label: "Automation", icon: Bot, keywords: "rules triggers" },
  { href: "/dashboard/schedules", label: "Schedules", icon: Clock, keywords: "timing calendar" },
  { href: "/dashboard/notifications", label: "Notifications", icon: Bell, keywords: "alerts messages" },
  { href: "/dashboard/tasks", label: "Tasks", icon: CheckSquare, keywords: "todo checklist" },
  { href: "/dashboard/strains", label: "Strains", icon: Dna, keywords: "genetics library" },
  { href: "/dashboard/audit", label: "Audit Trail", icon: ClipboardList, keywords: "logs history" },
  { href: "/dashboard/api-keys", label: "API Keys", icon: KeyRound, keywords: "tokens access" },
  { href: "/dashboard/billing", label: "Billing", icon: CreditCard, keywords: "subscription plan" },
  { href: "/dashboard/settings", label: "Settings", icon: Settings, keywords: "profile preferences" },
];

const RECENT_KEY = "tendril-cmd-recent";
const MAX_RECENT = 5;

function getRecent(): { href: string; label: string }[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(RECENT_KEY) || "[]");
  } catch {
    return [];
  }
}

function addRecent(href: string, label: string) {
  const list = getRecent().filter((r) => r.href !== href);
  list.unshift({ href, label });
  localStorage.setItem(RECENT_KEY, JSON.stringify(list.slice(0, MAX_RECENT)));
}

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [recent, setRecent] = useState<{ href: string; label: string }[]>([]);

  // Dynamic data (loaded on open)
  const [grows, setGrows] = useState<GrowResponse[]>([]);
  const [tents, setTents] = useState<TentResponse[]>([]);
  const [strains, setStrains] = useState<StrainResponse[]>([]);
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const loaded = useRef(false);

  // Keyboard shortcut
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((o) => !o);
      }
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, []);

  // Load data on open
  useEffect(() => {
    if (!open) return;
    setRecent(getRecent());
    if (loaded.current) return;
    const token = getAccessToken();
    if (!token) return;
    Promise.all([
      listGrows(token).catch(() => []),
      listTents(token).catch(() => []),
      listStrains(token).catch(() => []),
      listDevices(token).catch(() => []),
    ]).then(([g, t, s, d]) => {
      setGrows(g);
      setTents(t);
      setStrains(s);
      setDevices(d);
      loaded.current = true;
    });
  }, [open]);

  const { openChat } = useChat();

  const go = useCallback(
    (href: string, label: string) => {
      addRecent(href, label);
      setOpen(false);
      setSearch("");
      router.push(href);
    },
    [router],
  );

  const openAiChat = useCallback(() => {
    setOpen(false);
    setSearch("");
    openChat();
  }, [openChat]);

  const themeIcon = theme === "dark" ? Moon : theme === "light" ? Sun : Monitor;
  const ThemeIcon = themeIcon;
  const nextTheme = theme === "dark" ? "light" : theme === "light" ? "system" : "dark";
  const nextThemeLabel = nextTheme === "dark" ? "Dark" : nextTheme === "light" ? "Light" : "System";

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <Command loop>
        <CommandInput placeholder="Search pages, grows, strains..." value={search} onValueChange={setSearch} />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>

          {/* Recent */}
          {!search && recent.length > 0 && (
            <CommandGroup heading="Recent">
              {recent.map((r) => (
                <CommandItem key={r.href} onSelect={() => go(r.href, r.label)}>
                  <ArrowRight className="mr-2 size-4 text-muted-foreground" />
                  {r.label}
                </CommandItem>
              ))}
            </CommandGroup>
          )}

          {/* Pages */}
          <CommandGroup heading="Pages">
            {PAGES.map((p) => {
              const Icon = p.icon;
              return (
                <CommandItem
                  key={p.href}
                  value={`${p.label} ${p.keywords}`}
                  onSelect={() => go(p.href, p.label)}
                >
                  <Icon className="mr-2 size-4 text-muted-foreground" />
                  {p.label}
                </CommandItem>
              );
            })}
            <CommandItem
              value="AI Chat assistant bot"
              onSelect={openAiChat}
            >
              <MessageSquare className="mr-2 size-4 text-muted-foreground" />
              AI Chat
            </CommandItem>
          </CommandGroup>

          {/* Grows */}
          {grows.length > 0 && (
            <>
              <CommandSeparator />
              <CommandGroup heading="Grows">
                {grows.slice(0, 10).map((g) => (
                  <CommandItem
                    key={g.id}
                    value={`grow ${g.name} ${g.grow_type} ${g.stage}`}
                    onSelect={() => go(`/dashboard/grows/${g.id}`, g.name)}
                  >
                    <Sprout className="mr-2 size-4 text-muted-foreground" />
                    <span className="flex-1">{g.name}</span>
                    <span className="text-xs text-muted-foreground capitalize">{g.stage}</span>
                  </CommandItem>
                ))}
              </CommandGroup>
            </>
          )}

          {/* Tents */}
          {tents.length > 0 && (
            <>
              <CommandSeparator />
              <CommandGroup heading="Grow Spaces">
                {tents.map((t) => (
                  <CommandItem
                    key={t.id}
                    value={`tent space ${t.name} ${t.environment_type || ""}`}
                    onSelect={() => go(`/dashboard/tents/${t.id}`, t.name)}
                  >
                    <Warehouse className="mr-2 size-4 text-muted-foreground" />
                    {t.name}
                  </CommandItem>
                ))}
              </CommandGroup>
            </>
          )}

          {/* Strains */}
          {strains.length > 0 && (
            <>
              <CommandSeparator />
              <CommandGroup heading="Strains">
                {strains.slice(0, 10).map((s) => (
                  <CommandItem
                    key={s.id}
                    value={`strain ${s.name} ${s.breeder || ""} ${s.genetics || ""}`}
                    onSelect={() => go(`/dashboard/strains`, s.name)}
                  >
                    <Dna className="mr-2 size-4 text-muted-foreground" />
                    {s.name}
                  </CommandItem>
                ))}
              </CommandGroup>
            </>
          )}

          {/* Devices */}
          {devices.length > 0 && (
            <>
              <CommandSeparator />
              <CommandGroup heading="Devices">
                {devices.slice(0, 10).map((d) => (
                  <CommandItem
                    key={d.id}
                    value={`device ${d.label || d.device_id} ${d.status}`}
                    onSelect={() => go(`/dashboard/devices`, d.label || d.device_id)}
                  >
                    <Cpu className="mr-2 size-4 text-muted-foreground" />
                    <span className="flex-1">{d.label || d.device_id}</span>
                    <span className={`text-xs ${d.status === "online" ? "text-green-500" : "text-muted-foreground"}`}>
                      {d.status}
                    </span>
                  </CommandItem>
                ))}
              </CommandGroup>
            </>
          )}

          {/* Quick Actions */}
          <CommandSeparator />
          <CommandGroup heading="Actions">
            <CommandItem value="create new grow" onSelect={() => go("/dashboard/grows", "New Grow")}>
              <Plus className="mr-2 size-4 text-muted-foreground" />
              Create New Grow
            </CommandItem>
            <CommandItem value="create new tent space" onSelect={() => go("/dashboard/tents", "New Tent")}>
              <Plus className="mr-2 size-4 text-muted-foreground" />
              Create New Grow Space
            </CommandItem>
            <CommandItem value="run health check ai" onSelect={() => go("/dashboard/ai/health", "Health Check")}>
              <Stethoscope className="mr-2 size-4 text-muted-foreground" />
              Run Health Check
            </CommandItem>
            <CommandItem
              value={`toggle theme ${nextThemeLabel}`}
              onSelect={() => {
                setTheme(nextTheme);
                setOpen(false);
              }}
            >
              <ThemeIcon className="mr-2 size-4 text-muted-foreground" />
              Switch to {nextThemeLabel} Theme
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </Command>
    </CommandDialog>
  );
}
