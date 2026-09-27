import time
import logging
import requests
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

logger = logging.getLogger(__name__)

USER_AGENT = "NutriGuideBot/1.0 (+educational portfolio project)"

def _is_allowed_by_robots(url: str, user_agent: str = USER_AGENT) -> bool:
    """Fails open (allowed) if robots.txt itself can't be read - don't let a
    missing/broken robots.txt block a page that's otherwise fine to fetch."""
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True

def fetch_page(url: str, timeout: int = 8) -> tuple[str | bytes, str] | None:
    """
    Fetch one URL's raw content, respecting robots.txt. Returns (content, content_type) -
    content is decode text for HTML, raw bytes for PDF. Returns None if disallowed,
    unsupported content-type, or fetch fails. Never raises.
    """
    if not _is_allowed_by_robots(url):
        logger.info(f"Skipped (robots.txt disallows): {url}")
        return None

    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()

        if content_type == "text/html":
            return response.text, content_type

        if content_type == "application/pdf":
            return response.content, content_type

        logger.info(f"Skipped (unsupported content-type={content_type}): {url}")
        return None
    
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None

def fetch_pages(urls: list[str], timeout: int = 8, delay_seconds: float = 0.5) -> dict[str, tuple[str | bytes, str]]:
    """Fetch multiple URLs sequentially with a small delay between requests
    (polinteness). Returns {url: (content, content_type)} only for URLs that succeeded."""
    pages = {}
    for i, url in enumerate(urls):
        result = fetch_page(url, timeout=timeout)
        if result:
            pages[url] = result
        if i < len(urls) - 1:
            time.sleep(delay_seconds)
    return pages