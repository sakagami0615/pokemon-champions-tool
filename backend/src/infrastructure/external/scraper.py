from bs4 import BeautifulSoup
from infrastructure.external.base_scraper import BaseScraper
from infrastructure.external.constants import USAGE_RANKING_URL


class GameWithScraper(BaseScraper):
    def fetch_usage_ranking(self) -> list[dict]:
        soup = self._fetch(USAGE_RANKING_URL)
        results = []
        for pkm in soup.select(".wd-pkch-battleranking ._list ._pkm"):
            name_el = pkm.select_one("._name")
            if name_el:
                results.append({"name": name_el.get_text(strip=True)})
        return results
