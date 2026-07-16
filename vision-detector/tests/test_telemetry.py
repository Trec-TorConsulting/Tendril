from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.telemetry import TelemetryStore


class TelemetryTests(unittest.TestCase):
    def test_snapshot_tracks_counts_and_rates(self) -> None:
        store = TelemetryStore()
        store.record_success(tier="coral", latency_ms=10.0, classes=["cannabis", "powdery_mildew"])
        store.record_success(tier="gpu", latency_ms=30.0, classes=["cannabis"])
        store.record_error(tier="cpu", latency_ms=20.0)
        store.record_unavailable(latency_ms=40.0)

        snapshot = store.snapshot()

        self.assertEqual(snapshot["total_requests"], 4)
        self.assertEqual(snapshot["successful_requests"], 2)
        self.assertEqual(snapshot["failed_requests"], 1)
        self.assertEqual(snapshot["unavailable_requests"], 1)
        self.assertEqual(snapshot["fallback_requests"], 2)
        self.assertEqual(snapshot["fallback_rate"], 0.5)
        self.assertEqual(snapshot["avg_latency_ms"], 25.0)
        self.assertEqual(snapshot["max_latency_ms"], 40.0)

        class_counts = snapshot["class_counts"]
        self.assertEqual(class_counts["cannabis"], 2)
        self.assertEqual(class_counts["powdery_mildew"], 1)

        tier_counts = snapshot["tier_counts"]
        self.assertEqual(tier_counts["coral"], 1)
        self.assertEqual(tier_counts["gpu"], 1)
        self.assertEqual(tier_counts["cpu"], 1)
        self.assertEqual(tier_counts["unavailable"], 1)

    def test_prometheus_metrics_contains_expected_series(self) -> None:
        store = TelemetryStore()
        store.record_success(tier="coral", latency_ms=12.0, classes=["cannabis"])
        store.record_error(tier="gpu", latency_ms=18.0)

        metrics = store.prometheus_metrics()

        self.assertIn("vision_detector_requests_total 2", metrics)
        self.assertIn('vision_detector_requests_by_tier_total{tier="coral"} 1', metrics)
        self.assertIn('vision_detector_requests_by_tier_total{tier="gpu"} 1', metrics)
        self.assertIn('vision_detector_class_detections_total{class="cannabis"} 1', metrics)


if __name__ == "__main__":
    unittest.main()
