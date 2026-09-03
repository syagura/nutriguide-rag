import logging
from core.services.llm.base_llm import BaseLLM
from core.prompts.templates import SYSTEM_PROMPT, build_rag_prompt
from core.services.web.source_priority import get_source_label

logger = logging.getLogger(__name__)

def run_rag_chain(
        query: str, 
        llm: BaseLLM, 
        pdf_chunks: list[dict] | None = None, 
        web_chunks: list[dict] | None = None, 
        conversation_history: list[dict] | None = None
    ) -> dict:
    """
    Run the full RAG chain: build prompt from chunks and generate LLM response.

    Args:
        query: The user's question
        chunks: Reranked chunks from the retrieval pipeline
        llm: Initialized LLM backend instance (Groq or local)

    Returns:
        Dict containing 'answer' and 'soruces' used to generate the response
    """
    pdf_chunks = pdf_chunks or []
    web_chunks = web_chunks or []

    if not pdf_chunks and not web_chunks:
        logger.warning("No chunks (PDF or web) given to the RAG chain")
        return {
            "answer": "I'm sorry, I couldn't find relevant information to answer your question.",
            "sources": []
        }
    
    logger.info(f"Running RAG chain with {len(pdf_chunks)} PDF chunks and {len(web_chunks)} web chunks - model: {llm.model_name}")

    # Build prompt from chunks
    prompt = build_rag_prompt(query, pdf_chunks, web_chunks, conversation_history)

    # Generate prompt from LLM with system prompt 
    answer = llm.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)

    pdf_sources = {
        f"{chunk['metadata'].get('source', 'unknown')} - PDF"
        for chunk in pdf_chunks
    }

    web_sources = {
        get_source_label(chunk["metadata"]["source"], chunk["metadata"].get("title", "untitled"))
        for chunk in web_chunks
    }

    sources = list(pdf_sources | web_sources)

    logger.info(f"RAG chain completed - {len(sources)} sources used")

    return {
        "answer": answer,
        "sources": sources
    }