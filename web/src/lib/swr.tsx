"use client";

/**
 * Shared SWR foundation for the dashboard.
 *
 * Goals:
 *   - Make data-fetching pages cache-aware (refocus revalidation, dedupe,
 *     mutation hooks) without changing the existing `apiFetch`-based API
 *     client in `@/lib/api`.
 *   - Key every request on the user's access token so cache is automatically
 *     evicted on sign-out.
 *
 * Usage:
 *   const { data, error, isLoading, mutate } = useApiSWR(
 *     ['my-tickets'],
 *     (token) => listMyTickets(token),
 *   );
 *
 * Cache keys must be JSON-serialisable. Pass an array; the token is folded
 * into the cache key internally so callers never have to repeat it.
 */

import { ReactNode, useCallback } from "react";
import useSWR, { SWRConfig, SWRConfiguration, useSWRConfig } from "swr";

import { getAccessToken } from "@/lib/auth";

/**
 * Default SWR config for the dashboard.
 *
 * Conservative defaults that match what hand-rolled `useEffect` fetches
 * have been doing (single load, no auto-revalidation surprises) while
 * still giving us focus-revalidation and dedupe-by-key for free.
 */
const defaultSWRConfig: SWRConfiguration = {
  // Revalidate on tab/window focus — cheap freshness for dashboards.
  revalidateOnFocus: true,
  // Don't auto-revalidate on network reconnect (avoids surprise refetches
  // on flaky mobile connections); manual `mutate()` is still available.
  revalidateOnReconnect: false,
  // 5 second dedupe — guards against double-renders refetching the same key.
  dedupingInterval: 5_000,
  // No automatic retries; the page can decide whether to surface an error.
  shouldRetryOnError: false,
};

/**
 * Wrap a subtree with the shared SWR config. Mounted by `dashboard/layout`.
 */
export function AppSWRProvider({ children }: { children: ReactNode }) {
  return <SWRConfig value={defaultSWRConfig}>{children}</SWRConfig>;
}

/**
 * Fetcher signature: receives the current access token and returns a promise.
 * Returning `undefined` (e.g. when token is absent) suspends the request.
 */
export type ApiFetcher<T> = (token: string) => Promise<T>;

/**
 * Token-aware SWR hook. The current access token is read on every render
 * and folded into the cache key so requests for different users never
 * collide and sign-out evicts everything for the old user automatically.
 *
 * When no token is available the hook returns `{ data: undefined, isLoading: false }`
 * and skips the fetch — mirrors the `if (!token) return;` guard pages
 * have been writing by hand.
 */
export function useApiSWR<T>(
  key: readonly unknown[] | null,
  fetcher: ApiFetcher<T>,
  config?: SWRConfiguration<T>,
) {
  const token = getAccessToken();
  const cacheKey = key && token ? ([...key, token] as const) : null;

  return useSWR<T>(
    cacheKey,
    cacheKey ? () => fetcher(token as string) : null,
    config,
  );
}

/**
 * Cache-evict helper for sign-out flows: clears every entry whose key
 * includes the (now-stale) access token.
 */
export function useEvictCache() {
  const { cache, mutate } = useSWRConfig();
  return useCallback(() => {
    // Iterating the cache map is the SWR-blessed way to clear it.
    for (const key of cache.keys()) {
      mutate(key, undefined, { revalidate: false });
    }
  }, [cache, mutate]);
}
