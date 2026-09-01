import logging
from sentence_transformers import CrossEncoder

from core.services.web.search import search_web
from core.services.web.fetcher import fetch_pages
from core.services.web.extractor import extract_content
from core.services.processing.preprocessor import clean_text, is_meaningful
from core.services.processing.chunker import create_chunker
from core.services.rag.reranker import rerank_chunks
from config.settings import TRUSTED_HEALTH_DOMAINS

logger = logging.getLogger(__name__)

def _build_web_chunks(pages: dict[str, str], chunk_size: int = 512, chunk_overlap: int = 128) -> list[dict]:
    """
    Extract, clean, and chunk fetched HTML into PDF-chunk-compatible dicts
    (same 'txt' + 'metadata' shape as PDF chunks, tagged source_type='web').
    """
    chunker = create_chunker(chunk_size, chunk_overlap)
    all_chunks = []

    for url, html in pages.items():
        extracted = extract_content(html, url)
        if not extracted:
            continue

        cleaned = clean_text(extracted["text"])
        if not is_meaningful(cleaned):
            logger.info(f"Skipped (not meaningful after cleaning): {url}")
            continue

        raw_chunks = chunker.split_text(cleaned)
        for idx, chunk_text in enumerate(raw_chunks):
            if len(chunk_text.strip()) < 30:
                continue
            all_chunks.append({
                "text": chunk_text.strip(),
                "metadata": {
                    "source": url,
                    "title": extracted["title"],
                    "chunk_index": idx,
                    "source_type": "web"
                }
            })

    return all_chunks

def retrieve_web_context(
        query: str,
        reranker: CrossEncoder,
        max_search_results: int = 5,
        rerank_top_k: int = 3,
        fetch_timeout: int = 8,
        trusted_domains: list[str] | None = None
) -> list[dict]:
    """
    Full pipeline: search -> fetch -> extract -> clean -> chunk -> rerank.

    Best-effort at every stage - returns [] (never raises) if search fails,
    every page fails to fetch, or nothing extractable is found. Caller should
    treat [] as "no web context available" and fallback to other sourecs.
    """
    domains = trusted_domains if trusted_domains is not None else TRUSTED_HEALTH_DOMAINS
    results = search_web(query, max_results=max_search_results, trusted_domains=domains)
    if not results:
        logger.info(f"No web search results, skipping web retrieval")
        return []

    urls = [r["url"] for r in results]
    pages = fetch_pages(urls, timeout=fetch_timeout)
    if not pages:
        logger.info("No pages successfully fetched, skipping web retrieval")
        return []

    chunks = _build_web_chunks(pages)
    if not chunks:
        logger.info("No usable chunks extracted from fetched pages")
        return []

    reranked = rerank_chunks(query, chunks, reranker, top_k=rerank_top_k)
    logger.info(f"Wen retrieval completed: {len(reranked)} chunk(s) selected from {len(pages)} pag(s)")
    return reranked