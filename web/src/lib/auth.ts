/**
 * Auth tokens are now stored in httpOnly cookies (set by the server).
 * JavaScript cannot read them — this is intentional (XSS protection).
 * The browser sends them automatically with `credentials: 'include'`.
 *
 * We still track the CSRF token in memory for mutation requests.
 */

let _csrfToken: string | null = null;

export function getCsrfToken(): string | null {
  if (_csrfToken) return _csrfToken;
  if (typeof document === "undefined") return null;
  // Read from cookie (not httpOnly, so JS can access it)
  const match = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

export function setCsrfToken(token: string) {
  _csrfToken = token;
}

export function clearAuth() {
  _csrfToken = null;
}

export function isAuthenticated(): boolean {
  if (typeof document === "undefined") return false;
  // Check if the csrf_token cookie exists (set alongside auth cookies)
  return document.cookie.includes("csrf_token=");
}

// ── Legacy compatibility shims ──────────────────────────────────
// These functions were used when tokens lived in localStorage.
// Now tokens are in httpOnly cookies (sent automatically by the browser).
// Callers that pass `token` to apiFetch will still work — the API client
// uses `credentials: 'include'` so the cookie takes precedence.

/** @deprecated Tokens are in httpOnly cookies. Returns "cookie" as a sentinel. */
export function getAccessToken(): string | null {
  return isAuthenticated() ? "cookie" : null;
}

/** @deprecated Refresh tokens are in httpOnly cookies. */
export function getRefreshToken(): string | null {
  return isAuthenticated() ? "cookie" : null;
}

/** @deprecated Tokens are set by the server via Set-Cookie. This is a no-op. */
export function setTokens(_access: string, _refresh: string) {
  // No-op: tokens are now set as httpOnly cookies by the server.
  // CSRF token is captured automatically by the API client.
}

/** @deprecated Use clearAuth() instead. */
export function clearTokens() {
  clearAuth();
}
