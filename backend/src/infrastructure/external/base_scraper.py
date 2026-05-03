import logging
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from infrastructure.external.constants import HEADERS, REQUEST_INTERVAL

_logger = logging.getLogger(__name__)


class BaseScraper:
    def __init__(self, sprites_dir: Path | str):
        self.sprites_dir = Path(sprites_dir)
        self.sprites_dir.mkdir(parents=True, exist_ok=True)

    def _fetch(self, url: str) -> BeautifulSoup:
        _logger.debug("GET %s", url)
        time.sleep(REQUEST_INTERVAL)
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")

    def _download_sprite(self, url: str, filename: str) -> str:
        _logger.debug("スプライト取得: %s", filename)
        time.sleep(REQUEST_INTERVAL)
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        path = self.sprites_dir / filename
        path.write_bytes(resp.content)
        return f"sprites/{filename}"
