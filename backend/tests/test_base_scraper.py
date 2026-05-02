import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from infrastructure.external.base_scraper import BaseScraper


class ConcreteScraper(BaseScraper):
    pass


@pytest.fixture
def scraper(tmp_path: Path) -> ConcreteScraper:
    return ConcreteScraper(sprites_dir=tmp_path)


def test_fetch_returns_beautifulsoup(scraper: ConcreteScraper) -> None:
    html = "<html><body><p>test</p></body></html>"
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status = MagicMock()
    with patch("infrastructure.external.base_scraper.requests.get", return_value=mock_resp):
        with patch("infrastructure.external.base_scraper.time.sleep"):
            result = scraper._fetch("https://example.com")
    assert isinstance(result, BeautifulSoup)


def test_fetch_sleeps_before_request(scraper: ConcreteScraper) -> None:
    mock_resp = MagicMock()
    mock_resp.text = "<html></html>"
    mock_resp.raise_for_status = MagicMock()
    with patch("infrastructure.external.base_scraper.requests.get", return_value=mock_resp):
        with patch("infrastructure.external.base_scraper.time.sleep") as mock_sleep:
            scraper._fetch("https://example.com")
    mock_sleep.assert_called_once_with(1.0)


def test_download_sprite_saves_file(scraper: ConcreteScraper, tmp_path: Path) -> None:
    mock_resp = MagicMock()
    mock_resp.content = b"png_bytes"
    mock_resp.raise_for_status = MagicMock()
    with patch("infrastructure.external.base_scraper.requests.get", return_value=mock_resp):
        with patch("infrastructure.external.base_scraper.time.sleep"):
            path = scraper._download_sprite("https://example.com/img.png", "test.png")
    assert (tmp_path / "test.png").read_bytes() == b"png_bytes"
    assert path == "sprites/test.png"
