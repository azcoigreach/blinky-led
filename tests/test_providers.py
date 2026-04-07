import pytest

from app.providers.crypto import FixtureCryptoProvider, build_crypto_provider
from app.providers.gas import build_gas_provider
from app.providers.markets import build_market_provider
from app.providers.news import build_news_provider
from app.providers.polls import build_poll_provider
from app.widgets.crypto import CryptoWidget
from app.widgets.gas import GasWidget
from app.widgets.news import NewsWidget
from app.widgets.poll import PollWidget
from app.widgets.stocks import StocksWidget


@pytest.mark.asyncio
async def test_fixture_news_provider_normalizes_and_dedupes() -> None:
    provider = build_news_provider(
        {"provider": "fixture", "fixture_headlines": ["A", "A", "B"]},
        source_label="fixture-news",
    )
    snapshot = await provider.fetch_news()

    assert [item.title for item in snapshot.items] == ["A", "B"]
    assert snapshot.meta.source_label == "fixture-news"


@pytest.mark.asyncio
async def test_fixture_crypto_provider_returns_quote() -> None:
    provider = FixtureCryptoProvider(price=12345.0, change_percent=-1.5)
    quote = await provider.fetch_quote("BTCUSDT")

    assert quote.symbol == "BTCUSDT"
    assert quote.price == 12345.0
    assert quote.change_percent == -1.5


def test_marketdata_provider_requires_endpoint() -> None:
    with pytest.raises(RuntimeError):
        build_market_provider({"provider": "marketdata"}, source_label="market-api")


@pytest.mark.asyncio
async def test_widget_uses_fixture_crypto_provider_from_config() -> None:
    widget = CryptoWidget(
        "crypto",
        config={
            "provider": "fixture",
            "symbol": "BTCUSDT",
            "fixture_price": 64000,
            "fixture_change_percent": 2.25,
        },
        source_label="fixture-crypto",
    )
    data = await widget.fetch_primary()

    assert data.source_label == "fixture-crypto"
    assert data.extra["symbol"] == "BTCUSDT"
    assert data.delta == "+2.25%"


@pytest.mark.asyncio
async def test_widget_provider_selection_for_markets_poll_gas_news() -> None:
    stocks = StocksWidget(
        "stocks",
        config={"provider": "fixture", "symbol": "ES1!", "market_type": "futures", "fixture_price": 5100, "fixture_delta": -0.4},
        source_label="fixture-market",
    )
    poll = PollWidget(
        "poll",
        config={"provider": "fixture", "candidate": "Candidate A", "fixture_percent": 47.3},
        source_label="fixture-poll",
    )
    gas = GasWidget(
        "gas",
        config={"provider": "manual", "manual_price": 3.67, "region": "CA"},
        source_label="manual-gas",
    )
    news = NewsWidget(
        "news",
        config={"provider": "fixture", "fixture_headlines": ["X", "Y", "Y"]},
        source_label="fixture-news",
    )

    stocks_data = await stocks.fetch_primary()
    poll_data = await poll.fetch_primary()
    gas_data = await gas.fetch_primary()
    news_data = await news.fetch_primary()

    assert stocks_data.source_label == "fixture-market"
    assert stocks_data.extra["market_type"] == "futures"
    assert poll_data.source_label == "fixture-poll"
    assert poll_data.value.startswith("Candidate A")
    assert gas_data.source_label == "manual-gas"
    assert gas_data.value == "$3.67/gal"
    assert news_data.source_label == "fixture-news"
    assert news_data.extra["headline_count"] == 2


def test_poll_and_gas_provider_builders_support_modes() -> None:
    fixture_poll = build_poll_provider({"provider": "fixture", "candidate": "A", "fixture_percent": 51.0}, source_label="fixture-poll")
    manual_gas = build_gas_provider({"provider": "manual", "manual_price": 4.01}, source_label="manual-gas")

    assert fixture_poll.__class__.__name__ == "FixturePollProvider"
    assert manual_gas.__class__.__name__ == "ManualGasProvider"


def test_crypto_provider_builder_supports_coingecko() -> None:
    provider = build_crypto_provider({"provider": "coingecko"}, source_label="coingecko")
    assert provider.__class__.__name__ == "CoinGeckoProvider"
