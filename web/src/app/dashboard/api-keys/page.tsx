"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { listApiKeys, createApiKey, revokeApiKey } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn, formatCalendarDate, formatDate } from "@/lib/utils";
import {
  Plus,
  Copy,
  X,
  MoreHorizontal,
  ShieldOff,
  AlertTriangle,
  Key,
  Calendar,
  Clock,
} from "lucide-react";

interface ApiKeyItem {
  id: string;
  name: string;
  key_prefix: string;
  scopes: string;
  last_used: string | null;
  expires_at: string | null;
  revoked: boolean;
  created_at: string;
}

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<ApiKeyItem[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newKey, setNewKey] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [scopes, setScopes] = useState("read");
  const [expiresDays, setExpiresDays] = useState("");
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      setKeys(await listApiKeys(token));
    } catch {
      /* tier restricted */
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleCreate = async () => {
    const token = getAccessToken();
    if (!token || !name) return;
    setError("");
    try {
      const result = await createApiKey(
        {
          name,
          scopes,
          expires_in_days: expiresDays ? parseInt(expiresDays, 10) : undefined,
        },
        token,
      );
      setNewKey(result.key);
      setShowCreate(false);
      setName("");
      setScopes("read");
      setExpiresDays("");
      refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create");
    }
  };

  const handleRevoke = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    await revokeApiKey(id, token);
    refresh();
  };

  const copyKey = () => {
    if (newKey) {
      navigator.clipboard.writeText(newKey);
    }
  };

  return (
    <>
      <PageHeader
        title="API Keys"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "API Keys" },
        ]}
        actions={
          <Button onClick={() => setShowCreate(true)} size="sm">
            <Plus className="mr-1 h-4 w-4" />
            Generate Key
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        <p className="text-sm text-muted-foreground">
          Create API keys for external integrations. Commercial plan only.
        </p>

        {/* New key reveal */}
        {newKey && (
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="space-y-3">
              <p className="font-semibold">
                Copy your API key now — it won&apos;t be shown again!
              </p>
              <div className="flex items-center gap-2">
                <code className="flex-1 rounded bg-muted px-3 py-2 text-sm font-mono break-all">
                  {newKey}
                </code>
                <Button variant="outline" size="sm" onClick={copyKey}>
                  <Copy className="mr-1 h-4 w-4" />
                  Copy
                </Button>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setNewKey(null)}
              >
                <X className="mr-1 h-4 w-4" />
                Dismiss
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Create dialog */}
        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Generate API Key</DialogTitle>
            </DialogHeader>
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <Label htmlFor="key-name">Name</Label>
                <Input
                  id="key-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Home Assistant Integration"
                />
              </div>
              <div className="space-y-2">
                <Label>Scopes</Label>
                <Select value={scopes} onValueChange={(v) => setScopes(v ?? "")}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="read">Read only</SelectItem>
                    <SelectItem value="read,write">Read & Write</SelectItem>
                    <SelectItem value="read,write,admin">Full Access</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="key-expires">Expires in (days, blank = never)</Label>
                <Input
                  id="key-expires"
                  type="number"
                  value={expiresDays}
                  onChange={(e) => setExpiresDays(e.target.value)}
                  placeholder="e.g. 90"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreate(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreate}>Generate</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Key list */}
        {keys.length === 0 ? (
          <p className="text-muted-foreground">No API keys yet.</p>
        ) : (
          <div className="space-y-3">
            {keys.map((k) => (
              <Card key={k.id}>
                <CardContent className="flex items-center justify-between p-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Key className="h-4 w-4 text-muted-foreground" />
                      <h3 className="font-medium">{k.name}</h3>
                    </div>
                    <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                      <Badge variant="outline" className="font-mono">
                        {k.key_prefix}...
                      </Badge>
                      <Badge variant="secondary">{k.scopes}</Badge>
                      {k.expires_at && (
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          Expires: {formatCalendarDate(k.expires_at)}
                        </span>
                      )}
                      {k.last_used && (
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          Last used: {formatDate(k.last_used)}
                        </span>
                      )}
                    </div>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger render={<Button variant="ghost" size="sm" className="h-8 w-8 p-0" />}>
                      <MoreHorizontal className="h-4 w-4" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        className="text-destructive focus:text-destructive"
                        onClick={() => handleRevoke(k.id)}
                      >
                        <ShieldOff className="mr-2 h-4 w-4" />
                        Revoke
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
