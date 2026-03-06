from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseLLM(ABC):
    """
    Abstract base class for all LLM client implementations.

    Any LLM backend (Groq, Ollama, etc.) must inherit this class
    and implement all abstract methods to ensure a consistent interface
    across the codebase.
    """

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate a response from the LLM given a prompt

        Args:
            prompt: The user prompt to send to the LLM
            system_prompt: Optional system instruction to guide LLM behavior

        Returns:
            Generated response string from the LLM
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check whether this LLM backend is currently available.

        Returns:
            True if the backend is reachable and ready, False otherwise
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Return the name of the model being used.

        Returns:
            Model name string (e.g. 'llama-3.1-8b-instant)
        """
        pass