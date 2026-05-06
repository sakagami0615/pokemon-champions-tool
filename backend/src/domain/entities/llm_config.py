from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderSettings:
    model: str | None
    base_url: str | None
    api_key: str | None = None


@dataclass(frozen=True)
class LLMConfig:
    selected_provider: str
    providers: dict[str, ProviderSettings]
