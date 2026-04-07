from __future__ import annotations

from typing import Any

import httpx


async def fetch_json(url: str, timeout: float = 8.0, params: dict[str, Any] | None = None) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_text(url: str, timeout: float = 8.0, params: dict[str, Any] | None = None) -> str:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.text
