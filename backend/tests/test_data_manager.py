import json
import pytest
from pathlib import Path
from services.data_manager import DataManager
from models.pokemon import PokemonList, PokemonInfo, BaseStats, UsageData, UsageEntry, RatedItem, EvSpread
from models.party import PartiesData, Party


@pytest.fixture
def data_dir(tmp_path):
    (tmp_path / "sprites").mkdir()
    (tmp_path / "usage_rates").mkdir()
    return tmp_path


@pytest.fixture
def manager(data_dir):
    return DataManager(data_dir=data_dir)


def test_save_and_load_pokemon_list(manager, data_dir):
    pl = PokemonList(
        collected_at="2026-04-26T12:00:00",
        pokemon=[
            PokemonInfo(
                pokedex_id=6, name="リザードン", types=["ほのお"], sprite_path="sprites/006.png",
                base_stats=BaseStats(hp=78, attack=84, defense=78, sp_attack=109, sp_defense=85, speed=100),
                height_m=1.7, weight_kg=90.5, low_kick_power=100,
                abilities=["もうか"], weaknesses=["いわ"], resistances=["くさ"],
            )
        ],
    )
    manager.save_pokemon_list(pl)
    loaded = manager.load_pokemon_list()
    assert loaded.pokemon[0].name == "リザードン"
    assert loaded.pokemon[0].base_stats.hp == 78


def test_load_pokemon_list_returns_none_when_missing(manager):
    assert manager.load_pokemon_list() is None


def test_save_and_load_parties(manager):
    data = PartiesData(
        parties=[Party(id="p1", name="テスト", pokemon=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "ゲンガー", "カビゴン"])],
        last_used_id="p1",
    )
    manager.save_parties(data)
    loaded = manager.load_parties()
    assert loaded.parties[0].name == "テスト"
    assert loaded.last_used_id == "p1"


def test_load_parties_returns_empty_when_missing(manager):
    data = manager.load_parties()
    assert data.parties == []


def test_save_and_load_usage_data(manager):
    usage = UsageData(
        collected_at="2026-04-26T12:00:00",
        season=1,
        regulation="レギュレーションA",
        source_updated_at="2026-04-25",
        pokemon=[
            UsageEntry(
                name="リザードン",
                moves=[RatedItem(name="かえんほうしゃ", rate=78)],
                items=[RatedItem(name="いのちのたま", rate=61)],
                abilities=[RatedItem(name="もうか", rate=82)],
                natures=[RatedItem(name="ひかえめ", rate=67)],
                teammates=[],
                evs=[EvSpread(spread={"H": 0, "A": 0, "B": 0, "C": 252, "D": 4, "S": 252}, rate=52)],
            )
        ],
    )
    manager.save_usage_data(usage)
    loaded = manager.load_latest_usage_data()
    assert loaded.pokemon[0].name == "リザードン"
    assert loaded.season == 1


def test_load_usage_data_returns_none_when_missing(manager):
    assert manager.load_latest_usage_data() is None
