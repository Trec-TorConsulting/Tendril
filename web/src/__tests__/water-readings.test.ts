import { describe, expect, it } from "vitest";

import { selectPreferredWaterReadings } from "@/lib/water-readings";

type Reading = {
  recorded_at: string;
  device_id?: string | null;
  ph?: number | null;
};

type Bucket = {
  id: string;
  role?: string | null;
};

describe("selectPreferredWaterReadings", () => {
  it("prefers Tuya readings when present", () => {
    const buckets: Bucket[] = [{ id: "b1" }, { id: "b2" }];
    const perBucket: Reading[][] = [
      [
        { recorded_at: "2026-06-24T10:00:00Z", device_id: "manual", ph: 6.0 },
        { recorded_at: "2026-06-24T09:00:00Z", device_id: "tuya:a", ph: 5.4 },
      ],
      [{ recorded_at: "2026-06-24T11:00:00Z", device_id: "tuya:b", ph: 5.3 }],
    ];

    const out = selectPreferredWaterReadings(perBucket, buckets, "dwc");
    expect(out.every((r) => (r.device_id ?? "").startsWith("tuya:"))).toBe(true);
    expect(out[0].recorded_at).toBe("2026-06-24T11:00:00Z");
  });

  it("uses RDWC header stream when header exists", () => {
    const buckets: Bucket[] = [
      { id: "header", role: "header" },
      { id: "site-1", role: "site" },
    ];
    const perBucket: Reading[][] = [
      [{ recorded_at: "2026-06-24T08:00:00Z", device_id: "manual", ph: 5.8 }],
      [{ recorded_at: "2026-06-24T12:00:00Z", device_id: "manual", ph: 6.4 }],
    ];

    const out = selectPreferredWaterReadings(perBucket, buckets, "rdwc");
    expect(out).toHaveLength(1);
    expect(out[0].recorded_at).toBe("2026-06-24T08:00:00Z");
  });

  it("falls back to all readings when no Tuya samples exist", () => {
    const buckets: Bucket[] = [{ id: "b1" }];
    const perBucket: Reading[][] = [[
      { recorded_at: "2026-06-24T08:00:00Z", device_id: "manual", ph: 6.1 },
      { recorded_at: "2026-06-24T09:00:00Z", device_id: "manual", ph: 6.0 },
    ]];

    const out = selectPreferredWaterReadings(perBucket, buckets, "dwc");
    expect(out).toHaveLength(2);
    expect(out[0].recorded_at).toBe("2026-06-24T09:00:00Z");
  });
});
