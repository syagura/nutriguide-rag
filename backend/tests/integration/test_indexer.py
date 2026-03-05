import pytest
import fitz
from pathlib import Path
from tests.integration.helpers import create_dummy_pdf
from src.core.services.rag.indexer import build_index

@pytest.fixture
def dummy_pdf_dir(tmp_path):
    pdf_path = tmp_path / "test_doc.pdf"
    create_dummy_pdf(str(pdf_path))
    return str(tmp_path)

def test_build_index_returns_summary(dummy_pdf_dir, tmp_path):
    vector_dir = str(tmp_path / "vectordb")
    bm25_dir = str(tmp_path / "vectordb")

    summary = build_index(
        raw_dir=dummy_pdf_dir,
        vector_dir=vector_dir,
        bm25_dir=bm25_dir
    )

    assert "n_pages" in summary
    assert "n_chunks" in summary
    assert "vector_dir" in summary
    assert "bm25_dir" in summary

def test_build_index_creates_index_files(dummy_pdf_dir, tmp_path):
    vector_dir = str(tmp_path / "vectordb")

    build_index(
        raw_dir=dummy_pdf_dir,
        vector_dir=vector_dir,
        bm25_dir=vector_dir
    )

    assert (Path(vector_dir) / "index.faiss").exists()
    assert (Path(vector_dir) / "chunks.pkl").exists()
    assert (Path(vector_dir) / "bm25.pkl").exists()

def test_build_index_empty_dir_raises(tmp_path):
    with pytest.raises(ValueError):
        build_index(raw_dir=str(tmp_path))