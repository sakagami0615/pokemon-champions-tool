import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.ai_predictor import AIPredictor
from services.data_manager import DataManager

router = APIRouter(prefix="/api", tags=["prediction"])
_manager = DataManager()


class PredictRequest(BaseModel):
    opponent_party: list[str]
    my_party: list[str]


@router.post("/predict")
def predict(req: PredictRequest):
    usage_data = _manager.load_latest_usage_data()
    if usage_data is None:
        raise HTTPException(status_code=400, detail="使用率データがありません。先にデータを取得してください。")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY が設定されていません。")

    predictor = AIPredictor(api_key=api_key)
    result = predictor.predict(
        opponent_party=req.opponent_party,
        my_party=req.my_party,
        usage_data=usage_data,
    )
    return result
