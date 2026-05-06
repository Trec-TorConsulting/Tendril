"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listInvoices,
  cancelSubscription,
  requestAccountDeletion,
  cancelAccountDeletion,
  getAccountDeletionStatus,
  type InvoiceEntry,
  type CancelResponse,
  type DeletionStatus,
} from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { FileText, Download, AlertTriangle, Trash2, X } from "lucide-react";
import { toast } from "sonner";

export default function AccountPage() {
  const [invoices, setInvoices] = useState<InvoiceEntry[]>([]);
  const [deletionStatus, setDeletionStatus] = useState<DeletionStatus | null>(null);
  const [loading, setLoading] = useState(true);

  // Cancellation flow state
  const [showCancelFlow, setShowCancelFlow] = useState(false);
  const [cancelReason, setCancelReason] = useState("");
  const [cancelFeedback, setCancelFeedback] = useState("");
  const [cancelResponse, setCancelResponse] = useState<CancelResponse | null>(null);

  // Deletion flow state
  const [showDeleteFlow, setShowDeleteFlow] = useState(false);
  const [deleteEmail, setDeleteEmail] = useState("");

  useEffect(() => {
    refresh();
  }, []);

  async function refresh() {
    const token = getAccessToken();
    if (!token) return;
    setLoading(true);
    try {
      const [inv, del] = await Promise.all([
        listInvoices(token, 12),
        getAccountDeletionStatus(token),
      ]);
      setInvoices(inv);
      setDeletionStatus(del);
    } catch {
      // Non-critical
    } finally {
      setLoading(false);
    }
  }

  async function handleCancel(confirmed: boolean) {
    const token = getAccessToken();
    if (!token) return;
    try {
      const data = confirmed
        ? { reason: "__confirmed_cancel__" }
        : { reason: cancelReason || undefined, feedback: cancelFeedback || undefined };
      const result = await cancelSubscription(token, data);
      setCancelResponse(result);
      if (result.status === "cancelled") {
        toast.success("Subscription cancelled");
        setShowCancelFlow(false);
      }
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Failed to cancel");
    }
  }

  async function handleDelete() {
    const token = getAccessToken();
    if (!token || !deleteEmail) return;
    try {
      const result = await requestAccountDeletion(token, deleteEmail);
      toast.success(result.message);
      setShowDeleteFlow(false);
      refresh();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Failed to schedule deletion");
    }
  }

  async function handleCancelDeletion() {
    const token = getAccessToken();
    if (!token) return;
    try {
      const result = await cancelAccountDeletion(token);
      toast.success(result.message);
      refresh();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Failed to cancel deletion");
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Account" description="Invoices, subscription management, and data controls" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Account" description="Invoices, subscription management, and data controls" />

      {/* Deletion Warning Banner */}
      {deletionStatus?.deletion_scheduled && (
        <div className="flex items-center justify-between rounded-lg border border-red-800 bg-red-950/50 px-4 py-3">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-red-400" />
            <div>
              <p className="text-sm font-medium text-red-300">Account deletion scheduled</p>
              <p className="text-xs text-red-400">
                Your data will be permanently deleted on {new Date(deletionStatus.deletion_date!).toLocaleDateString()}.
                {deletionStatus.days_remaining} days remaining.
              </p>
            </div>
          </div>
          <Button size="sm" variant="outline" onClick={handleCancelDeletion}>
            Cancel Deletion
          </Button>
        </div>
      )}

      {/* Invoice History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" /> Invoice History
          </CardTitle>
          <CardDescription>Past payments and receipts for your subscription</CardDescription>
        </CardHeader>
        <CardContent>
          {invoices.length === 0 ? (
            <p className="text-sm text-neutral-500">No invoices yet. Invoices appear after your first payment.</p>
          ) : (
            <div className="space-y-2">
              {invoices.map((inv) => (
                <div key={inv.id} className="flex items-center justify-between rounded-md border border-neutral-800 px-4 py-3">
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-neutral-400">{inv.date}</span>
                    <span className="text-sm font-medium text-white">{inv.amount}</span>
                    <Badge className={inv.status === "paid" ? "bg-green-900 text-green-300" : "bg-neutral-800 text-neutral-400"}>
                      {inv.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    {inv.pdf_url && (
                      <a href={inv.pdf_url} target="_blank" rel="noopener noreferrer" className="text-neutral-400 hover:text-white">
                        <Download className="h-4 w-4" />
                      </a>
                    )}
                    {inv.hosted_url && (
                      <a href={inv.hosted_url} target="_blank" rel="noopener noreferrer" className="text-xs text-green-500 hover:text-green-400">
                        View
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Cancel Subscription */}
      <Card>
        <CardHeader>
          <CardTitle>Cancel Subscription</CardTitle>
          <CardDescription>Cancel your paid subscription. Access continues until the end of the billing period.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!showCancelFlow ? (
            <Button variant="outline" onClick={() => setShowCancelFlow(true)}>
              Cancel Subscription
            </Button>
          ) : cancelResponse?.status === "retention_offered" ? (
            <div className="space-y-4">
              <div className="rounded-lg border border-green-800 bg-green-950/30 p-4">
                <p className="text-sm font-medium text-green-300 mb-1">We&apos;d hate to see you go!</p>
                <p className="text-sm text-neutral-300">
                  How about <strong className="text-green-400">{cancelResponse.retention_offer?.discount}</strong>?
                </p>
                <p className="text-xs text-neutral-500 mt-1">Code: {cancelResponse.retention_offer?.offer_code}</p>
              </div>
              <div className="flex gap-3">
                <Button onClick={() => setShowCancelFlow(false)}>
                  Keep My Subscription
                </Button>
                <Button variant="destructive" onClick={() => handleCancel(true)}>
                  Cancel Anyway
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="space-y-3">
                <label className="text-sm text-neutral-400">Why are you leaving?</label>
                <select
                  className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white"
                  value={cancelReason}
                  onChange={(e) => setCancelReason(e.target.value)}
                >
                  <option value="">Select a reason...</option>
                  <option value="too_expensive">Too expensive</option>
                  <option value="not_using">Not using it enough</option>
                  <option value="missing_features">Missing features I need</option>
                  <option value="switching">Switching to another product</option>
                  <option value="other">Other</option>
                </select>
                <Input
                  placeholder="Any additional feedback? (optional)"
                  value={cancelFeedback}
                  onChange={(e) => setCancelFeedback(e.target.value)}
                />
              </div>
              <div className="flex gap-3">
                <Button variant="destructive" onClick={() => handleCancel(false)}>
                  Continue with Cancellation
                </Button>
                <Button variant="outline" onClick={() => setShowCancelFlow(false)}>
                  <X className="h-4 w-4 mr-1" /> Never Mind
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Account Deletion (Danger Zone) */}
      <Card className="border-red-900/50">
        <CardHeader>
          <CardTitle className="text-red-400 flex items-center gap-2">
            <Trash2 className="h-5 w-5" /> Delete Account
          </CardTitle>
          <CardDescription>
            Permanently delete your account and all associated data. This action cannot be undone after the 30-day retention period.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!showDeleteFlow ? (
            <Button variant="destructive" onClick={() => setShowDeleteFlow(true)} disabled={deletionStatus?.deletion_scheduled || false}>
              {deletionStatus?.deletion_scheduled ? "Deletion Already Scheduled" : "Delete My Account"}
            </Button>
          ) : (
            <div className="space-y-4">
              <div className="rounded-lg border border-red-800 bg-red-950/30 p-4">
                <p className="text-sm text-red-300 mb-2">This will permanently delete:</p>
                <ul className="text-xs text-neutral-400 space-y-1 list-disc list-inside">
                  <li>All grow cycles, sensor data, and journal entries</li>
                  <li>All photos and uploaded files</li>
                  <li>All expense and ROI tracking data</li>
                  <li>All automations and notification settings</li>
                  <li>Your account credentials and team memberships</li>
                </ul>
                <p className="text-xs text-neutral-500 mt-3">
                  Data will be retained for 30 days (in case you change your mind), then permanently purged.
                </p>
              </div>
              <div className="space-y-2">
                <label className="text-sm text-neutral-400">Type your email address to confirm:</label>
                <Input
                  type="email"
                  placeholder="your@email.com"
                  value={deleteEmail}
                  onChange={(e) => setDeleteEmail(e.target.value)}
                />
              </div>
              <div className="flex gap-3">
                <Button variant="destructive" onClick={handleDelete} disabled={!deleteEmail}>
                  Permanently Delete Account
                </Button>
                <Button variant="outline" onClick={() => setShowDeleteFlow(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
