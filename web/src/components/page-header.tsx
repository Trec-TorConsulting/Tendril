"use client";

import { SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { Search, Sprout } from "lucide-react";
import { useIsMobile } from "@/hooks/use-mobile";
import { useGrow } from "@/hooks/use-grow";
import { usePathname, useRouter } from "next/navigation";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

interface PageHeaderProps {
  title: string;
  description?: string;
  breadcrumbs?: { label: string; href?: string }[];
  actions?: React.ReactNode;
}

export function PageHeader({ title, description, breadcrumbs, actions }: PageHeaderProps) {
  const isMobile = useIsMobile();
  const { grows, selectedGrow, setSelectedGrowId } = useGrow();
  const pathname = usePathname();
  const router = useRouter();
  const handleMobileGrowChange = (growId: string | null) => {
    if (!growId) return;
    setSelectedGrowId(growId);
    if (pathname.startsWith("/dashboard/grows/")) {
      router.push(`/dashboard/grows/${growId}`);
    }
  };
  const openCommandPalette = () => {
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "k", metaKey: true }));
  };

  return (
    <header className="flex h-14 shrink-0 items-center gap-2 border-b border-border px-4 lg:px-6">
      {!isMobile && (
        <>
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 !h-4" />
        </>
      )}
      {/* Mobile grow switcher — sidebar not rendered on mobile */}
      {isMobile && grows.length > 0 && (
        <>
          <Select value={selectedGrow?.id} onValueChange={handleMobileGrowChange}>
            <SelectTrigger className="h-8 w-auto max-w-[140px] gap-1.5 border-none bg-transparent px-1.5 text-xs font-medium shadow-none">
              <Sprout className="size-3 shrink-0 text-primary" />
              <span className="truncate">{selectedGrow?.name || "Grow"}</span>
            </SelectTrigger>
            <SelectContent>
              {grows.filter((g) => g.status === "active").map((g) => (
                <SelectItem key={g.id} value={g.id}>{g.name}</SelectItem>
              ))}
              {grows.filter((g) => g.status !== "active").map((g) => (
                <SelectItem key={g.id} value={g.id}>{g.name} ({g.status})</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Separator orientation="vertical" className="!h-4" />
        </>
      )}
      <div className="flex flex-1 items-center justify-between gap-2 min-w-0">
        {breadcrumbs && breadcrumbs.length > 0 && !isMobile ? (
          <Breadcrumb className="min-w-0">
            <BreadcrumbList className="flex-nowrap overflow-hidden">
              {breadcrumbs.map((crumb, i) => (
                <span key={crumb.label} className="contents">
                  {i > 0 && <BreadcrumbSeparator />}
                  <BreadcrumbItem>
                    {crumb.href ? (
                      <BreadcrumbLink href={crumb.href}>{crumb.label}</BreadcrumbLink>
                    ) : (
                      <BreadcrumbPage>{crumb.label}</BreadcrumbPage>
                    )}
                  </BreadcrumbItem>
                </span>
              ))}
            </BreadcrumbList>
          </Breadcrumb>
        ) : (
          <h1 className="text-sm font-semibold lg:text-base truncate">{title}</h1>
        )}
        <div className="flex items-center gap-2 shrink-0">
          <Button
            variant="outline"
            size="sm"
            className="hidden text-muted-foreground sm:flex"
            onClick={openCommandPalette}
          >
            <Search className="mr-2 size-4" />
            <span className="text-xs">Search...</span>
            <kbd className="ml-4 rounded border border-border bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
              ⌘K
            </kbd>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="sm:hidden size-8"
            onClick={openCommandPalette}
          >
            <Search className="size-4" />
          </Button>
          {actions}
        </div>
      </div>
    </header>
  );
}
