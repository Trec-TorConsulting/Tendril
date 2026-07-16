from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock


@dataclass(slots=True)
class DetectorTelemetry:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    unavailable_requests: int = 0
    fallback_requests: int = 0
    total_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    tier_counts: dict[str, int] = field(default_factory=dict)
    class_counts: dict[str, int] = field(default_factory=dict)


class TelemetryStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._state = DetectorTelemetry()

    def _record_common(self, *, tier: str, latency_ms: float) -> None:
        self._state.total_requests += 1
        self._state.total_latency_ms += latency_ms
        if latency_ms > self._state.max_latency_ms:
            self._state.max_latency_ms = latency_ms
        self._state.tier_counts[tier] = self._state.tier_counts.get(tier, 0) + 1
        if tier in {"gpu", "cpu"}:
            self._state.fallback_requests += 1

    def record_unavailable(self, *, latency_ms: float) -> None:
        with self._lock:
            self._record_common(tier="unavailable", latency_ms=latency_ms)
            self._state.unavailable_requests += 1

    def record_error(self, *, tier: str, latency_ms: float) -> None:
        with self._lock:
            self._record_common(tier=tier, latency_ms=latency_ms)
            self._state.failed_requests += 1

    def record_success(self, *, tier: str, latency_ms: float, classes: list[str]) -> None:
        with self._lock:
            self._record_common(tier=tier, latency_ms=latency_ms)
            self._state.successful_requests += 1
            for class_name in classes:
                self._state.class_counts[class_name] = self._state.class_counts.get(class_name, 0) + 1

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            total = self._state.total_requests
            avg_latency = (self._state.total_latency_ms / total) if total else 0.0
            fallback_rate = (self._state.fallback_requests / total) if total else 0.0
            return {
                "total_requests": total,
                "successful_requests": self._state.successful_requests,
                "failed_requests": self._state.failed_requests,
                "unavailable_requests": self._state.unavailable_requests,
                "fallback_requests": self._state.fallback_requests,
                "fallback_rate": round(fallback_rate, 4),
                "avg_latency_ms": round(avg_latency, 3),
                "max_latency_ms": round(self._state.max_latency_ms, 3),
                "tier_counts": dict(sorted(self._state.tier_counts.items())),
                "class_counts": dict(sorted(self._state.class_counts.items())),
            }

    def prometheus_metrics(self) -> str:
        snapshot = self.snapshot()
        lines = [
            "# HELP vision_detector_requests_total Total number of detect requests.",
            "# TYPE vision_detector_requests_total counter",
            f"vision_detector_requests_total {snapshot['total_requests']}",
            "# HELP vision_detector_requests_success_total Successful detect requests.",
            "# TYPE vision_detector_requests_success_total counter",
            f"vision_detector_requests_success_total {snapshot['successful_requests']}",
            "# HELP vision_detector_requests_failed_total Failed detect requests.",
            "# TYPE vision_detector_requests_failed_total counter",
            f"vision_detector_requests_failed_total {snapshot['failed_requests']}",
            "# HELP vision_detector_requests_unavailable_total Unavailable detect requests.",
            "# TYPE vision_detector_requests_unavailable_total counter",
            f"vision_detector_requests_unavailable_total {snapshot['unavailable_requests']}",
            "# HELP vision_detector_fallback_requests_total Requests served by fallback tiers.",
            "# TYPE vision_detector_fallback_requests_total counter",
            f"vision_detector_fallback_requests_total {snapshot['fallback_requests']}",
            "# HELP vision_detector_fallback_rate Ratio of fallback requests.",
            "# TYPE vision_detector_fallback_rate gauge",
            f"vision_detector_fallback_rate {snapshot['fallback_rate']}",
            "# HELP vision_detector_latency_ms_avg Average inference latency in milliseconds.",
            "# TYPE vision_detector_latency_ms_avg gauge",
            f"vision_detector_latency_ms_avg {snapshot['avg_latency_ms']}",
            "# HELP vision_detector_latency_ms_max Maximum inference latency in milliseconds.",
            "# TYPE vision_detector_latency_ms_max gauge",
            f"vision_detector_latency_ms_max {snapshot['max_latency_ms']}",
        ]

        tier_counts: dict[str, int] = snapshot["tier_counts"]  # type: ignore[assignment]
        class_counts: dict[str, int] = snapshot["class_counts"]  # type: ignore[assignment]

        lines.append("# HELP vision_detector_requests_by_tier_total Requests by accelerator tier.")
        lines.append("# TYPE vision_detector_requests_by_tier_total counter")
        for tier, count in tier_counts.items():
            lines.append(f'vision_detector_requests_by_tier_total{{tier="{tier}"}} {count}')

        lines.append("# HELP vision_detector_class_detections_total Detected class counts.")
        lines.append("# TYPE vision_detector_class_detections_total counter")
        for class_name, count in class_counts.items():
            lines.append(f'vision_detector_class_detections_total{{class="{class_name}"}} {count}')

        lines.append("")
        return "\n".join(lines)


telemetry = TelemetryStore()
