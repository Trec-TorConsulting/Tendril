"use client";

import { useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  LayoutDashboard,
  Sprout,
  MessageSquare,
  Plus,
  X,
  Droplets,
  Stethoscope,
  Camera,
  Thermometer,
  Warehouse,
  FlaskConical,
  Cpu,
  BarChart3,
  Bot,
  Clock,
  Bell,
  CheckSquare,
  Dna,
  ClipboardList,
  KeyRound,
  CreditCard,
  Settings,
  Moon,
  Sun,
  Monitor,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useTheme } from "next-themes";

/* ── FAB quick actions ── */
const FAB_ACTIONS = [
  { label: "Log Reading", icon: Droplets, href: "/dashboard/grows" },
  { label: "Health Check", icon: Stethoscope, href: "/dashboard/ai/health" },
  { label: "Quick Photo", icon: Camera, href: "/dashboard/grows" },
  { label: "Log Ambient", icon: Thermometer, href: "/dashboard/grows" },
];

/* ── More menu items ── */
const MORE_ITEMS = [
  { href: "/dashboard/tasks", label: "Tasks", icon: CheckSquare },
  { href: "/dashboard/devices", label: "Devices", icon: Cpu },
  { href: "/dashboard/automation", label: "Automation", icon: Bot },
  { href: "/dashboard/schedules", label: "Schedules", icon: Clock },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/strains", label: "Strains", icon: Dna },
  { href: "/dashboard/tents", label: "Grow Spaces", icon: Warehouse },
  { href: "/dashboard/grow-types", label: "Grow Types", icon: FlaskConical },
  { href: "/dashboard/notifications", label: "Notifications", icon: Bell },
  { href: "/dashboard/audit", label: "Audit Trail", icon: ClipboardList },
  { href: "/dashboard/api-keys", label: "API Keys", icon: KeyRound },
  { href: "/dashboard/billing", label: "Billing", icon: CreditCard },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

/* ── Bottom tabs (2 left + FAB + 2 right) ── */
const LEFT_TABS = [
  { href: "/dashboard", label: "Home", icon: LayoutDashboard },
  { href: "/dashboard/grows", label: "Grows", icon: Sprout },
];
const RIGHT_TABS = [
  { href: "/dashboard/ai", label: "AI", icon: MessageSquare },
];

export function MobileBottomNav() {
  const pathname = usePathname();
  const router = useRouter();
  const [fabOpen, setFabOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const { theme, setTheme } = useTheme();

  const isTabActive = (href: string) =>
    href === "/dashboard"
      ? pathname === "/dashboard"
      : pathname.startsWith(href);

  const isMoreActive =
    !isTabActive("/dashboard") &&
    !isTabActive("/dashboard/grows") &&
    !isTabActive("/dashboard/ai") &&
    pathname !== "/dashboard";

  return (
    <>
      {/* FAB overlay */}
      <AnimatePresence>
        {fabOpen && (
          <motion.div
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm md:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setFabOpen(false)}
          >
            <div className="absolute bottom-24 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3">
              {FAB_ACTIONS.map((action, i) => (
                <motion.button
                  key={action.label}
                  className="flex items-center gap-3 rounded-full bg-card border border-border px-4 py-2.5 shadow-lg"
                  initial={{ opacity: 0, y: 20, scale: 0.8 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.8 }}
                  transition={{ delay: i * 0.05, type: "spring", stiffness: 400, damping: 25 }}
                  onClick={(e) => {
                    e.stopPropagation();
                    setFabOpen(false);
                    router.push(action.href);
                  }}
                >
                  <div className="flex size-9 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <action.icon className="size-4" />
                  </div>
                  <span className="text-sm font-medium text-foreground pr-1">{action.label}</span>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* More sheet */}
      <AnimatePresence>
        {moreOpen && (
          <>
            <motion.div
              className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm md:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMoreOpen(false)}
            />
            <motion.div
              className="fixed bottom-0 left-0 right-0 z-50 rounded-t-2xl border-t bg-card md:hidden"
              style={{ paddingBottom: "env(safe-area-inset-bottom, 0px)" }}
              initial={{ y: "100%" }}
              animate={{ y: 0 }}
              exit={{ y: "100%" }}
              transition={{ type: "spring", stiffness: 400, damping: 35 }}
            >
              <div className="mx-auto mt-2 h-1 w-10 rounded-full bg-muted-foreground/30" />
              <div className="px-4 pt-4 pb-2 flex items-center justify-between">
                <h3 className="text-sm font-semibold">More</h3>
                <div className="flex items-center gap-2">
                  <button
                    className="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                    onClick={() => {
                      const next = theme === "dark" ? "light" : theme === "light" ? "system" : "dark";
                      setTheme(next);
                    }}
                  >
                    {theme === "dark" ? <Moon className="size-3.5" /> : theme === "light" ? <Sun className="size-3.5" /> : <Monitor className="size-3.5" />}
                    {theme === "dark" ? "Dark" : theme === "light" ? "Light" : "Auto"}
                  </button>
                  <button onClick={() => setMoreOpen(false)} className="rounded-full p-1 hover:bg-muted transition-colors">
                    <X className="size-4 text-muted-foreground" />
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-1 px-3 pb-6">
                {MORE_ITEMS.map((item) => (
                  <button
                    key={item.href}
                    className={cn(
                      "flex flex-col items-center gap-1.5 rounded-xl px-2 py-3 text-[11px] font-medium transition-colors",
                      pathname.startsWith(item.href)
                        ? "bg-primary/10 text-primary"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    )}
                    onClick={() => {
                      setMoreOpen(false);
                      router.push(item.href);
                    }}
                  >
                    <item.icon className="size-5" />
                    {item.label}
                  </button>
                ))}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Bottom nav bar */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 border-t border-border bg-card/95 backdrop-blur-lg supports-[backdrop-filter]:bg-card/80 md:hidden safe-area-pb">
        <div className="flex items-center justify-around px-2">
          {/* Left tabs */}
          {LEFT_TABS.map((tab) => (
            <TabButton key={tab.href} tab={tab} active={isTabActive(tab.href)} />
          ))}

          {/* Center FAB */}
          <button
            className="relative -mt-5 flex size-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg shadow-primary/30 active:scale-95 transition-transform"
            onClick={() => { setMoreOpen(false); setFabOpen(!fabOpen); }}
            aria-label="Quick actions"
          >
            <motion.div
              animate={{ rotate: fabOpen ? 45 : 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              {fabOpen ? <X className="size-6" /> : <Plus className="size-6" />}
            </motion.div>
          </button>

          {/* Right tabs */}
          {RIGHT_TABS.map((tab) => (
            <TabButton key={tab.href} tab={tab} active={isTabActive(tab.href)} />
          ))}

          {/* More */}
          <button
            className={cn(
              "flex flex-col items-center gap-0.5 px-3 py-2 text-[10px] font-medium transition-colors",
              isMoreActive || moreOpen ? "text-primary" : "text-muted-foreground"
            )}
            onClick={() => { setFabOpen(false); setMoreOpen(!moreOpen); }}
          >
            <svg className="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="4" y1="6" x2="20" y2="6" />
              <line x1="4" y1="12" x2="20" y2="12" />
              <line x1="4" y1="18" x2="20" y2="18" />
            </svg>
            More
          </button>
        </div>
      </nav>
    </>
  );
}

function TabButton({
  tab,
  active,
}: {
  tab: { href: string; label: string; icon: React.ComponentType<{ className?: string }> };
  active: boolean;
}) {
  return (
    <a
      href={tab.href}
      className={cn(
        "flex flex-col items-center gap-0.5 px-3 py-2 text-[10px] font-medium transition-colors",
        active ? "text-primary" : "text-muted-foreground"
      )}
    >
      <tab.icon className="size-5" />
      {tab.label}
    </a>
  );
}
