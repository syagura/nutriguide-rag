import numpy as np
import logging
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import faiss

logger = logging.getLogger(__name__)

RRF_K = 60

def reciprocal_rank_fusion(
        semantic_results: list[tuple[int, float]],
        bm25_results: list[tuple[int, float]],
        top_k: int = 5,
    ) -> list[tuple[int, float]]:
    """
    Combine semantic and BM25 search results using Reciprocal Rank Fusion (RRF).

    Args:
        semantic_resutls: List of (chunk_index, score) from FAISS search
        bm25_results: List of (chunk_index, score) from BM25 search
        top_k: Number of top results to return after fusion (default: 5)

    Returns:
        List of (chunk_index, rrf_score) sorted by descending RRF score
    """
    rrf_scores: dict[int, float] = {}

    for rank, (chunk_idx, _) in enumerate(semantic_results, start=1):
        rrf_scores[chunk_idx] = rrf_scores.get(chunk_idx, 0) + 1 / (RRF_K + rank)

    for rank, (chunk_idx, _) in enumerate(bm25_results, start=1):
        rrf_scores[chunk_idx] = rrf_scores.get(chunk_idx, 0) + 1  / (RRF_K + rank)

    sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_results[:top_k]

def hybrid_search(
        query: str,
        chunks: list[dict],
        faiss_index: faiss.IndexFlatIP,
        bm25: BM25Okapi,
        embedding_model: SentenceTransformer,
        top_k: int = 5
    ) -> list[dict]:
    """
    Perform hybrid search combining semantic (FAISS) and keyword (BM25) retrieval.

    Args:
        query: Raw query string from the user
        chunks: Original list of chunks used to build both indexes
        faiss_index: Built FAISS index for semantic search
        bm25: Fitted BM25kapi instance for keyword search
        embedding_model: Loaded SentenceTransformer model for query embedding
        top_k: Number of final results to return (default: 5)

    Returns: 
        List of chunk dicts sorted by RRF score, ready for reranking
    """
    logger.info(f"Hybrid search for query: '{query}'")

    from core.services.rag.vector_store import search_vector_store
    from core.services.rag.bm25_retriever import search_bm25

    # Embbed query 
    query_embedding = embedding_model.encode(query, convert_to_numpy=True)

    candidate_k = top_k * 2

    semantic_scores, semantic_indices = search_vector_store(faiss_index, query_embedding, top_k=candidate_k)
    semantic_results = list(zip(semantic_indices.tolist(), semantic_scores.tolist()))

    bm25_results = search_bm25(bm25, query, chunks, top_k=candidate_k)
    
    fused_results = reciprocal_rank_fusion(semantic_results, bm25_results, top_k=top_k)

    result_chunks = []
    for chunk_idx, rrf_score in fused_results:
        if 0 <= chunk_idx < len(chunks):
            chunk = chunks[chunk_idx].copy()
            chunk["metadata"]["rrf_score"] = round(rrf_score, 6)
            result_chunks.append(chunk)

    logger.info(f"Hybride search completed: {len(result_chunks)} chunks founded")
    return result_chunks