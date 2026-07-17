import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { VisionScanPanel } from "@/components/vision/vision-scan-panel";

const scanTentSnapshot = vi.fn();
const scanGrowPhoto = vi.fn();

vi.mock("@/lib/api", () => ({
  scanTentSnapshot: (...args: unknown[]) => scanTentSnapshot(...args),
  scanGrowPhoto: (...args: unknown[]) => scanGrowPhoto(...args),
}));

vi.mock("@/lib/auth", () => ({
  getAccessToken: () => "test-token",
}));

const toast = { success: vi.fn(), error: vi.fn(), info: vi.fn() };
vi.mock("sonner", () => ({ toast: { success: (m: string) => toast.success(m), error: (m: string) => toast.error(m), info: (m: string) => toast.info(m) } }));

describe("VisionScanPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("scans a tent snapshot and lists detections", async () => {
    scanTentSnapshot.mockResolvedValue({
      model_version: "v1",
      accelerator_tier: "coral",
      message: null,
      detections: [
        { class_name: "powdery_mildew", confidence: 0.92, bbox: [0.1, 0.1, 0.2, 0.2] },
        { class_name: "nutrient_deficiency", confidence: 0.6, bbox: [0.4, 0.4, 0.2, 0.2] },
      ],
    });
    const user = userEvent.setup();
    render(<VisionScanPanel source="tent" sourceId="tent-1" imageSrc="data:image/jpeg;base64,abc" />);

    await user.click(screen.getByRole("button", { name: /scan for issues/i }));

    await waitFor(() => expect(scanTentSnapshot).toHaveBeenCalledWith("test-token", "tent-1", undefined));
    expect(await screen.findByText("powdery_mildew")).toBeInTheDocument();
    expect(screen.getByText("nutrient_deficiency")).toBeInTheDocument();
    expect(toast.success).toHaveBeenCalled();
  });

  it("shows an empty state when no detections are found", async () => {
    scanGrowPhoto.mockResolvedValue({
      model_version: "v1",
      accelerator_tier: "cpu",
      message: null,
      detections: [],
    });
    const user = userEvent.setup();
    render(<VisionScanPanel source="photo" sourceId="photo-1" imageSrc="http://x/img.jpg" />);

    await user.click(screen.getByRole("button", { name: /scan for issues/i }));

    expect(await screen.findByText(/no issues detected/i)).toBeInTheDocument();
    expect(scanGrowPhoto).toHaveBeenCalledWith("test-token", "photo-1", undefined);
  });

  it("shows an unavailable state when no model is active", async () => {
    scanTentSnapshot.mockResolvedValue({
      model_version: null,
      accelerator_tier: "unavailable",
      message: "detection unavailable",
      detections: [],
    });
    const user = userEvent.setup();
    render(<VisionScanPanel source="tent" sourceId="tent-2" imageSrc="x" />);

    await user.click(screen.getByRole("button", { name: /scan for issues/i }));

    expect(await screen.findByText(/detection is not configured/i)).toBeInTheDocument();
    expect(toast.info).toHaveBeenCalled();
  });

  it("surfaces scan errors via toast", async () => {
    scanTentSnapshot.mockRejectedValue(new Error("Camera unreachable"));
    const user = userEvent.setup();
    render(<VisionScanPanel source="tent" sourceId="tent-3" imageSrc="x" />);

    await user.click(screen.getByRole("button", { name: /scan for issues/i }));

    await waitFor(() => expect(toast.error).toHaveBeenCalledWith("Camera unreachable"));
  });
});
