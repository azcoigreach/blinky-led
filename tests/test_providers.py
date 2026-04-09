import pytest

from app.core.market_data import CryptoQuoteNormalized
from app.providers.crypto import FixtureCryptoProvider, build_crypto_provider
from app.providers.futures.yahoo import YahooFuturesProvider
import app.providers.gas as gas_module
from app.providers.gas import build_gas_provider
from app.providers.markets import ProxyEtfMarketProvider, build_market_provider
from app.providers.news import build_news_provider
from app.providers.polls import build_poll_provider
from app.providers.stocks.base import FixtureStockProvider
from app.widgets.crypto import CryptoWidget
from app.widgets.futures import FuturesWidget
from app.widgets.gas import GasWidget
from app.widgets.markets import MarketsWidget
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
    assert data.extra["items"][0]["symbol"] == "BTCUSDT"
    assert data.delta == "+2.25%"


@pytest.mark.asyncio
async def test_widget_provider_selection_for_markets_poll_gas_news() -> None:
    stocks = StocksWidget(
        "stocks",
        config={"primary": "fixture", "symbols": ["SPY"], "fixture_price": 5100, "fixture_percent_change": -0.4},
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
    assert stocks_data.extra["items"][0]["symbol"] == "SPY"
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


@pytest.mark.asyncio
async def test_proxy_etf_market_provider_reuses_stock_quotes() -> None:
    stock_provider = FixtureStockProvider(price=600.0, percent_change=0.5, source="fixture-stock")
    provider = ProxyEtfMarketProvider(stock_provider=stock_provider, source="proxy-etf")
    quotes = await provider.fetch_overview(["SPY", "QQQ"], labels={"SPY": "S&P", "QQQ": "NASDAQ"})

    assert len(quotes) == 2
    assert quotes[0].asset_type == "market_proxy"
    assert quotes[0].label == "S&P"


@pytest.mark.asyncio
async def test_futures_widget_disabled_state() -> None:
    widget = FuturesWidget("futures", config={"enabled": False}, source_label="futures")
    data = await widget.fetch_primary()

    assert data.value == "disabled"
    assert data.status_summary == "futures provider disabled"


@pytest.mark.asyncio
async def test_markets_widget_compact_output() -> None:
    widget = MarketsWidget(
        "markets",
        config={
            "symbols": ["DIA", "QQQ", "SPY"],
            "stocks_provider": {"primary": "fixture", "fixture_price": 520.0, "fixture_percent_change": -0.6},
        },
        source_label="markets",
    )
    data = await widget.fetch_primary()

    assert data.title == "Markets"
    assert "DIA" in data.value
    assert data.extra["items"][0]["asset_type"] == "market_proxy"


@pytest.mark.asyncio
async def test_yahoo_futures_provider_parses_chart_payload(monkeypatch) -> None:
    async def fake_fetch_json(url: str, timeout: float = 8.0, params: dict | None = None) -> dict:
        return {
            "chart": {
                "result": [
                    {
                        "meta": {
                            "regularMarketPrice": 5050.25,
                            "chartPreviousClose": 5000.0,
                            "regularMarketTime": 1712505600,
                            "marketState": "REGULAR",
                        }
                    }
                ]
            }
        }

    import app.providers.futures.yahoo as yahoo_module

    monkeypatch.setattr(yahoo_module, "fetch_json", fake_fetch_json)
    provider = YahooFuturesProvider(source="yahoo", aliases={"ES": "ES=F"})
    quote = await provider.fetch_quote("ES")

    assert quote.contract == "ES"
    assert quote.root_symbol == "ES"
    assert quote.asset_type == "future"
    assert quote.percent_change > 0


@pytest.mark.asyncio
async def test_fixture_crypto_batch_shape() -> None:
    provider = FixtureCryptoProvider(price=2000.0, change_percent=1.0)
    quotes = await provider.fetch_quotes(["BTC", "ETH"])
    assert isinstance(quotes[0], CryptoQuoteNormalized)
    assert quotes[1].symbol == "ETH"


@pytest.mark.asyncio
async def test_aaa_gas_provider_fetches_current_unleaded(monkeypatch) -> None:
    async def fake_post_form_json(
        url: str,
        timeout: float = 8.0,
        data: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict:
        assert url == "https://gasprices.aaa.com/wp-admin/admin-ajax.php"
        assert data == {
            "action": "states_cost_data",
            "data[locL]": "CA",
            "data[locR]": "US",
        }
        assert headers is not None
        assert headers.get("Referer") == "https://gasprices.aaa.com/"
        return {
            "success": True,
            "data": {
                "unleaded": ["5.9290000", "4.1190000", "5.9230000", "4.1100000"],
            },
        }

    monkeypatch.setattr(gas_module, "post_form_json", fake_post_form_json)
    provider = build_gas_provider(
        {"provider": "aaa", "region": "ca"},
        source_label="aaa",
    )

    price = await provider.fetch_gas_price()

    assert price.region == "CA"
    assert price.usd_per_gallon == pytest.approx(5.929)
    assert price.meta.source_label == "aaa"


@pytest.mark.asyncio
async def test_aaa_gas_provider_raises_for_unsuccessful_payload(monkeypatch) -> None:
    async def fake_post_form_json(
        url: str,
        timeout: float = 8.0,
        data: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict:
        return {"success": False}

    monkeypatch.setattr(gas_module, "post_form_json", fake_post_form_json)
    provider = build_gas_provider({"provider": "aaa", "region": "US"}, source_label="aaa")

    with pytest.raises(RuntimeError, match="unsuccessful response"):
        await provider.fetch_gas_price()
