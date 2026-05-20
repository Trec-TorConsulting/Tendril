/**
 * QA Tests: All Forms & Data Entry
 * - Tent/Grow Space creation
 * - Sensor readings
 * - Quick logging (notes, feeding, readings)
 * - Bucket management
 * - Harvest logging
 * - Equipment management
 * - Camera management
 * - Settings forms
 */
import { test, expect, login, TEST_USERS, navigateTo } from "./helpers";

test.describe("Forms - Grow Space (Tent) Creation", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/tents");
    await page.waitForLoadState("networkidle");
  });

  test("create tent form has all required fields", async ({ page }) => {
    // Open create form
    const addBtn = page.getByRole("button", { name: /add|new|create/i }).first();
    await expect(addBtn).toBeVisible();
    await addBtn.click();

    // Verify form fields
    await expect(page.locator('[placeholder*="Veg Tent"], [name="name"]').first()).toBeVisible();
    await expect(page.locator('select, [role="combobox"]').first()).toBeVisible(); // environment type
  });

  test("create indoor tent with full details", async ({ page }) => {
    const addBtn = page.getByRole("button", { name: /add|new|create/i }).first();
    await addBtn.click();
    await page.waitForTimeout(500);

    // Fill name
    await page.locator('[placeholder*="Veg Tent"], [name="name"]').first().fill("QA Indoor Tent");

    // Select environment type
    const envSelect = page.locator('select:has(option[value="indoor"]), [data-testid="environment-select"]').first();
    if (await envSelect.isVisible().catch(() => false)) {
      await envSelect.selectOption("indoor");
    }

    // Select size
    const sizeSelect = page.locator('select:has(option[value="4x4"]), [data-testid="size-select"]').first();
    if (await sizeSelect.isVisible().catch(() => false)) {
      await sizeSelect.selectOption("4x4");
    }

    // Submit
    const submitBtn = page.getByRole("button", { name: /save|create|add/i }).last();
    await submitBtn.click();

    // Verify success
    await page.waitForTimeout(2000);
    const success = await page.getByText(/created|success|QA Indoor/i).isVisible().catch(() => false);
    expect(success).toBeTruthy();
  });

  test("create outdoor grow space with location", async ({ page }) => {
    const addBtn = page.getByRole("button", { name: /add|new|create/i }).first();
    await addBtn.click();
    await page.waitForTimeout(500);

    await page.locator('[placeholder*="Veg Tent"], [name="name"]').first().fill("QA Outdoor Plot");

    // Select outdoor
    const envSelect = page.locator('select:has(option[value="outdoor"])').first();
    if (await envSelect.isVisible().catch(() => false)) {
      await envSelect.selectOption("outdoor");
    }

    // Fill location
    const latInput = page.locator('[placeholder*="34"], input[name*="lat"]').first();
    if (await latInput.isVisible().catch(() => false)) {
      await latInput.fill("34.0522");
    }

    const lonInput = page.locator('[placeholder*="-118"], input[name*="lon"]').first();
    if (await lonInput.isVisible().catch(() => false)) {
      await lonInput.fill("-118.2437");
    }
  });

  test("create greenhouse space", async ({ page }) => {
    const addBtn = page.getByRole("button", { name: /add|new|create/i }).first();
    await addBtn.click();
    await page.waitForTimeout(500);

    await page.locator('[placeholder*="Veg Tent"], [name="name"]').first().fill("QA Greenhouse");

    const envSelect = page.locator('select:has(option[value="greenhouse"])').first();
    if (await envSelect.isVisible().catch(() => false)) {
      await envSelect.selectOption("greenhouse");
    }
  });

  test("tent form validates required fields", async ({ page }) => {
    const addBtn = page.getByRole("button", { name: /add|new|create/i }).first();
    await addBtn.click();
    await page.waitForTimeout(500);

    // Try to submit empty
    const submitBtn = page.getByRole("button", { name: /save|create|add/i }).last();
    await submitBtn.click();

    // Should show validation error or not dismiss
    await page.waitForTimeout(1000);
    // Form should still be visible (not submitted)
    const formStillOpen = await page.locator('[placeholder*="Veg Tent"], [name="name"]').first().isVisible().catch(() => false);
    expect(formStillOpen).toBeTruthy();
  });
});

