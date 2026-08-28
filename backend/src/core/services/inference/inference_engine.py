import logging
from core.services.rag.hybrid_retriever import hybrid_search
from core.services.rag.reranker import rerank_chunks
from core.services.rag.query_translator import translate_query
from core.services.llm.base_llm import BaseLLM
from core.prompts.chain import run_rag_chain
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import faiss

logger = logging.getLogger(__name__)

def run_inference(
        query: str,
        chunks: list[dict],
        faiss_index: faiss.IndexFlatIP,
        bm25: BM25Okapi,
        embedding_model: SentenceTransformer,
        reranker: CrossEncoder,
        llm: BaseLLM,
        retrieval_top_k: int = 10,
        rerank_top_k: int = 3,
        conversation_history: list[dict] | None = None
    ) -> dict:
    """
    Run the full inference pipeline: retrieve, rerank, and generate answer.

    Args:
        query: The user's question
        chunks: Full list of indexed chunks
        faiss_index: Built FAISS index for semantic search
        bm25: Fitted BM25 index for keyword search
        embedding_model: SentenceTansformer model for query embedding
        reranker: CrossEncoder model for reranking
        llm: Initialized LLM backend instance
        retrieval_top_k: Number of candidates to retrieve before reranking (default: 10)
        rerank_top_k: Number of final chunks after reranking to send to LLM (default: 3)

    Returns:
        Dict containing 'answer', 'sources', and 'query'
    """
    logger.info(f"Starting Inference for query: '{query}'")

    translated_query, detected_lang = translate_query(query)
    if detected_lang == 'id':
        logger.info(f"Query translated for retrieval: '{translated_query}'")

    # Hybrid Retrieval 
    retrieved_en = hybrid_search(
        query=translated_query,
        chunks=chunks,
        faiss_index=faiss_index,
        bm25=bm25,
        embedding_model=embedding_model,
        top_k=retrieval_top_k // 2
    )

    retrieved_id = hybrid_search(
        query=query,
        chunks=chunks,
        faiss_index=faiss_index,
        bm25=bm25,
        embedding_model=embedding_model,
        top_k=retrieval_top_k // 2
    )

    seen = set()
    combined = []
    for chunk in retrieved_en + retrieved_id:
        key = chunk['text'][:100]
        if key not in seen:
            seen.add(key)
            combined.append(chunk)
    
    logger.info(f"Combined retrieval: {len(retrieved_en)} EN + {len(retrieved_id)} ID = {len(combined)} unique chunks")

    # Reranking 
    reranked = rerank_chunks(
        query=translated_query,
        chunks=combined,
        reranker=reranker,
        top_k=rerank_top_k
    )

    # Generate Answer from LLM base on chunk 
    result = run_rag_chain(
        query=query,
        chunks=reranked,
        llm=llm,
        conversation_history=conversation_history
    )

    # Add query to result 
    result["query"] = query
    result["detected_language"] = detected_lang

    logger.info(f"Inference completed - query: '{query}' | lang: {detected_lang}")
    return result