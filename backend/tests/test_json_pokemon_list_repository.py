import pytest
from pathlib import Path
from domain.entities.pokemon import PokemonList, PokemonInfo, BaseStats
from infrastructure.persistence.json_pokemon_list_repository import JsonPokemonListRepository


def _make_pokemon_info(name: str = "フシギバナ", pokedex_id: int = 3) -> PokemonInfo:
    return PokemonInfo(
        pokedex_id=pokedex_id,
        name=name,
        types=["くさ", "どく"],
        base_stats=BaseStats(hp=80, attack=82, defense=83, sp_attack=100, sp_defense=100, speed=80),
        height_m=2.0,
        weight_kg=100.0,
        low_kick_power=100,
        abilities=["しんりょく", "ようりょくそ"],
        no_effect_types=[],
        quarter_damage_types=["くさ"],
        half_damage_types=["みず", "でんき", "かくとう", "フェアリー"],
        double_damage_types=["ほのお", "こおり", "ひこう", "エスパー"],
        quad_damage_types=[],
        sprite_path="sprites/003.png",
    )


@pytest.fixture
def repo(tmp_path: Path) -> JsonPokemonListRepository:
    return JsonPokemonListRepository(data_dir=tmp_path)


def test_get_pokemon_list_returns_none_when_file_missing(repo: JsonPokemonListRepository) -> None:
    assert repo.get_pokemon_list() is None


def test_save_and_get_pokemon_list(repo: JsonPokemonListRepository) -> None:
    data = PokemonList(
        collected_at="2026-05-02T00:00:00",
        pokemons=[_make_pokemon_info()],
        mega_pokemons=[],
    )
    repo.save_pokemon_list(data)
    result = repo.get_pokemon_list()
    assert result is not None
    assert len(result.pokemons) == 1
    assert result.pokemons[0].name == "フシギバナ"
    assert result.mega_pokemons == []


def test_save_and_get_pokemon_list_with_mega(repo: JsonPokemonListRepository) -> None:
    mega = _make_pokemon_info(name="メガフシギバナ")
    data = PokemonList(
        collected_at="2026-05-02T00:00:00",
        pokemons=[_make_pokemon_info()],
        mega_pokemons=[mega],
    )
    repo.save_pokemon_list(data)
    result = repo.get_pokemon_list()
    assert result is not None
    assert len(result.mega_pokemons) == 1
    assert result.mega_pokemons[0].name == "メガフシギバナ"


def test_save_overwrites_existing_file(repo: JsonPokemonListRepository) -> None:
    data1 = PokemonList(
        collected_at="2026-05-01T00:00:00",
        pokemons=[_make_pokemon_info("フシギバナ")],
        mega_pokemons=[],
    )
    data2 = PokemonList(
        collected_at="2026-05-02T00:00:00",
        pokemons=[_make_pokemon_info("リザードン", pokedex_id=6)],
        mega_pokemons=[],
    )
    repo.save_pokemon_list(data1)
    repo.save_pokemon_list(data2)
    result = repo.get_pokemon_list()
    assert result is not None
    assert result.pokemons[0].name == "リザードン"
