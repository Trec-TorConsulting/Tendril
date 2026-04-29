"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { getMe, getMyTenant, updateProfile } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2, Pencil, X, Download, Trash2, Check } from "lucide-react";
import { useLayoutMode } from "@/hooks/use-layout-mode";
import { LAYOUT_CONFIGS, type LayoutMode } from "@/lib/layout-config";

export default function ProfilePage() {
  const [user, setUser] = useState<{
    id: string;
    email: string;
    display_name: string | null;
    role: string;
    tenant_id: string;
    is_platform_admin: boolean;
    is_support: boolean;
  } | null>(null);
  const [tenant, setTenant] = useState<{ name: string; plan: string } | null>(null);
  const [editing, setEditing] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    const [u, t] = await Promise.all([getMe(token), getMyTenant(token)]);
    setUser(u);
    setTenant(t);
    setDisplayName(u.display_name || "");
    setEmail(u.email);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleSave = async () => {
    const token = getAccessToken();
    if (!token || !user) return;
    setSaving(true);
    setMessage({ type: "", text: "" });
    try {
      const updates: { display_name?: string; email?: string } = {};
      if (displayName !== (user.display_name || "")) updates.display_name = displayName;
      if (email !== user.email) updates.email = email;

      if (Object.keys(updates).length === 0) {
        setEditing(false);
        return;
      }

      await updateProfile(token, updates);
      setMessage({ type: "success", text: "Profile updated successfully" });
      setEditing(false);
      refresh();
    } catch (e: unknown) {
      setMessage({ type: "error", text: e instanceof Error ? e.message : "Failed to update" });
    } finally {
      setSaving(false);
    }
  };

  const initials = user?.display_name
    ? user.display_name.split(" ").map((w) => w[0]).join("").toUpperCase().slice(0, 2)
    : user?.email?.slice(0, 2).toUpperCase() ?? "?";

  return (
    <>
      <PageHeader
        title="Profile"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Settings", href: "/dashboard/settings" },
          { label: "Profile" },
        ]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {message.text && (
          <Alert variant={message.type === "success" ? "default" : "destructive"}>
            <AlertDescription>{message.text}</AlertDescription>
          </Alert>
        )}

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Profile Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Personal Information</CardTitle>
                {!editing && user && (
                  <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
                    <Pencil className="mr-1 size-3" />
                    Edit
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {!user ? (
                <div className="space-y-4">
                  <Skeleton className="h-12 w-12 rounded-full" />
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-4 w-48" />
                </div>
              ) : !editing ? (
                <div className="flex items-start gap-4">
                  <Avatar className="size-14">
                    <AvatarFallback className="bg-primary/20 text-primary text-lg">
                      {initials}
                    </AvatarFallback>
                  </Avatar>
                  <div className="space-y-3 text-sm">
                    <div>
                      <p className="text-muted-foreground">Display Name</p>
                      <p className="font-medium">{user.display_name || "Not set"}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Email</p>
                      <p className="font-medium">{user.email}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Role</p>
                      <Badge variant="secondary" className="capitalize">{user.role}</Badge>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Display Name</Label>
                    <Input
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                    {email !== user.email && (
                      <p className="text-xs text-amber-400">
                        Changing email will require re-verification
                      </p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleSave} disabled={saving}>
                      {saving && <Loader2 className="mr-1 size-3 animate-spin" />}
                      {saving ? "Saving…" : "Save Changes"}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setEditing(false);
                        setDisplayName(user.display_name || "");
                        setEmail(user.email);
                      }}
                    >
                      <X className="mr-1 size-3" />
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Organization */}
          <Card>
            <CardHeader>
              <CardTitle>Organization</CardTitle>
            </CardHeader>
            <CardContent>
              {tenant ? (
                <div className="space-y-3 text-sm">
                  <div>
                    <p className="text-muted-foreground">Name</p>
                    <p className="font-medium">{tenant.name}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Plan</p>
                    <Badge variant="secondary" className="capitalize">{tenant.plan}</Badge>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-4 w-24" />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Layout Mode */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>UI Layout Mode</CardTitle>
              <CardDescription>Choose how the interface is organized based on your experience level.</CardDescription>
            </CardHeader>
            <CardContent>
              <LayoutModeSelector />
            </CardContent>
          </Card>

          {/* Data & Privacy */}
          <Card>
            <CardHeader>
              <CardTitle>Data & Privacy</CardTitle>
              <CardDescription>Export or delete your account data.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <Download className="mr-1 size-3" />
                  Export Data
                </Button>
                <Button variant="outline" size="sm" className="text-destructive hover:text-destructive">
                  <Trash2 className="mr-1 size-3" />
                  Delete Account
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}

function LayoutModeSelector() {
  const { mode: currentMode, setMode } = useLayoutMode();
  const [switching, setSwitching] = useState<LayoutMode | null>(null);

  const handleSelect = async (mode: LayoutMode) => {
    if (mode === currentMode) return;
    setSwitching(mode);
    try {
      await setMode(mode);
    } finally {
      setSwitching(null);
    }
  };

  const modes = Object.values(LAYOUT_CONFIGS);

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      {modes.map((cfg) => (
        <button
          key={cfg.mode}
          onClick={() => handleSelect(cfg.mode)}
          disabled={switching !== null}
          className={`relative rounded-lg border p-4 text-left transition-colors hover:bg-accent/50 ${
            currentMode === cfg.mode
              ? "border-primary bg-primary/5"
              : "border-border"
          }`}
        >
          {currentMode === cfg.mode && (
            <div className="absolute right-2 top-2">
              <Check className="size-4 text-primary" />
            </div>
          )}
          <p className="font-medium text-sm">{cfg.label}</p>
          <p className="mt-1 text-xs text-muted-foreground">{cfg.description}</p>
          <Badge variant="outline" className="mt-2 text-[10px]">
            {cfg.density}
          </Badge>
          {switching === cfg.mode && (
            <Loader2 className="absolute right-2 top-2 size-4 animate-spin" />
          )}
        </button>
      ))}
    </div>
  );
}
