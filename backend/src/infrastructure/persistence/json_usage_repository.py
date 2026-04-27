from pathlib import Path
from typing import Optional
from domain.entities.pokemon import UsageData, PokemonList
from domain.repositories.usage_repository import IUsageRepository


class JsonUsageRepository(IUsageRepository):
    def __init__(self, data_dir: Path | str = Path(__file__).parent.parent.parent.parent / "data"):
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        (self._data_dir / "usage_rates").mkdir(exist_ok=True)

    def get_usage_data(self) -> Optional[UsageData]:
        rate_dir = self._data_dir / "usage_rates"
        files = sorted(rate_dir.glob("*.json"), reverse=True)
        if not files:
            return None
        return UsageData.model_validate_json(files[0].read_text(encoding="utf-8"))

    def save_usage_data(self, data: UsageData) -> None:
        date_str = data.collected_at[:10]  # "YYYY-MM-DD" from ISO datetime string
        path = self._data_dir / "usage_rates" / f"{date_str}.json"
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    def get_pokemon_list(self) -> Optional[PokemonList]:
        path = self._data_dir / "pokemon_list.json"
        if not path.exists():
            return None
        return PokemonList.model_validate_json(path.read_text(encoding="utf-8"))

    def save_pokemon_list(self, data: PokemonList) -> None:
        path = self._data_dir / "pokemon_list.json"
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
