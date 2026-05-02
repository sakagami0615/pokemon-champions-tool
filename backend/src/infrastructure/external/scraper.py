from bs4 import BeautifulSoup
from infrastructure.external.base_scraper import BaseScraper
from infrastructure.external.constants import USAGE_RANKING_URL


class GameWithScraper(BaseScraper):
    def fetch_usage_ranking(self) -> list[dict]:
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
        soup = self._fetch(url)
        try:
            name = soup.select_one("h1.pokemon-name").get_text(strip=True)
            return {"name": name}
        except AttributeError:
            return None
