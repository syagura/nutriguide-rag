import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_chat_endpoint_success():
    mock_components = {
        "faiss_index": MagicMock(),
        "chunks": [{"text": "test", "metadata": {"source": "who.pdf", "page": 1}}],
        "bm25": MagicMock(),
        "embedding_model": MagicMock(),
        "reranker": MagicMock(),
        "llm": MagicMock()
    }
    mock_routing = {"need_memory": False, "need_pdf": True, "need_web": False, "query_type": "pdf_lookup"}
    mock_pdf_chunks =[{  "text": "Iron requirement is 11mg/day", "metadata": {"source": "who.pdf", "page": 1 }}]

    mock_result = {
        "query": "What are iron requirements?",
        "answer": "Iron requirements for a 6-month-old is 11mg per day.",
        "sources": ["who.pdf - PDF"],
        "has_sources": True
    }

    with patch("api.routes.chat.get_pipeline_components", return_value=mock_components), \
         patch("api.routes.chat.route_query", return_value=mock_routing), \
         patch("api.routes.chat.retrieve_pdf_chunks", return_value=(mock_pdf_chunks, "en")), \
         patch("api.routes.chat.run_rag_chain", return_value=mock_result), \
         patch("api.routes.chat.parse_response", return_value=mock_result):
         response = client.post("/api/v1/chat", json={"query": "What are iron requirements?"})

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data

def test_chat_endpoint_falls_back_to_web_when_pdf_empty():
    mock_components = {
        "faiss_index": MagicMock(), "chunks": [], "bm25": MagicMock(),
        "embedding_model": MagicMock(), "reranker": MagicMock(), "llm": MagicMock()
    }
    mock_routing = {"need_memory": False, "need_pdf": True, "need_web": False, "query_type": "pdf_lookup"}
    mock_result = {"query": "q", "answer": "answer from web", "sources": ["WHO - Title"], "has_sources": True}

    with patch("api.routes.chat.get_pipeline_components", return_value=mock_components), \
         patch("api.routes.chat.route_query", return_value=mock_routing), \
         patch("api.routes.chat.retrieve_pdf_chunks", return_value=([], "id")), \
         patch("api.routes.chat.retrieve_web_context", return_value=[{"text": "x", "metadata": {"source": "https://who.int/x", "title": "Title"}}]) as mock_web, \
         patch("api.routes.chat.run_rag_chain", return_value=mock_result), \
         patch("api.routes.chat.parse_response", return_value=mock_result):
        response = client.post("/api/v1/chat", json={"query": "bagaimana jika disertai pilek?"})

    assert response.status_code == 200
    mock_web.assert_called_once()

def test_chat_endpoint_query_too_short():
    response = client.post("/api/v1/chat", json={"query": "hi"})
    assert response.status_code == 422

def test_chat_endpoint_missing_query():
    response = client.post("/api/v1/chat", json={})
    assert response.status_code == 422