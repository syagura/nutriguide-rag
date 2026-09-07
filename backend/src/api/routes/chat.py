import logging
from fastapi import APIRouter, HTTPException
from schemas.request import ChatRequest
from schemas.response import ChatRespose
from api.dependencies import get_pipeline_components, get_session_store, get_web_cache
from core.services.inference.inference_engine import retrieve_pdf_chunks
from core.services.inference.response_parser import parse_response
from core.prompts.chain import run_rag_chain
from core.services.router.query_router import route_query
from core.services.router.query_rewriter import rewrite_query_for_retrieval
from core.services.web.web_retriever import retrieve_web_context

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])

@router.post("/chat", response_model=ChatRespose)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - runs the full RAG inference pipeline.

    Accepts a user query, retrieves relevant chunks from the knowledge base,
    reranks them, and generates an evidence-based answer using the LLM.
    """
    logger.info(f"Received chat request - query: '{request.query}' | session: {request.session_id}")

    try:
        components = get_pipeline_components()
        session_store = get_session_store()

        session_id = session_store.get_or_create(request.session_id)
        conversation_history = session_store.get_recent_messages(session_id)
        web_cache = get_web_cache()

        routing = route_query(request.query, conversation_history, components["llm"])
        logger.info(f"Routing decision: {routing}")

        memory_context = conversation_history if routing["need_memory"] else []

        web_chunks = []
        if routing["need_web"]:
            web_chunks = retrieve_web_context(request.query, components["reranker"])

        memory_context = conversation_history if routing["need_memory"] else []

        retrieval_query = request.query
        if memory_context and (routing["need_pdf"] or routing["need_web"]):
            retrieval_query = rewrite_query_for_retrieval(request.query, memory_context, components["llm"])

        pdf_chunks = []
        if routing["need_pdf"]:
            pdf_chunks, _ = retrieve_pdf_chunks(
                retrieval_query, components["chunks"], components["faiss_index"],
                components["bm25"], components["embedding_model"], components["reranker"]
            )

        need_web = routing["need_web"]
        if routing["need_pdf"] and not pdf_chunks and not need_web:
            logger.info("PDF retrieval returned nothing, falling back to web retrieval")
            need_web = True

        web_chunks = []
        if need_web:
            web_chunks = retrieve_web_context(retrieval_query, components["reranker"], cache=web_cache)

        raw_result = run_rag_chain(
            query=request.query,
            llm=components["llm"],
            pdf_chunks=pdf_chunks,
            web_chunks=web_chunks,
            conversation_history=memory_context,
        )
        raw_result["query"] = request.query

        session_store.add_message(session_id, "user", request.query)
        session_store.add_message(session_id, "assistant", raw_result["answer"])

        parsed = parse_response(raw_result)
        parsed["session_id"] = session_id
        return ChatRespose(**parsed)
    
    except Exception as e:
        logger.error(f"Chat request failed - query: '{request.query}' | error: {e}")
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")