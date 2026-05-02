import re
from pathlib import Path
from typing import Optional
from domain.entities.pokemon import UsageData
from domain.repositories.usage_repository import IUsageRepository

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class JsonUsageRepository(IUsageRepository):
    def __init__(self, data_dir: Path | str = Path(__file__).parent.parent.parent.parent / "data"):
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        (self._data_dir / "usage_rates").mkdir(exist_ok=True)

    def _sorted_rate_files(self) -> list[Path]:
        return sorted((self._data_dir / "usage_rates").glob("*.json"), reverse=True)

    def get_usage_data(self) -> Optional[UsageData]:
        files = self._sorted_rate_files()
        if not files:
            return None
        return UsageData.model_validate_json(files[0].read_text(encoding="utf-8"))

    def save_usage_data(self, data: UsageData) -> None:
        date_str = data.collected_at[:10]
        path = self._data_dir / "usage_rates" / f"{date_str}.json"
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    def get_available_dates(self) -> list[str]:
        return [f.stem for f in self._sorted_rate_files()]

    def get_usage_data_by_date(self, date: str) -> Optional[UsageData]:
        if not _DATE_RE.fullmatch(date):
            raise ValueError(f"date must be YYYY-MM-DD, got: {date!r}")
        path = self._data_dir / "usage_rates" / f"{date}.json"
        if not path.exists():
            return None
        return UsageData.model_validate_json(path.read_text(encoding="utf-8"))
