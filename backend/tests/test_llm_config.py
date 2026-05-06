import pytest
from domain.entities.llm_config import LLMConfig, ProviderSettings


def test_provider_settings_immutable():
    s = ProviderSettings(model="claude-sonnet-4-6", base_url=None)
    with pytest.raises(Exception):
        s.model = "other"  # type: ignore


def test_provider_settings_allows_none_model():
    s = ProviderSettings(model=None, base_url=None)
    assert s.model is None


def test_provider_settings_api_key_defaults_to_none():
    s = ProviderSettings(model="gpt-4o", base_url=None)
    assert s.api_key is None


def test_provider_settings_api_key_stored():
    s = ProviderSettings(model="gpt-4o", base_url=None, api_key="sk-test")
    assert s.api_key == "sk-test"


def test_llm_config_field_access():
    config = LLMConfig(
        selected_provider="anthropic",
        providers={"anthropic": ProviderSettings(model="claude-sonnet-4-6", base_url=None)},
    )
    assert config.selected_provider == "anthropic"
    assert config.providers["anthropic"].model == "claude-sonnet-4-6"


def test_llm_config_immutable():
    config = LLMConfig(
        selected_provider="anthropic",
        providers={"anthropic": ProviderSettings(model="claude-sonnet-4-6", base_url=None)},
    )
    with pytest.raises(Exception):
        config.selected_provider = "openai"  # type: ignore
