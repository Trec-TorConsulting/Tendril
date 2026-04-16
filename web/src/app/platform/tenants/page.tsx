"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { adminListTenants, adminListTenantUsers } from "@/lib/api";
import type { AdminTenantSummary, AdminUserSummary } from "@/lib/api";
import { cn } from "@/lib/utils";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Building2, ChevronDown, CheckCircle, XCircle } from "lucide-react";

export default function PlatformTenantsPage() {
  const [tenants, setTenants] = useState<AdminTenantSummary[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [expandedUsers, setExpandedUsers] = useState<AdminUserSummary[]>([]);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      setTenants(await adminListTenants(token));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const toggleExpand = async (tenantId: string) => {
    if (expandedId === tenantId) {
      setExpandedId(null);
      setExpandedUsers([]);
      return;
    }
    const token = getAccessToken();
    if (!token) return;
    try {
      const users = await adminListTenantUsers(token, tenantId);
      setExpandedUsers(users);
      setExpandedId(tenantId);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load users");
    }
  };

  return (
    <>
      <PageHeader
        title="Organizations"
        breadcrumbs={[
          { label: "Platform", href: "/platform" },
          { label: "Organizations" },
        ]}
        actions={
          <Badge variant="secondary">{tenants.length} total</Badge>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-2">
          {tenants.length === 0 && !error && (
            <Card className="flex flex-col items-center justify-center py-16">
              <Building2 className="size-12 text-amber-500/50" />
              <h3 className="mt-4 text-lg font-semibold">No organizations</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Organizations will appear here once tenants are created.
              </p>
            </Card>
          )}

          {tenants.map((t) => (
            <Collapsible
              key={t.id}
              open={expandedId === t.id}
              onOpenChange={() => toggleExpand(t.id)}
            >
              <CollapsibleTrigger
                render={
                  <Card
                    className={cn(
                      "cursor-pointer transition hover:border-border/80",
                      expandedId === t.id && "border-amber-500/50",
                    )}
                  />
                }
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Building2 className="size-4 text-amber-500" />
                      <span className="font-medium">{t.name}</span>
                      <span className="text-sm text-muted-foreground">{t.slug}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant="outline" className="capitalize">
                        {t.plan}
                      </Badge>
                      <span className="text-sm text-muted-foreground">{t.user_count} users</span>
                      <span className="text-sm text-muted-foreground">
                        {new Date(t.created_at).toLocaleDateString()}
                      </span>
                      <ChevronDown
                        className={cn(
                          "size-4 text-muted-foreground transition-transform",
                          expandedId === t.id && "rotate-180",
                        )}
                      />
                    </div>
                  </div>
                </CardContent>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <Card className="mx-4 rounded-t-none border-t-0">
                  <CardContent className="p-4">
                    <h3 className="mb-2 text-xs font-semibold text-muted-foreground">Members</h3>
                    {expandedUsers.length === 0 ? (
                      <p className="text-sm text-muted-foreground">No users.</p>
                    ) : (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Email</TableHead>
                            <TableHead>Name</TableHead>
                            <TableHead>Role</TableHead>
                            <TableHead>Verified</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {expandedUsers.map((u) => (
                            <TableRow key={u.id}>
                              <TableCell>{u.email}</TableCell>
                              <TableCell className="text-muted-foreground">
                                {u.display_name || "—"}
                              </TableCell>
                              <TableCell>
                                <Badge variant="secondary">{u.role}</Badge>
                              </TableCell>
                              <TableCell>
                                {u.email_verified ? (
                                  <CheckCircle className="size-4 text-green-500" />
                                ) : (
                                  <XCircle className="size-4 text-muted-foreground" />
                                )}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    )}
                  </CardContent>
                </Card>
              </CollapsibleContent>
            </Collapsible>
          ))}
        </div>
      </div>
    </>
  );
}
