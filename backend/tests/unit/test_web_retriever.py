from unittest.mock import patch, MagickMock
from src.core.services.web.web_retriever import retrieve_web_context, _build_web_chunks

@patch("src.core.services.web.web_retriever.search_web")
def test_retrieve_web_context_returns_empty_when_search_fails(mock_search):
    mock_search.return_value = []
    assert retrieve_web_context("query", reranker=MagickMock()) == []

@patch("src.core.services.web.web_retriever.fetch_pages")
@patch("src.core.services.web.web_retriever.search_web")
def test_retrieve_web_context_returns_empty_when_no_pages_fetched(mock_search, mock_fetch):
    mock_search.return_value = [{"title": "A", "url": "https://who.int/a", "snippet": "..."}]
    mock_fetch.return_value = {}
    assert retrieve_web_context("query", reranker=MagickMock()) == []

@patch("src.core.services.web.web_retriever.rerank_chunks")
@patch("src.core.services.web.web_retriever.extract_content")
@patch("src.core.services.web.web_retriever.fetch_pages")
@patch("src.core.services.web.web_retriever.search_web")
def test_retrieve_web_context_full_pipeline(mock_search, mock_fetch, mock_extract, mock_rerank):
    mock_search.return_value = [{"title": "A", "url": "https://who.int/a", "snippet": "..."}]
    mock_fetch.return_value = {"https://who.int/a": "<html>...</html>"}
    mock_extract.return_value = {
        "text": "Anak usia enam bulan membutuhkan zat besi yang cukup untuk tumbuh kembang. " * 5,
        "title": "Panduan Gizi"
    }
    mock_rerank.return_value = [{"text": "chunk terpilih", "metadata": {"source": "https://who.int/a"}}]

    result = retrieve_web_context("kebutuhan zat besi bayi", reranker=MagickMock())

    assert len(result) == 1
    assert result[0]["metadata"]["source"] == "https://who.int/a"
    mock_rerank.assert_called_once()

@patch("src.core.services.web.web_retriever.extract_content")
def test_build_web_chunks_skips_unextractable_pages(mock_extract):
    mock_extract.return_value = None
    assert _build_web_chunks({"https://who.int/a": "<html>...</html>"}) == []

@patch("src.core.services.web.web_retriever.extract_content")
def test_build_web_chunks_tags_source_type_web(mock_extract):
    mock_extract.return_value = {
        "text": "Vitamin D penting untuk pertumbuhan tulang anak. " * 10,
        "title": "Artikel Vitamin D"
    }
    chunks = _build_web_chunks({"https://who.int/vitd": "<html>...</html>"})

    assert len(chunks) > 0
    assert chunks[0]["metadata"]["source_type"] == "web"
    assert chunks[0]["metadata"]["source"] == "https://who.int/vitd"