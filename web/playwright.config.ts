import { defineConfig, devices } from "@playwright/test";

const BASE_URL = process.env.E2E_BASE_URL || "http://localhost:3000";

/**
 * Tendril Full QA Configuration
 * - All 3 browser engines (Chromium, Firefox, WebKit)
 * - 6 viewports + both orientations for mobile/tablet
 * - PWA standalone mode testing
 */
export default defineConfig({
  globalSetup: "./e2e/global-setup.ts",
  testDir: "./e2e",
  testIgnore: ["**/tendril.spec.ts"], // Ignore legacy test
  outputDir: "./qa-output/test-results",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ["html", { outputFolder: "./qa-output/playwright-report", open: "never" }],
    ["json", { outputFile: "./qa-output/qa-results.json" }],
    ["list"],
  ],
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "on-first-retry",
    actionTimeout: 15000,
    navigationTimeout: 30000,
  },
  projects: [
    // === DESKTOP BROWSERS ===
    {
      name: "chromium-desktop-1280",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1280, height: 720 },
      },
    },
    {
      name: "chromium-desktop-1920",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: "chromium-desktop-2560",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 2560, height: 1440 },
      },
    },
    {
      name: "firefox-desktop-1280",
      use: {
        ...devices["Desktop Firefox"],
        viewport: { width: 1280, height: 720 },
      },
    },
    {
      name: "firefox-desktop-1920",
      use: {
        ...devices["Desktop Firefox"],
        viewport: { width: 1920, height: 1080 },
      },
    },
    {
      name: "webkit-desktop-1280",
      use: {
        ...devices["Desktop Safari"],
        viewport: { width: 1280, height: 720 },
      },
    },
    {
      name: "webkit-desktop-1920",
      use: {
        ...devices["Desktop Safari"],
        viewport: { width: 1920, height: 1080 },
      },
    },

    // === MOBILE - Portrait ===
    {
      name: "chromium-mobile-375-portrait",
      use: {
        ...devices["iPhone 13"],
        viewport: { width: 375, height: 812 },
      },
    },
    {
      name: "chromium-mobile-428-portrait",
      use: {
        ...devices["iPhone 14 Pro Max"],
        viewport: { width: 428, height: 926 },
      },
    },
    {
      name: "webkit-mobile-375-portrait",
      use: {
        ...devices["iPhone 13"],
        viewport: { width: 375, height: 812 },
        isMobile: true,
      },
    },
    {
      name: "webkit-mobile-428-portrait",
      use: {
        ...devices["iPhone 14 Pro Max"],
        viewport: { width: 428, height: 926 },
        isMobile: true,
      },
    },

    // === MOBILE - Landscape ===
    {
      name: "chromium-mobile-375-landscape",
      use: {
        ...devices["iPhone 13 landscape"],
        viewport: { width: 812, height: 375 },
      },
    },
    {
      name: "chromium-mobile-428-landscape",
      use: {
        ...devices["iPhone 14 Pro Max landscape"],
        viewport: { width: 926, height: 428 },
      },
    },
    {
      name: "webkit-mobile-375-landscape",
      use: {
        ...devices["iPhone 13 landscape"],
        viewport: { width: 812, height: 375 },
        isMobile: true,
      },
    },
    {
      name: "webkit-mobile-428-landscape",
      use: {
        ...devices["iPhone 14 Pro Max landscape"],
        viewport: { width: 926, height: 428 },
        isMobile: true,
      },
    },

    // === TABLET - Portrait ===
    {
      name: "chromium-tablet-768-portrait",
      use: {
        ...devices["iPad (gen 7)"],
        viewport: { width: 768, height: 1024 },
      },
    },
    {
      name: "webkit-tablet-768-portrait",
      use: {
        ...devices["iPad (gen 7)"],
        viewport: { width: 768, height: 1024 },
        isMobile: true,
      },
    },

    // === TABLET - Landscape ===
    {
      name: "chromium-tablet-768-landscape",
      use: {
        ...devices["iPad (gen 7) landscape"],
        viewport: { width: 1024, height: 768 },
      },
    },
    {
      name: "webkit-tablet-768-landscape",
      use: {
        ...devices["iPad (gen 7) landscape"],
        viewport: { width: 1024, height: 768 },
        isMobile: true,
      },
    },

    // === PWA Standalone Mode ===
    {
      name: "pwa-chromium-mobile",
      use: {
        ...devices["iPhone 13"],
        viewport: { width: 375, height: 812 },
        contextOptions: {
          // Simulate standalone display mode
          colorScheme: "light",
        },
      },
    },
    {
      name: "pwa-chromium-desktop",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1280, height: 720 },
        contextOptions: {
          colorScheme: "light",
        },
      },
    },
  ],

  // Optionally start local dev server
  webServer: process.env.CI
    ? undefined
    : {
        command: "npm run dev",
        url: BASE_URL,
        reuseExistingServer: true,
        timeout: 60000,
      },
});
