from __future__ import annotations

from typing import Any

import httpx


async def fetch_json(url: str, timeout: float = 8.0) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
