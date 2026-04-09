from __future__ import annotations

from datetime import UTC, datetime

from app.core.market_data import FuturesQuoteNormalized
from app.services.http import fetch_json


def default_contract_aliases() -> dict[str, str]:
    return {
        "ES": "ES=F",
        "NQ": "NQ=F",
        "YM": "YM=F",
        "CL": "CL=F",
        "GC": "GC=F",
    }


class YahooFuturesProvider:
    def __init__(
        self,
        *,
        source: str = "yahoo-futures",
        aliases: dict[str, str] | None = None,
        base_url: str = "https://query1.finance.yahoo.com/v8/finance/chart",
    ) -> None:
        self.source = source
        self.aliases = aliases or default_contract_aliases()
        self.base_url = base_url.rstrip("/")

    async def fetch_quote(self, contract: str, *, label: str | None = None) -> FuturesQuoteNormalized:
        mapped = self.aliases.get(contract, contract)
        payload = await fetch_json(f"{self.base_url}/{mapped}", params={"range": "1d", "interval": "1m"})
        result = (payload.get("chart", {}).get("result") or [None])[0]
        if result is None:
            raise RuntimeError(f"yahoo futures quote missing for {contract}")

        meta = result.get("meta", {})
        price = float(meta.get("regularMarketPrice") or 0.0)
        previous_close = float(meta.get("chartPreviousClose") or meta.get("previousClose") or 0.0)
        absolute_change = price - previous_close
        percent_change = (absolute_change / previous_close * 100.0) if previous_close else 0.0
        ts = int(meta.get("regularMarketTime") or 0)
        timestamp = datetime.fromtimestamp(ts, tz=UTC) if ts else datetime.now(UTC)
        return FuturesQuoteNormalized(
            contract=contract,
            root_symbol=_root_symbol(contract),
            label=label or contract,
            price=price,
            absolute_change=absolute_change,
            percent_change=percent_change,
            session=str(meta.get("marketState") or "regular").lower(),
            timestamp=timestamp,
            source=self.source,
            stale=ts == 0,
        )

    async def fetch_quotes(
        self,
        contracts: list[str],
        *,
        labels: dict[str, str] | None = None,
        aliases: dict[str, str] | None = None,
    ) -> list[FuturesQuoteNormalized]:
        if aliases:
            merged_aliases = dict(self.aliases)
            merged_aliases.update(aliases)
            self.aliases = merged_aliases
        labels = labels or {}
        quotes: list[FuturesQuoteNormalized] = []
        for contract in contracts:
            quotes.append(await self.fetch_quote(contract, label=labels.get(contract)))
        return quotes


def _root_symbol(contract: str) -> str:
    return "".join(ch for ch in contract if ch.isalpha()) or contract
