SYSTEM_PROMPT = """You are NutriGuide, an AI assistant specialized in pediatric nutrition.
You provide evidence-based answer about child nutrition, growth, and feeding practices.

Your answer must follow these rules:
1. Base your answer ONLY on the provide context documents
2. If the context does not contain enough information, say so clearly
3. Always mention which source your answer comes from
4. Keep your answer clear, concise, and parent-friendly
5. Never make up information that is not in the context"""

def build_rag_prompt(query: str, chunks: list[dict]) -> str:
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
    prompt = f"""Use the following context documents to answer the question below.
    
CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""
    
    return prompt