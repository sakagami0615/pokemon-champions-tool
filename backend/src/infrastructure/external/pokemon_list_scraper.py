import re
from bs4 import BeautifulSoup
from domain.entities.pokemon import PokemonInfo, BaseStats
from infrastructure.external.base_scraper import BaseScraper
from infrastructure.external.constants import POKEMON_LIST_URL

_STAT_KEY_MAP = {
    "HP": "hp",
    "攻撃": "attack",
    "防御": "defense",
    "特攻": "sp_attack",
    "特防": "sp_defense",
    "素早": "speed",
}
_TYPE_ATTR_MAP = {
    "x0":    "no_effect_types",
    "x0.25": "quarter_damage_types",
    "x0.5":  "half_damage_types",
    "x2":    "double_damage_types",
}


class PokemonListScraper(BaseScraper):
    def fetch_pokemon_list(self) -> tuple[list[PokemonInfo], list[PokemonInfo]]:
        list_soup = self._fetch(POKEMON_LIST_URL)
        entries = self._parse_list_page(list_soup)
        normals, megas = self._group_entries(entries)

        pokemons: list[PokemonInfo] = []
        for pokedex_id, name, url, sprite_filename in normals:
            detail_soup = self._fetch(url)
            info = self._parse_detail_page(detail_soup, pokedex_id=pokedex_id, name=name, sprite_filename=sprite_filename)
            pokemons.append(info)

        mega_pokemons: list[PokemonInfo] = []
        for pokedex_id, name, url, sprite_filename in megas:
            detail_soup = self._fetch(url)
            info = self._parse_detail_page(detail_soup, pokedex_id=pokedex_id, name=name, sprite_filename=sprite_filename)
            mega_pokemons.append(info)

        return pokemons, mega_pokemons

    def _parse_list_page(self, soup: BeautifulSoup) -> list[tuple[int, str, str]]:
        entries: list[tuple[int, str, str]] = []
        for li in soup.select("ol.w-pokemon-list li.w-pokemon-list-element"):
            no_el = li.select_one("span._no")
            name_el = li.select_one("a._name")
            if not no_el or not name_el:
                continue
            pokedex_id = int(no_el.get_text(strip=True).replace("No.", ""))
            name = name_el.get_text(strip=True)
            url = name_el["href"]
            if not url.startswith("http"):
                url = f"https://gamewith.jp{url}"
            entries.append((pokedex_id, name, url))
        return entries

    def _group_entries(
        self, entries: list[tuple[int, str, str]]
    ) -> tuple[list[tuple[int, str, str, str]], list[tuple[int, str, str, str]]]:
        seen: dict[int, int] = {}
        normals: list[tuple[int, str, str, str]] = []
        megas: list[tuple[int, str, str, str]] = []
        for pokedex_id, name, url in entries:
            count = seen.get(pokedex_id, 0)
            if count == 0:
                sprite_filename = f"{pokedex_id:03d}.png"
                normals.append((pokedex_id, name, url, sprite_filename))
            else:
                sprite_filename = f"{pokedex_id:03d}-mega-{count}.png"
                megas.append((pokedex_id, name, url, sprite_filename))
            seen[pokedex_id] = count + 1
        return normals, megas

    def _parse_detail_page(self, soup: BeautifulSoup, pokedex_id: int, name: str, sprite_filename: str) -> PokemonInfo:
        status_table = soup.select_one("table._pokechamp_pkm_status")

        types = [img["alt"] for img in status_table.select("td.icon div._type img[alt]")]

        raw_stats: dict[str, int] = {}
        for tr in status_table.select("tr"):
            th = tr.select_one("th")
            if not th:
                continue
            th_text = th.get_text(strip=True)
            key = _STAT_KEY_MAP.get(th_text)
            if key:
                num_el = tr.select_one("div._num")
                if num_el:
                    raw_stats[key] = int(num_el.get_text(strip=True))

        hw_td = status_table.select_one("td._height_weight")
        hw_text = hw_td.get_text(strip=True)
        height_str, weight_str = hw_text.split("/")
        height_m = float(height_str.strip().replace("m", ""))
        weight_kg = float(weight_str.strip().replace("kg", ""))

        sex_td = status_table.select_one("td._sex")
        sex_text = sex_td.get_text(strip=True)
        power_match = re.search(r"：(\d+)", sex_text)
        low_kick_power = int(power_match.group(1)) if power_match else 0

        abilities: list[str] = []
        for tr in soup.select("table._pokechamp_ability tbody tr"):
            a_el = tr.select_one("th a")
            if a_el:
                abilities.append(a_el.get_text(strip=True))

        type_chart: dict[str, list[str]] = {
            "no_effect_types": [],
            "quarter_damage_types": [],
            "half_damage_types": [],
            "double_damage_types": [],
        }
        for li in soup.select("ol._pokechamp_pkm_typechart li"):
            attr = li.get("data-attr")
            field = _TYPE_ATTR_MAP.get(attr)
            if field:
                type_chart[field] = [img["alt"] for img in li.select("img[alt]")]

        icon_img = status_table.select_one("td.icon img")
        sprite_url = icon_img.get("data-original") or icon_img.get("src", "")
        sprite_path = self._download_sprite(sprite_url, sprite_filename)

        return PokemonInfo(
            pokedex_id=pokedex_id,
            name=name,
            types=types,
            base_stats=BaseStats(**raw_stats),
            height_m=height_m,
            weight_kg=weight_kg,
            low_kick_power=low_kick_power,
            abilities=abilities,
            **type_chart,
            sprite_path=sprite_path,
        )
