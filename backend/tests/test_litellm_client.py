from unittest.mock import patch, MagicMock
from infrastructure.external.litellm_client import LiteLLMClient
from domain.entities.llm_config import LLMConfig, ProviderSettings


def _make_config(provider: str, model: str, base_url=None, api_key=None) -> LLMConfig:
    return LLMConfig(
        selected_provider=provider,
        providers={
            provider: ProviderSettings(model=model, base_url=base_url, api_key=api_key)
        },
    )


def _mock_response(text: str) -> MagicMock:
    resp = MagicMock()
    resp.choices[0].message.content = text
    return resp


def test_anthropic_prefix():
    config = _make_config("anthropic", "claude-sonnet-4-6")
    client = LiteLLMClient(config)
    with patch("litellm.completion", return_value=_mock_response("ok")) as mock_c:
        client.generate("sys", "user")
    assert mock_c.call_args[1]["model"] == "anthropic/claude-sonnet-4-6"


def test_openai_prefix():
    config = _make_config("openai", "gpt-4o")
    client = LiteLLMClient(config)
    with patch("litellm.completion", return_value=_mock_response("ok")) as mock_c:
        client.generate("sys", "user")
    assert mock_c.call_args[1]["model"] == "openai/gpt-4o"


def test_google_uses_gemini_prefix():
    config = _make_config("google", "gemini-2.0-flash")
    client = LiteLLMClient(config)
    with patch("litellm.completion", return_value=_mock_response("ok")) as mock_c:
        client.generate("sys", "user")
    assert mock_c.call_args[1]["model"] == "gemini/gemini-2.0-flash"


def test_ollama_passes_api_base():
    config = _make_config("ollama", "llama3.2", base_url="http://host.docker.internal:11434")
    client = LiteLLMClient(config)
    with patch("litellm.completion", return_value=_mock_response("ok")) as mock_c:
        client.generate("sys", "user")
    assert mock_c.call_args[1]["api_base"] == "http://host.docker.internal:11434"


def test_messages_format():
    config = _make_config("anthropic", "claude-sonnet-4-6")
    client = LiteLLMClient(config)
    with patch("litellm.completion", return_value=_mock_response("ok")) as mock_c:
        client.generate("system text", "user text")
    msgs = mock_c.call_args[1]["messages"]
    assert msgs[0] == {"role": "system", "content": "system text"}
    assert msgs[1] == {"role": "user", "content": "user text"}


def test_api_key_passed_when_set():
    config = _make_config("anthropic", "claude-sonnet-4-6", api_key="sk-test-key")
    client = LiteLLMClient(config)
    with patch("litellm.completion", return_value=_mock_response("ok")) as mock_c:
        client.generate("sys", "user")
    assert mock_c.call_args[1]["api_key"] == "sk-test-key"


def test_api_key_not_passed_when_none():
    config = _make_config("anthropic", "claude-sonnet-4-6", api_key=None)
    client = LiteLLMClient(config)
    with patch("litellm.completion", return_value=_mock_response("ok")) as mock_c:
        client.generate("sys", "user")
    assert "api_key" not in mock_c.call_args[1]
