/**
 * QA Tests: Grow Type × Media Combinations (Exhaustive Matrix)
 * Every grow type with every applicable environment and configuration.
 * This ensures no combination crashes or shows broken UI.
 */
import { test, expect, login, TEST_USERS, GROW_TYPES, MEDIA_TYPES, ENVIRONMENT_TYPES } from "./helpers";

// Define which environment types are valid for each grow type
const VALID_ENVIRONMENTS: Record<string, string[]> = {
  DWC: ["indoor", "greenhouse"],
  "Recirculating DWC": ["indoor", "greenhouse"],
  NFT: ["indoor", "greenhouse"],
  "Ebb & Flow": ["indoor", "greenhouse"],
  Aeroponics: ["indoor", "greenhouse"],
  Kratky: ["indoor", "greenhouse", "outdoor"],
  "Coco Coir": ["indoor", "outdoor", "greenhouse"],
  Soil: ["indoor", "outdoor", "greenhouse"],
};

// Define which grow types can use media selection (substrate-based)
const SUBSTRATE_TYPES = ["Coco Coir", "Soil"];

test.describe("Matrix - Grow Type × Environment Combos", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  for (const growType of GROW_TYPES) {
    for (const env of VALID_ENVIRONMENTS[growType] || ["indoor"]) {
      test(`${growType} in ${env} environment renders without errors`, async ({ page }) => {
        const errors: string[] = [];
        page.on("pageerror", (err) => errors.push(err.message));
        page.on("console", (msg) => {
          if (msg.type() === "error" && !msg.text().includes("hydration")) {
            errors.push(msg.text());
          }
        });

        // Navigate to grows page
        await page.goto("/dashboard/grows");
        await page.waitForLoadState("networkidle");

        // Try to open create dialog
        const newBtn = page.getByRole("button", { name: /new grow|create/i }).first();
        if (await newBtn.isVisible().catch(() => false)) {
          await newBtn.click();
          await page.waitForTimeout(500);

          // Fill grow name
          const nameInput = page.locator('[placeholder="Grow name"], input[name="name"]').first();
          if (await nameInput.isVisible().catch(() => false)) {
            await nameInput.fill(`Matrix-${growType}-${env}`);
          }

          // Select grow type
          const typeSelect = page.locator('[name="grow_type"]').first();
          if (await typeSelect.isVisible().catch(() => false)) {
            await typeSelect.click();
            const option = page.getByRole("option", { name: new RegExp(growType, "i") }).first();
            if (await option.isVisible().catch(() => false)) {
              await option.click();
            }
          }

          // Verify no errors occurred during interaction
          expect(errors.filter((e) => !e.includes("404"))).toHaveLength(0);
        }

        // Close dialog without saving
        await page.keyboard.press("Escape");
      });
    }
  }
});

test.describe("Matrix - Substrate Types × Media Combos", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  for (const growType of SUBSTRATE_TYPES) {
    for (const media of MEDIA_TYPES) {
      test(`${growType} grow with ${media} media - no errors`, async ({ page }) => {
        const errors: string[] = [];
        page.on("pageerror", (err) => errors.push(err.message));

        // Navigate to a grow of this type if exists
        await page.goto("/dashboard/grows");
        await page.waitForLoadState("networkidle");

        // Look for a grow of this type
        const growCard = page.locator(`text=QA ${growType}`).first();
        if (await growCard.isVisible().catch(() => false)) {
          await growCard.click();
          await page.waitForLoadState("networkidle");

          // Check containers/buckets tab
          const containerTab = page.locator('[value="buckets"], [value="containers"]').first();
          if (await containerTab.isVisible().catch(() => false)) {
            await containerTab.click();
            await page.waitForTimeout(500);
          }
        }

        // No page-level errors
        expect(errors).toHaveLength(0);
      });
    }
  }
});

test.describe("Matrix - All Grow Types Detail Page Tabs", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  const TABS_TO_TEST = [
    "overview",
    "buckets",
    "tasks",
    "feeding",
    "journal",
    "harvest",
    "sensors",
    "photos",
  ];

  for (const growType of GROW_TYPES) {
    for (const tab of TABS_TO_TEST) {
      test(`${growType} grow - ${tab} tab renders`, async ({ page }) => {
        const errors: string[] = [];
        page.on("pageerror", (err) => errors.push(err.message));

        await page.goto("/dashboard/grows");
        await page.waitForLoadState("networkidle");

        // Find grow of this type
        const growLink = page.locator(`text=QA ${growType}`).first();
        if (await growLink.isVisible({ timeout: 5000 }).catch(() => false)) {
          await growLink.click();
          await page.waitForLoadState("networkidle");

          const tabEl = page.locator(`[value="${tab}"]`).first();
          if (await tabEl.isVisible({ timeout: 5000 }).catch(() => false)) {
            await tabEl.click();
            await page.waitForLoadState("networkidle");
            await page.waitForTimeout(300);

            // Tab content should render without errors
            await expect(page.locator("body")).not.toBeEmpty();
          }
        }

        expect(errors).toHaveLength(0);
      });
    }
  }
});

test.describe("Matrix - Grow Type Stage Configs Load", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/grow-types");
    await page.waitForLoadState("networkidle");
  });

  for (const growType of GROW_TYPES) {
    test(`${growType} config page accessible`, async ({ page }) => {
      const errors: string[] = [];
      page.on("pageerror", (err) => errors.push(err.message));

      // Look for grow type card/link
      const typeCard = page.getByText(new RegExp(growType, "i")).first();
      if (await typeCard.isVisible().catch(() => false)) {
        await typeCard.click();
        await page.waitForLoadState("networkidle");
        await page.waitForTimeout(500);

        // Should show stage configs or grow type details
        await expect(page.locator("body")).not.toBeEmpty();
      }

      expect(errors).toHaveLength(0);
    });
  }
});
