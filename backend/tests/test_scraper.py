from unittest.mock import patch, MagicMock
import pytest
from infrastructure.external.scraper import GameWithScraper


def test_scraper_initializes(tmp_path):
    scraper = GameWithScraper(sprites_dir=tmp_path)
    assert scraper.sprites_dir == tmp_path


@patch("infrastructure.external.base_scraper.requests.get")
def test_fetch_with_rate_limit(mock_get, tmp_path):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html></html>"
    mock_get.return_value = mock_resp

    scraper = GameWithScraper(sprites_dir=tmp_path)
    scraper._fetch("https://example.com")
    mock_get.assert_called_once()
