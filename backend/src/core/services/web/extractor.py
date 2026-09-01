import logging
import trafilatura
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

MIN_EXTRACTED_LENGTH = 200

def extract_content(html: str, url: str) -> dict | None:
    """
    Trafilatura first (strips nav/ads/boilerplate well), fall back to a
    plain BeautifulSoup text dump if trafilatura returns nothing useable.
    """
    text = trafilatura.extract(
        html, url=url, include_comments=False, include_tables=False, favor_recall=True
    )

    title = None
    metadata = trafilatura.extract_metadata(html)
    if metadata:
        title = metadata.title

    if not text or len(text.strip()) < MIN_EXTRACTED_LENGTH:
        logger.info(f"Trafilatura extraction too short/empty for {url}, falling back to BeautifulSoup")
        text, fallback_title = _extract_with_bs4(html)
        title = title or fallback_title

    if not text or len(text.strip()) < MIN_EXTRACTED_LENGTH:
        logger.warning(f"No meaningful content extraxted from {url}")
        return None

    return {"text": text.strip(), "title": title or url}

def _extract_with_bs4(html: str) -> tuple[str | None, str | None]:
    try:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        title_tag = soup.find("title")
        title = title_tag.get_text().strip() if title_tag else None
        text = soup.get_text(separator="\n")
        return text, title
    except Exception as e:
        logger.warning(f"BeautifulSoup fallback failed: {e}")
        return None, None