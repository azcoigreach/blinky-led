from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

AssetType = Literal["stock", "market_proxy", "future", "crypto"]


@dataclass(slots=True)
class StockQuoteNormalized:
    symbol: str
    label: str
    price: float
    absolute_change: float
    percent_change: float
    previous_close: float
    day_high: float | None
    day_low: float | None
    market_state: str
    timestamp: datetime
    source: str
    stale: bool = False
    asset_type: AssetType = "stock"


@dataclass(slots=True)
class MarketOverviewQuote:
    symbol: str
    label: str
    price: float
    absolute_change: float
    percent_change: float
    market_state: str
    timestamp: datetime
    source: str
    stale: bool = False
    asset_type: AssetType = "market_proxy"


@dataclass(slots=True)
class FuturesQuoteNormalized:
    contract: str
    root_symbol: str
    label: str
    price: float
    absolute_change: float
    percent_change: float
    session: str
    timestamp: datetime
    source: str
    stale: bool = False
    asset_type: AssetType = "future"


@dataclass(slots=True)
class CryptoQuoteNormalized:
    symbol: str
    label: str
    price: float
    absolute_change: float | None
    percent_change_24h: float
    timestamp: datetime
    source: str
    stale: bool = False
    asset_type: AssetType = "crypto"


def utc_now() -> datetime:
    return datetime.now(UTC)
