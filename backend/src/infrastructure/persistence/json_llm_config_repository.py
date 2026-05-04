import json
import dataclasses
from pathlib import Path
from domain.entities.llm_config import LLMConfig, ProviderSettings
from domain.repositories.llm_config_repository import ILLMConfigRepository

_DEFAULT_CONFIG: dict = {
    "selected_provider": "anthropic",
    "providers": {
        "anthropic": {"model": "claude-sonnet-4-6", "base_url": None},
        "openai": {"model": "gpt-4o", "base_url": None},
        "google": {"model": "gemini-2.0-flash", "base_url": None},
        "ollama": {"model": None, "base_url": "http://host.docker.internal:11434"},
    },
}


class JsonLLMConfigRepository(ILLMConfigRepository):
    def __init__(
        self,
        data_dir: Path | str = Path(__file__).parent.parent.parent.parent / "data",
    ) -> None:
        self._path = Path(data_dir) / "llm_config.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def get_config(self) -> LLMConfig:
        if not self._path.exists():
            return self._from_dict(_DEFAULT_CONFIG)
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return self._from_dict(data)

    def save_config(self, config: LLMConfig) -> None:
        self._path.write_text(
            json.dumps(dataclasses.asdict(config), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _from_dict(self, data: dict) -> LLMConfig:
        providers = {
            k: ProviderSettings(model=v["model"], base_url=v["base_url"])
            for k, v in data["providers"].items()
        }
        return LLMConfig(selected_provider=data["selected_provider"], providers=providers)
