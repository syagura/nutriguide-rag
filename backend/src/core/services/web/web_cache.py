import time
import logging
from threading import Lock

logger = logging.getLogger(__name__)

class WebCache:
    """
    In-memory TTL cache for web retrieval results, the key is the query (which has been
    reformulated, if necessary). Not persistent—it is lost if the backend restarts,
    uses the same lazy-TTL-cleanup pattern as SessionStore
    """

    def __init__(self, ttl_seconds: int = 21600): # 6 hour by default
        self._store: dict[str, dict] = {}
        self._lock = Lock()
        self.ttl_seconds = ttl_seconds

    @staticmethod
    def _normalized_key(query: str) -> str:
        return query.strip().lower()

    def _is_expired(self, entry: dict) -> bool:
        return (time.time() - entry["cached_at"]) > self.ttl_seconds

    def _cleanup_expired(self) -> None:
        expired = [k for k, v in self._store.items() if self._is_expired(v)]
        for k in expired:
            del self._store[k]
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired web cache entry(-ies)")

    def get(self, query: str) -> list[dict] | None:
        key = self._normalized_key(query)
        with self._lock:
            self._cleanup_expired()
            entry = self._store.get(key)
            if entry is None:
                return None
            logger.info(f"Web cache hit for: '{query}'")
            return entry["chunks"]

    def set(self, query: str, chunks: list[dict]) -> None:
        key = self._normalized_key(query)
        with self._lock:
            self._store[key] = {"chunks": chunks, "cached_at": time.time()}

web_cache = WebCache()