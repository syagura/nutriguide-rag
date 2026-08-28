SYSTEM_PROMPT = """You are NutriGuide, an AI assistant specialized in pediatric nutrition.
You provide evidence-based answer about child nutrition, growth, and feeding practices.

Your answer must follow these rules:
1. Base your answer ONLY on the provide context documents
2. If the context does not contain enough information, say so clearly
3. Always mention which source your answer comes from
4. Keep your answer clear, concise, and parent-friendly
5. Never make up information that is not in the context"""

def build_conversation_block(conversation_history: list[dict] | None) -> str:
    if not conversation_history:
        return ""
    lines = [
        f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
        for msg in conversation_history
    ]
    return "[CONVERSATION CONTEXT]\n" + "\n".join(lines) + "\n\n"

def build_rag_prompt(query: str, chunks: list[dict], conversation_history: list[dict] | None = None) -> str:
    """
    Build a RAG prompt by combining retrieved chunks with the user query.

    Args:
        query: The user's question
        chunks: List of retrieved and reranked chunk dicts containing 'text' and 'metadata'

    Returns:
        Formatted prompt string ready to be sent to the LLM
    """
    context_blocks = []
    for i, chunk in enumerate(chunks, start=1):
        source = chunk["metadata"].get("source", "unknown")
        page = chunk["metadata"].get("page", "?")
        context_blocks.append(
            f"[Source {i}: {source}, page {page}]\n{chunk['text']}"
        )

    context = "\n\n".join(context_blocks)
    conversation_block = build_conversation_block(conversation_history)
    prompt = f"""{conversation_block}Use the following context documents to answer the question below.
    If the question refers to the earlier conversation (e.g. "yang murah", "yang tadi"), use the conversation context above to understand what it refers to.
    
CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""
    
    return prompt