import { test, expect, login, TEST_USERS } from "./helpers";

/**
 * Vision detection e2e: exercises the on-demand "Scan" flow on the tent camera
 * view. All backend endpoints the view needs are mocked so the test does not
 * depend on seeded cameras or a running detector.
 */
test.describe("Vision detection scan flow", () => {
  const TENT_ID = "tent-vision-1";

  test.beforeEach(async ({ page }) => {
    // Tent detail (the only hard dependency of the tent page).
    await page.route(`**/v1/tents/${TENT_ID}`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: TENT_ID,
          name: "Vision QA Tent",
          environment_type: "indoor",
          size: "4x4",
          location: null,
          notes: null,
          equipment: [],
          created_at: "2026-06-24T00:00:00Z",
        }),
      });
    });

    // Cameras rendered by CameraGrid.
    await page.route(`**/v1/tents/${TENT_ID}/cameras**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          {
            id: "cam-1",
            tent_id: TENT_ID,
            label: "Canopy Cam",
            url: "http://camera.local/snapshot",
            camera_type: "http_snapshot",
            is_primary: true,
            created_at: "2026-06-24T00:00:00Z",
          },
        ]),
      });
    });

    // Snapshot proxy — a truthy base64 string is enough to render the tile + scan button.
    await page.route(`**/v1/tents/${TENT_ID}/camera-snapshot-b64**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          image_base64: "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAt=",
          timestamp: "2026-06-24T00:00:00Z",
        }),
      });
    });

    // The detector scan result.
    await page.route("**/v1/vision/scan/tent/**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          model_version: "v1",
          accelerator_tier: "coral",
          message: null,
          detections: [
            { class_name: "powdery_mildew", confidence: 0.92, bbox: [0.1, 0.1, 0.2, 0.2] },
            { class_name: "nutrient_deficiency", confidence: 0.61, bbox: [0.5, 0.5, 0.2, 0.2] },
          ],
        }),
      });
    });

    await page.addInitScript(() => {
      window.localStorage.setItem("tendril_onboarding_seen", "true");
    });
  });

  test("scans a tent snapshot and renders detections", async ({ page }) => {
    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto(`/dashboard/tents/${TENT_ID}`);

    // The camera tile exposes a "Scan for issues" control once a snapshot loads.
    const tileScanButton = page.getByRole("button", { name: "Scan for issues" });
    await expect(tileScanButton).toBeVisible({ timeout: 15000 });
    await tileScanButton.click();

    // Full-screen scan panel opens; run the scan.
    const runScanButton = page.getByRole("button", { name: /scan for issues/i });
    await expect(runScanButton).toBeVisible();
    await runScanButton.click();

    // Detections from the mocked detector are listed.
    await expect(page.getByText("powdery_mildew")).toBeVisible({ timeout: 15000 });
    await expect(page.getByText("nutrient_deficiency")).toBeVisible();
    await expect(page.getByText(/sent to the AI approval queue/i)).toBeVisible();
  });
});
