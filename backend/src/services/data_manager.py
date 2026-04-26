import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from models.pokemon import PokemonList, UsageData
from models.party import PartiesData, Party


class DataManager:
    def __init__(self, data_dir: Path | str = Path(__file__).parent.parent.parent / "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "sprites").mkdir(exist_ok=True)
        (self.data_dir / "usage_rates").mkdir(exist_ok=True)

    def save_pokemon_list(self, data: PokemonList) -> None:
        path = self.data_dir / "pokemon_list.json"
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    def load_pokemon_list(self) -> Optional[PokemonList]:
        path = self.data_dir / "pokemon_list.json"
        if not path.exists():
            return None
        return PokemonList.model_validate_json(path.read_text(encoding="utf-8"))

    def save_parties(self, data: PartiesData) -> None:
        path = self.data_dir / "parties.json"
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    def load_parties(self) -> PartiesData:
        path = self.data_dir / "parties.json"
        if not path.exists():
            return PartiesData(parties=[])
        return PartiesData.model_validate_json(path.read_text(encoding="utf-8"))

    def save_usage_data(self, data: UsageData) -> None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        path = self.data_dir / "usage_rates" / f"{date_str}.json"
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    def load_latest_usage_data(self) -> Optional[UsageData]:
        rate_dir = self.data_dir / "usage_rates"
        files = sorted(rate_dir.glob("*.json"), reverse=True)
        if not files:
            return None
        return UsageData.model_validate_json(files[0].read_text(encoding="utf-8"))
