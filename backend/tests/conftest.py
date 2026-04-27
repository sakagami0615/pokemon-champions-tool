import pytest
from infrastructure.persistence.json_party_repository import JsonPartyRepository
from infrastructure.persistence.json_usage_repository import JsonUsageRepository


@pytest.fixture(autouse=True)
def use_temp_data_dir(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "sprites").mkdir()
    (data_dir / "usage_rates").mkdir()

    temp_party_repo = JsonPartyRepository(data_dir=data_dir)
    temp_usage_repo = JsonUsageRepository(data_dir=data_dir)

    import presentation.routers.party as rp
    import presentation.routers.prediction as rpred
    import presentation.routers.data as rd

    original_party = rp._repo
    original_pred_usage = rpred._usage_repo
    original_data_usage = rd._usage_repo

    rp._repo = temp_party_repo
    rpred._usage_repo = temp_usage_repo
    rd._usage_repo = temp_usage_repo

    yield

    rp._repo = original_party
    rpred._usage_repo = original_pred_usage
    rd._usage_repo = original_data_usage
