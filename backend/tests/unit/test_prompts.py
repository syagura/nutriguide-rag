from src.core.prompts.templates import build_rag_prompt, SYSTEM_PROMPT
from src.core.prompts.chain import run_rag_chain
from unittest.mock import MagicMock

def test_build_rag_prompt_contains_query():
    chunks = [
        {"text": "Anak usia 6 bulan butuh zat besi.", "metadata": {"source": "who.pdf", "page": 1}}
    ]
    prompt = build_rag_prompt("Berapa kebutuhan zat besi anak?", chunks)
    assert "Berapa kebutuhan zat besi anak?" in prompt

def test_build_rag_prompt_contains_source():
    chunks = [
        {"text": "Anak usia 6 bulan butuh zat besi.", "metadata": {"source": "who.pdf", "page": 1}}
    ]
    prompt = build_rag_prompt("test query", chunks)
    assert "who.pdf" in prompt

def test_build_rag_prompt_conatains_context():
    chunks = [
        {"text": "Anak usia 6 bulan butuh zat besi.", "metadata": {"source": "who.pdf", "page": 1}}
    ]
    prompt = build_rag_prompt("test query", chunks)
    assert "Anak usia 6 bulan butuh zat besi." in prompt

def test_system_prompt_not_empty():
    assert len(SYSTEM_PROMPT.strip()) > 0

def test_run_rag_chain_empty_chunks():
    mock_llm = MagicMock()
    result = run_rag_chain("test query", [], mock_llm)
    assert "answer" in result
    assert "sources" in result
    mock_llm.generate.assert_not_called()

def test_run_rag_chain_returns_answer_and_sources():
    mock_llm = MagicMock()
    mock_llm.model_name = "test-model"
    mock_llm.generate.return_value = "Anak usia 6 bulan butuh 11mg zat besi per hari."

    chunks = [
        {"text": "Anak usia 6 bulan butuh zat besi.", "metadata": {"source": "who.pdf", "page": 1}}
    ]
    result = run_rag_chain("Berapa kebutuhan zat besi?", chunks, mock_llm)

    assert result["answer"] == "Anak usia 6 bulan butuh 11mg zat besi per hari."
    assert len(result["sources"]) > 0