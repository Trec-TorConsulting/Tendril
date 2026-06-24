import type { ReactNode } from "react";
import { vi } from "vitest";

type WithChildren = { children?: ReactNode };

const passthrough = ({ children }: WithChildren) => children;
const empty = () => null;

/**
 * Shared, typed mock for `@/components/ui/sidebar`.
 *
 * The real sidebar primitives are layout wrappers that are irrelevant to
 * page-level rendering tests, so they're stubbed as passthroughs / no-ops.
 * Previously each test inlined this block with `: any` props (~20 casts per
 * file); this centralizes it with real types.
 *
 * Use from a test's `vi.mock` factory (async factory so the hoisted mock can
 * pull in this helper):
 *
 *   vi.mock("@/components/ui/sidebar", async () =>
 *     (await import("./helpers/sidebar-mock")).sidebarModuleMock());
 */
export function sidebarModuleMock() {
  return {
    Sidebar: passthrough,
    SidebarContent: passthrough,
    SidebarFooter: passthrough,
    SidebarGroup: passthrough,
    SidebarGroupAction: passthrough,
    SidebarGroupContent: passthrough,
    SidebarGroupLabel: passthrough,
    SidebarHeader: passthrough,
    SidebarInput: empty,
    SidebarInset: passthrough,
    SidebarMenu: passthrough,
    SidebarMenuAction: passthrough,
    SidebarMenuBadge: passthrough,
    SidebarMenuButton: passthrough,
    SidebarMenuItem: passthrough,
    SidebarMenuSkeleton: empty,
    SidebarMenuSub: passthrough,
    SidebarMenuSubButton: passthrough,
    SidebarMenuSubItem: passthrough,
    SidebarProvider: passthrough,
    SidebarRail: empty,
    SidebarSeparator: empty,
    SidebarTrigger: passthrough,
    useSidebar: () => ({
      state: "expanded" as const,
      open: true,
      setOpen: vi.fn(),
      openMobile: false,
      setOpenMobile: vi.fn(),
      isMobile: false,
      toggleSidebar: vi.fn(),
    }),
  };
}
