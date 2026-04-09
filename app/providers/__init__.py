from app.providers.crypto import (
    BinanceProvider,
    CoinGeckoCryptoProvider,
    CoinGeckoProvider,
    FixtureCryptoProvider,
    build_crypto_provider,
)
from app.providers.futures import YahooFuturesProvider
from app.providers.gas import AaaGasProvider, FixtureGasProvider, ManualGasProvider, build_gas_provider
from app.providers.markets import (
    FixtureMarketProvider,
    MarketDataProvider,
    ProxyEtfMarketProvider,
    build_market_provider,
)
from app.providers.news import FixtureNewsProvider, NewsApiProvider, RssNewsProvider, build_news_provider
from app.providers.polls import ExternalPollProvider, FixturePollProvider, build_poll_provider
from app.providers.stocks import AlphaVantageStockProvider, FinnhubStockProvider

__all__ = [
    "AaaGasProvider",
    "BinanceProvider",
    "CoinGeckoCryptoProvider",
    "CoinGeckoProvider",
    "ExternalPollProvider",
    "FixtureCryptoProvider",
    "FixtureGasProvider",
    "FixtureMarketProvider",
    "FixtureNewsProvider",
    "FixturePollProvider",
    "ManualGasProvider",
    "MarketDataProvider",
    "NewsApiProvider",
    "ProxyEtfMarketProvider",
    "RssNewsProvider",
    "YahooFuturesProvider",
    "FinnhubStockProvider",
    "AlphaVantageStockProvider",
    "build_crypto_provider",
    "build_gas_provider",
    "build_market_provider",
    "build_news_provider",
    "build_poll_provider",
]
