import pytest

from domain.entities.prompt_config import PromptConfig
from domain.repositories.prompt_config_repository import IPromptConfigRepository


def test_prompt_config_is_frozen():
    config = PromptConfig(system_prompt="sys", user_prompt_template="user {x}")
    assert config.system_prompt == "sys"
    assert config.user_prompt_template == "user {x}"

    with pytest.raises(Exception):
        config.system_prompt = "other"  # type: ignore


def test_prompt_config_repository_is_abstract():
    with pytest.raises(TypeError):
        IPromptConfigRepository()  # type: ignore
