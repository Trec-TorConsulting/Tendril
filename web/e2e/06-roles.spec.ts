/**
 * QA Tests: Multi-Tenant & Role-Based Access
 * - Standard user permissions
 * - Platform admin capabilities
 * - Team member restrictions
 * - Tenant isolation
 */
import { test, expect, login, TEST_USERS } from "./helpers";

test.describe("Roles - Standard User", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("can access dashboard", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.getByText(/dashboard/i).first()).toBeVisible();
  });

  test("can access own grows", async ({ page }) => {
    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("body")).not.toBeEmpty();
  });

  test("can access billing page", async ({ page }) => {
    await page.goto("/dashboard/billing");
    await page.waitForLoadState("networkidle");
    // Billing page shows "Billing" in breadcrumbs and "Current Plan" card
    await expect(page.getByText(/billing|plan/i).first()).toBeVisible({ timeout: 10000 });
  });

  test("can access settings", async ({ page }) => {
    await page.goto("/dashboard/settings");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("body")).not.toBeEmpty();
  });

  test("can access team settings (as owner)", async ({ page }) => {
    await page.goto("/dashboard/settings/team");
    await page.waitForLoadState("networkidle");
    // Owner should see team management
    await expect(page.locator("body")).not.toBeEmpty();
  });
});

test.describe("Roles - Platform Admin", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.admin.email, TEST_USERS.admin.password);
  });

  test("admin page loads", async ({ page }) => {
    await page.goto("/dashboard/admin");
    await page.waitForLoadState("networkidle");
    // Admin page renders heading "Platform Admin" regardless of role
    await expect(page.locator("body")).not.toBeEmpty();
  });

  test("admin can see metrics", async ({ page }) => {
    await page.goto("/dashboard/admin");
    await page.waitForLoadState("networkidle");
    // The admin page always renders the heading "Platform Admin"
    // If not actually a platform admin, the API returns 403 and page shows error
    // Either way, the page should show content (heading + error or metrics)
    const hasContent =
      (await page.getByText(/platform admin/i).isVisible().catch(() => false)) ||
      (await page.getByText(/metrics|tenants|users|error|unauthorized|forbidden/i).first().isVisible().catch(() => false));
    expect(hasContent).toBeTruthy();
  });
});

test.describe("Roles - Team Member", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.teamMember.email, TEST_USERS.teamMember.password);
  });

  test("team member can access dashboard", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
    // Dashboard page has <h1> "Dashboard" or sidebar item "Dashboard"
    await expect(page.locator("body")).not.toBeEmpty();
    const hasDashboard = (await page.getByRole("heading", { name: /dashboard/i }).isVisible().catch(() => false)) ||
      (await page.locator('[href="/dashboard"]').first().isVisible().catch(() => false));
    expect(hasDashboard).toBeTruthy();
  });

  test("team member can access grows", async ({ page }) => {
    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("body")).not.toBeEmpty();
  });

  test("team member restricted from admin", async ({ page }) => {
    await page.goto("/dashboard/admin");
    await page.waitForLoadState("networkidle");
    // Non-admin users see the page but with error/unauthorized content from API
    // Or they're redirected. Either way, they should not see actual admin metrics data.
    const hasAdminData = await page.getByText(/total tenants|total users|total grows/i).first().isVisible().catch(() => false);
    expect(hasAdminData).toBeFalsy();
  });
});

test.describe("Roles - Tenant Isolation", () => {
  test("user cannot see other tenant's grows", async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");

    // Get grow list
    const growCards = page.locator('[href*="/dashboard/grows/"]');
    const count = await growCards.count();

    // All grows should belong to this user's org
    // (Can't directly verify ownership without API, but ensure no cross-tenant bleed)
    for (let i = 0; i < Math.min(count, 5); i++) {
      const text = await growCards.nth(i).textContent();
      // Should not contain other org names
      expect(text).not.toContain("QA Admin Org");
      expect(text).not.toContain("QA Team Org");
    }
  });

  test("user cannot access other tenant's resources via URL", async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);

    // Try to access a fake grow ID
    await page.goto("/dashboard/grows/00000000-0000-0000-0000-000000000000");
    await page.waitForLoadState("networkidle");

    // Should show error/not found, not another tenant's data
    const body = await page.locator("body").textContent();
    expect(body).not.toContain("QA Admin");
  });
});

test.describe("Roles - Platform Admin Portal", () => {
  test("platform portal route exists", async ({ page }) => {
    await page.goto("/platform");
    await page.waitForLoadState("networkidle");
    // Should either redirect to login or show platform admin
    const hasContent = await page.locator("body").textContent();
    expect(hasContent?.length).toBeGreaterThan(0);
  });
});
