import pytest
from pathlib import Path
from domain.entities.party import Party, PartiesData
from infrastructure.persistence.json_party_repository import JsonPartyRepository


@pytest.fixture
def repo(tmp_path):
    return JsonPartyRepository(data_dir=tmp_path)


def test_get_all_returns_empty_when_no_file(repo):
    result = repo.get_all()
    assert result.parties == []
    assert result.last_used_id is None


def test_save_and_get_all(repo):
    data = PartiesData(
        parties=[Party(id="p1", name="テスト", pokemon=["リザードン", "カメックス"])],
        last_used_id="p1",
    )
    repo.save(data)
    loaded = repo.get_all()
    assert loaded.parties[0].name == "テスト"
    assert loaded.last_used_id == "p1"


def test_save_overwrites_existing(repo):
    data1 = PartiesData(parties=[Party(id="p1", name="最初", pokemon=[])])
    repo.save(data1)
    data2 = PartiesData(parties=[Party(id="p2", name="更新後", pokemon=[])])
    repo.save(data2)
    loaded = repo.get_all()
    assert len(loaded.parties) == 1
    assert loaded.parties[0].name == "更新後"
