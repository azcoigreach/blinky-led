from app.core.cache import TTLCache


def test_ttl_cache_set_get() -> None:
    cache: TTLCache[str] = TTLCache()
    cache.set("k", "v", ttl_seconds=5)
    assert cache.get("k") == "v"
    assert cache.has("k")
