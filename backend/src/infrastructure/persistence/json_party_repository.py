from pathlib import Path
from domain.entities.party import PartiesData
from domain.repositories.party_repository import IPartyRepository


class JsonPartyRepository(IPartyRepository):
    def __init__(self, data_dir: Path | str = Path(__file__).parent.parent.parent.parent / "data"):
        self._path = Path(data_dir) / "parties.json"

    def get_all(self) -> PartiesData:
        if not self._path.exists():
            return PartiesData(parties=[])
        return PartiesData.model_validate_json(self._path.read_text(encoding="utf-8"))

    def save(self, data: PartiesData) -> None:
        self._path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
