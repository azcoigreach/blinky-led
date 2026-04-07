from __future__ import annotations

from typing import Protocol

from app.providers.base import PollReading, ProviderResultMeta
from app.services.http import fetch_json


class PollProvider(Protocol):
    async def fetch_poll(self) -> PollReading:
        ...


class FixturePollProvider:
    def __init__(self, *, candidate: str, percent: float, source_label: str = "fixture-poll") -> None:
        self.candidate = candidate
        self.percent = percent
        self.source_label = source_label

    async def fetch_poll(self) -> PollReading:
        return PollReading(
            candidate=self.candidate,
            percent=self.percent,
            meta=ProviderResultMeta(source_label=self.source_label),
        )


class ExternalPollProvider:
    """Placeholder external provider with adapter-friendly response mapping."""

    def __init__(
        self,
        *,
        endpoint: str,
        candidate_field: str = "candidate",
        percent_field: str = "percent",
        source_label: str = "poll-api",
    ) -> None:
        self.endpoint = endpoint
        self.candidate_field = candidate_field
        self.percent_field = percent_field
        self.source_label = source_label

    async def fetch_poll(self) -> PollReading:
        payload = await fetch_json(self.endpoint)
        candidate = str(payload.get(self.candidate_field, "candidate"))
        percent = float(payload.get(self.percent_field, 0.0))
        return PollReading(
            candidate=candidate,
            percent=percent,
            meta=ProviderResultMeta(source_label=self.source_label, debug={"endpoint": self.endpoint}),
        )


def build_poll_provider(config: dict, *, source_label: str) -> PollProvider:
    provider_name = str(config.get("provider", "fixture")).lower()
    if provider_name == "external":
        endpoint = str(config.get("endpoint", "")).strip()
        if not endpoint:
            raise RuntimeError("external poll provider requires config.endpoint")
        return ExternalPollProvider(
            endpoint=endpoint,
            candidate_field=str(config.get("candidate_field", "candidate")),
            percent_field=str(config.get("percent_field", "percent")),
            source_label=source_label or "poll-api",
        )
    return FixturePollProvider(
        candidate=str(config.get("candidate", "Candidate A")),
        percent=float(config.get("fixture_percent", 49.0)),
        source_label=source_label or "fixture-poll",
    )
