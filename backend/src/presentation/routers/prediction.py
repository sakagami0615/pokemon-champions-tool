from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from application.use_cases.predict_use_case import PredictUseCase
from infrastructure.persistence.json_usage_repository import JsonUsageRepository
from infrastructure.persistence.json_llm_config_repository import JsonLLMConfigRepository
from infrastructure.external.litellm_client import LiteLLMClient
import application.state.scraping_state as _state

router = APIRouter(prefix="/api", tags=["prediction"])
_usage_repo = JsonUsageRepository()
_llm_config_repo = JsonLLMConfigRepository()


class PredictRequest(BaseModel):
    opponent_party: list[str]
    my_party: list[str]


@router.post("/predict")
def predict(req: PredictRequest):
    if _state.selected_date:
        usage_data = _usage_repo.get_usage_data_by_date(_state.selected_date)
    else:
        usage_data = _usage_repo.get_usage_data()

    if usage_data is None:
        raise HTTPException(
            status_code=400,
            detail="使用率データがありません。先にデータを取得してください。",
        )

    config = _llm_config_repo.get_config()
    provider = config.selected_provider
    provider_settings = config.providers.get(provider)
    if provider_settings is None or provider_settings.model is None:
        raise HTTPException(
            status_code=400,
            detail="LLMのモデルが設定されていません。設定ページでモデルを選択してください。",
        )
    if provider != "ollama" and provider_settings.api_key is None:
        raise HTTPException(
            status_code=400,
            detail="APIキーが設定されていません。設定ページでAPIキーを入力してください。",
        )

    llm_client = LiteLLMClient(config)
    use_case = PredictUseCase(llm_client=llm_client)
    return use_case.predict(
        opponent_party=req.opponent_party,
        my_party=req.my_party,
        usage_data=usage_data,
    )
