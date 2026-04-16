"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Sprout,
  Cpu,
  BarChart3,
  MoreHorizontal,
} from "lucide-react";
import { cn } from "@/lib/utils";

const BOTTOM_TABS = [
  { href: "/dashboard", label: "Home", icon: LayoutDashboard },
  { href: "/dashboard/grows", label: "Grows", icon: Sprout },
  { href: "/dashboard/devices", label: "Devices", icon: Cpu },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
];

export function MobileBottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-card/95 backdrop-blur-lg supports-[backdrop-filter]:bg-card/80 md:hidden safe-area-pb">
      <div className="flex items-center justify-around px-2 py-1">
        {BOTTOM_TABS.map((tab) => {
          const isActive =
            tab.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(tab.href);
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                "flex flex-col items-center gap-0.5 px-3 py-2 text-[10px] font-medium transition-colors",
                isActive
                  ? "text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <tab.icon className={cn("size-5", isActive && "text-primary")} />
              {tab.label}
            </Link>
          );
        })}
        <Link
          href="/dashboard/tents"
          className={cn(
            "flex flex-col items-center gap-0.5 px-3 py-2 text-[10px] font-medium transition-colors",
            !["/dashboard", "/dashboard/grows", "/dashboard/devices", "/dashboard/analytics"].some(
              (p) => p === "/dashboard" ? pathname === p : pathname.startsWith(p)
            ) && pathname !== "/dashboard"
              ? "text-primary"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <MoreHorizontal className="size-5" />
          More
        </Link>
      </div>
    </nav>
  );
}
