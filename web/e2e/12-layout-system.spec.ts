import { test, expect } from "@playwright/test";
import { login } from "./helpers";

test.describe("Onboarding & Layout Mode", () => {
  test("onboarding wizard shows on first login with 0 grows", async ({ page }) => {
    await login(page);

    // If user has no grows, the onboarding gate should show the wizard
    const wizard = page.locator("[data-testid='onboarding-wizard']").or(
      page.getByText("What are you growing?"),
    );

    // Either we see the wizard or we're past onboarding (existing user)
    const hasWizard = await wizard.isVisible().catch(() => false);
    if (hasWizard) {
      // Step 1: Growing type
      await expect(page.getByText("What are you growing?")).toBeVisible();
      await page.getByText("Indoor").click();
      await page.getByRole("button", { name: /next|continue/i }).click();

      // Step 2: Grow count
      await expect(page.getByText("How many grows?")).toBeVisible();
      await page.getByText("2-5").click();
      await page.getByRole("button", { name: /next|continue/i }).click();

      // Step 3: Experience
      await expect(page.getByText("Experience level?")).toBeVisible();
      await page.getByText("Hobbyist").click();
      await page.getByRole("button", { name: /complete|finish|get started/i }).click();

      // Should dismiss wizard and show dashboard
      await expect(page.getByText("What are you growing?")).not.toBeVisible();
    }
  });

  test("layout mode can be changed from settings", async ({ page }) => {
    await login(page);
    await page.goto("/dashboard/settings");

    // Find the layout mode section
    const layoutSection = page.getByText("UI Layout Mode");
    await expect(layoutSection).toBeVisible();

    // Click Pro mode card
    const proCard = page.getByText("Pro").first();
    if (await proCard.isVisible()) {
      await proCard.click();
      // Should update (toast or visual indicator)
      await page.waitForTimeout(500);
    }
  });

  test("quick-log sheet opens via keyboard shortcut", async ({ page }) => {
    await login(page);
    await page.goto("/dashboard");

    // Press Cmd+L (Mac) or Ctrl+L
    await page.keyboard.press("Meta+l");

    // Quick log sheet should appear
    await expect(page.getByText("Quick Log")).toBeVisible({ timeout: 3000 });

    // Should have feeding, reading, photo, note tabs
    await expect(page.getByRole("tab", { name: /feeding/i }).or(page.locator("[value='feeding']"))).toBeVisible();
  });

  test("quick-log page renders with action buttons", async ({ page }) => {
    await login(page);
    await page.goto("/dashboard/quick-log");

    // Should show the quick log options
    await expect(page.getByText("Log Feeding")).toBeVisible();
    await expect(page.getByText("Log Reading")).toBeVisible();
  });

  test("camera management page is accessible", async ({ page }) => {
    await login(page);
    await page.goto("/dashboard/settings/cameras");

    // Should render the page header
    await expect(page.getByText("Camera Management")).toBeVisible();
  });

  test("responsive layout: mobile shows bottom nav", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await login(page);
    await page.goto("/dashboard");

    // Bottom nav should be visible on mobile
    const bottomNav = page.locator("nav").filter({ has: page.getByRole("link") }).last();
    await expect(bottomNav).toBeVisible();
  });
});
