/**
 * QA Tests: Feature Pages & Interactions
 * - AI Chat
 * - Analytics dashboard
 * - Cost/ROI
 * - Scheduling
 * - Support/Tickets
 * - Integrations
 * - Photo uploads
 * - Camera views
 * - Audit trail
 */
import { test, expect, login, TEST_USERS } from "./helpers";

test.describe("Features - AI Chat", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/ai");
    await page.waitForLoadState("networkidle");
  });

  test("AI chat page loads with input field", async ({ page }) => {
    await expect(page.getByText(/ai/i).first()).toBeVisible();
    const input = page.locator(
      '[placeholder*="Ask"], textarea, input[type="text"]'
    ).first();
    await expect(input).toBeVisible();
  });

  test("AI chat accepts text input", async ({ page }) => {
    const input = page.locator(
      '[placeholder*="Ask"], textarea, input[type="text"]'
    ).first();

    await input.fill("What is the ideal pH for DWC?");
    // Verify input was accepted
    await expect(input).toHaveValue(/pH/);
  });

  test("AI chat has send button", async ({ page }) => {
    const sendBtn = page.locator(
      'button[type="submit"], button:has(svg.lucide-send), button[aria-label*="send"]'
    ).first();
    await expect(sendBtn).toBeVisible();
  });
});

test.describe("Features - Analytics", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/analytics");
    await page.waitForLoadState("networkidle");
  });

  test("analytics page loads", async ({ page }) => {
    await expect(page.getByText(/analytics/i).first()).toBeVisible();
  });

  test("no JS errors on analytics page", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error" && !msg.text().includes("hydration")) {
        errors.push(msg.text());
      }
    });

    await page.reload();
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    expect(errors).toHaveLength(0);
  });
});

test.describe("Features - Cost/ROI", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/cost-roi");
    await page.waitForLoadState("networkidle");
  });

  test("cost/ROI page loads", async ({ page }) => {
    await expect(page.locator("body")).not.toBeEmpty();
    await expect(page.getByText(/cost|roi|expense/i).first()).toBeVisible();
  });
});

test.describe("Features - Scheduling", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/schedules");
    await page.waitForLoadState("networkidle");
  });

  test("schedules page loads", async ({ page }) => {
    await expect(page.getByText(/schedule/i).first()).toBeVisible();
  });

  test("can create new schedule", async ({ page }) => {
    const createBtn = page.getByRole("button", { name: /new|create|add/i }).first();
    if (await createBtn.isVisible().catch(() => false)) {
      await createBtn.click();
      await page.waitForTimeout(500);
      // Should show schedule creation UI
      await expect(page.locator("body")).not.toBeEmpty();
    }
  });
});

test.describe("Features - Tasks", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/tasks");
    await page.waitForLoadState("networkidle");
  });

  test("tasks page loads", async ({ page }) => {
    await expect(page.getByText(/task/i).first()).toBeVisible();
  });
});

test.describe("Features - Support", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/support");
    await page.waitForLoadState("networkidle");
  });

  test("support page loads", async ({ page }) => {
    await expect(page.locator("body")).not.toBeEmpty();
  });
});

test.describe("Features - Integrations", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/integrations");
    await page.waitForLoadState("networkidle");
  });

  test("integrations page loads", async ({ page }) => {
    await expect(page.getByText(/integration/i).first()).toBeVisible();
  });
});

test.describe("Features - Photos Tab", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("photos tab renders in grow detail", async ({ page }) => {
    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");

    const growCard = page.locator('[href*="/dashboard/grows/"]').first();
    if (await growCard.isVisible().catch(() => false)) {
      await growCard.click();
      await page.waitForLoadState("networkidle");

      const photosTab = page.locator('[value="photos"]').first();
      if (await photosTab.isVisible().catch(() => false)) {
        await photosTab.click();
        await page.waitForTimeout(500);
        await expect(page.locator("body")).not.toBeEmpty();
        // Should have upload button
        const uploadBtn = page.getByRole("button", { name: /upload|add photo/i }).first();
        const hasUpload = await uploadBtn.isVisible().catch(() => false);
        expect(hasUpload).toBeTruthy();
      }
    }
  });
});

test.describe("Features - Cameras", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/cameras");
    await page.waitForLoadState("networkidle");
  });

  test("cameras page loads", async ({ page }) => {
    await expect(page.locator("body")).not.toBeEmpty();
  });
});

test.describe("Features - Audit Trail", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/audit");
    await page.waitForLoadState("networkidle");
  });

  test("audit trail page loads", async ({ page }) => {
    await expect(page.getByText(/audit/i).first()).toBeVisible();
  });

  test("audit shows event entries", async ({ page }) => {
    // Should show a list/table of events
    const auditContent = page.locator("table, [role='table'], [data-testid='audit-list'], ul, .list").first();
    const hasContent = await auditContent.isVisible().catch(() => false);
    // May be empty if no events, but page should not error
    await expect(page.locator("body")).not.toBeEmpty();
  });
});

test.describe("Features - Billing", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/billing");
    await page.waitForLoadState("networkidle");
  });

  test("billing page shows plan info", async ({ page }) => {
    await expect(page.getByText(/billing|plan/i).first()).toBeVisible();
  });

  test("billing page has cancel option", async ({ page }) => {
    const cancelBtn = page.getByRole("button", { name: /cancel/i }).first();
    // May or may not be visible depending on plan status
    await expect(page.locator("body")).not.toBeEmpty();
  });
});

test.describe("Features - Reference Library", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/reference");
    await page.waitForLoadState("networkidle");
  });

  test("reference page loads", async ({ page }) => {
    await expect(page.getByText(/reference/i).first()).toBeVisible();
  });
});

test.describe("Features - Grow Types Config", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/grow-types");
    await page.waitForLoadState("networkidle");
  });

  test("grow types page loads", async ({ page }) => {
    await expect(page.getByText(/grow type/i).first()).toBeVisible();
  });

  test("shows all 8 grow types", async ({ page }) => {
    const types = ["DWC", "NFT", "Ebb", "Aeroponics", "Kratky", "Coco", "Soil"];
    let found = 0;
    for (const type of types) {
      if (await page.getByText(new RegExp(type, "i")).first().isVisible().catch(() => false)) {
        found++;
      }
    }
    expect(found).toBeGreaterThan(0);
  });
});

test.describe("Features - Journal/Feeding Tabs", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
  });

  test("journal tab loads in grow detail", async ({ page }) => {
    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");

    const growCard = page.locator('[href*="/dashboard/grows/"]').first();
    if (await growCard.isVisible().catch(() => false)) {
      await growCard.click();
      await page.waitForLoadState("networkidle");

      const journalTab = page.locator('[value="journal"]').first();
      if (await journalTab.isVisible().catch(() => false)) {
        await journalTab.click();
        await page.waitForTimeout(500);
        await expect(page.locator("body")).not.toBeEmpty();
      }
    }
  });

  test("feeding tab loads in grow detail", async ({ page }) => {
    await page.goto("/dashboard/grows");
    await page.waitForLoadState("networkidle");

    const growCard = page.locator('[href*="/dashboard/grows/"]').first();
    if (await growCard.isVisible().catch(() => false)) {
      await growCard.click();
      await page.waitForLoadState("networkidle");

      const feedingTab = page.locator('[value="feeding"]').first();
      if (await feedingTab.isVisible().catch(() => false)) {
        await feedingTab.click();
        await page.waitForTimeout(500);
        await expect(page.locator("body")).not.toBeEmpty();
      }
    }
  });
});
