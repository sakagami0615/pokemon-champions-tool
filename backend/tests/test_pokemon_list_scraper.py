import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from domain.entities.pokemon import PokemonInfo
from infrastructure.external.pokemon_list_scraper import PokemonListScraper

LIST_HTML = """
<html><body>
<ol class="w-pokemon-list">
  <li class="w-pokemon-list-element">
    <div class="_inner">
      <div class="_inner-header">
        <span class="_no">No.0003</span>
        <a href="https://gamewith.jp/pokemon-champions/553138" class="_name">フシギバナ</a>
      </div>
    </div>
  </li>
  <li class="w-pokemon-list-element">
    <div class="_inner">
      <div class="_inner-header">
        <span class="_no">No.0003</span>
        <a href="https://gamewith.jp/pokemon-champions/553140" class="_name">メガフシギバナ</a>
      </div>
    </div>
  </li>
  <li class="w-pokemon-list-element">
    <div class="_inner">
      <div class="_inner-header">
        <span class="_no">No.0006</span>
        <a href="https://gamewith.jp/pokemon-champions/553141" class="_name">リザードン</a>
      </div>
    </div>
  </li>
</ol>
</body></html>
"""

DETAIL_HTML = """
<html><body>
<table class="_pokechamp_pkm_status">
  <tbody>
    <tr>
      <td width="40%" rowspan="7" class="icon">
        <div class="_inner">
          <div class="w-article-img">
            <img data-original="https://example.com/bulbasaur.png" src="placeholder" />
          </div>
          <div class="_no">No.0003</div>
          フシギバナ
          <hr/>
          <div class="_type">
            <img alt="くさ" /><img alt="どく" />
          </div>
        </div>
      </td>
    </tr>
    <tr>
      <th width="12%">HP</th>
      <td><div class="_inner-table"><div class="_bar-column"><div class="pokeza_bar_bg"><div class="_num">80</div></div></div></div></td>
    </tr>
    <tr>
      <th>攻撃</th>
      <td><div class="_inner-table"><div class="_bar-column"><div class="pokeza_bar_bg"><div class="_num">82</div></div></div></div></td>
    </tr>
    <tr>
      <th>防御</th>
      <td><div class="_inner-table"><div class="_bar-column"><div class="pokeza_bar_bg"><div class="_num">83</div></div></div></div></td>
    </tr>
    <tr>
      <th>特攻</th>
      <td><div class="_inner-table"><div class="_bar-column"><div class="pokeza_bar_bg"><div class="_num">100</div></div></div></div></td>
    </tr>
    <tr>
      <th>特防</th>
      <td><div class="_inner-table"><div class="_bar-column"><div class="pokeza_bar_bg"><div class="_num">100</div></div></div></div></td>
    </tr>
    <tr>
      <th>素早</th>
      <td><div class="_inner-table"><div class="_bar-column"><div class="pokeza_bar_bg"><div class="_num">80</div></div></div></div></td>
    </tr>
    <tr>
      <td class="_height_weight">2.0m / 100.0kg</td>
      <td colspan="2" class="_sex">けたぐり・くさむすびの威力：100</td>
    </tr>
  </tbody>
</table>
<table class="_pokechamp_ability">
  <tbody>
    <tr>
      <th><span>特性1</span><a href="/p/555131">しんりょく</a></th>
      <td>HPが最大HPの1/3以下になると威力が上がる。</td>
    </tr>
    <tr>
      <th><span>隠れ特性</span><a href="/p/555039">ようりょくそ</a></th>
      <td>にほんばれ状態の時、素早さが2倍になる。</td>
    </tr>
  </tbody>
</table>
<ol class="_pokechamp_pkm_typechart">
  <li data-attr="x2">
    <div class="_inner"><div class="_inner-body">
      <img alt="ほのお"/><img alt="こおり"/><img alt="ひこう"/><img alt="エスパー"/>
    </div></div>
  </li>
  <li data-attr="x0.5">
    <div class="_inner"><div class="_inner-body">
      <img alt="みず"/><img alt="でんき"/><img alt="かくとう"/><img alt="フェアリー"/>
    </div></div>
  </li>
  <li data-attr="x0.25">
    <div class="_inner"><div class="_inner-body">
      <img alt="くさ"/>
    </div></div>
  </li>
  <li data-attr="x0">
    <div class="_inner"><div class="_inner-body"></div></div>
  </li>
</ol>
</body></html>
"""


@pytest.fixture
def scraper(tmp_path: Path) -> PokemonListScraper:
    return PokemonListScraper(sprites_dir=tmp_path)


def _make_list_soup() -> BeautifulSoup:
    return BeautifulSoup(LIST_HTML, "html.parser")


