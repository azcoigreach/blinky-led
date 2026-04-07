from __future__ import annotations

from typing import Protocol

from app.providers.base import GasPrice, ProviderResultMeta
from app.services.http import fetch_json


class GasProvider(Protocol):
    async def fetch_gas_price(self) -> GasPrice:
        ...


class FixtureGasProvider:
    def __init__(self, *, usd_per_gallon: float, region: str, source_label: str = "fixture-gas") -> None:
        self.usd_per_gallon = usd_per_gallon
        self.region = region
        self.source_label = source_label

    async def fetch_gas_price(self) -> GasPrice:
        return GasPrice(
            usd_per_gallon=self.usd_per_gallon,
            region=self.region,
            meta=ProviderResultMeta(source_label=self.source_label),
        )


class ManualGasProvider:
    def __init__(self, *, manual_price: float, region: str, source_label: str = "manual-gas") -> None:
        self.manual_price = manual_price
        self.region = region
        self.source_label = source_label

    async def fetch_gas_price(self) -> GasPrice:
        return GasPrice(
            usd_per_gallon=self.manual_price,
            region=self.region,
            meta=ProviderResultMeta(source_label=self.source_label),
        )


class AaaGasProvider:
    """Adapter-ready provider for future AAA integration."""

    def __init__(self, *, endpoint: str, region: str, source_label: str = "aaa") -> None:
        self.endpoint = endpoint
        self.region = region
        self.source_label = source_label

    async def fetch_gas_price(self) -> GasPrice:
        payload = await fetch_json(self.endpoint, params={"region": self.region})
        return GasPrice(
            usd_per_gallon=float(payload.get("usd_per_gallon", 0.0)),
            region=str(payload.get("region", self.region)),
            meta=ProviderResultMeta(source_label=self.source_label, debug={"endpoint": self.endpoint}),
        )


def build_gas_provider(config: dict, *, source_label: str) -> GasProvider:
    provider_name = str(config.get("provider", "fixture")).lower()
    region = str(config.get("region", "US"))
    if provider_name == "manual":
        return ManualGasProvider(
            manual_price=float(config.get("manual_price", config.get("fixture_price", 3.89))),
            region=region,
            source_label=source_label or "manual-gas",
        )
    if provider_name == "aaa":
        endpoint = str(config.get("endpoint", "")).strip()
        if not endpoint:
            raise RuntimeError("aaa gas provider requires config.endpoint")
        return AaaGasProvider(endpoint=endpoint, region=region, source_label=source_label or "aaa")
    return FixtureGasProvider(
        usd_per_gallon=float(config.get("fixture_price", 3.89)),
        region=region,
        source_label=source_label or "fixture-gas",
    )
