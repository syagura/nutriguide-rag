import pytest
from src.core.services.rag.bm25_retriever import build_bm25, search_bm25, save_bm25, load_bm25

@pytest.fixture
def dummy_chunks():
    return [
        {"text": "anak usia enam bulan membutuhkan zat besi", "metadata": {"source": "who.pdf", "page": 1}},
        {"text": "stunting disebabkan oleh kekurangan gizi kronis pada anak", "metadata": {"source": "kemenkes.pdf", "page": 2}},
        {"text": "pemberian ASI eksklusif dianjurkan selama enam bulan pertama", "metadata": {"source": "kia.pdf", "page": 3}},
        {"text": "vitamin A penting untuk pertumbuhan dan imunitas anak", "metadata": {"source": "unicef.pdf", "page": 4}},
        {"text": "berat badan anak harus dipantau secara rutin setiap bulan", "metadata": {"source": "kemenkes.pdf", "page": 5}},
    ]

def test_build_bm25(dummy_chunks):
    bm25 = build_bm25(dummy_chunks)
    assert bm25 is not None

def test_build_bm25_empty_chunks():
    with pytest.raises(ValueError):
        build_bm25([])

def test_search_bm25_returns_top_k(dummy_chunks):
    bm25 = build_bm25(dummy_chunks)
    results = search_bm25(bm25, "zat besi anak", dummy_chunks,top_k=3)
    assert len(results) == 3

def test_search_bm25_result_structure(dummy_chunks):
    bm25 = build_bm25(dummy_chunks)
    results = search_bm25(bm25, "stunting gizi", dummy_chunks, top_k=2)

    for idx, score in results:
        assert isinstance(idx, int)
        assert isinstance(score, float)

def test_search_bm25_sorted_descending(dummy_chunks):
    bm25 = build_bm25(dummy_chunks)
    results = search_bm25(bm25, "anak gizi", dummy_chunks, top_k=5)
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)

def test_save_and_load_bm25(dummy_chunks, tmp_path):
    bm25 = build_bm25(dummy_chunks)
    save_bm25(bm25, str(tmp_path))

    loaded_bm25 = load_bm25(str(tmp_path))
    results = search_bm25(loaded_bm25, "zat besi", dummy_chunks, top_k=3)
    assert len(results) == 3

def test_load_bm25_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_bm25(str(tmp_path))