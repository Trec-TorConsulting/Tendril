"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { adminListUsers, adminUpdateUserFlags, adminDeleteUser } from "@/lib/api";
import type { AdminUserSummary } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Users, CheckCircle, XCircle, Search, Trash2 } from "lucide-react";

export default function PlatformUsersPage() {
  const [users, setUsers] = useState<AdminUserSummary[]>([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      setUsers(await adminListUsers(token));
      setError("");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const toggleFlag = async (
    userId: string,
    flag: "is_platform_admin" | "is_support",
    current: boolean,
  ) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      // Map boolean flag toggles to platform_role values
      let newRole: string;
      if (flag === "is_platform_admin") {
        newRole = current ? "user" : "super_admin";
      } else {
        newRole = current ? "user" : "support";
      }
      await adminUpdateUserFlags(token, userId, { platform_role: newRole });
      refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to update");
    }
  };

  const handleDeleteUser = async (userId: string, email: string) => {
    if (!confirm(`Permanently delete "${email}"?\n\nThis will remove the user and all their memberships. This cannot be undone.`)) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await adminDeleteUser(token, userId);
      refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to delete user");
    }
  };

  const filtered = users.filter(
    (u) =>
      u.email.toLowerCase().includes(search.toLowerCase()) ||
      (u.display_name || "").toLowerCase().includes(search.toLowerCase()) ||
      u.tenant_name.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <>
      <PageHeader
        title="All Users"
        breadcrumbs={[
          { label: "Platform", href: "/platform" },
          { label: "Users" },
        ]}
        actions={
          <Badge variant="secondary">{users.length} total</Badge>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search by email, name, or organization..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* Table */}
        <div className="overflow-x-auto rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Email</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Organization</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Platform Admin</TableHead>
                <TableHead>Support</TableHead>
                <TableHead>Verified</TableHead>
                <TableHead>Joined</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((u) => (
                <TableRow key={u.id}>
                  <TableCell>{u.email}</TableCell>
                  <TableCell className="text-muted-foreground">{u.display_name || "—"}</TableCell>
                  <TableCell className="text-muted-foreground">{u.tenant_name}</TableCell>
                  <TableCell>
                    <Badge variant="secondary" className="capitalize">
                      {u.role}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={u.is_platform_admin}
                        onCheckedChange={() =>
                          toggleFlag(u.id, "is_platform_admin", u.is_platform_admin)
                        }
                        className="data-[state=checked]:bg-amber-500"
                      />
                      {u.is_platform_admin && (
                        <Badge variant="outline" className="border-amber-500/50 text-amber-500">
                          Admin
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={u.is_support}
                        onCheckedChange={() =>
                          toggleFlag(u.id, "is_support", u.is_support)
                        }
                        className="data-[state=checked]:bg-blue-500"
                      />
                      {u.is_support && (
                        <Badge variant="outline" className="border-blue-500/50 text-blue-500">
                          Support
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    {u.email_verified ? (
                      <CheckCircle className="size-4 text-green-500" />
                    ) : (
                      <XCircle className="size-4 text-muted-foreground" />
                    )}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {formatDate(u.created_at)}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      size="sm"
                      variant="destructive"
                      className="h-7 px-2 text-xs"
                      onClick={() => handleDeleteUser(u.id, u.email)}
                    >
                      <Trash2 className="size-3 mr-1" />
                      Delete
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {filtered.length === 0 && (
                <TableRow>
                  <TableCell colSpan={9} className="py-8 text-center text-muted-foreground">
                    {search ? "No users match your search." : "No users found."}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </>
  );
}
