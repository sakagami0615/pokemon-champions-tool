#!/usr/bin/env python3
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

from application.use_cases.scrape_pokemon_list_use_case import ScrapePokemonListUseCase
from infrastructure.external.pokemon_list_scraper import PokemonListScraper
from infrastructure.persistence.json_pokemon_list_repository import JsonPokemonListRepository

_DATA_DIR = Path(__file__).parent / "output"
_SPRITES_DIR = _DATA_DIR / "sprites"


_logger = logging.getLogger(__name__)


def main() -> None:
    scraper = PokemonListScraper(sprites_dir=_SPRITES_DIR)
    repository = JsonPokemonListRepository(data_dir=_DATA_DIR)
    use_case = ScrapePokemonListUseCase(scraper=scraper, repository=repository)

    _logger.info("スクレイピングを開始します...")
    use_case.execute()

    result = repository.get_pokemon_list()
    if result:
        _logger.info(
            "完了: 通常ポケモン %d 体 / メガシンカ %d 体",
            len(result.pokemons), len(result.mega_pokemons),
        )
        _logger.info("保存先: %s", _DATA_DIR / "pokemon_list.json")


if __name__ == "__main__":
    main()
