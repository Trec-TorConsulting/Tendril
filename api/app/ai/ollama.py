"""Ollama client — wraps Ollama HTTP API for chat, vision, and tool-calling."""
from __future__ import annotations

import logging
from typing import AsyncIterator

import httpx

from app.config import get_settings

logger = logging.getLogger("tendril.ai.ollama")


async def chat_completion(
    messages: list[dict],
    *,
    model: str | None = None,
    stream: bool = False,
) -> str:
    """Send a chat completion request to Ollama. Returns the full response text."""
    settings = get_settings()
    payload = {
        "model": model or settings.ollama_model,
        "messages": messages,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{settings.ollama_base_url}/api/chat",
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "")


async def chat_with_tools(
    messages: list[dict],
    tools: list[dict],
    *,
    model: str | None = None,
) -> dict:
    """Non-streaming chat that may return tool calls.

    Returns dict with keys: content, tool_calls, message (full msg for history).
    """
    settings = get_settings()
    payload = {
        "model": model or settings.ollama_model,
        "messages": messages,
        "tools": tools,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{settings.ollama_base_url}/api/chat",
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        msg = data.get("message", {})
        return {
            "content": msg.get("content", ""),
            "tool_calls": msg.get("tool_calls"),
            "message": msg,
        }


async def chat_completion_stream(
    messages: list[dict],
    *,
    model: str | None = None,
) -> AsyncIterator[str]:
    """Stream a chat completion from Ollama. Yields text chunks."""
    settings = get_settings()
    payload = {
        "model": model or settings.ollama_model,
        "messages": messages,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream(
            "POST",
            f"{settings.ollama_base_url}/api/chat",
            json=payload,
        ) as resp:
            resp.raise_for_status()
            import json
            async for line in resp.aiter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue


async def vision_analysis(
    image_url: str,
    prompt: str,
    *,
    model: str | None = None,
) -> str:
    """Analyze an image using Ollama vision model."""
    settings = get_settings()
    # For Ollama vision, we pass the image as a URL in the message
    messages = [
        {
            "role": "user",
            "content": prompt,
            "images": [image_url],
        }
    ]
    payload = {
        "model": model or settings.ollama_model,
        "messages": messages,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{settings.ollama_base_url}/api/chat",
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "")
