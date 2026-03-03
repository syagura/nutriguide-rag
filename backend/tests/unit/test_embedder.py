import numpy as np
import pytest
from src.core.services.rag.embedder import load_embedding_model, embed_chunks

@pytest.fixture(scope="module")
def model():
    return load_embedding_model()

def test_load_embedding_model(model):
    # Model must be loaded not None
    assert model is not None

def test_embed_chunks_output_shape(model):
    # Shpae embeddings must be (number of chunks, embedding dimensions)
    chunks = [
        {"text": "Anak usia 6 bulan membutuhkan zat besi.", "metadata": {"source": "who.pdf", "page": 1}},
        {"text": "Stunting disebabkan oleh kekurangan gizi kronis.", "metadata": {"source": "kemenkes.pdf", "page": 2}},
    ]
    returned_chunks, embeddings = embed_chunks(chunks, model)

    assert embeddings.shape[0] == len(chunks)
    assert embeddings.shape[1] > 0

def test_embed_chunks_returns_numpy(model):
    # Embeddings must be numpy arrays to be compatible with FAISS
    chunks = [
        {"text": "Anak usia 6 bulan membutuhkan zat besi.", "metadata": {"source": "who.pdf", "page": 1}},
    ]
    _, embeddings = embed_chunks(chunks, model)
    assert isinstance(embeddings, np.ndarray)

def test_embed_chunks_empty_input(model):
    # An empty input should return an empty array, not an error 
    returned_chunks, embeddings = embed_chunks([], model)
    assert returned_chunks == []
    assert len(embeddings) == 0

def test_embed_chunks_preserves_chunks(model):
    # The retuned chunks must be exactly the same as the input 
    chunks = [
        {"text": "Anak usia 6 bulan membutuhkan zat besi.", "metadata": {"source": "who.pdf", "page": 1}}
    ]
    returned_chunks, _ = embed_chunks(chunks, model)
    assert returned_chunks == chunks