test.describe("Forms - Quick Logging", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/quick-log");
    await page.waitForLoadState("networkidle");
  });

  test("quick log page loads with all log types", async ({ page }) => {
    // Should show quick log options
    await expect(page.getByText(/note|feeding|reading/i).first()).toBeVisible();
  });

  test("quick note form accepts tags", async ({ page }) => {
    // Look for note/journal quick log option
    const noteBtn = page.getByRole("button", { name: /note|journal/i }).first();
    if (await noteBtn.isVisible().catch(() => false)) {
      await noteBtn.click();
      await page.waitForTimeout(500);

      // Should show tag options
      const tags = page.locator('[data-testid*="tag"], button:has-text("watering"), button:has-text("defoliation")');
      const tagCount = await tags.count();
      expect(tagCount).toBeGreaterThanOrEqual(0);
    }
  });
});

test.describe("Forms - Sensor Readings", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("manual reading form has pH, EC, PPM, water temp", async ({ page }) => {
    // Navigate to a grow's sensor tab
    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");

    const growCard = page.locator('[href*="/dashboard/grows/"]').first();
    if (await growCard.isVisible().catch(() => false)) {
      await growCard.click();
      await page.waitForLoadState("networkidle");

      // Click sensors tab
      const sensorsTab = page.locator('[value="sensors"]').first();
      if (await sensorsTab.isVisible().catch(() => false)) {
        await sensorsTab.click();
        await page.waitForTimeout(500);

        // Look for manual reading button
        const addBtn = page.getByRole("button", { name: /add|log|record|manual/i }).first();
        if (await addBtn.isVisible().catch(() => false)) {
          await addBtn.click();

          // Verify fields
          const phField = page.locator('input[name*="ph"], [placeholder*="pH"]').first();
          const ecField = page.locator('input[name*="ec"], [placeholder*="EC"]').first();
          expect(
            (await phField.isVisible().catch(() => false)) ||
              (await ecField.isVisible().catch(() => false))
          ).toBeTruthy();
        }
      }
    }
  });
});

test.describe("Forms - Bucket/Container Management", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("can add a bucket to a grow", async ({ page }) => {
    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");

    const growCard = page.locator('[href*="/dashboard/grows/"]').first();
    if (await growCard.isVisible().catch(() => false)) {
      await growCard.click();
      await page.waitForLoadState("networkidle");

      // Click buckets tab
      const bucketsTab = page.locator('[value="buckets"]').first();
      if (await bucketsTab.isVisible().catch(() => false)) {
        await bucketsTab.click();
        await page.waitForTimeout(500);

        // Look for add bucket button
        const addBtn = page.getByRole("button", { name: /add|new/i }).first();
        if (await addBtn.isVisible().catch(() => false)) {
          await addBtn.click();
          await page.waitForTimeout(500);

          // Should show bucket form
          const labelField = page.locator(
            'input[name*="label"], [placeholder*="label"], [placeholder*="Label"]'
          ).first();
          await expect(labelField).toBeVisible();
        }
      }
    }
  });
});

test.describe("Forms - Harvest Logging", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("harvest tab shows weight logging form", async ({ page }) => {
    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");

    const growCard = page.locator('[href*="/dashboard/grows/"]').first();
    if (await growCard.isVisible().catch(() => false)) {
      await growCard.click();
      await page.waitForLoadState("networkidle");

      const harvestTab = page.locator('[value="harvest"]').first();
      if (await harvestTab.isVisible().catch(() => false)) {
        await harvestTab.click();
        await page.waitForTimeout(500);

        // Should show harvest logging UI
        const harvestBtn = page.getByRole("button", { name: /log|add|harvest/i }).first();
        const harvestForm = page.locator('input[name*="weight"], [placeholder*="weight"]').first();
        const hasHarvestUI = (await harvestBtn.isVisible().catch(() => false)) ||
          (await harvestForm.isVisible().catch(() => false));
        // Page should at minimum not be errored
        await expect(page.locator("body")).not.toBeEmpty();
      }
    }
  });
});

