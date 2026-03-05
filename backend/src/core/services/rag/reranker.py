from sentence_transformers import CrossEncoder
import logging

logger = logging.getLogger(__name__)

DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

def load_reranker(model_name: str = DEFAULT_RERANKER_MODEL) -> CrossEncoder:
    """
    Load a CrossEncoder model for reranking retrieved chunks.

    Args:
        model_name: HuggingFace model name for the cross-encoder (default: ms-marco-MiniLM-L-6-v2)

    Returns:
        Loaded CrossEncoder instance
    """
    logger.info(f"Loading reranker model: {model_name}")

    model = CrossEncoder(model_name)

    logger.info("Reranker model loaded successfully")
    return model

def rerank_chunks(
        query: str,
        chunks: list[dict],
        reranker: CrossEncoder,
        top_k: int = 3
    ) -> list[dict]:
    """
    Reranker retrieved chunks based on relevance to the query using a cross-encoder.

    Args:
        query: Raw query string from the user
        chunks: List of candidate chunks from hybrid retrieval
        reranker: Loaded CrossEncoder instance
        top_k: Number of top chunks to return after reranking (default: 3)

    Returns:
        List of reranked chunk dicts sorted by descending relevance score
    """
    if not chunks:
        logger.warning("Empty chunks received for reranking, returning empty list")
        return []
    
    logger.info(f"Reranking {len(chunks)} chunks for query: '{query}'")

    pairs = [(query, chunk["text"]) for chunk in chunks]
    scores = reranker.predict(pairs)

    scored_chunks = list(zip(chunks, scores))
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    reranked = []
    for chunk, score in scored_chunks[:top_k]:
        chunk = chunk.copy()
        chunk["metadata"]["reranker_score"] = round(float(score), 6)
        reranked.append(chunk)

    logger.info(f"Reranking completed: {len(reranked)} chunks choosen")
    return reranked