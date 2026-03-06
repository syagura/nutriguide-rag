from src.core.services.inference.respon_parser import parse_response

def test_parse_response_structure():
    raw = {
        "answer": "Anak butuh zat besi 11mg per hari.",
        "sources": ["who.pdf (page 1)"],
        "query": "Berapa kebutuhan zat besi?"
    }
    result = parse_response(raw)

    assert "query" in result
    assert "answer" in result
    assert "sources" in result
    assert "has_sources" in result

def test_parse_response_has_sources_true():
    raw = {
        "answer": "test answer",
        "sources": ["who.pdf (page 1)"],
        "query": "test"
    }
    result = parse_response(raw)
    assert result["has_sources"] is True

def test_parse_response_has_sources_false():
    raw = {"answer": "test answer", "sources": [], "query": "test"}
    result = parse_response(raw)
    assert result["has_sources"] is False

def test_parse_response_empty_answer_fallback():
    raw = {"answer": "", "sources": [], "query": "test"}
    result = parse_response(raw)
    assert len(result["answer"]) > 0

def test_parse_response_strips_whitespace():
    raw = {"answer": "   test answer   ", "sources": [], "query": "test"}
    result = parse_response(raw)
    assert result["answer"] == "test answer"