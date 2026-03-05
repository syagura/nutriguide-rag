import pytest
import numpy as np
from src.core.services.rag.hybrid_retriever import reciprocal_rank_fusion, hybrid_search
from src.core.services.rag.embedder import load_embedding_model, embed_chunks
from src.core.services.rag.vector_store import build_vector_store
from src.core.services.rag.bm25_retriever import build_bm25

@pytest.fixture(scope="module")
def model():
    return load_embedding_model()


@pytest.fixture
def dummy_chunks():
    return [
        {"text": "anak usia enam bulan membutuhkan zat besi", "metadata": {"source": "who.pdf", "page": 1}},
        {"text": "stunting disebabkan oleh kekurangan gizi kronis pada anak", "metadata": {"source": "kemenkes.pdf", "page": 2}},
        {"text": "pemberian ASI eksklusif dianjurkan selama enam bulan pertama", "metadata": {"source": "kia.pdf", "page": 3}},
        {"text": "Vitamin A penting untuk pertumbuhan dan imunitas anak", "metadata": {"source": "unicef.pdf", "page": 4}},
        {"text": "berat badan anak harus dipantau secara rutin setiap bulan", "metadata": {"source": "kemenkes.pdf", "page": 5}},
    ]

def test_reciprocal_rank_fusion_returns_top_k():
    # RRF must return the top_k result
    semantic = [(0, 0.9), (1, 0.8), (2, 0.7)]
    bm25 = [(2, 5.0), (0, 4.0), (3, 3.0)]
    results = reciprocal_rank_fusion(semantic, bm25, top_k=2)
    assert len(results) == 2

def test_reciprocal_rank_fusion_sorted_descending():
    # RRF results must be sorted from highest to lowest score.
    semantic = [(0, 0.9), (1, 0.8), (2, 0.7)]
    bm25 = [(1, 5.0), (0, 4.0), (2, 3.0)]
    results = reciprocal_rank_fusion(semantic, bm25, top_k=3)
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)

def test_reciprocal_rank_fusion_combines_both_sources():
    semantic = [(0, 0.9), (1, 0.8)]
    bm25 = [(0, 5.0), (2, 3.0)]
    results = reciprocal_rank_fusion(semantic, bm25, top_k=3)
    top_chunk_idx = results[0][0]
    assert top_chunk_idx == 0

def test_hybrid_search_returns_chunks(dummy_chunks, model):
    # Hybrid search must return a non-empty chunk list
    _, embeddings = embed_chunks(dummy_chunks, model)
    faiss_index = build_vector_store(embeddings)
    bm25 = build_bm25(dummy_chunks)

    results = hybrid_search("gizi anak", dummy_chunks, faiss_index, bm25, model, top_k=3)
    assert len(results) > 0

def test_hybrid_search_chunks_have_rrf_score(dummy_chunks, model):
    # Each chunk resulting from hybrid search must have an rrf_score in its metadata.
    _, embeddings = embed_chunks(dummy_chunks, model)
    faiss_index = build_vector_store(embeddings)
    bm25 = build_bm25(dummy_chunks)

    results = hybrid_search("gizi anak", dummy_chunks, faiss_index, bm25, model, top_k=3)
    for chunk in results:
        assert "rrf_score" in chunk["metadata"]