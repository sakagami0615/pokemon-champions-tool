from unittest.mock import MagicMock, patch
import pytest
from services.ai_predictor import AIPredictor
from models.pokemon import UsageData, UsageEntry, RatedItem, EvSpread
from models.party import PredictionResult


MOCK_CLAUDE_RESPONSE = """
パターン1: リザードン, カメックス, フシギバナ
パターン2: ピカチュウ, リザードン, イワーク
パターン3: フシギバナ, カメックス, ゲンガー
"""


def _make_usage_data():
    entry = UsageEntry(
        name="リザードン",
        moves=[RatedItem(name="かえんほうしゃ", rate=78)],
        items=[RatedItem(name="いのちのたま", rate=61)],
        abilities=[RatedItem(name="もうか", rate=82)],
        natures=[RatedItem(name="ひかえめ", rate=67)],
        teammates=[],
        evs=[EvSpread(spread={"H": 0, "A": 0, "B": 0, "C": 252, "D": 4, "S": 252}, rate=52)],
    )
    return UsageData(
        collected_at="2026-04-26T12:00:00",
        season=1,
        regulation="レギュレーションA",
        source_updated_at="2026-04-25",
        pokemon=[entry],
    )


@patch("services.ai_predictor.anthropic.Anthropic")
def test_predict_returns_three_patterns(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=MOCK_CLAUDE_RESPONSE)]
    )

    predictor = AIPredictor(api_key="test-key")
    result = predictor.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )

    assert isinstance(result, PredictionResult)
    assert len(result.patterns) == 3
    assert len(result.patterns[0].pokemon) == 3
    assert result.patterns[0].pokemon[0] == "リザードン"


@patch("services.ai_predictor.anthropic.Anthropic")
def test_predict_calls_api_with_both_parties(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=MOCK_CLAUDE_RESPONSE)]
    )

    predictor = AIPredictor(api_key="test-key")
    predictor.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )

    call_kwargs = mock_client.messages.create.call_args
    prompt_text = str(call_kwargs)
    assert "リザードン" in prompt_text
    assert "カビゴン" in prompt_text
