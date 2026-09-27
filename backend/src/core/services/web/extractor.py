import logging
import trafilatura
from bs4 import BeautifulSoup
import fitz
import io
import pdfplumber
from core.services.processing.pdf_tables import extract_page_tables_text

logger = logging.getLogger(__name__)

MAX_PDF_PAGES = 30
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

def extract_pdf_content(pdf_bytes: bytes, url: str) -> dict | None:
    """
    Extract text from PDFs found through a web search (e.g. WHO/UNICEF/Ministry of Health reports published as pdf files, not HTML articles)
    """
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            title = (doc.metadata or {}).get("title") or ""

            try:
                plumber_doc = pdfplumber.open(io.BytesIO(pdf_bytes))
            except Exception as e:
                logger.warning(f"pdfplumber failed to open PDF from {url}, tables won't be extracted: {e}")
                plumber_doc = None

            pages_text = []
            for i, page in enumerate(doc):
                if i >= MAX_PDF_PAGES:
                    logger.info(f"Reached {MAX_PDF_PAGES}-oage cap for {url}, stopping extraction early")
                    break

                text = page.get_text()
                if plumber_doc is not None and i < len(plumber_doc.pages):
                    text += extract_page_tables_text(plumber_doc.pages[i])
                pages_text.append(text)

            if plumber_doc is not None:
                plumber_doc.close()

    except Exception as e:
        logger.warning(f"Failed to parse PDF from {url}: {e}")
        return None

    text = "\n".join(pages_text).strip()

    if len(text) < MIN_EXTRACTED_LENGTH:
        logger.warning(f"No meaningful content extracted from PDF at {url}")
        return None

    return {"text": text, "title": title.strip() or url}