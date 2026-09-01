from unittest.mock import patch, MagicMock
from src.core.services.web.search import search_web, _is_trusted_domain
from ddgs.exceptions import RatelimitException, DDGSException

def test_is_trusted_domain_mathces_exact_domain():
    assert _is_trusted_domain("https://who.int/news/artikel", ["who.int"]) is True

def test_is_trusted_domain_mathces_subdomain():
    assert _is_trusted_domain("https://sehatnegeriku.kemkes.go.id/artikel", ["kemkes.go.id"]) is True

def test_is_trusted_domain_strips_www():
    assert _is_trusted_domain("https://www.alodokter.com/artikel", ["alodokter.com"]) is True

def test_is_trusted_domain_rejects_untrusted():
    assert _is_trusted_domain("https://random-blog.com/artikel", ["who.int", "alodokter.com"]) is False

@patch("src.core.services.web.search.DDGS")
def test_search_web_filters_to_trusted_domain_only(mock_ddgs_class):
    mock_ddgs = MagicMock()
    mock_ddgs.text.return_value = [
        {"title": "Trusted", "href": "https://who.int/artikel-gizi", "body": "..."},
        {"title": "Untrusted", "href": "https://random-blog.com/artikel-gizi", "body": "..."},
    ]
    mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs

    results = search_web("gizi anak", max_results=5, trusted_domains=["who.int"])

    assert len(results) == 1
    assert results[0]["url"] == "https://who.int/artikel-gizi"

@patch("src.core.services.web.search.DDGS")
def test_search_web_respects_max_results_after_filtering(mock_ddgs_class):
    mock_ddgs = MagicMock()
    mock_ddgs.text.return_value = [
        {"title": f"Artikel {i}", "href": f"https://who.int/artikel-{i}", "body": "..."}
        for i in range(10)
    ]
    mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs

    results = search_web("gizi anak", max_results=3, trusted_domains=["who.int"])
    assert len(results) == 3

@patch("src.core.services.web.search.DDGS")
def test_search_web_returns_empty_on_ratelimit(mock_ddgs_class):
    mock_ddgs_class.return_value.__enter__.side_effect = RatelimitException("rate limited")
    assert search_web("gizi anak") == []

@patch("src.core.services.web.search.DDGS")
def test_search_web_returns_empty_on_ddgs_error(mock_ddgs_class):
    mock_ddgs_class.return_value.__enter__.side_effect = DDGSException("search failed")
    assert search_web("gizi anak") == []

@patch("src.core.services.web.search.DDGS")
def test_search_web_skips_results_whitout_url(mock_ddgs_class):
    mock_ddgs = MagicMock()
    mock_ddgs.text.return_value = [
        {"title": "No URL", "href": "", "body": "..."},
        {"title": "Valid", "href": "https://who.int/valid", "body": "..."},
    ]
    mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs

    results = search_web("test", trusted_domains=["who.int"])
    assert len(results) == 1