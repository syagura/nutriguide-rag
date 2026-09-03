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

def _retrieve_pdf_chunks(
        query: str, chunks: list[dict], faiss_index: faiss.IndexFlatIP, bm25: BM25Okapi,
        embedding_model: SentenceTransformer, reranker: CrossEncoder, 
        retrieval_top_k: int, rerank_top_k: int
    ) -> tuple[list[dict], str]:
    """
    Hybrid PDF retrieval + reranking—the logic is exactly the same as before
    (bilingual EN/ID search + fusion), but it’s been extracted into a separate function
    so it can be skipped entirely if the router determines that the PDF isn’t needed.
    """
    translated_query, detected_lang = translate_query(query)
    if detected_lang == 'id':
        logger.info(f"Query translated for retrieval: '{translated_query}'")

    retrieved_en = hybrid_search(
        query=translated_query, chunks=chunks, faiss_index=faiss_index,
        bm25=bm25, embedding_model=embedding_model, top_k=retrieval_top_k // 2
    )
    retrieved_id = hybrid_search(
        query=query, chunks=chunks, faiss_index=faiss_index,
        bm25=bm25, embedding_model=embedding_model, top_k=retrieval_top_k // 2
    )

    seen = set()
    combined = []
    for chunk in retrieved_en + retrieved_id:
        key = chunk['text'][:100]
        if key not in seen:
            seen.add(key)
            combined.append(chunk)

    logger.info(f"Combined retrievsl: {len(retrieved_en)} EN + {len(retrieved_id)} ID = {len(combined)} unique chunks")

    reranked = rerank_chunks(query=translated_query, chunks=combined, reranker=reranker, top_k=rerank_top_k)
    return reranked, detected_lang

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
        conversation_history: list[dict] | None = None,
        web_chunks: list[dict] | None = None,
        retrieve_pdf: bool = True
    ) -> dict:
    """
    Run the inference pipeline: retrieve PDF context, combine with any pre-fetched
    web context and conversation history, then generate.

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
        conversation_history: Recent session message
        web_chunks: Pre-retrieved & tier-sorted web chunks, or None if web retrieval wasn't run
        retrieve_pdf: False skips embedding/BM25/rerank entirely - set by the router when need_pdf is False,
                        so we don't pay for retrieval work that gets thrown away

    Returns:
        Dict containing 'answer', 'sources', and 'query'
    """
    logger.info(f"Starting Inference for query: '{query}' | retrieve_pdf={retrieve_pdf} | web-chunks={len(web_chunks or [])}")

    detected_lang = "id"
    pdf_chunks: list[dict] = []

    if retrieve_pdf:
        pdf_chunks, deteceted_lang = _retrieve_pdf_chunks(
            query, chunks, faiss_index, bm25, embedding_model, reranker,
            retrieval_top_k, rerank_top_k
        )

    result = run_rag_chain(
        query=query,
        llm=llm,
        pdf_chunks=pdf_chunks,
        web_chunks=web_chunks,
        conversation_history=conversation_history
    )

    result["query"] = query
    result["detected_language"] = detected_lang

    logger.info(f"Inference completed - query: '{query}' | lang: {detected_lang}")
    return result

    # translated_query, detected_lang = translate_query(query)
    # if detected_lang == 'id':
    #     logger.info(f"Query translated for retrieval: '{translated_query}'")

    # # Hybrid Retrieval 
    # retrieved_en = hybrid_search(
    #     query=translated_query,
    #     chunks=chunks,
    #     faiss_index=faiss_index,
    #     bm25=bm25,
    #     embedding_model=embedding_model,
    #     top_k=retrieval_top_k // 2
    # )

    # retrieved_id = hybrid_search(
    #     query=query,
    #     chunks=chunks,
    #     faiss_index=faiss_index,
    #     bm25=bm25,
    #     embedding_model=embedding_model,
    #     top_k=retrieval_top_k // 2
    # )

    # seen = set()
    # combined = []
    # for chunk in retrieved_en + retrieved_id:
    #     key = chunk['text'][:100]
    #     if key not in seen:
    #         seen.add(key)
    #         combined.append(chunk)
    
    # logger.info(f"Combined retrieval: {len(retrieved_en)} EN + {len(retrieved_id)} ID = {len(combined)} unique chunks")

    # # Reranking 
    # reranked = rerank_chunks(
    #     query=translated_query,
    #     chunks=combined,
    #     reranker=reranker,
    #     top_k=rerank_top_k
    # )

    # # Generate Answer from LLM base on chunk 
    # result = run_rag_chain(
    #     query=query,
    #     chunks=reranked,
    #     llm=llm,
    #     conversation_history=conversation_history
    # )

    # # Add query to result 
    # result["query"] = query
    # result["detected_language"] = detected_lang

    # logger.info(f"Inference completed - query: '{query}' | lang: {detected_lang}")
    # return result