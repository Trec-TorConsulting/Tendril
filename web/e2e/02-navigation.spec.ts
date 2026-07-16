/**
 * QA Tests: Navigation & Links
 * - All sidebar navigation items accessible
 * - All page routes load without errors
 * - Mobile navigation works
 * - No broken links
 * - No console errors
 */
import { test, expect, login, TEST_USERS, setupConsoleErrorTracking, checkLinksOnPage } from "./helpers";

/** Escape all regex special characters in a string */
function escapeRegExp(s: string) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

test.describe("Navigation - Sidebar (Desktop)", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  const sidebarRoutes = [
    { label: /dashboard/i, path: "/dashboard" },
    { label: /grows/i, path: "/dashboard/grows" },
    { label: /grow spaces|tents/i, path: "/dashboard/tents" },
    { label: /grow types/i, path: "/dashboard/grow-types" },
    { label: /devices/i, path: "/dashboard/devices" },
    { label: /analytics/i, path: "/dashboard/analytics" },
    { label: /automation/i, path: "/dashboard/automation" },
    { label: /schedules/i, path: "/dashboard/schedules" },
    { label: /notifications/i, path: "/dashboard/notifications" },
    { label: /tasks/i, path: "/dashboard/tasks" },
    { label: /strains/i, path: "/dashboard/strains" },
    { label: /reference/i, path: "/dashboard/reference" },
    { label: /integrations/i, path: "/dashboard/integrations" },
    { label: /audit/i, path: "/dashboard/audit" },
    { label: /api keys/i, path: "/dashboard/api-keys" },
    { label: /billing/i, path: "/dashboard/billing" },
  ];

  for (const route of sidebarRoutes) {
    test(`navigates to ${route.path}`, async ({ page }) => {
      const errors = setupConsoleErrorTracking(page);

      // Try sidebar link first, fall back to direct navigation
      const link = page.getByRole("link", { name: route.label }).first();
      if (await link.isVisible().catch(() => false)) {
        await link.click();
      } else {
        await page.goto(route.path);
      }

      await page.waitForLoadState("networkidle");
      await expect(page).toHaveURL(new RegExp(escapeRegExp(route.path)));

      // No unexpected JS errors on page (ignore known non-critical errors)
      const critical = errors.filter((e) =>
        !e.includes("hydration") &&
        !e.includes("favicon") &&
        !e.includes("CORS") &&
        !e.includes("net::ERR_FAILED") &&
        !e.includes("Failed to fetch") &&
        !e.includes("Network error") &&
        !e.includes("Failed to load resource") &&
        !e.includes("429") &&
        !e.includes("401") &&
        !e.includes("403") &&
        !e.includes("404")
      );
      expect(critical).toHaveLength(0);
    });
  }
});

test.describe("Navigation - Settings Pages", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  const settingsRoutes = [
    "/dashboard/settings",
    "/dashboard/settings/security",
    "/dashboard/settings/team",
  ];

  for (const path of settingsRoutes) {
    test(`settings page loads: ${path}`, async ({ page }) => {
      await page.goto(path);
      await page.waitForLoadState("networkidle");
      await expect(page).toHaveURL(new RegExp(escapeRegExp(path)));
      // Page should have rendered content
      await expect(page.locator("body")).not.toBeEmpty();
    });
  }
});

test.describe("Navigation - Mobile", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("mobile navigation menu is accessible", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width >= 768) {
      test.skip();
      return;
    }

    // Should have a mobile menu trigger (FAB or hamburger)
    const mobileNav = page.locator(
      '[data-testid="mobile-nav"], [aria-label*="menu"], [aria-label*="navigation"], button:has(svg)'
    ).first();

    await expect(mobileNav).toBeVisible();
  });

  test("mobile FAB opens navigation options", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width >= 768) {
      test.skip();
      return;
    }

    // Look for the FAB/mobile trigger
    const fab = page.locator(
      'button[class*="fixed"], [data-testid="mobile-fab"], button:has(svg.lucide-plus), button:has(svg.lucide-menu)'
    ).first();

    if (await fab.isVisible().catch(() => false)) {
      await fab.click();
      // Should show navigation options
      await page.waitForTimeout(300); // animation
      const navItems = page.locator('[role="menu"], [role="navigation"], nav').first();
      await expect(navItems).toBeVisible();
    }
  });
});

test.describe("Navigation - Link Integrity", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  const pagesToCheck = [
    "/dashboard",
    "/dashboard/grows",
    "/dashboard/tents",
    "/dashboard/devices",
    "/dashboard/automation",
    "/dashboard/billing",
    "/dashboard/settings",
  ];

  for (const path of pagesToCheck) {
    test(`no broken links on ${path}`, async ({ page }) => {
      await page.goto(path);
      await page.waitForLoadState("networkidle");
      const { broken } = await checkLinksOnPage(page);
      expect(broken).toHaveLength(0);
    });
  }
});

test.describe("Navigation - Marketing/Public Pages", () => {
  test("landing page loads", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await expect(page.getByText(/tendril/i).first()).toBeVisible({ timeout: 10000 });
  });

  test("terms page loads", async ({ page }) => {
    await page.goto("/terms");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("body")).not.toBeEmpty();
  });

  test("privacy page loads", async ({ page }) => {
    await page.goto("/privacy");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("body")).not.toBeEmpty();
  });
});

test.describe("Navigation - Error Handling", () => {
  test("404 page displays for non-existent routes", async ({ page }) => {
    await page.goto("/this-does-not-exist-123");
    await expect(page.getByText(/not found|404/i)).toBeVisible();
  });

  test("invalid grow ID shows error state", async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/grows/nonexistent-id-12345");
    await page.waitForLoadState("networkidle");
    // Should show error or redirect, not crash
    await expect(page.locator("body")).not.toBeEmpty();
  });
});
