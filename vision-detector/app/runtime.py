from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class AcceleratorTier(StrEnum):
    CORAL = "coral"
    GPU = "gpu"
    CPU = "cpu"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    model_version: str
    model_path: str
    coral_enabled: bool
    gpu_enabled: bool
    cpu_enabled: bool


@dataclass(frozen=True, slots=True)
class RuntimeState:
    model_version: str | None
    accelerator_tier: AcceleratorTier


def _env_flag(name: str, default: bool) -> bool:
    value = os.environ.get(name, str(default)).strip().lower()
    return value in {"1", "true", "yes", "on"}


def load_runtime_config() -> RuntimeConfig:
    return RuntimeConfig(
        model_version=os.environ.get("VISION_MODEL_VERSION", "").strip(),
        model_path=os.environ.get("VISION_MODEL_PATH", "").strip(),
        coral_enabled=_env_flag("VISION_CORAL_ENABLED", True),
        gpu_enabled=_env_flag("VISION_GPU_ENABLED", True),
        cpu_enabled=_env_flag("VISION_CPU_ENABLED", True),
    )


def _coral_available(enabled: bool) -> bool:
    return enabled and Path("/dev/apex_0").exists()


def _gpu_available(enabled: bool) -> bool:
    if not enabled:
        return False
    nvidia_devices = os.environ.get("NVIDIA_VISIBLE_DEVICES", "").strip().lower()
    if not nvidia_devices or nvidia_devices == "void":
        return False
    return True


def choose_accelerator(config: RuntimeConfig) -> AcceleratorTier:
    if _coral_available(config.coral_enabled):
        return AcceleratorTier.CORAL
    if _gpu_available(config.gpu_enabled):
        return AcceleratorTier.GPU
    if config.cpu_enabled:
        return AcceleratorTier.CPU
    return AcceleratorTier.UNAVAILABLE


def build_runtime_state(config: RuntimeConfig) -> RuntimeState:
    if not config.model_version or not config.model_path:
        return RuntimeState(model_version=None, accelerator_tier=AcceleratorTier.UNAVAILABLE)
    return RuntimeState(model_version=config.model_version, accelerator_tier=choose_accelerator(config))
