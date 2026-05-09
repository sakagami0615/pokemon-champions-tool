from pathlib import Path
import yaml
from domain.entities.prompt_config import PromptConfig
from domain.repositories.prompt_config_repository import IPromptConfigRepository


class YamlPromptConfigRepository(IPromptConfigRepository):
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path

    def get_config(self) -> PromptConfig:
        with open(self._config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return PromptConfig(
            system_prompt=data["system_prompt"],
            user_prompt_template=data["user_prompt_template"],
        )
