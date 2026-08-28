import logging
from core.services.llm.base_llm import BaseLLM
from core.prompts.templates import SYSTEM_PROMPT, build_rag_prompt

logger = logging.getLogger(__name__)

def run_rag_chain(query: str, chunks: list[dict], llm: BaseLLM, conversation_history: list[dict] | None = None) -> dict:
    """
    Run the full RAG chain: build prompt from chunks and generate LLM response.

    Args:
        query: The user's question
        chunks: Reranked chunks from the retrieval pipeline
        llm: Initialized LLM backend instance (Groq or local)

    Returns:
        Dict containing 'answer' and 'soruces' used to generate the response
    """
    if not chunks:
        logger.warning("No chunks are given to the RAG chain")
        return {
            "answer": "I'm sorry, I couldn't find relevant information to answer your question.",
            "sources": []
        }
    
    logger.info(f"Running RAG chain with {len(chunks)} chunks - model: {llm.model_name}")

    # Build prompt from chunks
    prompt = build_rag_prompt(query, chunks, conversation_history)

    # Generate prompt from LLM with system prompt 
    answer = llm.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)

    sources = list({
        f"{chunk['metadata'].get('source', 'unknown')} (page {chunk['metadata'].get('page', '?')})"
        for chunk in chunks
    })

    logger.info(f"RAG chain completed - {len(sources)} sources used")

    return {
        "answer": answer,
        "sources": sources
    }