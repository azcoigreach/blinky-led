from __future__ import annotations

from datetime import datetime
from typing import Protocol
from xml.etree import ElementTree

from app.providers.base import NewsItem, NewsSnapshot, ProviderResultMeta
from app.services.headlines import dedupe_headlines
from app.services.http import fetch_json, fetch_text


class NewsProvider(Protocol):
    async def fetch_news(self) -> NewsSnapshot:
        ...


class FixtureNewsProvider:
    def __init__(self, *, headlines: list[str], source_label: str = "fixture-news") -> None:
        self.headlines = headlines
        self.source_label = source_label

    async def fetch_news(self) -> NewsSnapshot:
        unique = dedupe_headlines([str(item) for item in self.headlines])
        items = [NewsItem(title=title) for title in unique]
        return NewsSnapshot(items=items, meta=ProviderResultMeta(source_label=self.source_label))


class RssNewsProvider:
    def __init__(self, *, feed_url: str, source_label: str = "rss") -> None:
        self.feed_url = feed_url
        self.source_label = source_label

    async def fetch_news(self) -> NewsSnapshot:
        body = await fetch_text(self.feed_url)
        root = ElementTree.fromstring(body)
        titles: list[str] = []
        for element in root.iter():
            if element.tag.lower().endswith("title") and element.text:
                titles.append(element.text.strip())
        cleaned = dedupe_headlines([title for title in titles if title])
        # Skip the first title because it is typically the channel title.
        items = [NewsItem(title=title) for title in cleaned[1:8]]
        if not items:
            raise RuntimeError("rss feed returned no headlines")
        return NewsSnapshot(
            items=items,
            meta=ProviderResultMeta(source_label=self.source_label, debug={"feed_url": self.feed_url}),
        )


class NewsApiProvider:
    def __init__(self, *, api_key: str | None, query: str = "markets", source_label: str = "newsapi") -> None:
        self.api_key = api_key
        self.query = query
        self.source_label = source_label

    async def fetch_news(self) -> NewsSnapshot:
        if not self.api_key:
            raise RuntimeError("NEWS_API_KEY is required for newsapi provider")
        payload = await fetch_json(
            "https://newsapi.org/v2/everything",
            params={"q": self.query, "pageSize": 8, "sortBy": "publishedAt", "apiKey": self.api_key},
        )
        articles = payload.get("articles", [])
        items: list[NewsItem] = []
        for article in articles:
            title = str(article.get("title") or "").strip()
            if not title:
                continue
            published = article.get("publishedAt")
            published_at: datetime | None = None
            if isinstance(published, str) and published:
                try:
                    published_at = datetime.fromisoformat(published.replace("Z", "+00:00"))
                except ValueError:
                    published_at = None
            items.append(NewsItem(title=title, url=article.get("url"), published_at=published_at))
        if not items:
            raise RuntimeError("newsapi returned no headlines")
        return NewsSnapshot(items=items, meta=ProviderResultMeta(source_label=self.source_label))


def build_news_provider(config: dict, *, source_label: str, news_api_key: str | None = None) -> NewsProvider:
    provider_name = str(config.get("provider", "fixture")).lower()
    if provider_name == "rss":
        feed_url = str(config.get("feed_url", "https://feeds.reuters.com/reuters/businessNews"))
        return RssNewsProvider(feed_url=feed_url, source_label=source_label or "rss")
    if provider_name == "newsapi":
        return NewsApiProvider(
            api_key=config.get("api_key") or news_api_key,
            query=str(config.get("query", "markets")),
            source_label=source_label or "newsapi",
        )
    fixture_headlines = config.get(
        "fixture_headlines",
        [
            "Markets mixed ahead of CPI",
            "Energy prices edge lower",
            "Treasury yields drift lower",
        ],
    )
    return FixtureNewsProvider(
        headlines=[str(item) for item in fixture_headlines],
        source_label=source_label or "fixture-news",
    )
