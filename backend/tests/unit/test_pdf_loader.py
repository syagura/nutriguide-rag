import pytest
from pathlib import Path
from src.core.services.processing.pdf_loader import load_pdf, load_all_pdfs
from unittest.mock import patch, MagicMock

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

@patch("src.core.services.processing.pdf_loader.pdfplumber.open")
def test_load_pdf_appends_table_text(mock_plumber_open, tmp_path):
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Isi halaman yang cukup panjang untuk lolos filter minimal. " * 3)
    pdf_path = tmp_path / "test.pdf"
    doc.save(str(pdf_path))
    doc.close()

    mock_plumber_page = MagicMock()
    mock_plumber_page.extract_tables.return_value = [[["Gejala", "Klasifikasi"], ["Pilek", "Ringan"]]]
    mock_plumber_doc = MagicMock()
    mock_plumber_doc.pages = [mock_plumber_page]
    mock_plumber_doc.close = MagicMock()
    mock_plumber_open.return_value = mock_plumber_doc

    pages = load_pdf(str(pdf_path))

    assert len(pages) == 1
    assert "[TABLE]" in pages[0]["text"]
    assert "Gejala | Klasifikasi" in pages[0]["text"]

def test_load_pdf_works_when_pdfplumber_fails(tmp_path):
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Isi halaman yang cukup panjang untuk lolos filter minimal. " * 3)
    pdf_path = tmp_path / "test.pdf"
    doc.save(str(pdf_path))
    doc.close()

    with patch("src.core.services.processing.pdfloader.pdfplumber.open", side_effect=Exception("gagal buka")):
        pages = load_pdf(str(pdf_path))

    assert len(pages) == 1