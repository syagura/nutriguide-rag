import os
import logging
import requests
from core.services.llm.base_llm import BaseLLM

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
DEFAULT_LOCAL_MODEL = "llama3.1"

class LocalLLM(BaseLLM):
    """
    LLM client implementation using a local ollama instance.

    Used as a fallback when the Groq API is unavailable.
    Requires ollama to be installed and running locally
    """

    def __init__(self, model_name: str = DEFAULT_LOCAL_MODEL, base_url: str = OLLAMA_BASE_URL):
        """
        Initialize the local Ollama client.

        Args:
            model_name: Ollama model name to use (default: llama3.1)
            base_url: Base URL of the ollama API (default: http://localhost:11434)
        """
        self._model_name = model_name
        self._base_url = base_url
        logger.info(f"LocalLMM initialized - model: {model_name}, url: {base_url}")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate a response using the local Ollama API.

        Args:
            prompt: The user prompt to send
            system_prompt: Optional system instruction for the LLM

        Returns:
            Generated response string

        Raises:
            RuntimeError: If Ollama is unreachacle or returns an error
        """

        url = f"{self._base_url}/api/chat"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self._model_name,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.3}
        }

        logger.info(f"Sending request to Ollama -model: {self._model_name}")

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()["message"]["content"]
            logger.info("Response from Ollama successfully received.")
            return result
        
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Ollama cannot be conected - make sure Ollama is running on localhost")
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise RuntimeError(f"Ollama error: {e}")
        
    def is_available(self) -> bool:
        """
        Check if the local Ollama instance is running and reachable.

        Returns:
            True if Ollsms is running and accessible, False Otherwise
        """
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            logger.warning("Ollama is not available")
            return False
        
    @property
    def model_name(self) -> str:
        """Return the local Ollama model name being used"""
        return self._model_name