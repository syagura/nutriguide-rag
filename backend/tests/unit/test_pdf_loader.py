import pytest
from pathlib import Path
from src.core.services.processing.pdf_loader import load_pdf, load_all_pdfs

def test_load_pdf_file_not_found():
    # Harus raise FileNotFoundError kalau file ga ada
    with pytest.raises(FileNotFoundError):
        load_pdf("contoh.pdf")

def test_load_pdf_not_pdf(tmp_path):
    # tmp_path itu fixture bawaan pytest - otomatis bikin folder temporary
    # yang bakal ke-delete sendiri setelah test selesai
    fake_file = tmp_path / "test.txt"
    fake_file.write_text("ini bukan pdf")

    with pytest.raises(ValueError):
        load_pdf(str(fake_file))

def test_load_all_pdfs_empty_folder(tmp_path):
    # folder kosong herus return list kosong, bukan error atau Exception
    result = load_all_pdfs(str(tmp_path))
    assert result == []