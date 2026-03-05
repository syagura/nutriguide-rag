import pytest
from src.core.services.rag.reranker import load_reranker, rerank_chunks

@pytest.fixture(scope="module")
def reranker():
    return load_reranker()


@pytest.fixture
def dummy_chunks():
    return [
        {"text": "anak usia enam bulan membutuhkan zat besi dari MPASI", "metadata": {"source": "who.pdf", "page": 1}},
        {"text": "stunting disebabkan oleh kekurangan gizi kronis pada masa pertumbuhan", "metadata": {"source": "kemenkes.pdf", "page": 2}},
        {"text": "pemberian ASI eksklusif dianjurkan selama enam bulan pertama kehidupan", "metadata": {"source": "kia.pdf", "page": 3}},
        {"text": "vitamin A penting untuk pertumbuhan dan sistem imunitas anak", "metadata": {"source": "unicef.pdf", "page": 4}},
        {"text": "berat badan anak harus dipantau secara rutin setiap bulan posyandu", "metadata": {"source": "kemenkes.pdf", "page": 5}}
    ]

def test_laod_reranker(reranker):
    assert reranker is not None

def test_rerank_chunks_returns_top_k(reranker, dummy_chunks):
    results = rerank_chunks("zat besi untuk anak", dummy_chunks, reranker, top_k=3)
    assert len(results) == 3

def test_rerank_chunks_has_reranker_score(reranker, dummy_chunks):
    results = rerank_chunks("kebutuhan gizi anak", dummy_chunks, reranker, top_k=2)
    for chunk in results:
        assert "reranker_score" in chunk["metadata"]
        assert isinstance(chunk["metadata"]["reranker_score"], float)

def test_rerank_chunks_empty_input(reranker):
    results = rerank_chunks("zat besi anak", [], reranker, top_k=3)
    assert results == []

def test_rerank_chunks_sorted_by_score(reranker, dummy_chunks):
    results = rerank_chunks("zat besi untuk anak", dummy_chunks, reranker, top_k=5)
    scores = [chunk["metadata"]["reranker_score"] for chunk in results]
    assert scores == sorted(scores, reverse=True)