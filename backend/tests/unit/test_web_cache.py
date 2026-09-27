import time
from src.core.services.web.web_cache import WebCache

def test_get_returns_none_when_empty():
    assert WebCache().get("child's fever") is None

def test_set_then_get_returns_cached_chunks():
    cache = WebCache()
    chunks = [{"text": "content", "metadata": {"source": "https://who.int/x"}}]
    cache.set("child's fever", chunks)
    assert cache.get("child's fever") == chunks

def test_get_is_case_and_whitespace_insentive():
    cache = WebCache()
    cache.set("  Child's Fever  ", [{"text": "content"}])
    assert cache.get("child's fever") == [{"text": "content"}]

def test_entry_expires_adter_ttl():
    cache = WebCache(ttl_seconds=0.05)
    cache.set("child's fever", [{"text": "content"}])
    time.sleep(0.1)
    assert cache.get("child's fever") is None

def test_different_queries_are_isolated():
    cache = WebCache()
    cache.set("child's fever", [{"text": "a"}])
    assert cache.get("healthy food") is None