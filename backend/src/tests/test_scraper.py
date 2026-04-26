from unittest.mock import patch, MagicMock
import pytest
from services.scraper import GameWithScraper


MOCK_POKEMON_LIST_HTML = """
<html><body>
  <div class="pokemon-item">
    <img src="https://img.gamewith.jp/sprites/006.png" alt="リザードン">
    <span class="pokemon-name">リザードン</span>
    <span class="pokemon-type">ほのお/ひこう</span>
    <td class="hp">78</td><td class="attack">84</td><td class="defense">78</td>
    <td class="sp-attack">109</td><td class="sp-defense">85</td><td class="speed">100</td>
    <span class="height">1.7m</span><span class="weight">90.5kg</span>
    <span class="ability">もうか</span>
  </div>
</body></html>
"""


def test_scraper_initializes(tmp_path):
    scraper = GameWithScraper(sprites_dir=tmp_path)
    assert scraper.sprites_dir == tmp_path


@patch("services.scraper.requests.get")
def test_fetch_with_rate_limit(mock_get, tmp_path):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html></html>"
    mock_get.return_value = mock_resp

    scraper = GameWithScraper(sprites_dir=tmp_path, request_interval=0)
    scraper._fetch("https://example.com")
    mock_get.assert_called_once()
