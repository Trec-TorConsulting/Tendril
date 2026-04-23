"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { listAuditLogs } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
import { cn, formatDateTime } from "@/lib/utils";
import { ChevronLeft, ChevronRight, Eye, EyeOff } from "lucide-react";
import { PageSkeleton } from "@/components/page-skeleton";

interface AuditEntry {
  id: string;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  before_value: Record<string, unknown> | null;
  after_value: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

const ACTION_VARIANT: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  create: "default",
  update: "secondary",
  delete: "destructive",
};

export default function AuditPage() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [actionFilter, setActionFilter] = useState("");
  const [resourceFilter, setResourceFilter] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const data = await listAuditLogs(token, {
        page,
        page_size: 50,
        action: actionFilter || undefined,
        resource_type: resourceFilter || undefined,
      });
      setEntries(data.items);
      setTotal(data.total);
    } catch {
      /* tier restricted */
    } finally { setLoading(false); }
  }, [page, actionFilter, resourceFilter]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const totalPages = Math.ceil(total / 50);

  if (loading) return <PageSkeleton rows={6} />;

  return (
    <>
      <PageHeader
        title="Audit Trail"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Audit Trail" },
        ]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        <p className="text-sm text-muted-foreground">
          Complete log of all user actions. Commercial plan only.
        </p>

        {/* Filters */}
        <div className="flex flex-wrap gap-3">
          <Select
            value={actionFilter || "all"}
            onValueChange={(v) => {
              setActionFilter(v === "all" ? "" : (v ?? ""));
              setPage(1);
            }}
          >
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="All Actions" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Actions</SelectItem>
              <SelectItem value="create">Create</SelectItem>
              <SelectItem value="update">Update</SelectItem>
              <SelectItem value="delete">Delete</SelectItem>
            </SelectContent>
          </Select>
          <Input
            value={resourceFilter}
            onChange={(e) => {
              setResourceFilter(e.target.value);
              setPage(1);
            }}
            placeholder="Filter by resource type..."
            className="w-[220px]"
          />
        </div>

        {/* Table */}
        {entries.length === 0 ? (
          <Card className="flex flex-col items-center justify-center py-16">
            <Eye className="size-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No audit entries found</h3>
            <p className="mt-1 text-sm text-muted-foreground">Activity will appear here as changes are made.</p>
          </Card>
        ) : (
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Resource</TableHead>
                    <TableHead>Resource ID</TableHead>
                    <TableHead>IP</TableHead>
                    <TableHead className="w-20">Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {entries.map((e) => (
                    <>
                      <TableRow key={e.id}>
                        <TableCell className="text-xs text-muted-foreground">
                          {formatDateTime(e.created_at)}
                        </TableCell>
                        <TableCell>
                          <Badge variant={ACTION_VARIANT[e.action] || "outline"}>
                            {e.action}
                          </Badge>
                        </TableCell>
                        <TableCell>{e.resource_type}</TableCell>
                        <TableCell className="font-mono text-xs">
                          {e.resource_id.slice(0, 8)}...
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground">
                          {e.ip_address || "—"}
                        </TableCell>
                        <TableCell>
                          {(e.before_value || e.after_value) && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-7 px-2"
                              onClick={() =>
                                setExpanded(expanded === e.id ? null : e.id)
                              }
                            >
                              {expanded === e.id ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                      {expanded === e.id && (
                        <TableRow key={`${e.id}-detail`}>
                          <TableCell colSpan={6} className="p-0">
                            <div className="grid grid-cols-2 gap-4 rounded bg-muted p-3 text-xs">
                              <div>
                                <span className="mb-1 block text-muted-foreground">
                                  Before
                                </span>
                                <pre className="whitespace-pre-wrap">
                                  {e.before_value
                                    ? JSON.stringify(e.before_value, null, 2)
                                    : "—"}
                                </pre>
                              </div>
                              <div>
                                <span className="mb-1 block text-muted-foreground">
                                  After
                                </span>
                                <pre className="whitespace-pre-wrap">
                                  {e.after_value
                                    ? JSON.stringify(e.after_value, null, 2)
                                    : "—"}
                                </pre>
                              </div>
                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between pt-2">
            <span className="text-sm text-muted-foreground">
              Page {page} of {totalPages} ({total} entries)
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
              >
                <ChevronLeft className="mr-1 h-4 w-4" />
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={page === totalPages}
                onClick={() => setPage(page + 1)}
              >
                Next
                <ChevronRight className="ml-1 h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
