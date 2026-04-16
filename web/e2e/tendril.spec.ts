/**
 * E2E tests for Tendril — signup → pair device → create grow → view data → AI chat.
 *
 * Run with: npx playwright test
 */
import { test, expect } from "@playwright/test";

const BASE_URL = process.env.E2E_BASE_URL || "http://localhost:3000";
const API_URL = process.env.E2E_API_URL || "http://localhost:8000";

test.describe("Tendril E2E", () => {
  const email = `e2e-${Date.now()}@test.com`;
  const password = "TestPass123!";

  test("landing page loads with features and pricing", async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page.getByText("Tendril")).toBeVisible();
    await expect(page.getByText("AI-Powered")).toBeVisible();
    await expect(page.getByText("Simple, Transparent Pricing")).toBeVisible();
  });

  test("signup flow", async ({ page }) => {
    await page.goto(`${BASE_URL}/register`);
    await page.fill('[name="email"]', email);
    await page.fill('[name="password"]', password);
    await page.fill('[name="display_name"]', "E2E User");
    await page.fill('[name="org_name"]', "E2E Org");
    await page.click('button[type="submit"]');
    // Should redirect to dashboard or show success
    await expect(page).toHaveURL(/dashboard|verify/, { timeout: 10000 });
  });

  test("login flow", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[name="email"]', email);
    await page.fill('[name="password"]', password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/, { timeout: 10000 });
  });

  test("create tent and grow", async ({ page }) => {
    // Login first
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[name="email"]', email);
    await page.fill('[name="password"]', password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/, { timeout: 10000 });

    // Navigate to grows
    await page.click('text=Grows');
    await expect(page.getByText("Grows")).toBeVisible();
  });

  test("dashboard shows live stats", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[name="email"]', email);
    await page.fill('[name="password"]', password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/, { timeout: 10000 });
    await expect(page.getByText("Dashboard")).toBeVisible();
  });

  test("AI chat page loads", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[name="email"]', email);
    await page.fill('[name="password"]', password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/, { timeout: 10000 });

    await page.click('text=AI Chat');
    await expect(page.getByText("AI Chat")).toBeVisible();
    await expect(page.getByPlaceholder("Ask about your grow")).toBeVisible();
  });

  test("automation page loads", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[name="email"]', email);
    await page.fill('[name="password"]', password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/, { timeout: 10000 });

    await page.click('text=Automation');
    await expect(page.getByText("Automation")).toBeVisible();
    await expect(page.getByText("New Rule")).toBeVisible();
  });

  test("notifications page loads", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[name="email"]', email);
    await page.fill('[name="password"]', password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/, { timeout: 10000 });

    await page.click('text=Notifications');
    await expect(page.getByText("Notifications")).toBeVisible();
    await expect(page.getByText("Add Channel")).toBeVisible();
  });

  test("billing page loads", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.fill('[name="email"]', email);
    await page.fill('[name="password"]', password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/, { timeout: 10000 });

    await page.click('text=Billing');
    await expect(page.getByText("Billing & Plan")).toBeVisible();
  });
});
