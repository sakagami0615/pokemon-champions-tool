import pytest
from pathlib import Path
from domain.entities.pokemon import (
    UsageData, UsageEntry, RatedItem, EvSpread,
)
from infrastructure.persistence.json_usage_repository import JsonUsageRepository


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "usage_rates").mkdir()
    return JsonUsageRepository(data_dir=tmp_path)


def _make_usage_data():
    return UsageData(
        collected_at="2026-04-27T00:00:00",
        season=1,
        regulation="レギュレーションA",
        source_updated_at="2026-04-26",
        pokemons=[
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


def test_get_usage_data_returns_none_when_missing(repo):
    assert repo.get_usage_data() is None


def test_save_and_get_usage_data(repo):
    repo.save_usage_data(_make_usage_data())
    loaded = repo.get_usage_data()
    assert loaded.pokemons[0].name == "リザードン"
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
    assert loaded.pokemons[0].name == "リザードン"


def test_get_usage_data_by_date_raises_on_invalid_format(repo):
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        repo.get_usage_data_by_date("not-a-date")
