"use client";

import { useCallback, useEffect, useState } from "react";
import { getQueueCount, triggerSync } from "@/lib/offline-queue";
import { RefreshCw, Loader2, WifiOff } from "lucide-react";
import { toast } from "sonner";

export function OfflineIndicator() {
  const [offline, setOffline] = useState(false);
  const [queueCount, setQueueCount] = useState(0);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    const goOffline = () => {
      setOffline(true);
      toast.warning("You're offline. Changes will sync when reconnected.");
    };
    const goOnline = () => {
      setOffline(false);
      toast.success("Back online");
      // Auto-sync on reconnect
      handleSync();
    };
    window.addEventListener("offline", goOffline);
    window.addEventListener("online", goOnline);
    setOffline(!navigator.onLine);
    return () => {
      window.removeEventListener("offline", goOffline);
      window.removeEventListener("online", goOnline);
    };
  }, []);

  // Poll queue count
  useEffect(() => {
    const updateCount = async () => {
      try {
        const count = await getQueueCount();
        setQueueCount(count);
      } catch {
        // IndexedDB unavailable
      }
    };
    updateCount();
    const interval = setInterval(updateCount, 5000);
    return () => clearInterval(interval);
  }, []);

  // Listen for SW sync messages
  useEffect(() => {
    if (!("serviceWorker" in navigator)) return;
    const handler = (event: MessageEvent) => {
      if (event.data?.type === "SYNC_PROGRESS" || event.data?.type === "SYNC_COMPLETE") {
        getQueueCount().then(setQueueCount).catch(() => {});
      }
    };
    navigator.serviceWorker.addEventListener("message", handler);
    return () => navigator.serviceWorker.removeEventListener("message", handler);
  }, []);

  const handleSync = useCallback(async () => {
    if (offline || syncing) return;
    setSyncing(true);
    try {
      const synced = await triggerSync();
      if (synced > 0) {
        toast.success(`Synced ${synced} pending ${synced === 1 ? "change" : "changes"}`);
      }
      const count = await getQueueCount();
      setQueueCount(count);
    } catch {
      // silent
    }
    setSyncing(false);
  }, [offline, syncing]);

  if (!offline && queueCount === 0) return null;

  return (
    <div className="fixed left-0 right-0 top-0 z-50 flex items-center justify-center gap-3 bg-amber-600 px-4 py-1.5 text-xs font-medium text-white">
      {offline && (
        <span className="flex items-center gap-1.5">
          <WifiOff className="size-3.5" />
          You&apos;re offline — changes will sync when reconnected
        </span>
      )}
      {queueCount > 0 && (
        <button
          onClick={handleSync}
          disabled={offline || syncing}
          className="flex items-center gap-1 rounded bg-white/20 px-2 py-0.5 text-[11px] hover:bg-white/30 disabled:opacity-50"
        >
          {syncing ? (
            <Loader2 className="size-3 animate-spin" />
          ) : (
            <RefreshCw className="size-3" />
          )}
          {queueCount} pending
        </button>
      )}
    </div>
  );
}
