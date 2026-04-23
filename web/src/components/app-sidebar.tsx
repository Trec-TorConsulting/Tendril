"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Warehouse,
  Sprout,
  FlaskConical,
  BarChart3,
  Cpu,
  MessageSquare,
  Stethoscope,
  Bot,
  Clock,
  Bell,
  Dna,
  CheckSquare,
  ClipboardList,
  KeyRound,
  CreditCard,
  Settings,
  Lock,
  Users,
  Shield,
  LogOut,
  ChevronUp,
  ChevronRight,
  Leaf,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  SidebarSeparator,
} from "@/components/ui/sidebar";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ThemeToggle } from "@/components/theme-toggle";
import { useGrow } from "@/hooks/use-grow";
import type { UserData } from "@/hooks/use-user";

const MAIN_NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/tents", label: "Grow Spaces", icon: Warehouse },
  { href: "/dashboard/grows", label: "Grows", icon: Sprout },
  { href: "/dashboard/grow-types", label: "Grow Types", icon: FlaskConical },
  { href: "/dashboard/devices", label: "Devices", icon: Cpu },
];

const INSIGHTS_NAV = [
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/ai", label: "AI Chat", icon: MessageSquare },
  { href: "/dashboard/ai/health", label: "Health Check", icon: Stethoscope },
];

const AUTOMATION_NAV = [
  { href: "/dashboard/automation", label: "Automation", icon: Bot },
  { href: "/dashboard/schedules", label: "Schedules", icon: Clock },
  { href: "/dashboard/notifications", label: "Notifications", icon: Bell },
  { href: "/dashboard/tasks", label: "Tasks", icon: CheckSquare },
];

const LIBRARY_NAV = [
  { href: "/dashboard/strains", label: "Strains", icon: Dna },
];

const ACCOUNT_NAV = [
  { href: "/dashboard/audit", label: "Audit Trail", icon: ClipboardList },
  { href: "/dashboard/api-keys", label: "API Keys", icon: KeyRound },
  { href: "/dashboard/billing", label: "Billing", icon: CreditCard },
];

interface AppSidebarProps {
  user: UserData | null;
  onLogout: () => void;
}

