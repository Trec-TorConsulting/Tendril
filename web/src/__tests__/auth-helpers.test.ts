import { describe, it, expect, beforeEach } from "vitest";
import {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens,
  isAuthenticated,
} from "@/lib/auth";

describe("auth helpers", () => {
  beforeEach(() => {
    localStorage.removeItem("tendril_access_token");
    localStorage.removeItem("tendril_refresh_token");
  });

  it("returns null when no tokens stored", () => {
    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
  });

  it("stores and retrieves tokens", () => {
    setTokens("access-123", "refresh-456");
    expect(getAccessToken()).toBe("access-123");
    expect(getRefreshToken()).toBe("refresh-456");
  });

  it("clears tokens", () => {
    setTokens("access-123", "refresh-456");
    clearTokens();
    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
  });

  it("isAuthenticated returns true when token exists", () => {
    expect(isAuthenticated()).toBe(false);
    setTokens("token", "refresh");
    expect(isAuthenticated()).toBe(true);
  });
});
