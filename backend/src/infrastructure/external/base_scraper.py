import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from infrastructure.external.constants import HEADERS, REQUEST_INTERVAL


class BaseScraper:
    def __init__(self, sprites_dir: Path | str):
        self.sprites_dir = Path(sprites_dir)
        self.sprites_dir.mkdir(parents=True, exist_ok=True)

    def _fetch(self, url: str) -> BeautifulSoup:
        time.sleep(REQUEST_INTERVAL)
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")

    def _download_sprite(self, url: str, filename: str) -> str:
        time.sleep(REQUEST_INTERVAL)
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        path = self.sprites_dir / filename
        path.write_bytes(resp.content)
        return f"sprites/{filename}"
