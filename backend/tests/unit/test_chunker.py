import pytest
from src.core.services.processing.chunker import create_chunker, chunk_pages

def test_create_chunker_default():
    # Ensure that chunker is created without errors using the deafult parameters
    chunker = create_chunker()
    assert chunker is not None

def test_create_chunker_custom_params():
    # Custom parameters must be set correctly in the instance 
    chunker = create_chunker(chunk_size=256, chunk_overlap=64)
    assert chunker._chunk_size == 256
    assert chunker._chunk_overlap == 64

def test_chunk_pages_output_structure():
    # Each chunk must have the keys 'text', 'metadata', and 'chunk_index'
    pages = [
        {
            "text": "Anak usia 6 bulan membutuhkan MPASI yang bergizi. " * 20, # long text to be split
            "metadata": {"source": "who.pdf", "page": 1}
        }
    ]

    chunks = chunk_pages(pages)

    assert len(chunks) > 0
    for chunk in chunks:
        assert "text" in chunk
        assert "metadata" in chunk
        assert "chunk_index" in chunk["metadata"]

def test_chunk_pages_metadata_preserved():
    # The original metadata (source, page) must remain in each chunk 
    pages = [
        {
            "text": "Anak usia 6 bulan membutuhkan MPASI yang bergizi" * 20,
            "metadata": {"source": "who.pdf", "page": 3}
        }
    ]
    chunks = chunk_pages(pages)

    for chunk in chunks:
        assert chunk["metadata"]["source"] == "who.pdf"
        assert chunk["metadata"]["page"] == 3

def test_chunk_pages_empty_input():
    # An empty input should return an empty list, not an error.
    result = chunk_pages([])
    assert result == []

def test_chunk_pages_respects_chunk_size():
    # All chunks should be shorter than the specified chunk_size.
    pages = [
        {
            "text": "Anak usia 6 bulan membutuhkan MPASI yang bergizi" * 20,
            "metadata": {"source": "who.pdf", "page": 1}
        }
    ]
    chunks = chunk_pages(pages, chunk_size=200, chunk_overlap=50)

    for chunk in chunks:
        assert len(chunk["text"]) <= 200