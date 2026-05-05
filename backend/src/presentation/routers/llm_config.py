import dataclasses
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from domain.entities.llm_config import LLMConfig, ProviderSettings
from infrastructure.persistence.json_llm_config_repository import JsonLLMConfigRepository

router = APIRouter(prefix="/api", tags=["llm_config"])
_llm_config_repo = JsonLLMConfigRepository()


class ProviderSettingsRequest(BaseModel):
    model: str | None
    base_url: str | None


class LLMConfigRequest(BaseModel):
    selected_provider: str
    providers: dict[str, ProviderSettingsRequest]


@router.get("/llm-config")
def get_llm_config():
    config = _llm_config_repo.get_config()
    return dataclasses.asdict(config)


@router.put("/llm-config")
def put_llm_config(req: LLMConfigRequest):
    providers = {
        k: ProviderSettings(model=v.model, base_url=v.base_url)
        for k, v in req.providers.items()
    }
    config = LLMConfig(selected_provider=req.selected_provider, providers=providers)
    _llm_config_repo.save_config(config)
    return dataclasses.asdict(config)


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
