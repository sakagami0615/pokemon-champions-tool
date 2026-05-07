from unittest.mock import MagicMock
from application.use_cases.predict_use_case import PredictUseCase
from domain.entities.pokemon import UsageData, UsageEntry, RatedItem, EvSpread
from domain.entities.party import PredictionResult
from domain.entities.prompt_config import PromptConfig
from domain.repositories.llm_client import ILLMClient
from domain.repositories.prompt_config_repository import IPromptConfigRepository


MOCK_LLM_RESPONSE = """
パターン1: リザードン, カメックス, フシギバナ
パターン2: ピカチュウ, リザードン, イワーク
パターン3: フシギバナ, カメックス, ゲンガー
"""

DEFAULT_PROMPT_CONFIG = PromptConfig(
    system_prompt="テスト用システムプロンプト",
    user_prompt_template="【相手パーティ】{opponent_party}\n【自分のパーティ】{my_party}\n【使用率】{usage_text}",
)


def _make_mock_prompt_repo(config: PromptConfig = DEFAULT_PROMPT_CONFIG) -> IPromptConfigRepository:
    mock = MagicMock(spec=IPromptConfigRepository)
    mock.get_config.return_value = config
    return mock


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
    use_case = PredictUseCase(llm_client=_make_mock_client(), prompt_config_repo=_make_mock_prompt_repo())
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
    use_case = PredictUseCase(llm_client=mock_client, prompt_config_repo=_make_mock_prompt_repo())
    use_case.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )
    mock_client.generate.assert_called_once()
    _system, user = mock_client.generate.call_args[0]
    assert "リザードン" in user
    assert "カビゴン" in user


def test_predict_calls_generate_with_system_prompt():
    mock_client = _make_mock_client()
    custom_config = PromptConfig(
        system_prompt="カスタムシステムプロンプト",
        user_prompt_template="【相手】{opponent_party}\n【自分】{my_party}\n{usage_text}",
    )
    use_case = PredictUseCase(llm_client=mock_client, prompt_config_repo=_make_mock_prompt_repo(custom_config))
    use_case.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )
    _system, _ = mock_client.generate.call_args[0]
    assert _system == "カスタムシステムプロンプト"
