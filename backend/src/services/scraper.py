import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup

POKEMON_LIST_URL = "https://gamewith.jp/pokemon-champions/546414"
USAGE_RANKING_URL = "https://gamewith.jp/pokemon-champions/555373"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PokemonChampionsTool/1.0)"}


class GameWithScraper:
    def __init__(self, sprites_dir: Path, request_interval: float = 2.0):
        self.sprites_dir = Path(sprites_dir)
        self.request_interval = request_interval

    def _fetch(self, url: str) -> BeautifulSoup:
        time.sleep(self.request_interval)
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")

    def _download_sprite(self, url: str, filename: str) -> str:
        """スプライト画像をダウンロードして保存パスを返す"""
        time.sleep(self.request_interval)
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        path = self.sprites_dir / filename
        path.write_bytes(resp.content)
        return str(path.relative_to(self.sprites_dir.parent))

    def fetch_pokemon_list(self) -> list[dict]:
        """
        内定ポケモン一覧ページをスクレイピングして各ポケモンの基本情報を返す。
        実際のHTMLの構造に応じてselectorを調整すること。
        返り値: PokemonInfo に変換可能なdictのリスト
        """
        soup = self._fetch(POKEMON_LIST_URL)
        results = []
        for row in soup.select("table.pokemon-table tr.pokemon-row"):
            try:
                name = row.select_one(".pokemon-name").get_text(strip=True)
                sprite_url = row.select_one("img.pokemon-sprite")["src"]
                sprite_filename = f"{name}.png"
                sprite_path = self._download_sprite(sprite_url, sprite_filename)
                results.append({
                    "name": name,
                    "sprite_path": sprite_path,
                })
            except (AttributeError, KeyError):
                continue
        return results

    def fetch_usage_ranking(self) -> list[dict]:
        """
        使用率ランキングTOP30ページをスクレイピングして各ポケモンの詳細を返す。
        返り値: UsageEntry に変換可能なdictのリスト
        """
        soup = self._fetch(USAGE_RANKING_URL)
        results = []
        detail_links = soup.select("a.pokemon-detail-link")[:30]
        for link in detail_links:
            detail_url = link["href"]
            if not detail_url.startswith("http"):
                detail_url = f"https://gamewith.jp{detail_url}"
            detail = self._fetch_pokemon_detail(detail_url)
            if detail:
                results.append(detail)
        return results

    def _fetch_pokemon_detail(self, url: str) -> dict | None:
        """ポケモン詳細ページから型情報を取得する"""
        soup = self._fetch(url)
        try:
            name = soup.select_one("h1.pokemon-name").get_text(strip=True)
            return {"name": name}
        except AttributeError:
            return None
