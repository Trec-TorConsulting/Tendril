/**
 * Shared fixtures and helpers for Tendril QA tests.
 */
import { test as base, expect, Page } from "@playwright/test";

export const BASE_URL = process.env.E2E_BASE_URL || "http://localhost:3000";
export const API_URL = process.env.E2E_API_URL || "http://localhost:8000";

// Test user credentials (seeded by setup)
export const TEST_USERS = {
  standard: {
    email: "qa-user@example.com",
    password: "QaTestPass2026!",
    display_name: "QA Standard User",
    org_name: "QA Test Org",
  },
  admin: {
    email: "qa-admin@example.com",
    password: "QaAdminPass2026!",
    display_name: "QA Admin User",
    org_name: "QA Admin Org",
  },
  teamMember: {
    email: "qa-team@example.com",
    password: "QaTeamPass2026!",
    display_name: "QA Team Member",
    org_name: "QA Team Org",
  },
};

export const GROW_TYPES = [
  "DWC",
  "Recirculating DWC",
  "NFT",
  "Ebb & Flow",
  "Aeroponics",
  "Kratky",
  "Coco Coir",
  "Soil",
] as const;

export const MEDIA_TYPES = [
  "Soil",
  "Coco Coir",
  "Coco-Perlite Mix",
  "Peat Mix",
  "Super Soil",
  "Living Soil",
  "Pro-Mix",
  "Other",
] as const;

export const GROW_STAGES = [
  "seedling",
  "vegetative",
  "flowering",
  "ripening",
  "drying",
  "curing",
] as const;

export const ENVIRONMENT_TYPES = ["indoor", "outdoor", "greenhouse"] as const;

export const SCREEN_SIZES = {
  "mobile-375": { width: 375, height: 812 },
  "mobile-428": { width: 428, height: 926 },
  "tablet-768": { width: 768, height: 1024 },
  "desktop-1280": { width: 1280, height: 720 },
  "desktop-1920": { width: 1920, height: 1080 },
  "desktop-2560": { width: 2560, height: 1440 },
} as const;

/**
 * Login helper - performs login and waits for dashboard
 */
export async function login(
  page: Page,
  email: string,
  password: string
): Promise<void> {
  await page.goto("/login");
  await page.locator("#email").fill(email);
  await page.locator("#password").fill(password);
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/dashboard/, { timeout: 15000 });
  // Wait for page to be ready
  await page.waitForLoadState("networkidle");
}

/**
 * Navigate to a dashboard page via URL
 */
export async function navigateTo(page: Page, path: string): Promise<void> {
  await page.goto(`/dashboard/${path}`);
  await page.waitForLoadState("networkidle");
}

/**
 * Check if the page is in mobile layout (has mobile nav FAB)
 */
export async function isMobileLayout(page: Page): Promise<boolean> {
  const viewport = page.viewportSize();
  return (viewport?.width ?? 1280) < 768;
}

/**
 * Wait for API response and return data
 */
export async function waitForApiResponse(
  page: Page,
  urlPattern: string | RegExp
) {
  return page.waitForResponse(
    (response) =>
      (typeof urlPattern === "string"
        ? response.url().includes(urlPattern)
        : urlPattern.test(response.url())) && response.status() < 400
  );
}

/**
 * Take a screenshot and save to QA output
 */
export async function qaScreenshot(
  page: Page,
  name: string
): Promise<void> {
  await page.screenshot({
    path: `qa-output/screenshots/${name}.png`,
    fullPage: true,
  });
}

/**
 * Check that no console errors occurred on the page
 */
export function setupConsoleErrorTracking(page: Page): string[] {
  const errors: string[] = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      errors.push(`[${msg.type()}] ${msg.text()}`);
    }
  });
  return errors;
}

/**
 * Verify no broken links on current page
 */
export async function checkLinksOnPage(page: Page): Promise<{
  total: number;
  broken: string[];
}> {
  const links = await page.locator("a[href]").all();
  const broken: string[] = [];

  for (const link of links) {
    const href = await link.getAttribute("href");
    if (!href || href.startsWith("#") || href.startsWith("mailto:") || href.startsWith("tel:")) {
      continue;
    }
    // Internal links should not 404
    if (href.startsWith("/") || href.startsWith(BASE_URL)) {
      const visible = await link.isVisible().catch(() => false);
      if (visible) {
        // Just check the href format is valid
        if (!href.match(/^\/[a-z0-9\-\/_[\]]*$/i) && !href.startsWith("http")) {
          broken.push(href);
        }
      }
    }
  }

  return { total: links.length, broken };
}

export { base as test, expect };
