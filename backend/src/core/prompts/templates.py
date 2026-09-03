SYSTEM_PROMPT = """You are NutriGuide, an AI assistant specialized in pediatric nutrition.
You provide evidence-based answer about child nutrition, growth, and feeding practices.

Your answer must follow these rules:
1. Base your answer ONLY on the provide context (conversation, PDF, and/or web sources)
2. If the context does not contain enough information, say so clearly
3. Always mention which source your answer comes from
4. Keep your answer clear, concise, and parent-friendly
5. Never make up information that is not in the context
6. When PDF and web sources disagree, or when multiple web sources disagree, prefer the more authoritative one (official government/medical institutions > academic/research institutions > reputable health organizations)"""

def build_conversation_block(conversation_history: list[dict] | None) -> str:
    if not conversation_history:
        return ""
    lines = [
        f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
        for msg in conversation_history
    ]
    return "[CONVERSATION CONTEXT]\n" + "\n".join(lines) + "\n\n"

def build_pdf_block(pdf_chunks: list[dict]) -> str:
    if not pdf_chunks:
        return ""
    blocks = []
    for i, chunk in enumerate(pdf_chunks, start=1):
        source = chunk["metadata"].get("source", "unknown")
        page = chunk["metadata"].get("page", "?")
        blocks.append(f"[Document {i}: {source}, page {page}]\n{chunk['text']}")
    return "[PDF SOURCE]\n" + "\n\n".join(blocks) + "\n\n"

def build_web_block(web_chunks: list[dict]) -> str:
    if not web_chunks:
        return ""
    blocks = []
    for i, chunk in enumerate(web_chunks, start=1):
        title = chunk["metadata"].get("title", "untitled")
        url = chunk["metadata"].get("source", "unknown")
        blocks.append(f"[Web {i}: {title} ({url})]\n{chunk['text']}")
    return "[WEB SOURCE]\n" + "\n\n".join(blocks) + "\n\n"

def build_rag_prompt(
        query: str, 
        pdf_chunks: list[dict] | None = None, 
        web_chunks: list[dict] | None = None, 
        conversation_history: list[dict] | None = None
    ) -> str:
    """
    Build a RAG prompt by combining retrieved chunks with the user query.

    Args:
        query: The user's question
        pdf_chunks: List of retrieved and reranked PDF chunks containing 'text' and 'metadata'
        web_chunks: List of retrieved and reranked web chunks containing 'text' and 'metadata'
        conversation_history: List of previous conversation messages

    Returns:
        Formatted prompt string ready to be sent to the LLM
    """
    conversation_block = build_conversation_block(conversation_history)
    pdf_block = build_pdf_block(pdf_chunks or [])
    web_block = build_web_block(web_chunks or [])

    prompt = f"""{conversation_block}{pdf_block}{web_block}Use the source blocks above (if any) to answer the question below.
    If the question refers to the earlier conversation (e.g "yang murah", "yadi tadi"),  use [CONVERSATION CONTEXT] to understand what it refers to.
    When you use information from soruce, mention which source it came from so the user knows where the answer is grounded.
    If none of the source blocks contain relevant information, say so honestly instead of guessing.

QUESTION:
{query}

ANSWER:"""
    
    return prompt