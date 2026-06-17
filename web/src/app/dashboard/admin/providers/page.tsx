"use client";

import { useEffect, useState } from "react";
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
import { CreditCard, Plus, Trash2, CheckCircle, XCircle, Zap } from "lucide-react";
import { toast } from "sonner";
import { useApiSWR } from "@/lib/swr";

const PROVIDER_TYPES = [
  { value: "stripe", label: "Stripe", fields: ["secret_key", "publishable_key", "webhook_secret"] },
  { value: "paypal", label: "PayPal", fields: ["client_id", "client_secret", "mode", "webhook_id"] },
  { value: "square", label: "Square", fields: ["access_token", "mode", "location_id", "webhook_signature_key"] },
  { value: "paddle", label: "Paddle", fields: ["api_key", "mode", "webhook_secret"] },
];

export default function AdminProvidersPage() {
  const [providers, setProviders] = useState<PaymentProviderSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [error, setError] = useState("");

  // Form state
  const [formType, setFormType] = useState("stripe");
  const [formName, setFormName] = useState("");
  const [formConfig, setFormConfig] = useState<Record<string, string>>({});

  const { data, isLoading, error: loadError, mutate } = useApiSWR(
    ["dashboard", "admin", "providers"],
    (token) => adminListProviders(token),
  );

  useEffect(() => {
    setLoading(isLoading);
  }, [isLoading]);

  useEffect(() => {
    if (data) {
      setProviders(data);
      setError("");
    }
  }, [data]);

  useEffect(() => {
    if (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Access denied — platform admin required");
    }
  }, [loadError]);

  const refresh = mutate;

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

  if (error) {
    return (
      <div className="space-y-4">
        <PageHeader title="Payment Providers" description="Configure payment provider credentials" />
        <div className="rounded-md bg-red-900/50 p-4 text-red-300">{error}</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Payment Providers" description="Configure payment provider credentials" />
        <div className="grid gap-4 md:grid-cols-2">
          {[1, 2].map((i) => <Skeleton key={i} className="h-40" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Payment Providers" description="Configure payment provider credentials and manage active integrations" />

      {/* Add Provider */}
      <div className="flex justify-end">
        <Button onClick={() => setShowForm(!showForm)}>
          <Plus className="h-4 w-4 mr-1" /> Add Provider
        </Button>
      </div>

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
                  <label className="text-sm text-neutral-400 mb-1 block">Provider Type</label>
                  <select
                    className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white"
                    value={formType}
                    onChange={(e) => { setFormType(e.target.value); setFormConfig({}); }}
                  >
                    {PROVIDER_TYPES.map((t) => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm text-neutral-400 mb-1 block">Display Name</label>
                  <Input placeholder="e.g. Stripe Production" value={formName} onChange={(e) => setFormName(e.target.value)} required />
                </div>
              </div>

              {selectedType && (
                <div className="grid gap-3 md:grid-cols-2">
                  {selectedType.fields.map((field) => (
                    <div key={field}>
                      <label className="text-sm text-neutral-400 mb-1 block">{field.replace(/_/g, " ")}</label>
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

      {/* Provider List */}
      {providers.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12 text-neutral-500">
            <CreditCard className="h-12 w-12 mb-4 opacity-50" />
            <p>No payment providers configured</p>
            <p className="text-sm mt-1">Add Stripe, PayPal, Square, or Paddle to accept payments</p>
          </CardContent>
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
                      <Badge className="bg-neutral-800 text-neutral-400">Inactive</Badge>
                    )}
                  </CardTitle>
                  <CardDescription className="capitalize">{p.provider_type}</CardDescription>
                </div>
              </CardHeader>
              <CardContent>
                {p.supported_methods && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {p.supported_methods.map((m) => (
                      <span key={m} className="rounded bg-neutral-800 px-2 py-0.5 text-xs text-neutral-300">{m}</span>
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
                    <Zap className="h-3 w-3 mr-1" />
                    {testingId === p.id ? "Testing..." : "Test"}
                  </Button>
                  {!p.is_primary && p.is_active && (
                    <Button size="sm" variant="outline" onClick={() => handleSetPrimary(p.id)}>
                      <CheckCircle className="h-3 w-3 mr-1" /> Set Primary
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleToggleActive(p.id, p.is_active)}
                  >
                    {p.is_active ? <XCircle className="h-3 w-3 mr-1" /> : <CheckCircle className="h-3 w-3 mr-1" />}
                    {p.is_active ? "Deactivate" : "Activate"}
                  </Button>
                  {!p.is_primary && (
                    <Button size="sm" variant="destructive" onClick={() => handleDelete(p.id)}>
                      <Trash2 className="h-3 w-3 mr-1" /> Delete
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
