import pytest
from domain.entities.llm_config import LLMConfig, ProviderSettings


def test_provider_settings_is_immutable():
    s = ProviderSettings(model="claude-sonnet-4-6", base_url=None)
    with pytest.raises((AttributeError, TypeError)):
        s.model = "other"  # type: ignore[misc]


def test_provider_settings_allows_none_model():
    s = ProviderSettings(model=None, base_url="http://host.docker.internal:11434")
    assert s.model is None
    assert s.base_url == "http://host.docker.internal:11434"


def test_llm_config_holds_selected_provider():
    config = LLMConfig(
        selected_provider="anthropic",
        providers={
            "anthropic": ProviderSettings(model="claude-sonnet-4-6", base_url=None),
        },
    )
    assert config.selected_provider == "anthropic"
    assert config.providers["anthropic"].model == "claude-sonnet-4-6"


def test_llm_config_is_immutable():
    config = LLMConfig(
        selected_provider="anthropic",
        providers={"anthropic": ProviderSettings(model="claude-sonnet-4-6", base_url=None)},
    )
    with pytest.raises((AttributeError, TypeError)):
        config.selected_provider = "openai"  # type: ignore[misc]
