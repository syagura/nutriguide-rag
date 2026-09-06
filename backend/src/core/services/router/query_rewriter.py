import logging
from core.services.llm.base_llm import BaseLLM

logger = logging.getLogger(__name__)

QUERY_REWRITE_SYSTEM_PROMPT = """You rewrite a user's latest chat message into a \
standalone, fully-specified search query, using the conversation so far to fill \
in anything the message leaves implicit (e.g. "kalau yang murah?" after a \
question about protein foods becomes "makanan sumber protein yang murah").

Rules:
- Write ONLY the rewritten query, nothing else - no explanation, no qoutes
- Preserve the same language as the user's latest message
- If the message is already standalone (doesn't depend on prior context), return it unchanged
- Keep it a natural question/phrase suitable for search/document retrieval, not a full sentence explanation"""

def _build_rewrite_prompt(query: str, conversation_history: list[dict]) -> str:
    lines = [
        f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
        for msg in conversation_history
    ]
    history_block = "\n".join(lines)
    return f'Conversation so far:\n{history_block}\n\nLatest message: "{query}"\n\nStandalone query:'

def rewrite_query_for_retrieval(query: str, conversation_history: list[dict], llm: BaseLLM) -> str:
    """
    Rewrite an elliptical follow-up into a standalone query for PDF/web retrieval,
    using recent conversation to fill in what/s implicit.

    Falls back to the raw query on any failure or empty history - a missed
    rewrite just means retrieval behaves like before this fix, not a crash.
    """
    if not conversation_history:
        return query

    prompt = _build_rewrite_prompt(query, conversation_history)

    try:
        rewritten = llm.generate(prompt=prompt, system_prompt=QUERY_REWRITE_SYSTEM_PROMPT)
    except Exception as e:
        logger.warning(f"Query rewrite failed, using raw query: {e}")
        return query

    rewritten = rewritten.strip().strip('"')
    if not rewritten:
        return query

    logger.info(f"Rewrote query fir retrieval: '{query}' -> '{rewritten}'")
    return rewritten