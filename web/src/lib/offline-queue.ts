/**
 * Offline queue client — queues mutations when offline, syncs when back online.
 *
 * Uses IndexedDB directly (same store as service worker) for the queue,
 * and the Background Sync API to trigger sync when connectivity returns.
 */

const DB_NAME = "tendril-offline-queue";
const DB_VERSION = 1;
const STORE_NAME = "queue";

export interface QueuedRequest {
  id?: number;
  url: string;
  method: string;
  headers: Record<string, string>;
  body: string | null;
  timestamp: number;
  description: string; // Human-readable ("Logged sensor reading", "Completed task", etc.)
}

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = (e) => {
      const db = (e.target as IDBOpenDBRequest).result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: "id", autoIncrement: true });
        store.createIndex("timestamp", "timestamp", { unique: false });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

/** Add a request to the offline queue. */
export async function enqueue(item: Omit<QueuedRequest, "id" | "timestamp">): Promise<void> {
  const db = await openDB();
  const tx = db.transaction(STORE_NAME, "readwrite");
  const store = tx.objectStore(STORE_NAME);
  store.add({ ...item, timestamp: Date.now() });
  await new Promise<void>((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });

  // Request background sync
  if ("serviceWorker" in navigator && "sync" in (navigator.serviceWorker as unknown as { sync: unknown })) {
    const reg = await navigator.serviceWorker.ready;
    try {
      await (reg as unknown as { sync: { register: (tag: string) => Promise<void> } }).sync.register(
        "tendril-offline-sync"
      );
    } catch {
      // Background sync not available — will sync on next manual trigger
    }
  }
}

/** Get all queued items. */
export async function getQueue(): Promise<QueuedRequest[]> {
  const db = await openDB();
  const tx = db.transaction(STORE_NAME, "readonly");
  const store = tx.objectStore(STORE_NAME);
  return new Promise((resolve) => {
    const request = store.getAll();
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => resolve([]);
  });
}

/** Get count of queued items. */
export async function getQueueCount(): Promise<number> {
  const db = await openDB();
  const tx = db.transaction(STORE_NAME, "readonly");
  const store = tx.objectStore(STORE_NAME);
  return new Promise((resolve) => {
    const request = store.count();
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => resolve(0);
  });
}

/** Clear a specific item from the queue. */
export async function dequeue(id: number): Promise<void> {
  const db = await openDB();
  const tx = db.transaction(STORE_NAME, "readwrite");
  tx.objectStore(STORE_NAME).delete(id);
  await new Promise<void>((resolve) => {
    tx.oncomplete = () => resolve();
  });
}

/** Manually trigger sync via service worker message. */
export async function triggerSync(): Promise<number> {
  if (!("serviceWorker" in navigator)) return 0;
  const reg = await navigator.serviceWorker.ready;
  return new Promise((resolve) => {
    const handler = (event: MessageEvent) => {
      if (event.data?.type === "SYNC_COMPLETE") {
        navigator.serviceWorker.removeEventListener("message", handler);
        resolve(event.data.count ?? 0);
      }
    };
    navigator.serviceWorker.addEventListener("message", handler);
    reg.active?.postMessage({ type: "SYNC_OFFLINE_QUEUE" });
    // Timeout after 30s
    setTimeout(() => {
      navigator.serviceWorker.removeEventListener("message", handler);
      resolve(0);
    }, 30_000);
  });
}

/** Check if the browser is currently online. */
export function isOnline(): boolean {
  return navigator.onLine;
}

/**
 * Wrap a fetch call to automatically queue if offline.
 * Returns the response if online, or null if queued.
 */
export async function fetchWithOfflineQueue(
  url: string,
  options: RequestInit & { description?: string } = {}
): Promise<Response | null> {
  const { description = "Pending request", ...fetchOptions } = options;

  if (navigator.onLine) {
    try {
      const response = await fetch(url, fetchOptions);
      if (response.ok) return response;
      // Don't queue client errors (4xx)
      if (response.status >= 400 && response.status < 500) return response;
      // Server errors when online — don't queue, let caller handle
      return response;
    } catch {
      // Network error — queue it
    }
  }

  // Offline or network error — queue the request
  const headers: Record<string, string> = {};
  if (fetchOptions.headers) {
    const h = fetchOptions.headers;
    if (h instanceof Headers) {
      h.forEach((v, k) => { headers[k] = v; });
    } else if (Array.isArray(h)) {
      h.forEach(([k, v]) => { headers[k] = v; });
    } else {
      Object.assign(headers, h);
    }
  }

  await enqueue({
    url,
    method: fetchOptions.method || "POST",
    headers,
    body: typeof fetchOptions.body === "string" ? fetchOptions.body : null,
    description,
  });

  return null; // Indicates request was queued
}
