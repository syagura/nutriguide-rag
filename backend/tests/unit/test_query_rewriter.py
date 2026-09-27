from unittest.mock import MagicMock
from src.core.services.router.query_rewriter import rewrite_query_for_retrieval

def test_rewrite_returns_raw_query_when_no_history():
    mock_llm = MagicMock()
    result = rewrite_query_for_retrieval("kalau yang murah?", [], mock_llm)
    assert result == "kalau yang murah?"
    mock_llm.generate.assert_not_called()

def test_rewrite_uses_llm_output_when_history_exists():
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "makanan sumber protein yang murah untuk anak"

    history = [{"role": "assistant", "content": "Ikan, telur, dan tempe kaya protein"}]
    result = rewrite_query_for_retrieval("kalau yang murah?", history, mock_llm)

    assert result == "makanan sumber protein yang murah untuk anak"

def test_rewrite_falls_back_to_raw_query_on_llm_failure():
    mock_llm = MagicMock()
    mock_llm.generate.side_effect = RuntimeError("Groq API error")

    result = rewrite_query_for_retrieval("coba carikan informasinya", [{"role": "user", "content": "..."}], mock_llm)
    assert result == "coba carikan informasinya"

def test_rewrite_falls_back_to_raw_query_on_empty_response():
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "   "

    result = rewrite_query_for_retrieval("coba carikan informasinya", [{"role": "user", "content": "..."}], mock_llm)

    assert result == "coba carikan informasinya"

def test_rewrite_strips_surrounding_quotes():
    mock_llm = MagicMock()
    mock_llm.generate.return_value = '"cara mengatasi demam disertai pilek pada anak"'

    result = rewrite_query_for_retrieval("bagaimana jika disertai pilek?", [{"role": "user", "content": "..."}], mock_llm)
    assert result == "cara mengatasi demam disertai pilek pada anak"