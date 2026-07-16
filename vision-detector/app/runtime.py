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
    model_storage_key: str
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
        model_storage_key=os.environ.get("VISION_MODEL_STORAGE_KEY", "").strip(),
        coral_enabled=_env_flag("VISION_CORAL_ENABLED", True),
        gpu_enabled=_env_flag("VISION_GPU_ENABLED", True),
        cpu_enabled=_env_flag("VISION_CPU_ENABLED", True),
    )


def _usb_coral_available() -> bool:
    # Common Coral USB IDs: pre-firmware (1a6e:089a), runtime (18d1:9302/9301)
    known_ids = {
        "1a6e": {"089a"},
        "18d1": {"9301", "9302"},
    }
    usb_root = Path("/sys/bus/usb/devices")
    if not usb_root.exists():
        return False

    for dev in usb_root.iterdir():
        vendor_file = dev / "idVendor"
        product_file = dev / "idProduct"
        if not vendor_file.exists() or not product_file.exists():
            continue
        vendor = vendor_file.read_text(encoding="utf-8").strip().lower()
        product = product_file.read_text(encoding="utf-8").strip().lower()
        if product in known_ids.get(vendor, set()):
            return True
    return False


def _coral_available(enabled: bool) -> bool:
    if not enabled:
        return False
    if Path("/dev/apex_0").exists():
        return True
    return _usb_coral_available()


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
    has_model_source = bool(config.model_path or config.model_storage_key)
    if not config.model_version or not has_model_source:
        return RuntimeState(model_version=None, accelerator_tier=AcceleratorTier.UNAVAILABLE)
    return RuntimeState(model_version=config.model_version, accelerator_tier=choose_accelerator(config))
