import re
import logging

logger = logging.getLogger(__name__)

MEMORY_REFERENCE_PATTERNS = [
    r"\btadi\b", r"\bbarusan\b", r"\bsebelumnya\b", r"\bkita bahas\b",
    r"\byang tadi\b", r"\bwhat did we\b", r"\bearlier\b", r"\bprevious(ly)?\b",
]

FOLLOW_UP_PATTERNS = [
    r"^kalau\b", r"^terus kalau\b", r"^gimana kalau\b", r"^bagaimana kalau\b",
    r"^what about\b", r"^how about\b",
]

CURRENT_INFO_PATTERNS = [
    r"\bterbaru\b", r"\bpenelitian terbaru\b", r"\briset terbaru\b",
    r"\bberita\b", r"\bupdate\b", r"\blatest\b", r"\brecent research\b",
    r"\bcurrent\b", r"\bhari ini\b", r"\btahun ini\b", r"\bnews\b",
]

FOLLOW_UP_MAX_WORDS = 8

def _matches_any(query: str, patterns: list[str]) -> bool:
    query_lower = query.lower()
    return any(re.search(p, query_lower) for p in patterns)

def rule_based_route(query: str, has_conversation_history: bool) -> dict | None:
    """
    Handle obvious routing cases with cheap keyword matching - no LLM call.

    Returns a routing decision dict, or None if the query is ambiguous and
    should fall through to LLM-based routing.
    """
    is_memory_reference = _matches_any(query, MEMORY_REFERENCE_PATTERNS)
    is_current_info = _matches_any(query, CURRENT_INFO_PATTERNS)
    is_follow_up = _matches_any(query, FOLLOW_UP_PATTERNS) and len(query.split()) <= FOLLOW_UP_MAX_WORDS

    # Case 1 just asking the previous conversation
    if is_memory_reference and not is_current_info and has_conversation_history:
        return {"need_memory": True, "need_pdf": False, "need_web": False, "query_type": "memory_reference"}

    # Case 2 follow-up elliptical
    if is_follow_up and has_conversation_history and not is_current_info:
        return {"need_memory": True, "need_pdf": True, "need_web": False, "query_type": "follow_up"}

    # Case 3 asking for current info
    if is_current_info and not is_memory_reference:
        return {"need_memory": has_conversation_history, "need_pdf": False, "need_web": True, "query_type": "current_information"}

    # Ambiguous
    return None