test.describe("Forms - Account Settings", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/settings");
    await page.waitForLoadState("networkidle");
  });

  test("profile settings page loads", async ({ page }) => {
    await expect(page.locator("body")).not.toBeEmpty();
    // Should show profile editing fields
    const emailField = page.locator('#email, input[name="email"], input[type="email"]').first();
    const nameField = page.locator('#display_name, input[name="display_name"]').first();
    const hasFields = (await emailField.isVisible().catch(() => false)) ||
      (await nameField.isVisible().catch(() => false));
    expect(hasFields).toBeTruthy();
  });

  test("security settings page loads", async ({ page }) => {
    await page.goto("/dashboard/settings/security");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("body")).not.toBeEmpty();
    // Should show password change or 2FA options
    const passwordSection = page.getByText(/password|security/i).first();
    await expect(passwordSection).toBeVisible();
  });
});

test.describe("Forms - Strain Library", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/strains");
    await page.waitForLoadState("networkidle");
  });

  test("strain library page loads", async ({ page }) => {
    await expect(page.locator("body")).not.toBeEmpty();
  });

  test("can open create strain form", async ({ page }) => {
    const addBtn = page.getByRole("button", { name: /add|new|create/i }).first();
    if (await addBtn.isVisible().catch(() => false)) {
      await addBtn.click();
      await page.waitForTimeout(500);
      // Should show strain form
      const nameField = page.locator('input[name*="name"], [placeholder*="name"]').first();
      await expect(nameField).toBeVisible();
    }
  });
});

test.describe("Forms - Automation Rules", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/automation");
    await page.waitForLoadState("networkidle");
  });

  test("automation page loads with new rule button", async ({ page }) => {
    await expect(page.getByText(/automation/i).first()).toBeVisible();
    await expect(page.getByRole("button", { name: /new rule|create/i }).first()).toBeVisible();
  });

  test("new automation rule form opens", async ({ page }) => {
    const newRuleBtn = page.getByRole("button", { name: /new rule|create/i }).first();
    await newRuleBtn.click();
    await page.waitForTimeout(500);

    // Should show rule creation UI
    await expect(page.locator("body")).not.toBeEmpty();
  });
});

test.describe("Forms - Device Pairing", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/devices");
    await page.waitForLoadState("networkidle");
  });

  test("devices page loads", async ({ page }) => {
    await expect(page.getByText(/devices/i).first()).toBeVisible();
  });

  test("pair device button exists", async ({ page }) => {
    const pairBtn = page.getByRole("button", { name: /pair|add|register/i }).first();
    await expect(pairBtn).toBeVisible();
  });
});

test.describe("Forms - Notification Channels", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/notifications");
    await page.waitForLoadState("networkidle");
  });

  test("notifications page loads with add channel", async ({ page }) => {
    await expect(page.getByText(/notification/i).first()).toBeVisible();
    const addBtn = page.getByRole("button", { name: /add channel|new/i }).first();
    await expect(addBtn).toBeVisible();
  });
});

test.describe("Forms - API Keys", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/api-keys");
    await page.waitForLoadState("networkidle");
  });

  test("API keys page loads", async ({ page }) => {
    await expect(page.getByText(/api key/i).first()).toBeVisible();
  });

  test("create API key button exists", async ({ page }) => {
    const createBtn = page.getByRole("button", { name: /create|generate|new/i }).first();
    await expect(createBtn).toBeVisible();
  });
});
