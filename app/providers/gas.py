from __future__ import annotations

from typing import Protocol

from app.providers.base import GasPrice, ProviderResultMeta
from app.services.http import post_form_json


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
    """AAA gas provider via gasprices.aaa.com WordPress AJAX endpoint."""

    def __init__(self, *, endpoint: str, region: str, source_label: str = "aaa") -> None:
        self.endpoint = endpoint
        self.region = region.upper()
        self.source_label = source_label

    async def fetch_gas_price(self) -> GasPrice:
        payload = await post_form_json(
            self.endpoint,
            data={
                "action": "states_cost_data",
                "data[locL]": self.region,
                "data[locR]": "US",
            },
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Origin": "https://gasprices.aaa.com",
                "Referer": "https://gasprices.aaa.com/",
                "User-Agent": "Mozilla/5.0",
            },
        )
        if not bool(payload.get("success")):
            raise RuntimeError("aaa gas provider returned unsuccessful response")
        data = payload.get("data")
        if not isinstance(data, dict):
            raise RuntimeError("aaa gas provider returned unexpected payload shape")
        unleaded = data.get("unleaded")
        if not isinstance(unleaded, list) or not unleaded:
            raise RuntimeError("aaa gas provider response missing unleaded prices")

        return GasPrice(
            usd_per_gallon=float(unleaded[0]),
            region=self.region,
            meta=ProviderResultMeta(
                source_label=self.source_label,
                debug={"endpoint": self.endpoint, "action": "states_cost_data"},
            ),
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
        endpoint = str(config.get("endpoint", "https://gasprices.aaa.com/wp-admin/admin-ajax.php")).strip()
        return AaaGasProvider(endpoint=endpoint, region=region, source_label=source_label or "aaa")
    return FixtureGasProvider(
        usd_per_gallon=float(config.get("fixture_price", 3.89)),
        region=region,
        source_label=source_label or "fixture-gas",
    )
