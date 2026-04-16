"use client";

import { SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
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
  breadcrumbs?: { label: string; href?: string }[];
  actions?: React.ReactNode;
}

export function PageHeader({ title, breadcrumbs, actions }: PageHeaderProps) {
  return (
    <header className="flex h-14 shrink-0 items-center gap-2 border-b border-border px-4 lg:px-6">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="mr-2 !h-4" />
      <div className="flex flex-1 items-center justify-between gap-2">
        {breadcrumbs && breadcrumbs.length > 0 ? (
          <Breadcrumb>
            <BreadcrumbList>
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
          <h1 className="text-sm font-semibold lg:text-base">{title}</h1>
        )}
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </header>
  );
}
