import logging
from core.services.llm.base_llm import BaseLLM
from core.services.llm.groq_client import GroqClient
from core.services.llm.local_llm import LocalLLM

logger = logging.getLogger((__name__))

def get_llm() -> BaseLLM:
    """
    Return the best available LLM backend using a priority-based selection.

    Tries Groq first (faster, higer, quality). Falls back to local Ollama
    if Groq unavailable. This pattern ensure the system stays resilient
    even when the external API is down or rate_limited

    Returns:
        An initialised BaseLLM instance (Either GroqClient or LocalLLm)

    Raises:
        RuntimeError: If not LLM backend is available
    """
    logger.info("Trying connected to Groq API...")
    groq = GroqClient()

    if groq.is_available():
        logger.info("Groq API is available - using GroqClient")
        return groq
    
    logger.warning("Groq is unavailable - trying local Ollama as a fallback")
    local = LocalLLM()

    if local.is_available():
        logger.info("Ollama is available - using LocalLLM")
        return local
    
    raise RuntimeError(
        "No LLM backend is available. "
        "Make sure GROQ_API_KEY is set or Ollama is running on localhost."
    )