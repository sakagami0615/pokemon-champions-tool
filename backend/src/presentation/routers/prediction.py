import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from application.use_cases.predict_use_case import PredictUseCase
from infrastructure.persistence.json_usage_repository import JsonUsageRepository
import application.state.scraping_state as _state

router = APIRouter(prefix="/api", tags=["prediction"])
_usage_repo = JsonUsageRepository()


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
        raise HTTPException(status_code=400, detail="使用率データがありません。先にデータを取得してください。")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY が設定されていません。")

    use_case = PredictUseCase(api_key=api_key)
    return use_case.predict(
        opponent_party=req.opponent_party,
        my_party=req.my_party,
        usage_data=usage_data,
    )
