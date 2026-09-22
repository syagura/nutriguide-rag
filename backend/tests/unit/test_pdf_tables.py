from unittest.mock import MagicMock
from src.core.services.processing.pdf_tables import format_table, extract_page_tables_text

def test_format_table_joins_rows_with_pipe():
    table = [["Gejala", "Klasifikasi"], ["Demam tinggi", "Berat"]]
    result = format_table(table)
    assert result == "Gejala | Klasifikasi\nDemam tinggi | Berat"

def test_format_table_handles_none_cells():
    table = [["A", None], [None, "B"]]
    result = format_table(table)
    assert result == "A | \n | B"

def test_extract_page_tables_text_returns_empty_when_no_tables():
    mock_page = MagicMock()
    mock_page.extract_tables.return_value = []
    assert extract_page_tables_text(mock_page) == ""

def test_extract_page_tables_text_formats_single_table():
    mock_page = MagicMock()
    mock_page.extract_tables.return_value = [[["Gejala", "Klafisikasi"], ["Pilek", "Ringan"]]]

    result = extract_page_tables_text(mock_page)
    assert "[TABLE]" in result
    assert "Gejala | Klasifikasi" in result

def test_extract_page_tables_text_handles_multiple_tables():
    mock_page = MagicMock()
    mock_page.extract_tables.return_value = [
        [["A", "B"]],
        [["C", "D"]]
    ]
    result = extract_page_tables_text(mock_page)
    assert result.count("[TABLE]") == 2

def test_extract_page_tables_text_returns_empty_on_exception():
    mock_page = MagicMock()
    mock_page.extract_tables.side_effect = Exception("parsing error")
    assert extract_page_tables_text(mock_page) == ""