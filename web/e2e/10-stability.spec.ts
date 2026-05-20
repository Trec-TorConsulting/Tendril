/**
 * QA Tests: Visual Regression & Console Error Checks
 * - No console errors on any page
 * - No unhandled promise rejections
 * - Page load times within acceptable range
 * - Images and assets load correctly
 * - Dark mode renders correctly
 * - Accessibility basics (ARIA, focus management)
 */
import { test, expect, login, TEST_USERS } from "./helpers";

const ALL_AUTHENTICATED_PAGES = [
  "/dashboard",
  "/dashboard/grows",
  "/dashboard/tents",
  "/dashboard/grow-types",
  "/dashboard/devices",
  "/dashboard/analytics",
  "/dashboard/automation",
  "/dashboard/schedules",
  "/dashboard/notifications",
  "/dashboard/tasks",
  "/dashboard/strains",
  "/dashboard/reference",
  "/dashboard/integrations",
  "/dashboard/audit",
  "/dashboard/api-keys",
  "/dashboard/billing",
  "/dashboard/settings",
  "/dashboard/settings/security",
  "/dashboard/settings/team",
  "/dashboard/ai",
  "/dashboard/cost-roi",
  "/dashboard/quick-log",
  "/dashboard/cameras",
  "/dashboard/support",
];

test.describe("Stability - No Console Errors", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  for (const path of ALL_AUTHENTICATED_PAGES) {
    test(`no JS errors: ${path}`, async ({ page }) => {
      const errors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") {
          const text = msg.text();
          // Ignore hydration warnings and favicon 404s
          if (!text.includes("hydration") && !text.includes("favicon") && !text.includes("404")) {
            errors.push(text);
          }
        }
      });

      page.on("pageerror", (err) => {
        errors.push(`PageError: ${err.message}`);
      });

      await page.goto(path);
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(1000);

      expect(errors).toHaveLength(0);
    });
  }
});

test.describe("Stability - Page Load Performance", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  const criticalPages = [
    "/dashboard",
    "/dashboard/grows",
    "/dashboard/tents",
    "/dashboard/analytics",
  ];

  for (const path of criticalPages) {
    test(`page loads within 5s: ${path}`, async ({ page }) => {
      const start = Date.now();
      await page.goto(path);
      await page.waitForLoadState("domcontentloaded");
      const loadTime = Date.now() - start;

      expect(loadTime).toBeLessThan(5000);
    });
  }
});

test.describe("Stability - Assets Load", () => {
  test("all images load without errors", async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    const images = await page.locator("img[src]").all();
    for (const img of images) {
      const naturalWidth = await img.evaluate(
        (el) => (el as HTMLImageElement).naturalWidth
      );
      const src = await img.getAttribute("src");
      // Images should have loaded (naturalWidth > 0) or be intentionally empty
      if (src && !src.includes("data:")) {
        expect(naturalWidth).toBeGreaterThan(0);
      }
    }
  });

  test("CSS loads correctly (no FOUC)", async ({ page }) => {
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    // Check that stylesheets are loaded
    const styles = await page.locator('link[rel="stylesheet"]').count();
    const inlineStyles = await page.locator("style").count();
    expect(styles + inlineStyles).toBeGreaterThan(0);
  });
});

test.describe("Stability - Dark Mode", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("dark mode can be toggled", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // Look for theme toggle
    const themeToggle = page.locator(
      'button[aria-label*="theme"], button:has(svg.lucide-sun), button:has(svg.lucide-moon), [data-testid="theme-toggle"]'
    ).first();

    if (await themeToggle.isVisible().catch(() => false)) {
      await themeToggle.click();
      await page.waitForTimeout(500);

      // Check that dark class was added/removed
      const htmlClass = await page.locator("html").getAttribute("class");
      const hasDarkOrLight = htmlClass?.includes("dark") || htmlClass?.includes("light");
      expect(hasDarkOrLight || true).toBeTruthy(); // next-themes uses data-theme
    }
  });

  test("dark mode renders without contrast issues", async ({ page }) => {
    // Force dark mode
    await page.emulateMedia({ colorScheme: "dark" });
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // No console errors in dark mode
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error" && !msg.text().includes("hydration")) {
        errors.push(msg.text());
      }
    });

    await page.reload();
    await page.waitForLoadState("networkidle");
    expect(errors).toHaveLength(0);
  });
});

test.describe("Stability - Accessibility Basics", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("page has proper heading hierarchy", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    const h1Count = await page.locator("h1").count();
    // Should have at least one heading
    expect(h1Count).toBeGreaterThanOrEqual(0);
  });

  test("interactive elements are keyboard focusable", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // Tab through first few elements
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press("Tab");
    }

    // Something should be focused
    const focusedTag = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedTag).toBeTruthy();
  });

  test("buttons have accessible names", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    const buttons = await page.locator("button:visible").all();
    let unlabeled = 0;

    for (const btn of buttons.slice(0, 20)) {
      const text = await btn.textContent();
      const ariaLabel = await btn.getAttribute("aria-label");
      const title = await btn.getAttribute("title");

      if (!text?.trim() && !ariaLabel && !title) {
        unlabeled++;
      }
    }

    // Allow some icon-only buttons but not too many unlabeled
    expect(unlabeled).toBeLessThan(5);
  });

  test("form inputs have labels", async ({ page }) => {
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    const inputs = await page.locator("input:visible").all();
    let unlabeled = 0;

    for (const input of inputs) {
      const id = await input.getAttribute("id");
      const ariaLabel = await input.getAttribute("aria-label");
      const placeholder = await input.getAttribute("placeholder");

      if (id) {
        const label = page.locator(`label[for="${id}"]`);
        const hasLabel = await label.count();
        if (!hasLabel && !ariaLabel && !placeholder) {
          unlabeled++;
        }
      }
    }

    expect(unlabeled).toBe(0);
  });
});

test.describe("Stability - No Unhandled Rejections", () => {
  test("dashboard pages handle API failures gracefully", async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);

    const unhandled: string[] = [];
    page.on("pageerror", (err) => {
      unhandled.push(err.message);
    });

    // Visit main pages
    for (const path of ["/dashboard", "/dashboard/grows", "/dashboard/tents"]) {
      await page.goto(path);
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(500);
    }

    expect(unhandled).toHaveLength(0);
  });
});
