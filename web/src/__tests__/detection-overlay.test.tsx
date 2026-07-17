import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DetectionOverlay, colorForClass, type OverlayDetection } from "@/components/vision/detection-overlay";

const DETECTIONS: OverlayDetection[] = [
  { class_name: "powdery_mildew", confidence: 0.92, bbox: [0.1, 0.2, 0.3, 0.25] },
  { class_name: "spider_mites", confidence: 0.71, bbox: [0.5, 0.5, 0.2, 0.2] },
];

describe("DetectionOverlay", () => {
  it("renders one positioned box per detection", () => {
    render(<DetectionOverlay src="data:image/jpeg;base64,abc" detections={DETECTIONS} />);
    const boxes = screen.getAllByTestId("detection-box");
    expect(boxes).toHaveLength(2);

    // First box uses normalized bbox as CSS percentages.
    expect(boxes[0].style.left).toBe("10%");
    expect(boxes[0].style.top).toBe("20%");
    expect(boxes[0].style.width).toBe("30%");
    expect(boxes[0].style.height).toBe("25%");
  });

  it("renders class label with rounded confidence percentage", () => {
    render(<DetectionOverlay src="x" detections={DETECTIONS} />);
    expect(screen.getByText("powdery_mildew 92%")).toBeInTheDocument();
    expect(screen.getByText("spider_mites 71%")).toBeInTheDocument();
  });

  it("hides boxes when show is false", () => {
    render(<DetectionOverlay src="x" detections={DETECTIONS} show={false} />);
    expect(screen.queryAllByTestId("detection-box")).toHaveLength(0);
  });

  it("assigns a stable, deterministic color per class", () => {
    expect(colorForClass("powdery_mildew")).toBe(colorForClass("powdery_mildew"));
  });
});
