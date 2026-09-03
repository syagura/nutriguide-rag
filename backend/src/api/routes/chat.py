import logging
from fastapi import APIRouter, HTTPException
from schemas.request import ChatRequest
from schemas.response import ChatRespose
from api.dependencies import get_pipeline_components, get_session_store
from core.services.inference.inference_engine import run_inference
from core.services.inference.response_parser import parse_response
from core.services.router.query_router import route_query
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

        routing = route_query(request.query, conversation_history, components["llm"])
        logger.info(f"Routing decision: {routing}")

        web_chunks = []
        if routing["need_web"]:
            web_chunks = retrieve_web_context(request.query, components["reranker"])

        memory_context = conversation_history if routing["need_memory"] else []

        raw_result = run_inference(
            query=request.query,
            chunks=components["chunks"],
            faiss_index=components["faiss_index"],
            bm25=components["bm25"],
            embedding_model=components["embedding_model"],
            reranker=components["reranker"],
            llm=components["llm"],
            conversation_history=memory_context,
            web_chunks=web_chunks,
            retrieve_pdf=routing["need_pdf"]
        )

        session_store.add_message(session_id, "user", request.query)
        session_store.add_message(session_id, "assistant", raw_result["answer"])

        parsed = parse_response(raw_result)
        parsed["session_id"] = session_id
        return ChatRespose(**parsed)
    
    except Exception as e:
        logger.error(f"Chat request failed - query: '{request.query}' | error: {e}")
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")