"use client";

import { useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { changePassword } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2 } from "lucide-react";

export default function SecurityPage() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage({ type: "", text: "" });

    if (newPassword.length < 8) {
      setMessage({ type: "error", text: "Password must be at least 8 characters" });
      return;
    }

    if (newPassword !== confirmPassword) {
      setMessage({ type: "error", text: "Passwords do not match" });
      return;
    }

    const token = getAccessToken();
    if (!token) return;

    setSaving(true);
    try {
      await changePassword(token, {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setMessage({ type: "success", text: "Password changed successfully" });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (e: unknown) {
      setMessage({
        type: "error",
        text: e instanceof Error ? e.message : "Failed to change password",
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Security"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Settings", href: "/dashboard/settings" },
          { label: "Security" },
        ]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {message.text && (
          <Alert variant={message.type === "success" ? "default" : "destructive"}>
            <AlertDescription>{message.text}</AlertDescription>
          </Alert>
        )}

        <Card className="max-w-lg">
          <CardHeader>
            <CardTitle>Change Password</CardTitle>
            <CardDescription>Update your password to keep your account secure.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label>Current Password</Label>
                <Input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />
              </div>
              <div className="space-y-2">
                <Label>New Password</Label>
                <Input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={8}
                  autoComplete="new-password"
                />
                <p className="text-xs text-muted-foreground">Minimum 8 characters</p>
              </div>
              <div className="space-y-2">
                <Label>Confirm New Password</Label>
                <Input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  autoComplete="new-password"
                />
              </div>
              <Button type="submit" disabled={saving}>
                {saving && <Loader2 className="mr-2 size-4 animate-spin" />}
                {saving ? "Changing…" : "Change Password"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
