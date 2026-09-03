from unittest.mock import MagicMock
from src.core.services.router.llm_router import llm_route, _parse_router_response, _safe_default_route

def test_parse_router_response_valid_json():
    raw = '{"need_memory": true, "need_pdf": false, "need_web": true, "query_type": "mixed"}'
    parsed = _parse_router_response(raw)
    assert parsed == {"need_memory": True, "need_pdf": False, "need_web": True, "query_type": "mixed"}

def test_parse_router_response_strips_markdown_fences():
    raw = '```json\n{"need_memory": false, "need_pdf": true, "need_web": false, "query_type": "pdf_lookup}\n```'
    parsed = _parse_router_response(raw)
    assert parsed["need_pdf"] is True

def test_parse_router_response_invalid_json_returns_none():
    assert _parse_router_response("not a json") is None

def test_parse_router_response_missing_keys_returns_none():
    raw = '{"need_memory": true, "need_pdf": false}'
    assert _parse_router_response(raw) is None

def test_safe_default_route_with_history():
    decision = _safe_default_route(has_conversation_history=True)
    assert decision == {"need_memory": True, "need_pdf": True, "need_web": False, "query_type": "fallback_default"}

def test_llm_route_uses_parsed_response():
    mock_llm = MagicMock()
    mock_llm.generate.return_value = '{"need_memory": false, "need_pdf": true, "need_web": true, "query_type": "mixed"}'

    decision = llm_route("Compare the PDF with the latest information from the WHO", has_conversation_history=False, llm=mock_llm)

    assert decision["need_pdf"] is True
    assert decision["need_web"] is True

def test_llm_route_falls_back_on_llm_exception():
    mock_llm = MagicMock()
    mock_llm.generate.side_effect = RuntimeError("Groq API error")

    decision = llm_route("Some query", has_conversation_history=True, llm=mock_llm)

    assert decision == _safe_default_route(True)

def test_llm_route_falls_back_on_unparseable_response():
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "maaf saya tidak mengerti"

    decision = llm_route("Some query", has_conversation_history=False, llm=mock_llm)

    assert decision == _safe_default_route(False)