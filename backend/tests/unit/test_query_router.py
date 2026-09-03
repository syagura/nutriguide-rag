from unittest.mock import MagickMock, patch
from src.core.services.router.query_router import route_query

def test_route_query_uses_rule_based_when_obvious():
    mock_llm = MagickMock()
    decision = route_query("What about affordable ones?", conversation_history=[{"role": "user", "content": "..."}], llm=mock_llm)

    assert decision["query_type"] == "follow_up"
    mock_llm.generate.assert_not_called()

@patch("src.core.services.router.query_router.llm_route")
def test_route_query_falls_back_to_llm_when_ambiguous(mock_llm_route):
    mock_llm_route.return_value = {"need_memory": False, "need_pdf": True, "need_web": False, "query_type": "pdf_lookup"}
    mock_llm = MagickMock()

    decision = route_query("What foods are high in protein?", conversation_history=[], llm=mock_llm)

    mock_llm_route.assert_called_once_with("What foods are high in protein?", False, llm=mock_llm)
    assert decision["query_type"] == "pdf_lookup"