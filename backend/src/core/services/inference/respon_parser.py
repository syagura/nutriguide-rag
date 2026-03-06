import logging

logger = logging.getLogger(__name__)

def parse_response(raw_result: dict) -> dict:
    """
    Parse and clean the raw inference into a structured response.

    Args:
        raw_result: Raw result dict from run_inference() containing 'answer', 'sources', 'query'

    Returns:
        Cleaned and structured response dict ready to be returned by the API
    """
    answer = raw_result.get("answer", "").strip()
    sources = raw_result.get("sources", [])
    query = raw_result.get("query", "").strip()

    if not answer:
        logger.warning("Empty answer after parsing - use fallback message")
        answer = "I'm sorry, I couldn't generate a response. Please try again."

    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "has_sources": len(sources) > 0
    }