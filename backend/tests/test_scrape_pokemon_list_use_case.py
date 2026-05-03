import pytest
from unittest.mock import MagicMock
from domain.entities.pokemon import PokemonInfo, PokemonList, BaseStats
from application.use_cases.scrape_pokemon_list_use_case import ScrapePokemonListUseCase


def _make_pokemon_info() -> PokemonInfo:
    return PokemonInfo(
        pokedex_id=3,
        name="フシギバナ",
        types=["くさ", "どく"],
        base_stats=BaseStats(hp=80, attack=82, defense=83, sp_attack=100, sp_defense=100, speed=80),
        height_m=2.0,
        weight_kg=100.0,
        low_kick_power=100,
        abilities=["しんりょく"],
        no_effect_types=[],
        quarter_damage_types=["くさ"],
        half_damage_types=["みず"],
        double_damage_types=["ほのお"],
        sprite_path="sprites/003.png",
    )


def test_execute_saves_pokemon_list() -> None:
    scraper = MagicMock()
    repo = MagicMock()
    scraper.fetch_pokemon_list.return_value = ([_make_pokemon_info()], [])

    use_case = ScrapePokemonListUseCase(scraper=scraper, repository=repo)
    use_case.execute()

    repo.save_pokemon_list.assert_called_once()
    saved: PokemonList = repo.save_pokemon_list.call_args[0][0]
    assert isinstance(saved, PokemonList)
    assert len(saved.pokemons) == 1
    assert saved.pokemons[0].name == "フシギバナ"
    assert saved.mega_pokemons == []


def test_execute_includes_mega_pokemons() -> None:
    scraper = MagicMock()
    repo = MagicMock()
    mega = _make_pokemon_info()
    scraper.fetch_pokemon_list.return_value = ([], [mega])

    use_case = ScrapePokemonListUseCase(scraper=scraper, repository=repo)
    use_case.execute()

    saved: PokemonList = repo.save_pokemon_list.call_args[0][0]
    assert len(saved.mega_pokemons) == 1


def test_execute_propagates_scraper_error() -> None:
    scraper = MagicMock()
    repo = MagicMock()
    scraper.fetch_pokemon_list.side_effect = RuntimeError("Network error")

    use_case = ScrapePokemonListUseCase(scraper=scraper, repository=repo)
    with pytest.raises(RuntimeError, match="Network error"):
        use_case.execute()
    repo.save_pokemon_list.assert_not_called()
