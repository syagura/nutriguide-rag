import os
import logging
from groq import Groq
from core.services.llm.base_llm import BaseLLM

logger =  logging.getLogger(__name__)

DEFAULT_GROQ_MODEL = 'llama-3.1-8b-instant'

class GroqClient(BaseLLM):
    """
    LLM client implementation using the groq API.

    Uses Llama 3.1 8B via Groq's LPU inference for fast response times.
    Reqiures GROQ_API_KEY to be set in the environment variables.
    """
    def __init__(self, model_name: str = DEFAULT_GROQ_MODEL):
        """
        Initialize the Groq Client.

        Args:
            model_name: Groq model identifier to use (default: llama-3.1-8b-instant)
        """
        self._model_name = model_name
        self._api_key = os.getenv("GROQ_API_KEY")

        if not self._api_key:
            logger.warning("GROQ_API_KEY not found")

        self._client = Groq(api_key=self._api_key) if self._api_key else None
        logger.info(f"GroqClient initialized with model: {self._model_name}")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate a response using the Groq API.

        Args:
            prompt: The user prompt to send
            system_prompt: Optional system intruction for the LLM

        Returns:
            Generated response string

        Raises:
            RuntimeError: If Groq client not initialied
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})
        logger.info(f"Sending request to Groq API - model: {self._model_name}")

        try:
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=0.3,
                max_tokens=1024
            )
            result = response.choices[0].message.content
            logger.info("Response from Groq API successfully received")
            return result
        
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise RuntimeError(f"Groq API error: {e}")
        
    def is_available(self) -> bool:
        """
        Check if the Groq API is reachable with the current API key.

        Returns:
            true if API key exists and a test request succeeds, False otherwise
        """
        if not self._client:
            return False

        try:
            self._client.chat.completions.create(
                model=self._model_name,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1
            )
            return True
        
        except Exception as e:
            logger.warning(f"Groq is not available: {e}")
            return False
        
    @property
    def model_name(self) -> str:
        """Return the Groq model name being used"""
        return self._model_name