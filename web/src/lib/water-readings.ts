export interface WaterReadingLike {
  recorded_at: string;
  device_id?: string | null;
}

export interface BucketLike {
  id: string;
  role?: string | null;
}

function descByRecordedAt<T extends WaterReadingLike>(a: T, b: T): number {
  return new Date(b.recorded_at).getTime() - new Date(a.recorded_at).getTime();
}

export function selectPreferredWaterReadings<T extends WaterReadingLike, B extends BucketLike>(
  perBucketReadings: T[][],
  buckets: B[],
  growType: string,
): T[] {
  const headerBucket = growType === "rdwc" ? buckets.find((b) => b.role === "header") : null;
  const headerIdx = headerBucket ? buckets.findIndex((b) => b.id === headerBucket.id) : -1;

  const waterReadingsBase = (
    headerIdx >= 0 && perBucketReadings[headerIdx]
      ? perBucketReadings[headerIdx]
      : perBucketReadings.flat()
  ).slice().sort(descByRecordedAt);

  const tuyaWaterReadings = waterReadingsBase.filter((r) => (r.device_id ?? "").startsWith("tuya:"));
  return (tuyaWaterReadings.length > 0 ? tuyaWaterReadings : waterReadingsBase).slice().sort(descByRecordedAt);
}
