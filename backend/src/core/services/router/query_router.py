import logging
from core.services.llm.base_llm import BaseLLM
from core.services.router.rules import rule_based_route
from core.services.router.llm_router import llm_route

logger = logging.getLogger(__name__)

def route_query(query: str, conversation_history: list[dict], llm: BaseLLM) -> dict:
    """
    Decide which sources (memory/PDF/web) are needed to answer a query.

    Cheap rule-based matching handles obvious cases first; only ambiguous
    query fall through to an LLM call, per the hybrid routing design.
    """
    has_history = bool(conversation_history)

    decision = rule_based_route(query, has_history)
    if decision is not None:
        logger.info(f"Rule-based router decision: {decision}")
        return decision

    logger.info("Query ambiguous for rule-based routing, falling back to LLM")
    return llm_route(query, has_history, llm)