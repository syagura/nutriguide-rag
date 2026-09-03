import re
import json
import logging
from core.services.llm.base_llm import BaseLLM

logger = logging.getLogger(__name__)

ROUTER_SYSTEM_PROMPT = """You are a routing component for a pediatric nutrition Q/A \
    assistant. Given a user query and whether there is prior conversation, decide \
    which information sources are needed to answer it.
    
    Respond with ONLY a JSON object, no other text, in this exact shape:
    {"need_memory": bool, "need_pdf": bool, "need_web": bool, "query_type": string}
    
    - need_memory: true if the query references earlier conversation or depends on it
    - need_pdf: true if the query needs the static nutrition knowledge base
    - need_web: true if the query needs current/recent information not in a static document
    - query_type: a short label such as "memory_reference", "pdf_lookup", "current_information", "follow_up", or "mixed"
    
    When unsure, prefer setting a flag to true over false - retrieving and unused source is cheap, missing a needed one gives a wrong answer."""

def _build_router_prompt(query: str, has_conversation_history: bool) -> str:
    context_note = (
        "There IS prior conversation in this session." if has_conversation_history
        else "There is NO prior conversation in this session (first message)."
    )
    return f'{context_note}\n\nUser query: "{query}"\n\nJSON routing decision:'

def _parse_router_response(raw_response: str) -> dict | None:
    """Extract and validate the routing JSON from the LLM's raw text output."""
    cleaned = re.sub(r"^```(json)?|```$", "", raw_response.strip(), flags=re.MULTILINE).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning(f"Router LLM returned non-JSON output: {raw_response[:200]}")
        return None

    required_keys = {"need_memory", "need_pdf", "need_web", "query_type"}
    if not required_keys.issubset(parsed.keys()):
        logger.warning(f"Router LLM JSON missing required keys: {parsed}")
        return None

    return {
        "need_memory": bool(parsed["need_memory"]),
        "need_pdf": bool(parsed["need_pdf"]),
        "need_web": bool(parsed["need_web"]),
        "query_type": str(parsed["query_type"]),
    }

def _safe_default_route(has_conversation_history: bool) -> dict:
    """Fallback when LLM routing fails entirely: assume PDF is needed (cheapest,
    most reliable source) and include memory if it's available."""
    return {"need_memory": has_conversation_history, "need_pdf": True, "need_web": False, "query_type": "fallback_default"}

def llm_route(query: str, has_conversation_history: bool, llm: BaseLLM) -> dict:
    """
    Ask the LLM to decide routing for an ambiguous query.

    Falls back to a safe default if the LLM call fails or returns unparseable
    output - a wrong-but-safe routing beats crashing the whole chat request.
    """
    prompt = _build_router_prompt(query, has_conversation_history)

    try:
        raw_response = llm.generate(prompt=prompt, system_prompt=ROUTER_SYSTEM_PROMPT)
    except Exception as e:
        logger.error(f"Router LLM call failed: {e}")
        return _safe_default_route(has_conversation_history)

    parsed = _parse_router_response(raw_response)
    if parsed is None:
        return _safe_default_route(has_conversation_history)

    logger.info(f"LLM router decision: {parsed}")
    return parsed