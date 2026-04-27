import pytest
from pathlib import Path
from domain.entities.pokemon import (
    PokemonList, PokemonInfo, BaseStats,
    UsageData, UsageEntry, RatedItem, EvSpread,
)
from infrastructure.persistence.json_usage_repository import JsonUsageRepository


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "usage_rates").mkdir()
    return JsonUsageRepository(data_dir=tmp_path)


def _make_pokemon_list():
    return PokemonList(
        collected_at="2026-04-27T00:00:00",
        pokemon=[
            PokemonInfo(
                pokedex_id=6, name="リザードン", types=["ほのお"],
                sprite_path="sprites/006.png",
                base_stats=BaseStats(hp=78, attack=84, defense=78,
                                     sp_attack=109, sp_defense=85, speed=100),
                height_m=1.7, weight_kg=90.5, low_kick_power=100,
                abilities=["もうか"], weaknesses=["いわ"], resistances=["くさ"],
            )
        ],
    )


def _make_usage_data():
    return UsageData(
        collected_at="2026-04-27T00:00:00",
        season=1,
        regulation="レギュレーションA",
        source_updated_at="2026-04-26",
        pokemon=[
            UsageEntry(
                name="リザードン",
                moves=[RatedItem(name="かえんほうしゃ", rate=78)],
                items=[RatedItem(name="いのちのたま", rate=61)],
                abilities=[RatedItem(name="もうか", rate=82)],
                natures=[RatedItem(name="ひかえめ", rate=67)],
                teammates=[],
                evs=[EvSpread(spread={"C": 252, "S": 252, "H": 0, "A": 0, "B": 0, "D": 4}, rate=52)],
            )
        ],
    )


def test_get_pokemon_list_returns_none_when_missing(repo):
    assert repo.get_pokemon_list() is None


def test_save_and_get_pokemon_list(repo):
    repo.save_pokemon_list(_make_pokemon_list())
    loaded = repo.get_pokemon_list()
    assert loaded.pokemon[0].name == "リザードン"


def test_get_usage_data_returns_none_when_missing(repo):
    assert repo.get_usage_data() is None


def test_save_and_get_usage_data(repo):
    repo.save_usage_data(_make_usage_data())
    loaded = repo.get_usage_data()
    assert loaded.pokemon[0].name == "リザードン"
    assert loaded.season == 1


def test_get_usage_data_returns_latest(repo):
    data_old = _make_usage_data()
    data_old = data_old.model_copy(update={"collected_at": "2026-04-25T00:00:00"})
    data_new = _make_usage_data()
    # data_new has collected_at="2026-04-27T00:00:00" from _make_usage_data()
    repo.save_usage_data(data_old)
    repo.save_usage_data(data_new)
    loaded = repo.get_usage_data()
    assert loaded is not None
    assert loaded.collected_at == "2026-04-27T00:00:00"


def test_get_available_dates_empty(repo):
    assert repo.get_available_dates() == []


def test_get_available_dates_returns_sorted_desc(repo):
    old = _make_usage_data().model_copy(update={"collected_at": "2026-04-25T00:00:00"})
    new = _make_usage_data()  # collected_at="2026-04-27T00:00:00"
    repo.save_usage_data(old)
    repo.save_usage_data(new)
    dates = repo.get_available_dates()
    assert dates == ["2026-04-27", "2026-04-25"]


def test_get_usage_data_by_date_returns_none_for_missing(repo):
    assert repo.get_usage_data_by_date("2026-04-27") is None


def test_get_usage_data_by_date_returns_correct_data(repo):
    data = _make_usage_data()  # collected_at="2026-04-27T00:00:00"
    repo.save_usage_data(data)
    loaded = repo.get_usage_data_by_date("2026-04-27")
    assert loaded is not None
    assert loaded.pokemon[0].name == "リザードン"
