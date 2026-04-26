import pytest
from pathlib import Path
from services.data_manager import DataManager


@pytest.fixture(autouse=True)
def use_temp_data_dir(tmp_path):
    """Redirect all DataManager instances in routers to use tmp_path for test isolation."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "sprites").mkdir()
    (data_dir / "usage_rates").mkdir()

    temp_manager = DataManager(data_dir=data_dir)

    import routers.party as rp
    import routers.prediction as rpred
    import routers.data as rd

    original_party = rp._manager
    original_pred = rpred._manager
    original_data = rd._manager

    rp._manager = temp_manager
    rpred._manager = temp_manager
    rd._manager = temp_manager

    yield

    rp._manager = original_party
    rpred._manager = original_pred
    rd._manager = original_data
