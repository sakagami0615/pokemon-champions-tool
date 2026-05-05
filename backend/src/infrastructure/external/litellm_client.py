import litellm
from domain.entities.llm_config import LLMConfig
from domain.repositories.llm_client import ILLMClient

_PROVIDER_PREFIX: dict[str, str] = {
    "anthropic": "anthropic",
    "openai": "openai",
    "google": "gemini",
    "ollama": "ollama",
}


class LiteLLMClient(ILLMClient):
    def __init__(self, config: LLMConfig) -> None:
        self._config = config

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        provider = self._config.selected_provider
        settings = self._config.providers[provider]
        model = f"{_PROVIDER_PREFIX[provider]}/{settings.model}"
        kwargs: dict = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 1024,
        }
        if provider == "ollama" and settings.base_url:
            kwargs["api_base"] = settings.base_url
        if settings.api_key:
            kwargs["api_key"] = settings.api_key
        response = litellm.completion(**kwargs)
        return response.choices[0].message.content
