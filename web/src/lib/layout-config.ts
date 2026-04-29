import {
  LayoutDashboard,
  Sprout,
  Camera,
  BookOpen,
  Bell,
  MoreHorizontal,
  Users,
  PenLine,
  Bot,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export type LayoutMode = "beginner" | "home" | "standard" | "pro" | "commercial";

export interface TabConfig {
  id: string;
  label: string;
  icon: LucideIcon;
  href: string;
}

export interface LayoutModeConfig {
  mode: LayoutMode;
  label: string;
  description: string;
  density: "relaxed" | "normal" | "compact";
  tabs: TabConfig[];
  showFab: boolean;
  sidebarCollapsed: boolean;
  animationSpeed: "slow" | "normal" | "instant";
}

export const LAYOUT_CONFIGS: Record<LayoutMode, LayoutModeConfig> = {
  beginner: {
    mode: "beginner",
    label: "Beginner",
    description: "Guided experience for your first grow",
    density: "relaxed",
    tabs: [
      { id: "home", label: "Home", icon: LayoutDashboard, href: "/dashboard" },
      { id: "log", label: "Log", icon: PenLine, href: "/dashboard/quick-log" },
      { id: "camera", label: "Camera", icon: Camera, href: "/dashboard/cameras" },
      { id: "guide", label: "Guide", icon: BookOpen, href: "/dashboard/guide" },
    ],
    showFab: false,
    sidebarCollapsed: true,
    animationSpeed: "slow",
  },
  home: {
    mode: "home",
    label: "Home",
    description: "Simple overview for 1-2 grows",
    density: "normal",
    tabs: [
      { id: "home", label: "Home", icon: LayoutDashboard, href: "/dashboard" },
      { id: "log", label: "Log", icon: PenLine, href: "/dashboard/quick-log" },
      { id: "camera", label: "Camera", icon: Camera, href: "/dashboard/cameras" },
      { id: "alerts", label: "Alerts", icon: Bell, href: "/dashboard/notifications" },
      { id: "more", label: "More", icon: MoreHorizontal, href: "#more" },
    ],
    showFab: false,
    sidebarCollapsed: false,
    animationSpeed: "normal",
  },
  standard: {
    mode: "standard",
    label: "Standard",
    description: "Full dashboard for multiple grows",
    density: "normal",
    tabs: [
      { id: "home", label: "Home", icon: LayoutDashboard, href: "/dashboard" },
      { id: "grows", label: "Grows", icon: Sprout, href: "/dashboard/grows" },
      { id: "log", label: "Log", icon: PenLine, href: "/dashboard/quick-log" },
      { id: "ai", label: "AI", icon: Bot, href: "/dashboard/ai" },
      { id: "more", label: "More", icon: MoreHorizontal, href: "#more" },
    ],
    showFab: true,
    sidebarCollapsed: false,
    animationSpeed: "normal",
  },
  pro: {
    mode: "pro",
    label: "Pro",
    description: "Dense panels for experienced growers",
    density: "compact",
    tabs: [
      { id: "home", label: "Home", icon: LayoutDashboard, href: "/dashboard" },
      { id: "grows", label: "Grows", icon: Sprout, href: "/dashboard/grows" },
      { id: "log", label: "Log", icon: PenLine, href: "/dashboard/quick-log" },
      { id: "cameras", label: "Cameras", icon: Camera, href: "/dashboard/cameras" },
      { id: "more", label: "More", icon: MoreHorizontal, href: "#more" },
    ],
    showFab: true,
    sidebarCollapsed: false,
    animationSpeed: "instant",
  },
  commercial: {
    mode: "commercial",
    label: "Commercial",
    description: "Fleet management for teams",
    density: "compact",
    tabs: [
      { id: "home", label: "Home", icon: LayoutDashboard, href: "/dashboard" },
      { id: "grows", label: "Grows", icon: Sprout, href: "/dashboard/grows" },
      { id: "log", label: "Log", icon: PenLine, href: "/dashboard/quick-log" },
      { id: "team", label: "Team", icon: Users, href: "/dashboard/team" },
      { id: "more", label: "More", icon: MoreHorizontal, href: "#more" },
    ],
    showFab: true,
    sidebarCollapsed: false,
    animationSpeed: "instant",
  },
};
