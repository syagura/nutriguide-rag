import pytest
from unittest.mock import patch, MagicMock
from src.core.services.llm.base_llm import BaseLLM
from src.core.services.llm.groq_client import GroqClient
from src.core.services.llm.local_llm import LocalLLM
from src.core.services.llm.model_factory import get_llm

# ====================
# Base LLM 
# ====================

def test_base_llm_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseLLM()

# ====================
# Groq Client
# ====================

def test_groq_client_no_api_key():
    with patch.dict("os.environ", {}, clear=True):
        client = GroqClient()
        assert client.is_available() is False

def test_groq_client_model_name():
    client = GroqClient(model_name="llama-3.1-8b-instant")
    assert client.model_name == "llama-3.1-8b-instant"

def test_groq_client_generate_no_client():
    with patch.dict("os.environ", {}, clear=True):
        client = GroqClient()
        with pytest.raises(RuntimeError):
            client.generate("test prompt")


# ====================
# Local LLM 
# ====================

def test_local_llm_model_name():
    client = LocalLLM(model_name="llama3.1")
    assert client.model_name == "llama3.1"

def test_local_llm_unavailable_when_ollama_not_running():
    with patch("requests.get", side_effect=Exception("Connection refused")):
        client = LocalLLM()
        assert client.is_available() is False

def test_local_llm_generate_connection_error():
    with patch("requests.post", side_effect=Exception("Connection refused")):
        client = LocalLLM()
        with pytest.raises(RuntimeError):
            client.generate("test_prompt")


# ====================
# Model Factory
# ====================

def test_get_llm_returns_groq_when_available():
    with patch("src.core.services.llm.model_factory.GroqClient") as MockGroq:
        MockGroq.return_value.is_available.return_value = True
        llm = get_llm()
        assert llm == MockGroq.return_value


def test_get_llm_fallback_to_local_when_groq_unavailable():
    with patch("src.core.services.llm.model_factory.GroqClient") as MockGroq:
        with patch("src.core.services.llm.model_factory.LocalLLM") as MockLocal:
            MockGroq.return_value.is_available.return_value = False
            MockLocal.return_value.is_available.return_value = True
            llm = get_llm()
            assert llm == MockLocal.return_value


def test_get_llm_raises_when_both_unavailable():
    with patch("src.core.services.llm.model_factory.GroqClient") as MockGroq:
        with patch("src.core.services.llm.model_factory.LocalLLM") as MockLocal:
            MockGroq.return_value.is_available.return_value = False
            MockLocal.return_value.is_available.return_value = False
            with pytest.raises(RuntimeError):
                get_llm()