def _make_detail_soup() -> BeautifulSoup:
    return BeautifulSoup(DETAIL_HTML, "html.parser")


def test_parse_list_page_extracts_entries(scraper: PokemonListScraper) -> None:
    entries = scraper._parse_list_page(_make_list_soup())
    assert len(entries) == 3
    assert entries[0] == (3, "フシギバナ", "https://gamewith.jp/pokemon-champions/553138")
    assert entries[1] == (3, "メガフシギバナ", "https://gamewith.jp/pokemon-champions/553140")
    assert entries[2] == (6, "リザードン", "https://gamewith.jp/pokemon-champions/553141")


def test_group_entries_separates_normal_and_mega(scraper: PokemonListScraper) -> None:
    entries = [
        (3, "フシギバナ", "https://gamewith.jp/pokemon-champions/553138"),
        (3, "メガフシギバナ", "https://gamewith.jp/pokemon-champions/553140"),
        (6, "リザードン", "https://gamewith.jp/pokemon-champions/553141"),
    ]
    normals, megas = scraper._group_entries(entries)
    assert len(normals) == 2
    assert len(megas) == 1
    assert normals[0] == (3, "フシギバナ", "https://gamewith.jp/pokemon-champions/553138", "003.png")
    assert normals[1] == (6, "リザードン", "https://gamewith.jp/pokemon-champions/553141", "006.png")
    assert megas[0] == (3, "メガフシギバナ", "https://gamewith.jp/pokemon-champions/553140", "003-mega-1.png")


def test_parse_detail_page_base_stats(scraper: PokemonListScraper, tmp_path: Path) -> None:
    with patch.object(scraper, "_download_sprite", return_value="sprites/003.png"):
        info = scraper._parse_detail_page(_make_detail_soup(), pokedex_id=3, name="フシギバナ", sprite_filename="003.png")
    assert info.base_stats.hp == 80
    assert info.base_stats.attack == 82
    assert info.base_stats.defense == 83
    assert info.base_stats.sp_attack == 100
    assert info.base_stats.sp_defense == 100
    assert info.base_stats.speed == 80


def test_parse_detail_page_types(scraper: PokemonListScraper) -> None:
    with patch.object(scraper, "_download_sprite", return_value="sprites/003.png"):
        info = scraper._parse_detail_page(_make_detail_soup(), pokedex_id=3, name="フシギバナ", sprite_filename="003.png")
    assert info.types == ["くさ", "どく"]


def test_parse_detail_page_abilities(scraper: PokemonListScraper) -> None:
    with patch.object(scraper, "_download_sprite", return_value="sprites/003.png"):
        info = scraper._parse_detail_page(_make_detail_soup(), pokedex_id=3, name="フシギバナ", sprite_filename="003.png")
    assert info.abilities == ["しんりょく", "ようりょくそ"]


def test_parse_detail_page_height_weight(scraper: PokemonListScraper) -> None:
    with patch.object(scraper, "_download_sprite", return_value="sprites/003.png"):
        info = scraper._parse_detail_page(_make_detail_soup(), pokedex_id=3, name="フシギバナ", sprite_filename="003.png")
    assert info.height_m == 2.0
    assert info.weight_kg == 100.0


def test_parse_detail_page_low_kick_power(scraper: PokemonListScraper) -> None:
    with patch.object(scraper, "_download_sprite", return_value="sprites/003.png"):
        info = scraper._parse_detail_page(_make_detail_soup(), pokedex_id=3, name="フシギバナ", sprite_filename="003.png")
    assert info.low_kick_power == 100


def test_parse_detail_page_type_chart(scraper: PokemonListScraper) -> None:
    with patch.object(scraper, "_download_sprite", return_value="sprites/003.png"):
        info = scraper._parse_detail_page(_make_detail_soup(), pokedex_id=3, name="フシギバナ", sprite_filename="003.png")
    assert info.double_damage_types == ["ほのお", "こおり", "ひこう", "エスパー"]
    assert info.half_damage_types == ["みず", "でんき", "かくとう", "フェアリー"]
    assert info.quarter_damage_types == ["くさ"]
    assert info.no_effect_types == []


def test_fetch_pokemon_list_splits_normals_and_megas(scraper: PokemonListScraper) -> None:
    detail_soup = _make_detail_soup()
    with patch.object(scraper, "_fetch", side_effect=[_make_list_soup(), detail_soup, detail_soup, detail_soup]):
        with patch.object(scraper, "_download_sprite", return_value="sprites/003.png"):
            pokemons, mega_pokemons = scraper.fetch_pokemon_list()
    assert len(pokemons) == 2
    assert len(mega_pokemons) == 1
    assert pokemons[0].name == "フシギバナ"
    assert mega_pokemons[0].name == "メガフシギバナ"
