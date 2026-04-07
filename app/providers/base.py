from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class ProviderResultMeta:
    source_label: str
    fetched_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    debug: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class NewsItem:
    title: str
    url: str | None = None
    published_at: datetime | None = None


@dataclass(slots=True)
class NewsSnapshot:
    items: list[NewsItem]
    meta: ProviderResultMeta


@dataclass(slots=True)
class CryptoQuote:
    symbol: str
    price: float
    change_percent: float
    meta: ProviderResultMeta


@dataclass(slots=True)
class MarketQuote:
    symbol: str
    price: float
    change_percent: float
    market_type: str
    meta: ProviderResultMeta


@dataclass(slots=True)
class PollReading:
    candidate: str
    percent: float
    meta: ProviderResultMeta


@dataclass(slots=True)
class GasPrice:
    usd_per_gallon: float
    region: str
    meta: ProviderResultMeta
