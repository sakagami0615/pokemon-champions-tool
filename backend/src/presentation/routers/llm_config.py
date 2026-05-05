import dataclasses
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from domain.entities.llm_config import LLMConfig, ProviderSettings
from infrastructure.persistence.json_llm_config_repository import JsonLLMConfigRepository

router = APIRouter(prefix="/api", tags=["llm_config"])
_llm_config_repo = JsonLLMConfigRepository()

_MASKED = "***"


class ProviderSettingsRequest(BaseModel):
    model: str | None
    base_url: str | None
    api_key: str | None = None


class LLMConfigRequest(BaseModel):
    selected_provider: str
    providers: dict[str, ProviderSettingsRequest]


def _mask_config(config: LLMConfig) -> dict:
    d = dataclasses.asdict(config)
    for provider_data in d["providers"].values():
        if provider_data.get("api_key") is not None:
            provider_data["api_key"] = _MASKED
    return d


@router.get("/llm-config")
def get_llm_config():
    config = _llm_config_repo.get_config()
    return _mask_config(config)


@router.put("/llm-config")
def put_llm_config(req: LLMConfigRequest):
    existing = _llm_config_repo.get_config()
    providers = {}
    for k, v in req.providers.items():
        if v.api_key == _MASKED:
            existing_settings = existing.providers.get(k)
            api_key = existing_settings.api_key if existing_settings else None
        else:
            api_key = v.api_key
        providers[k] = ProviderSettings(model=v.model, base_url=v.base_url, api_key=api_key)
    config = LLMConfig(selected_provider=req.selected_provider, providers=providers)
    _llm_config_repo.save_config(config)
    return _mask_config(config)


@router.get("/ollama-models")
def get_ollama_models(base_url: str):
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        models = [m["name"] for m in data.get("models", [])]
        return {"models": models}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Ollamaへの接続に失敗しました: {str(e)}",
        )
