import os
import logging
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

_translator_llm = None

def _get_translator():
    """Lazy load Groq client for translation - reuse instance"""
    global _translator_llm
    if _translator_llm is None:
        _translator_llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0
        )
    return _translator_llm

def detect_language(text: str) -> str:
    """
    Simple heuristic language detection - check Indonesian Character.
    Returns 'id' for Indonesian, 'en' for English.
    """
    indonesian_markers = [
        'anak', 'bayi', 'ibu', 'kapan', 'berapa', 'bagaimana',
        'kenapa', 'mengapa', 'apakah', 'boleh', 'harus', 'perlu',
        'berat', 'tinggi', 'makan', 'minum', 'tumbuh', 'kembang',
        'gizi', 'nutrisi', 'asi', 'mpasi', 'stunting', 'yang', 'dan',
        'atau', 'untuk', 'dengan', 'pada', 'dari', 'tidak', 'bisa'
    ]
    text_lower = text.lower()
    matches = sum(1 for marker in indonesian_markers if marker in text_lower)
    return 'id' if matches >= 1 else 'en'

def translate_to_english(query: str) -> str:
    """
    Translate Indonesian query to English using Groq.

    Args:
        query: Indonesian query string

    Returns: 
        English translation of the query

    Raises:
        RuntimeError: If translation fails
    """
    try:
        llm = _get_translator()
        prompt = (
            f"Translate this medical/nutrition query from Indonesia to English. "
            f"Return ONLY the translation, no explanation, no quotes.\n\n"
            f"Query: {query}"
        )
        result = llm.invoke(prompt)
        translated = result.content.strip()
        logger.info(f"Query translated: '{query}' -> '{translated}'")
        return translated

    except Exception as e:
        logger.warning(f"Translation failed, using original query: {e}")
        return query
    
def translate_query(query: str) -> tuple[str, str]:
    """
    Detect language and translate if Indonesian.

    Args:
        query: User query (any language)

    Returns:
        Tuple of (translated_query, detected_language)
        translated_query = English version for retrieval
        detected_langauge = 'id' or 'en'
    """
    lang = detect_language(query)

    if lang == 'id':
        translated = translate_to_english(query)
        return translated, lang
    
    return query, lang