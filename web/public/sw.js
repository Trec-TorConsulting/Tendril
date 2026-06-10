/* eslint-disable no-restricted-globals */
/**
 * Tendril Service Worker — Offline-first PWA support
 *
 * Caching strategies:
 * - Static assets (JS, CSS, fonts, images): Cache-first with long TTL
 * - API grow configs / grow types: Stale-while-revalidate (rarely change)
 * - API dynamic data (grows, readings): Network-first with cache fallback
 * - POST/PATCH/DELETE: Queue offline, sync when back online (Background Sync)
 */

const CACHE_VERSION = "v2";
const STATIC_CACHE = `tendril-static-${CACHE_VERSION}`;
const API_CACHE = `tendril-api-${CACHE_VERSION}`;
const OFFLINE_QUEUE_STORE = "tendril-offline-queue";

// Files to pre-cache on install
const PRECACHE_URLS = ["/dashboard", "/offline", "/manifest.json"];

// API paths that use stale-while-revalidate (config-like, rarely change)
const STALE_REVALIDATE_PATHS = [
  "/v1/reference/",
  "/v1/grow-types",
  "/v1/ai/treatments",
  "/v1/companion-plants",
];

// API paths that use network-first (dynamic data)
const NETWORK_FIRST_PATHS = [
  "/v1/grows",
  "/v1/tents",
  "/v1/buckets",
  "/v1/sensors",
  "/v1/tasks",
];

// ─── Install ────────────────────────────────────────────────────────────────────

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

// ─── Activate ───────────────────────────────────────────────────────────────────

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== STATIC_CACHE && k !== API_CACHE)
          .map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// ─── Fetch Handler ──────────────────────────────────────────────────────────────

self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET for caching (mutations handled by background sync)
  if (request.method !== "GET") return;

  // Skip WebSocket and non-http
  if (!url.protocol.startsWith("http")) return;

  // Skip cross-origin requests (e.g. api.tendrilgrow.com) — let the browser
  // handle CORS natively. Intercepting credentialed cross-origin fetches via
  // respondWith() can produce opaque responses that strip CORS headers.
  if (url.origin !== self.location.origin) return;

  // Static assets: cache-first
  if (isStaticAsset(url)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  // API: stale-while-revalidate for configs
  if (isStaleRevalidatePath(url)) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // API: network-first for dynamic data
  if (isNetworkFirstPath(url)) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Everything else API: network-first
  if (url.pathname.startsWith("/v1/") || url.pathname.startsWith("/api/")) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Navigation requests: network with offline fallback
  if (request.mode === "navigate") {
    event.respondWith(navigationHandler(request));
    return;
  }

  // Default: cache-first for same-origin static
  if (url.origin === self.location.origin) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
  }
});

// ─── Background Sync ────────────────────────────────────────────────────────────

self.addEventListener("sync", (event) => {
  if (event.tag === "tendril-offline-sync") {
    event.waitUntil(processOfflineQueue());
  }
});

self.addEventListener("periodicsync", (event) => {
  if (event.tag === "tendril-periodic-sync") {
    event.waitUntil(processOfflineQueue());
  }
});

// ─── Message Handler (manual sync trigger) ──────────────────────────────────────

self.addEventListener("message", (event) => {
  if (event.data?.type === "SYNC_OFFLINE_QUEUE") {
    processOfflineQueue().then((count) => {
      event.source?.postMessage({ type: "SYNC_COMPLETE", count });
    });
  }
  if (event.data?.type === "GET_QUEUE_COUNT") {
    getQueueCount().then((count) => {
      event.source?.postMessage({ type: "QUEUE_COUNT", count });
    });
  }
});

// ─── Caching Strategies ─────────────────────────────────────────────────────────

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response("Offline", { status: 503 });
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(API_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response(JSON.stringify({ error: "offline", cached: false }), {
      status: 503,
      headers: { "Content-Type": "application/json" },
    });
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(API_CACHE);
  const cached = await cache.match(request);

  const fetchPromise = fetch(request)
    .then((response) => {
      if (response.ok) cache.put(request, response.clone());
      return response;
    })
    .catch(() => null);

  return (
    cached ||
    (await fetchPromise) ||
    new Response(JSON.stringify({ error: "offline" }), {
      status: 503,
      headers: { "Content-Type": "application/json" },
    })
  );
}

async function navigationHandler(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    const offlinePage = await caches.match("/offline");
    if (offlinePage) return offlinePage;
    return new Response(
      "<h1>Offline</h1><p>Tendril is currently unavailable. Please check your connection.</p>",
      { headers: { "Content-Type": "text/html" } }
    );
  }
}

// ─── Helpers ────────────────────────────────────────────────────────────────────

function isStaticAsset(url) {
  const ext = url.pathname.split(".").pop()?.toLowerCase();
  return ["js", "css", "woff", "woff2", "ttf", "png", "jpg", "jpeg", "svg", "webp", "ico"].includes(ext || "");
}

function isStaleRevalidatePath(url) {
  return STALE_REVALIDATE_PATHS.some((p) => url.pathname.includes(p));
}

function isNetworkFirstPath(url) {
  return NETWORK_FIRST_PATHS.some((p) => url.pathname.includes(p));
}

// ─── IndexedDB Offline Queue ────────────────────────────────────────────────────

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(OFFLINE_QUEUE_STORE, 1);
    request.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains("queue")) {
        const store = db.createObjectStore("queue", { keyPath: "id", autoIncrement: true });
        store.createIndex("timestamp", "timestamp", { unique: false });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function processOfflineQueue() {
  const db = await openDB();
  const tx = db.transaction("queue", "readwrite");
  const store = tx.objectStore("queue");

  return new Promise((resolve) => {
    const request = store.getAll();
    request.onsuccess = async () => {
      const items = request.result;
      let synced = 0;

      for (const item of items) {
        try {
          const response = await fetch(item.url, {
            method: item.method,
            headers: item.headers,
            body: item.body,
            credentials: "include",
          });
          if (response.ok || response.status < 500) {
            const deleteTx = db.transaction("queue", "readwrite");
            deleteTx.objectStore("queue").delete(item.id);
            synced++;
          }
        } catch {
          break; // Network still down
        }
      }

      const clients = await self.clients.matchAll({ type: "window" });
      clients.forEach((client) => {
        client.postMessage({ type: "SYNC_PROGRESS", synced, total: items.length });
      });

      resolve(synced);
    };
  });
}

async function getQueueCount() {
  const db = await openDB();
  const tx = db.transaction("queue", "readonly");
  const store = tx.objectStore("queue");
  return new Promise((resolve) => {
    const request = store.count();
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => resolve(0);
  });
}
