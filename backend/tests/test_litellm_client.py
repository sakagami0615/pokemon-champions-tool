from unittest.mock import patch, MagicMock
from infrastructure.external.litellm_client import LiteLLMClient
from domain.entities.llm_config import LLMConfig, ProviderSettings


def _make_config(provider: str, model: str, base_url: str | None = None) -> LLMConfig:
    return LLMConfig(
        selected_provider=provider,
        providers={provider: ProviderSettings(model=model, base_url=base_url)},
    )


def _mock_response(text: str) -> MagicMock:
    return MagicMock(choices=[MagicMock(message=MagicMock(content=text))])


@patch("infrastructure.external.litellm_client.litellm.completion")
def test_generate_anthropic_uses_correct_prefix(mock_completion):
    mock_completion.return_value = _mock_response("result")
    client = LiteLLMClient(_make_config("anthropic", "claude-sonnet-4-6"))
    result = client.generate("system", "user")
    assert result == "result"
    assert mock_completion.call_args[1]["model"] == "anthropic/claude-sonnet-4-6"


@patch("infrastructure.external.litellm_client.litellm.completion")
def test_generate_openai_uses_correct_prefix(mock_completion):
    mock_completion.return_value = _mock_response("result")
    client = LiteLLMClient(_make_config("openai", "gpt-4o"))
    client.generate("system", "user")
    assert mock_completion.call_args[1]["model"] == "openai/gpt-4o"


@patch("infrastructure.external.litellm_client.litellm.completion")
def test_generate_google_uses_gemini_prefix(mock_completion):
    mock_completion.return_value = _mock_response("result")
    client = LiteLLMClient(_make_config("google", "gemini-2.0-flash"))
    client.generate("system", "user")
    assert mock_completion.call_args[1]["model"] == "gemini/gemini-2.0-flash"


@patch("infrastructure.external.litellm_client.litellm.completion")
def test_generate_ollama_passes_api_base(mock_completion):
    mock_completion.return_value = _mock_response("result")
    client = LiteLLMClient(
        _make_config("ollama", "llama3.2", "http://host.docker.internal:11434")
    )
    client.generate("system", "user")
    kwargs = mock_completion.call_args[1]
    assert kwargs["model"] == "ollama/llama3.2"
    assert kwargs["api_base"] == "http://host.docker.internal:11434"


@patch("infrastructure.external.litellm_client.litellm.completion")
def test_generate_passes_system_and_user_messages(mock_completion):
    mock_completion.return_value = _mock_response("response")
    client = LiteLLMClient(_make_config("anthropic", "claude-sonnet-4-6"))
    client.generate("my system", "my user prompt")
    messages = mock_completion.call_args[1]["messages"]
    assert messages[0] == {"role": "system", "content": "my system"}
    assert messages[1] == {"role": "user", "content": "my user prompt"}
