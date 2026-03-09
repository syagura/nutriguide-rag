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

    mock_result = {
        "query": "What are iron requirements?",
        "answer": "Iron requirements for a 6-month-old is 11mg per day.",
        "sources": ["who.pdf (page 1)"],
        "has_sources": True
    }

    with patch("api.routes.chat.get_pipeline_components", return_value=mock_components):
        with patch("api.routes.chat.run_inference", return_value=mock_result):
            with patch("api.routes.chat.parse_response", return_value=mock_result):
                response = client.post(
                    "/api/v1/chat",
                    json={"query": "What are iron requirements?"}
                )

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data

def test_chat_endpoint_query_too_short():
    response = client.post("/api/v1/chat", json={"query": "hi"})
    assert response.status_code == 422

def test_chat_endpoint_missing_query():
    response = client.post("/api/v1/chat", json={})
    assert response.status_code == 422