import pytest
from infrastructure.persistence.json_llm_config_repository import JsonLLMConfigRepository
from domain.entities.llm_config import LLMConfig, ProviderSettings


def test_get_config_returns_default_when_no_file(tmp_path):
    repo = JsonLLMConfigRepository(data_dir=tmp_path)
    config = repo.get_config()
    assert config.selected_provider == "anthropic"
    assert config.providers["anthropic"].model == "claude-sonnet-4-6"
    assert config.providers["openai"].model == "gpt-4o"
    assert config.providers["google"].model == "gemini-2.0-flash"
    assert config.providers["ollama"].model is None
    assert config.providers["ollama"].base_url is None


def test_save_and_get_config_roundtrip(tmp_path):
    repo = JsonLLMConfigRepository(data_dir=tmp_path)
    config = LLMConfig(
        selected_provider="openai",
        providers={
            "anthropic": ProviderSettings(model="claude-sonnet-4-6", base_url=None),
            "openai": ProviderSettings(model="gpt-4o-mini", base_url=None),
            "google": ProviderSettings(model="gemini-2.0-flash", base_url=None),
            "ollama": ProviderSettings(model=None, base_url="http://host.docker.internal:11434"),
        },
    )
    repo.save_config(config)
    loaded = repo.get_config()
    assert loaded.selected_provider == "openai"
    assert loaded.providers["openai"].model == "gpt-4o-mini"
    assert loaded.providers["ollama"].base_url == "http://host.docker.internal:11434"


def test_save_creates_json_file(tmp_path):
    repo = JsonLLMConfigRepository(data_dir=tmp_path)
    config = LLMConfig(
        selected_provider="anthropic",
        providers={"anthropic": ProviderSettings(model="claude-sonnet-4-6", base_url=None)},
    )
    repo.save_config(config)
    assert (tmp_path / "llm_config.json").exists()


def test_get_config_creates_data_dir_if_missing(tmp_path):
    nested = tmp_path / "nested" / "dir"
    repo = JsonLLMConfigRepository(data_dir=nested)
    config = repo.get_config()
    assert config.selected_provider == "anthropic"
