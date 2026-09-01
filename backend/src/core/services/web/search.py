import logging
from urllib.parse import urlparse
from ddgs import DDGS
from ddgs.exceptions import DDGSException, RatelimitException

logger = logging.getLogger(__name__)

def _is_trusted_domain(url: str, trusted_domains: list[str]) -> bool:
    """Check if host URL match with allowlist domain."""
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return any(netloc == d or netloc.endswith(f".{d}") for d in trusted_domains)

def search_web(query: str, max_results: int = 5, trusted_domains: list[str] | None = None) -> list[dict]:
    """
    Search the web via DuckDuckGo. Best-effort: returns [] on rate limit,
    network error, or any search failure - never raises.

    If trusted_domains is given, results are filtered to ONLY those hosts
    (or subdomains) before trimming to max_results. Since untrusted results
    get dropped, a larger raw pool is requested internally so filtering
    doesn't strave the final count.
    """
    search_pool_size = max(max_results * 4 ,15) if trusted_domains else max_results
    logger.info(f"Searching web for: '{query}' (pool={search_pool_size}) (trusted_only={bool(trusted_domains)})")

    try:
        with DDGS() as ddgs:
            raw_results = ddgs.text(query, max_results=search_pool_size)
    except RatelimitException:
        logger.warning("DuckDuckGo rate limit hit, returning no web results")
        return []
    except DDGSException as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during web search: {e}")
        return []

    results = [
        {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
        for r in raw_results
        if r.get("href")
    ]

    if trusted_domains:
        filtered = [r for r in results if _is_trusted_domain(r["url"], trusted_domains)]
        logger.info(f"Filtered to {len(filtered)}/{len(results)} trusted-domain result(s)")
        results = filtered

    results = results[:max_results]
    logger.info(f"Web search returned {len(results)} result(s)")
    return results