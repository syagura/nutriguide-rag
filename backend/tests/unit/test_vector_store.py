import pytest
import numpy as np
from src.core.services.rag.vector_store import (
    build_vector_store,
    search_vector_store,
    save_vector_store,
    load_vector_store
)

# Dummy embedding for all test 
@pytest.fixture
def dummy_embeddings():
    return np.random.rand(5, 64).astype(np.float32)

@pytest.fixture
def dummy_chunks():
    return [
        {"text": f"chunk ke-{i}", "metadata": {"source": "test.pdf", "page": 1}}
        for i in range(5)
    ]

def test_build_vector_store(dummy_embeddings):
    index = build_vector_store(dummy_embeddings)
    assert index.ntotal == len(dummy_embeddings)

def test_build_vector_store_invalid_input():
    # Input 1D array must be raise ValueError
    with pytest.raises(ValueError):
        build_vector_store(np.array([1.0, 2.0, 3.0]))

def test_search_vector_store_returns_top_k(dummy_embeddings):
    index = build_vector_store(dummy_embeddings)
    query = np.random.rand(64).astype(np.float32)

    scores, indices = search_vector_store(index, query, top_k=3)

    assert len(scores) == 3
    assert len(indices) == 3

def test_save_and_load_vector_store(dummy_embeddings, dummy_chunks, tmp_path):
    index = build_vector_store(dummy_embeddings)
    save_vector_store(index, dummy_chunks, str(tmp_path))

    loaded_index, loaded_chunks = load_vector_store(str(tmp_path))

    assert loaded_index.ntotal == index.ntotal
    assert len(loaded_chunks) == len(dummy_chunks)

def test_load_vector_store_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_vector_store(str(tmp_path))