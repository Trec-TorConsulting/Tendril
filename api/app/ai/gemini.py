"""Gemini client — wraps Google Generative AI REST API for health checks."""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
from typing import AsyncIterator

import httpx

logger = logging.getLogger("tendril.ai.gemini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash-lite")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

_TIMEOUT = httpx.Timeout(connect=15, read=120, write=15, pool=15)
_MAX_RETRIES = 3
_RETRY_DELAYS = [1, 3, 5]
_RETRYABLE_CODES = {429, 503}


class GeminiRateLimitError(RuntimeError):
    """All Gemini models are rate-limited after retries."""


def is_configured() -> bool:
    return bool(GEMINI_API_KEY)


def _build_contents(
    messages: list[dict],
    system_prompt: str,
    image_bytes: bytes | None = None,
    extra_images: list[tuple[str, bytes]] | None = None,
) -> tuple[list[dict], dict]:
    """Convert chat messages to Gemini API format with optional images."""
    system_instruction = {"parts": [{"text": system_prompt}]}
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        parts = [{"text": msg["content"]}]
        contents.append({"role": role, "parts": parts})

    # Attach image(s) to the last user message
    if contents and contents[-1]["role"] == "user":
        last_parts = contents[-1]["parts"]
        if image_bytes:
            last_parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(image_bytes).decode("utf-8"),
                }
            })
        if extra_images:
            for label, img in extra_images:
                last_parts.append({"text": f"\n[Additional image: {label}]"})
                last_parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(img).decode("utf-8"),
                    }
                })

    return contents, system_instruction


def _build_payload(contents: list[dict], system_instruction: dict) -> dict:
    return {
        "contents": contents,
        "system_instruction": system_instruction,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
        },
    }


async def chat_completion(
    messages: list[dict],
    image_bytes: bytes | None = None,
    extra_images: list[tuple[str, bytes]] | None = None,
) -> str:
    """Send a chat completion to Gemini with optional images.

    First message with role='system' is used as system instruction.
    Falls back to GEMINI_FALLBACK_MODEL on rate limits.
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured")

    # Extract system prompt from messages
    system_prompt = ""
    user_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_prompt = msg["content"]
        else:
            user_messages.append(msg)

    contents, system_instruction = _build_contents(
        user_messages, system_prompt, image_bytes, extra_images,
    )
    payload = _build_payload(contents, system_instruction)

    for model in [GEMINI_MODEL, GEMINI_FALLBACK_MODEL]:
        url = f"{GEMINI_BASE_URL}/models/{model}:generateContent?key={GEMINI_API_KEY}"
        for attempt in range(_MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code in _RETRYABLE_CODES:
                        delay = _RETRY_DELAYS[min(attempt, len(_RETRY_DELAYS) - 1)]
                        if resp.status_code == 429:
                            retry_after = resp.headers.get("retry-after")
                            if retry_after:
                                try:
                                    delay = max(int(retry_after), delay)
                                except ValueError:
                                    pass
                            else:
                                delay = max(delay * 4, 15)
                        logger.warning(
                            "Gemini %s returned %d, retry %d/%d in %ds",
                            model, resp.status_code, attempt + 1, _MAX_RETRIES, delay,
                        )
                        await asyncio.sleep(delay)
                        continue
                    resp.raise_for_status()
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        logger.warning("Gemini %s returned no candidates: %s", model, data.get("promptFeedback"))
                        return "I couldn't generate a response. Please try again."
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if model != GEMINI_MODEL:
                        logger.info("Used fallback model %s", model)
                    return "".join(p.get("text", "") for p in parts)
            except httpx.HTTPStatusError as e:
                if e.response.status_code in _RETRYABLE_CODES:
                    delay = _RETRY_DELAYS[min(attempt, len(_RETRY_DELAYS) - 1)]
                    if e.response.status_code == 429:
                        delay = max(delay * 4, 15)
                    logger.warning(
                        "Gemini %s %d, retry %d/%d in %ds",
                        model, e.response.status_code, attempt + 1, _MAX_RETRIES, delay,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise
        logger.warning("Gemini %s exhausted retries, trying fallback", model)

    raise GeminiRateLimitError("All Gemini models unavailable after retries")


async def check_health() -> bool:
    """Check if Gemini API is reachable."""
    if not GEMINI_API_KEY:
        return False
    try:
        url = f"{GEMINI_BASE_URL}/models/{GEMINI_MODEL}?key={GEMINI_API_KEY}"
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url)
            return resp.status_code == 200
    except Exception:
        return False
