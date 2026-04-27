import { describe, it, expect, beforeEach } from "vitest";
import {
  getCsrfToken,
  setCsrfToken,
  clearAuth,
  isAuthenticated,
  getAccessToken,
  clearTokens,
} from "@/lib/auth";

describe("auth helpers (cookie-based)", () => {
  beforeEach(() => {
    clearAuth();
    // Clear any document cookies in jsdom
    document.cookie = "csrf_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
  });

  it("returns null when no CSRF token", () => {
    expect(getCsrfToken()).toBeNull();
  });

  it("stores and retrieves CSRF token in memory", () => {
    setCsrfToken("csrf-abc");
    expect(getCsrfToken()).toBe("csrf-abc");
  });

  it("clearAuth resets CSRF token", () => {
    setCsrfToken("csrf-abc");
    clearAuth();
    // In-memory token is cleared; cookie check depends on jsdom
    expect(getCsrfToken()).toBeNull();
  });

  it("isAuthenticated checks for csrf_token cookie", () => {
    expect(isAuthenticated()).toBe(false);
    document.cookie = "csrf_token=test123; path=/;";
    expect(isAuthenticated()).toBe(true);
  });

  it("getAccessToken returns sentinel when authenticated", () => {
    expect(getAccessToken()).toBeNull();
    document.cookie = "csrf_token=test123; path=/;";
    expect(getAccessToken()).toBe("cookie");
  });

  it("clearTokens delegates to clearAuth", () => {
    setCsrfToken("csrf-abc");
    clearTokens();
    expect(getCsrfToken()).toBeNull();
  });
});
