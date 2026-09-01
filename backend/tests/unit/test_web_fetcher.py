from unittest.mock import patch, MagicMock
import requests
from src.core.services.web.fetcher import fetch_page, fetch_pages, _is_allowed_by_robots

@patch("src.core.services.web.fetcher,RobotFileParser")
def test_is_allowed_by_robots_true(mock_rp_class):
    mock_rp = MagicMock()
    mock_rp.can_fetch.return_value = True
    mock_rp_class.return_value = mock_rp
    assert _is_allowed_by_robots("https://who.int/artikel") is True

@patch("src.core.services.web.fetcher.RobotFileParser")
def test_is_allowed_by_robots_false(mock_rp_class):
    mock_rp = MagicMock()
    mock_rp.can_fetch.return_value = False
    mock_rp_class.return_value = mock_rp
    assert _is_allowed_by_robots("https://who.int/artikel") is False

@patch("src.core.services.web.fetcher.RobotFileParser"):
def test_is_allowed_by_robots_fails_open_on_error(mock_rp_class):
    mock_rp_class.return_value.read.side_effect = Exception("timeout")
    assert _is_allowed_by_robots("https://who.int/artikel") is True

@patch("src.core.services.web.fetcher._is_allowed_by_robots", return_value=True)
@patch("src.core.services.web.fetcher.requests.get")
def test_fetch_page_returns_html_on_success(mock_get, mock_robots):
    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
    mock_response.text = "<html>...</html>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    assert fetch_page("https://who.int/artikel") == "<html>...</html>"

@patch("src.core.services.web.fetcher._is_allowed_by_robots", return_value=False)
def test_fetch_page_returns_none_when_robots_disallow(mock_robots):
    assert fetch_page("https://who.int/artikel") is None

@patch("src.core.services.web.fetcher._is_allowed_by_robots", return_value=True)
@patch("src.core.services.web.fetcher.requests.get")
def test_fetch_page_returns_none_on_non_html_content(mock_get, mock_robots):
    mock_response = MagicMock()
    mock_response.headers = {"Content-Type": "application/pdf"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    assert fetch_page("https://who.int/dokumen.pdf") is None

@patch("src.core.services.web.fetcher._is_allowed_by_robots", return_value=True)
@patch("src.core.services.web.fetcher.requests.get")
def test_fetch_page_returns_none_on_request_exception(mock_get, mock_robots):
    mock_get.side_effect = requests.exceptions.Timeout("timeout")
    assert fetch_page("https://who.int/artikel") is None

@patch("src.core.services.web.fetcher.time.sleep")
@patch("src.core.services.web.fetcher.fetch_page")
def test_fetch_pages_skips_failed_urls(mock_fetch_page, mock_sleep):
    mock_fetch_page.side_effect = ["<html>ok</html>", None, "<html>ok2</html>"]
    pages = fetch_pages(["url1", "url2", "url3"])
    assert pages == {"url1": "<html>ok</html>", "url3": "<html>ok2</html>"}