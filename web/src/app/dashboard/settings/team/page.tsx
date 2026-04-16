"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listTenantMembers,
  addTenantMember,
  updateMemberRole,
  removeTenantMember,
  getMe,
} from "@/lib/api";
import type { TenantMember } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Plus, Trash2, CheckCircle2, Clock, Loader2, Users } from "lucide-react";

export default function TeamPage() {
  const [members, setMembers] = useState<TenantMember[]>([]);
  const [currentUserId, setCurrentUserId] = useState("");
  const [isOwner, setIsOwner] = useState(false);
  const [showAdd, setShowAdd] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [newName, setNewName] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState("member");
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [me, m] = await Promise.all([getMe(token), listTenantMembers(token)]);
      setCurrentUserId(me.id);
      setIsOwner(me.role === "owner");
      setMembers(m);
      setError("");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    setAdding(true);
    setError("");
    try {
      await addTenantMember(token, {
        email: newEmail,
        display_name: newName || undefined,
        password: newPassword,
        role: newRole,
      });
      setMessage("Member added successfully");
      setShowAdd(false);
      setNewEmail("");
      setNewName("");
      setNewPassword("");
      setNewRole("member");
      refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to add member");
    } finally {
      setAdding(false);
    }
  };

  const handleRoleChange = async (memberId: string, role: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await updateMemberRole(token, memberId, role);
      setMessage("Role updated");
      refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to update role");
    }
  };

  const handleRemove = async (memberId: string, email: string) => {
    if (!confirm(`Remove ${email} from the team?`)) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await removeTenantMember(token, memberId);
      setMessage("Member removed");
      refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to remove member");
    }
  };

  return (
    <>
      <PageHeader
        title="Team"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Settings", href: "/dashboard/settings" },
          { label: "Team" },
        ]}
        actions={
          isOwner ? (
            <Button size="sm" onClick={() => setShowAdd(true)}>
              <Plus className="mr-1 size-4" />
              Add Member
            </Button>
          ) : undefined
        }
      />
      <div className="flex flex-1 flex-col gap-4 p-4 lg:p-6">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {message && (
          <Alert>
            <AlertDescription className="flex items-center justify-between">
              {message}
              <button onClick={() => setMessage("")} className="text-muted-foreground hover:text-foreground">
                ✕
              </button>
            </AlertDescription>
          </Alert>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="size-5" />
              Members ({members.length})
            </CardTitle>
            <CardDescription>
              Manage your organization&apos;s team members and their roles.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {members.length === 0 ? (
              <div className="flex flex-col items-center py-8 text-center">
                <Users className="size-10 text-muted-foreground/50" />
                <p className="mt-2 text-sm text-muted-foreground">No team members found.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Member</TableHead>
                      <TableHead className="hidden sm:table-cell">Role</TableHead>
                      <TableHead className="hidden md:table-cell">Status</TableHead>
                      <TableHead className="hidden lg:table-cell">Joined</TableHead>
                      {isOwner && <TableHead className="w-16">Actions</TableHead>}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {members.map((m) => {
                      const isSelf = m.id === currentUserId;
                      const initial = (m.display_name || m.email).charAt(0).toUpperCase();
                      return (
                        <TableRow key={m.id}>
                          <TableCell>
                            <div className="flex items-center gap-3">
                              <Avatar className="size-8">
                                <AvatarFallback className="bg-primary/20 text-primary text-xs">
                                  {initial}
                                </AvatarFallback>
                              </Avatar>
                              <div className="min-w-0">
                                <p className="truncate font-medium">
                                  {m.display_name || "—"}
                                  {isSelf && (
                                    <span className="ml-1 text-xs text-muted-foreground">(you)</span>
                                  )}
                                </p>
                                <p className="truncate text-xs text-muted-foreground">{m.email}</p>
                              </div>
                            </div>
                          </TableCell>
                          <TableCell className="hidden sm:table-cell">
                            {isOwner && !isSelf ? (
                              <Select
                                value={m.role}
                                onValueChange={(v) => handleRoleChange(m.id, v ?? "")}
                              >
                                <SelectTrigger className="h-7 w-24 text-xs">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="owner">Owner</SelectItem>
                                  <SelectItem value="member">Member</SelectItem>
                                  <SelectItem value="viewer">Viewer</SelectItem>
                                </SelectContent>
                              </Select>
                            ) : (
                              <Badge variant="secondary" className="capitalize">
                                {m.role}
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell className="hidden md:table-cell">
                            {m.email_verified ? (
                              <Badge variant="outline" className="gap-1 text-primary">
                                <CheckCircle2 className="size-3" />
                                Verified
                              </Badge>
                            ) : (
                              <Badge variant="outline" className="gap-1 text-muted-foreground">
                                <Clock className="size-3" />
                                Pending
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell className="hidden lg:table-cell text-muted-foreground">
                            {new Date(m.created_at).toLocaleDateString()}
                          </TableCell>
                          {isOwner && (
                            <TableCell>
                              {!isSelf && (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="size-8 text-muted-foreground hover:text-destructive"
                                  onClick={() => handleRemove(m.id, m.email)}
                                >
                                  <Trash2 className="size-4" />
                                </Button>
                              )}
                            </TableCell>
                          )}
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Add Member Dialog */}
      <Dialog open={showAdd} onOpenChange={setShowAdd}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New Member</DialogTitle>
            <DialogDescription>
              Add a team member to your organization. They will be able to sign in with the password you set.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleAdd} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Email</Label>
                <Input
                  type="email"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  required
                  placeholder="user@example.com"
                />
              </div>
              <div className="space-y-2">
                <Label>Display Name</Label>
                <Input
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="Optional"
                />
              </div>
              <div className="space-y-2">
                <Label>Temporary Password</Label>
                <Input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                />
                <p className="text-xs text-muted-foreground">
                  User should change this after first login
                </p>
              </div>
              <div className="space-y-2">
                <Label>Role</Label>
                <Select value={newRole} onValueChange={(v) => setNewRole(v ?? "member")}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="member">Member</SelectItem>
                    <SelectItem value="viewer">Viewer</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" type="button" onClick={() => setShowAdd(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={adding}>
                {adding && <Loader2 className="mr-2 size-4 animate-spin" />}
                {adding ? "Adding…" : "Add Member"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}
