"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  adminListProviders,
  adminCreateProvider,
  adminUpdateProvider,
  adminDeleteProvider,
  adminTestProvider,
  type PaymentProviderSummary,
} from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { CreditCard, Plus, Trash2, CheckCircle, XCircle, Zap } from "lucide-react";
import { toast } from "sonner";

const PROVIDER_TYPES = [
  { value: "stripe", label: "Stripe", fields: ["secret_key", "publishable_key", "webhook_secret"] },
  { value: "paypal", label: "PayPal", fields: ["client_id", "client_secret", "mode", "webhook_id"] },
  { value: "square", label: "Square", fields: ["access_token", "mode", "location_id", "webhook_signature_key"] },
  { value: "paddle", label: "Paddle", fields: ["api_key", "mode", "webhook_secret"] },
];

export default function PlatformProvidersPage() {
  const [providers, setProviders] = useState<PaymentProviderSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [error, setError] = useState("");

  // Form state
  const [formType, setFormType] = useState("stripe");
  const [formName, setFormName] = useState("");
  const [formConfig, setFormConfig] = useState<Record<string, string>>({});

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const list = await adminListProviders(token);
      setProviders(list);
      setError("");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Access denied — platform admin required");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const token = getAccessToken();
    if (!token || !formName) return;
    try {
      await adminCreateProvider(token, {
        provider_type: formType,
        display_name: formName,
        config: formConfig,
        webhook_secret: formConfig.webhook_secret || formConfig.webhook_signature_key,
      });
      toast.success("Provider created and connection tested");
      setShowForm(false);
      setFormName("");
      setFormConfig({});
      refresh();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Failed to create provider");
    }
  }

  async function handleSetPrimary(providerId: string) {
    const token = getAccessToken();
    if (!token) return;
    try {
      await adminUpdateProvider(token, providerId, { is_primary: true });
      toast.success("Provider set as primary");
      refresh();
    } catch {
      toast.error("Failed to update provider");
    }
  }

  async function handleToggleActive(providerId: string, currentActive: boolean) {
    const token = getAccessToken();
    if (!token) return;
    try {
      await adminUpdateProvider(token, providerId, { is_active: !currentActive });
      toast.success(currentActive ? "Provider deactivated" : "Provider activated");
      refresh();
    } catch {
      toast.error("Failed to update provider");
    }
  }

  async function handleDelete(providerId: string) {
    const token = getAccessToken();
    if (!token) return;
    if (!confirm("Are you sure you want to delete this provider?")) return;
    try {
      await adminDeleteProvider(token, providerId);
      toast.success("Provider deleted");
      refresh();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Cannot delete primary provider");
    }
  }

  async function handleTest(providerId: string) {
    const token = getAccessToken();
    if (!token) return;
    setTestingId(providerId);
    try {
      const result = await adminTestProvider(token, providerId);
      if (result.success) {
        toast.success("Connection successful");
      } else {
        toast.error(`Connection failed: ${result.message}`);
      }
    } catch {
      toast.error("Connection test failed");
    } finally {
      setTestingId(null);
    }
  }

  const selectedType = PROVIDER_TYPES.find((t) => t.value === formType);

  if (loading) {
    return (
      <>
        <PageHeader
          title="Payment Providers"
          breadcrumbs={[
            { label: "Platform", href: "/platform" },
            { label: "Payment Providers" },
          ]}
        />
        <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
          <div className="grid gap-4 md:grid-cols-2">
            {[1, 2].map((i) => <Skeleton key={i} className="h-40" />)}
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="Payment Providers"
        breadcrumbs={[
          { label: "Platform", href: "/platform" },
          { label: "Payment Providers" },
        ]}
        actions={
          <Button size="sm" onClick={() => setShowForm(!showForm)}>
            <Plus className="mr-1 size-4" /> Add Provider
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {showForm && (
          <Card>
            <CardHeader>
              <CardTitle>Add Payment Provider</CardTitle>
              <CardDescription>Enter credentials for a new payment provider. Connection will be tested before saving.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-sm text-muted-foreground">Provider Type</label>
                    <select
                      className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
                      value={formType}
                      onChange={(e) => { setFormType(e.target.value); setFormConfig({}); }}
                    >
                      {PROVIDER_TYPES.map((t) => (
                        <option key={t.value} value={t.value}>{t.label}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block text-sm text-muted-foreground">Display Name</label>
                    <Input placeholder="e.g. Stripe Production" value={formName} onChange={(e) => setFormName(e.target.value)} required />
                  </div>
                </div>

                {selectedType && (
                  <div className="grid gap-3 md:grid-cols-2">
                    {selectedType.fields.map((field) => (
                      <div key={field}>
                        <label className="mb-1 block text-sm capitalize text-muted-foreground">{field.replace(/_/g, " ")}</label>
                        <Input
                          type={field.includes("secret") || field.includes("key") || field.includes("token") ? "password" : "text"}
                          placeholder={field === "mode" ? "sandbox or live/production" : field}
                          value={formConfig[field] || ""}
                          onChange={(e) => setFormConfig({ ...formConfig, [field]: e.target.value })}
                          required={field !== "mode"}
                        />
                      </div>
                    ))}
                  </div>
                )}

                <div className="flex gap-2">
                  <Button type="submit">Create & Test Connection</Button>
                  <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {providers.length === 0 && !error ? (
          <Card className="flex flex-col items-center justify-center py-16">
            <CreditCard className="size-12 text-amber-500/50" />
            <h3 className="mt-4 text-lg font-semibold">No payment providers configured</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Add Stripe, PayPal, Square, or Paddle to accept payments.
            </p>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {providers.map((p) => (
              <Card key={p.id} className={p.is_primary ? "border-green-700" : ""}>
                <CardHeader className="flex flex-row items-start justify-between pb-2">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      {p.display_name}
                      {p.is_primary && <Badge className="bg-green-900 text-green-300">Primary</Badge>}
                      {p.is_active ? (
                        <Badge className="bg-blue-900 text-blue-300">Active</Badge>
                      ) : (
                        <Badge variant="secondary">Inactive</Badge>
                      )}
                    </CardTitle>
                    <CardDescription className="capitalize">{p.provider_type}</CardDescription>
                  </div>
                </CardHeader>
                <CardContent>
                  {p.supported_methods && (
                    <div className="mb-3 flex flex-wrap gap-1">
                      {p.supported_methods.map((m) => (
                        <Badge key={m} variant="secondary" className="text-xs">{m}</Badge>
                      ))}
                    </div>
                  )}
                  <div className="flex flex-wrap gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleTest(p.id)}
                      disabled={testingId === p.id}
                    >
                      <Zap className="mr-1 size-3" />
                      {testingId === p.id ? "Testing..." : "Test"}
                    </Button>
                    {!p.is_primary && p.is_active && (
                      <Button size="sm" variant="outline" onClick={() => handleSetPrimary(p.id)}>
                        <CheckCircle className="mr-1 size-3" /> Set Primary
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleToggleActive(p.id, p.is_active)}
                    >
                      {p.is_active ? <XCircle className="mr-1 size-3" /> : <CheckCircle className="mr-1 size-3" />}
                      {p.is_active ? "Deactivate" : "Activate"}
                    </Button>
                    {!p.is_primary && (
                      <Button size="sm" variant="destructive" onClick={() => handleDelete(p.id)}>
                        <Trash2 className="mr-1 size-3" /> Delete
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
