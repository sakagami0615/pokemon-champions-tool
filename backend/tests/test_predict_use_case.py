from unittest.mock import MagicMock
from application.use_cases.predict_use_case import PredictUseCase
from domain.entities.pokemon import UsageData, UsageEntry, RatedItem, EvSpread
from domain.entities.party import PredictionResult
from domain.repositories.llm_client import ILLMClient


MOCK_LLM_RESPONSE = """
パターン1: リザードン, カメックス, フシギバナ
パターン2: ピカチュウ, リザードン, イワーク
パターン3: フシギバナ, カメックス, ゲンガー
"""


def _make_usage_data() -> UsageData:
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
        collected_at="2026-04-27T12:00:00",
        season=1,
        regulation="レギュレーションA",
        source_updated_at="2026-04-26",
        pokemons=[entry],
    )


def _make_mock_client(response: str = MOCK_LLM_RESPONSE) -> ILLMClient:
    mock = MagicMock(spec=ILLMClient)
    mock.generate.return_value = response
    return mock


def test_predict_returns_three_patterns():
    use_case = PredictUseCase(llm_client=_make_mock_client())
    result = use_case.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )
    assert isinstance(result, PredictionResult)
    assert len(result.patterns) == 3
    assert len(result.patterns[0].pokemons) == 3
    assert result.patterns[0].pokemons[0] == "リザードン"


def test_predict_calls_generate_with_both_parties():
    mock_client = _make_mock_client()
    use_case = PredictUseCase(llm_client=mock_client)
    use_case.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )
    mock_client.generate.assert_called_once()
    _system, user = mock_client.generate.call_args[0]
    assert "リザードン" in user
    assert "カビゴン" in user
