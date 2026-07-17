"""Coral Edge TPU inference path.

Runs an int8 Edge-TPU-compiled tflite model via ``pycoral``/``libedgetpu``.
These libraries and the physical accelerator only exist on the pinned
``node06`` pod, so every import and delegate initialization is lazy and guarded:
when the runtime or device is unavailable the caller receives
:class:`CoralUnavailableError` and falls back to the GPU/CPU ONNX path.
"""

from __future__ import annotations

import numpy as np
from PIL import Image


class CoralUnavailableError(RuntimeError):
    """Raised when the Edge TPU runtime, delegate, or model cannot be used."""


_INTERPRETER_CACHE: dict[str, object] = {}


def coral_runtime_available() -> bool:
    """Return True when the pycoral runtime can be imported (no device probe)."""
    try:
        import pycoral.utils.edgetpu  # noqa: F401
    except Exception:
        return False
    return True


def reset_interpreter_cache() -> None:
    _INTERPRETER_CACHE.clear()


def _load_interpreter(model_path: str) -> object:
    cached = _INTERPRETER_CACHE.get(model_path)
    if cached is not None:
        return cached

    try:
        from pycoral.utils.edgetpu import make_interpreter
    except Exception as exc:  # pragma: no cover - requires libedgetpu
        raise CoralUnavailableError("pycoral/libedgetpu is not installed") from exc

    try:
        interpreter = make_interpreter(model_path)
        interpreter.allocate_tensors()
    except Exception as exc:  # pragma: no cover - requires Edge TPU hardware
        raise CoralUnavailableError(f"failed to initialize Edge TPU delegate: {exc}") from exc

    _INTERPRETER_CACHE[model_path] = interpreter
    return interpreter


def run_coral_inference(
    image: Image.Image,
    *,
    model_path: str,
    input_width: int,
    input_height: int,
) -> np.ndarray:
    """Run Edge-TPU inference and return the dequantized output tensor.

    Raises :class:`CoralUnavailableError` if the runtime/delegate/model is
    unavailable so the caller can fall back to another accelerator tier.
    """
    if not model_path:
        raise CoralUnavailableError("no Edge TPU model path configured")

    interpreter = _load_interpreter(model_path)

    try:
        from pycoral.adapters import common
    except Exception as exc:  # pragma: no cover - requires pycoral
        raise CoralUnavailableError("pycoral adapters are unavailable") from exc

    resized = image.resize((input_width, input_height), Image.Resampling.BILINEAR)

    try:  # pragma: no cover - requires Edge TPU hardware
        common.set_input(interpreter, resized)
        interpreter.invoke()
        output_details = interpreter.get_output_details()[0]
        raw = interpreter.get_tensor(output_details["index"])
    except Exception as exc:  # pragma: no cover - requires Edge TPU hardware
        raise CoralUnavailableError(f"Edge TPU inference failed: {exc}") from exc

    arr = np.asarray(raw, dtype=np.float32)  # pragma: no cover - hardware only
    scale, zero_point = output_details.get("quantization", (0.0, 0))  # pragma: no cover
    if scale:  # pragma: no cover - dequantize int8 output
        arr = (arr - float(zero_point)) * float(scale)
    return arr  # pragma: no cover
