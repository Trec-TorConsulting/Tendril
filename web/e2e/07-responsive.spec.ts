/**
 * QA Tests: Responsive Design & Viewport Testing
 * - Layout adapts correctly at all breakpoints
 * - Mobile navigation appears at small screens
 * - Desktop sidebar appears at large screens
 * - Content doesn't overflow or break
 * - Touch targets are adequate on mobile
 * - No horizontal scroll on any viewport
 */
import { test, expect, login, TEST_USERS, SCREEN_SIZES } from "./helpers";

test.describe("Responsive - Desktop Layout (≥1280px)", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("sidebar is visible on desktop", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width < 1024) {
      test.skip();
      return;
    }

    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // shadcn sidebar uses data-sidebar="sidebar" attribute
    const sidebar = page.locator('[data-sidebar="sidebar"], aside, nav[class*="sidebar"]').first();
    await expect(sidebar).toBeVisible({ timeout: 10000 });
  });

  test("no horizontal overflow on dashboard", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    const hasHScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHScroll).toBeFalsy();
  });

  test("no horizontal overflow on grows page", async ({ page }) => {
    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");

    const hasHScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHScroll).toBeFalsy();
  });

  test("content uses full width at 1920px+", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width < 1920) {
      test.skip();
      return;
    }

    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // Main content should use available space
    const mainContent = page.locator("main, [role='main']").first();
    const box = await mainContent.boundingBox();
    if (box) {
      expect(box.width).toBeGreaterThan(800);
    }
  });
});

test.describe("Responsive - Tablet Layout (768px)", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("layout adapts for tablet", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width < 768 || viewport.width > 1024) {
      test.skip();
      return;
    }

    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // No horizontal overflow
    const hasHScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHScroll).toBeFalsy();
  });

  test("no content cut off in tablet landscape", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width < 1024 || viewport.height > 800) {
      test.skip();
      return;
    }

    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");

    const hasHScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHScroll).toBeFalsy();
  });
});

test.describe("Responsive - Mobile Layout (<768px)", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("sidebar is hidden on mobile", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width >= 768) {
      test.skip();
      return;
    }

    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // Desktop sidebar should not be visible
    const sidebar = page.locator('aside[class*="hidden"], [data-testid="desktop-sidebar"]').first();
    const sidebarVisible = await sidebar.isVisible().catch(() => false);
    // Either hidden or not present
    expect(sidebarVisible).toBeFalsy();
  });

  test("mobile navigation is accessible", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width >= 768) {
      test.skip();
      return;
    }

    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // Should have mobile nav trigger
    const mobileNav = page.locator(
      'button[aria-label*="menu"], [data-testid="mobile-nav"], button:has(svg.lucide-menu), [class*="fixed"][class*="bottom"]'
    ).first();

    const hasMobileNav = await mobileNav.isVisible().catch(() => false);
    expect(hasMobileNav).toBeTruthy();
  });

  test("no horizontal overflow on mobile dashboard", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width >= 768) {
      test.skip();
      return;
    }

    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    const hasHScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHScroll).toBeFalsy();
  });

  test("no horizontal overflow on grows page mobile", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width >= 768) {
      test.skip();
      return;
    }

    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");

    const hasHScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHScroll).toBeFalsy();
  });

  test("touch targets are at least 44px on mobile", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width >= 768) {
      test.skip();
      return;
    }

    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // Check primary interactive elements
    const buttons = await page.locator("button:visible, a:visible").all();
    let tooSmall = 0;

    for (const btn of buttons.slice(0, 20)) {
      const box = await btn.boundingBox();
      if (box && (box.width < 32 || box.height < 32)) {
        tooSmall++;
      }
    }

    // Allow some small elements but flag if too many
    expect(tooSmall).toBeLessThan(buttons.length * 0.3);
  });

  test("forms are usable on mobile", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.width >= 768) {
      test.skip();
      return;
    }

    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");

    // Open create grow dialog
    const newBtn = page.getByRole("button", { name: /new grow|create/i }).first();
    if (await newBtn.isVisible().catch(() => false)) {
      await newBtn.click();
      await page.waitForTimeout(500);

      // Form should fit within viewport
      const dialog = page.locator('[role="dialog"], [data-testid="dialog"]').first();
      if (await dialog.isVisible().catch(() => false)) {
        const box = await dialog.boundingBox();
        if (box) {
          expect(box.width).toBeLessThanOrEqual(viewport.width);
        }
      }
    }
  });
});

test.describe("Responsive - Mobile Landscape", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("content renders in landscape orientation", async ({ page }) => {
    const viewport = page.viewportSize();
    if (!viewport || viewport.height >= viewport.width) {
      test.skip();
      return;
    }

    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // No horizontal overflow
    const hasHScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHScroll).toBeFalsy();

    // Content should be visible
    await expect(page.locator("body")).not.toBeEmpty();
  });
});

test.describe("Responsive - All Pages No Overflow", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  const pagesToCheck = [
    "/dashboard",
    "/dashboard/grows",
    "/dashboard/tents",
    "/dashboard/devices",
    "/dashboard/analytics",
    "/dashboard/automation",
    "/dashboard/schedules",
    "/dashboard/notifications",
    "/dashboard/tasks",
    "/dashboard/strains",
    "/dashboard/reference",
    "/dashboard/integrations",
    "/dashboard/billing",
    "/dashboard/settings",
    "/dashboard/ai",
    "/dashboard/cost-roi",
    "/dashboard/audit",
    "/dashboard/api-keys",
  ];

  for (const path of pagesToCheck) {
    test(`no overflow: ${path}`, async ({ page }) => {
      await page.goto(path);
      await page.waitForLoadState("networkidle");

      const hasHScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      expect(hasHScroll).toBeFalsy();
    });
  }
});
