from unittest.mock import patch, MagicMock
from src.core.services.web.extractor import extract_content, _extract_with_bs4

@patch("src.core.services.web.extractor.trafilatura.extract_metadata")
@patch("src.core.services.web.extractor.trafilatura.extract")
def test_extract_content_uses_trafilatura_result(mock_extract, mock_metadata):
    mock_extract.return_value = "Ini adalah artikel gizi anak yang cukup panjang. " * 10
    mock_meta = MagicMock()
    mock_meta.title = "Panduan Gizi Anak"
    mock_metadata.return_value = mock_meta

    result = extract_content("<html>...</html>", "https://who.int/artikel")

    assert result is not None
    assert result["title"] == "Panduan Gizi Anak"
    assert "gizi anak" in result["text"]

@patch("src.core.services.web.extractor.trafilatura.extract_metadata")
@patch("src.core.services.web.extractor.trafilatura.extract")
def test_extract_content_falls_back_to_bs4_when_trafilatura_empty(mock_extract, mock_metadata):
    mock_extract.return_value = None
    mock_metadata.return_value = None

    html = f"<html><head><title>Judul BS4</title></head><body><p>{'Kontent gizi anak penting. ' * 15}</p></body></html>"
    result = extract_content(html, "https://who.int/artikel")

    assert result is not None
    assert result["title"] == "Judul BS4"
    assert "gizi anak" in result["text"]

@patch("src.core.services.web.extractor.trafilatura.extract_metadata")
@patch("src.core.services.web.extractor.trafilatura.extract")
def test_extract_content_returns_none_when_nothing_meaningful(mock_extract, mock_metadata):
    mock_extract.return_value = "terlalu pendek"
    mock_metadata.return_value = None

    result = extract_content("<html><body><nav>Menu</nav></body></html>", "https://who.int/artikel")
    assert result is None

def test_extract_with_bs4_strips_script_and_nav():
    html = """
    <html.><head><title>Test</title></head>
    <body>
        <nav>Navigasi</nav>
        <script>alert('x')</script>
        <p>Ini konten utama</p>
    </body></html>
    """
    text, title = _extract_with_bs4(html)

    assert title == "Test"
    assert "konten utama" in text
    assert "alert" not in text
    assert "Navigasi" not in text