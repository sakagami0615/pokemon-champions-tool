import pytest
from pathlib import Path
from infrastructure.persistence.yaml_prompt_config_repository import YamlPromptConfigRepository


def test_loads_config_from_yaml(tmp_path: Path):
    config_file = tmp_path / "prompts.yaml"
    config_file.write_text(
        "system_prompt: 'sys'\nuser_prompt_template: 'user {x}'\n", encoding="utf-8"
    )
    repo = YamlPromptConfigRepository(config_file)
    config = repo.get_config()
    assert config.system_prompt == "sys"
    assert config.user_prompt_template == "user {x}"


def test_reloads_on_each_call(tmp_path: Path):
    config_file = tmp_path / "prompts.yaml"
    config_file.write_text(
        "system_prompt: 'v1'\nuser_prompt_template: 'tmpl'\n", encoding="utf-8"
    )
    repo = YamlPromptConfigRepository(config_file)
    repo.get_config()
    config_file.write_text(
        "system_prompt: 'v2'\nuser_prompt_template: 'tmpl'\n", encoding="utf-8"
    )
    config = repo.get_config()
    assert config.system_prompt == "v2"


def test_raises_when_file_missing(tmp_path: Path):
    repo = YamlPromptConfigRepository(tmp_path / "nonexistent.yaml")
    with pytest.raises(FileNotFoundError):
        repo.get_config()