export function AppSidebar({ user, onLogout }: AppSidebarProps) {
  const pathname = usePathname();
  const { grows, selectedGrow, setSelectedGrowId } = useGrow();

  const initials = user?.display_name
    ? user.display_name.split(" ").map((w) => w[0]).join("").toUpperCase().slice(0, 2)
    : user?.email?.slice(0, 2).toUpperCase() ?? "?";

  const isPlatformUser = user?.is_platform_admin || user?.is_support;
  const isOwner = user?.role === "owner";

  return (
    <Sidebar collapsible="icon" className="border-r border-sidebar-border">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" render={<Link href="/dashboard" />}>
              <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <Leaf className="size-4" />
              </div>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">Tendril</span>
                <span className="truncate text-xs text-muted-foreground">Grow Platform</span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      {/* Global Grow Selector */}
      {grows.length > 0 && (
        <div className="px-3 pb-2 group-data-[collapsible=icon]:hidden">
          <Select value={selectedGrow?.id || ""} onValueChange={(v) => setSelectedGrowId(v ?? "")}>
            <SelectTrigger className="h-8 w-full text-xs">
              <SelectValue>
                {selectedGrow ? (
                  <span className="flex items-center gap-1.5">
                    <Sprout className="size-3 text-primary" />
                    {selectedGrow.name}
                  </span>
                ) : "Select a grow"}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {grows.filter((g) => g.status === "active").length > 0 && (
                <div className="px-2 py-1 text-[10px] font-medium text-muted-foreground">Active</div>
              )}
              {grows.filter((g) => g.status === "active").map((g) => (
                <SelectItem key={g.id} value={g.id}>
                  {g.name}
                </SelectItem>
              ))}
              {grows.filter((g) => g.status !== "active").length > 0 && (
                <div className="px-2 py-1 text-[10px] font-medium text-muted-foreground">Other</div>
              )}
              {grows.filter((g) => g.status !== "active").map((g) => (
                <SelectItem key={g.id} value={g.id}>
                  {g.name} ({g.status})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      <SidebarContent>
        <NavGroup label="Overview" items={MAIN_NAV} pathname={pathname} />
        <NavGroup label="Insights" items={INSIGHTS_NAV} pathname={pathname} />
        <NavGroup label="Automation" items={AUTOMATION_NAV} pathname={pathname} />
        <NavGroup label="Library" items={LIBRARY_NAV} pathname={pathname} />
        <NavGroup label="Account" items={ACCOUNT_NAV} pathname={pathname} />

        {/* Settings */}
        <SidebarSeparator />
        <SidebarGroup>
          <SidebarGroupLabel>Settings</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <NavItem href="/dashboard/settings" label="Profile" icon={Settings} pathname={pathname} />
              <NavItem href="/dashboard/settings/security" label="Security" icon={Lock} pathname={pathname} />
              {isOwner && (
                <NavItem href="/dashboard/settings/team" label="Team" icon={Users} pathname={pathname} />
              )}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Platform Admin */}
        {isPlatformUser && (
          <>
            <SidebarSeparator />
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <SidebarMenuButton render={<Link href="/platform" className="text-amber-400 hover:text-amber-300" />} tooltip="Platform Admin">
                      <Shield className="size-4" />
                      <span>Platform Admin</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </>
        )}
      </SidebarContent>

      <SidebarFooter>
        <div className="px-2 group-data-[collapsible=icon]:hidden">
          <ThemeToggle className="w-full justify-start" />
        </div>
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger
                render={
                  <SidebarMenuButton
                    size="lg"
                    className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                  />
                }
              >
                <Avatar className="h-8 w-8 rounded-lg">
                  <AvatarFallback className="rounded-lg bg-primary/20 text-primary text-xs">
                    {initials}
                  </AvatarFallback>
                </Avatar>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">
                    {user?.display_name || user?.email}
                  </span>
                  <span className="truncate text-xs text-muted-foreground">{user?.email}</span>
                </div>
                <ChevronUp className="ml-auto size-4" />
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
                side="top"
                align="start"
                sideOffset={4}
              >
                <DropdownMenuItem render={<Link href="/dashboard/settings" />}>
                  <Settings className="mr-2 size-4" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={onLogout} className="text-destructive focus:text-destructive">
                  <LogOut className="mr-2 size-4" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  );
}

function NavGroup({
  label,
  items,
  pathname,
}: {
  label: string;
  items: { href: string; label: string; icon: React.ComponentType<{ className?: string }> }[];
  pathname: string;
}) {
  const hasActive = items.some(
    (item) => pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href + "/"))
  );

  return (
    <Collapsible defaultOpen={hasActive || label === "Overview"}>
      <SidebarGroup>
        <CollapsibleTrigger
          render={
            <SidebarGroupLabel className="cursor-pointer select-none hover:text-sidebar-foreground transition-colors" />
          }
        >
          {label}
          <ChevronRight className="ml-auto size-4 transition-transform duration-200 [[data-panel-open]_&]:rotate-90" />
        </CollapsibleTrigger>
        <CollapsibleContent>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <NavItem key={item.href} {...item} pathname={pathname} />
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </CollapsibleContent>
      </SidebarGroup>
    </Collapsible>
  );
}

function NavItem({
  href,
  label,
  icon: Icon,
  pathname,
}: {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  pathname: string;
}) {
  const isActive = pathname === href || (href !== "/dashboard" && pathname.startsWith(href + "/"));
  return (
    <SidebarMenuItem>
      <SidebarMenuButton render={<Link href={href} />} isActive={isActive} tooltip={label}>
        <Icon className="size-4" />
        <span>{label}</span>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}
