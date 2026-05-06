# LiteLLM マルチプロバイダー対応 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Anthropic SDK 直接依存を LiteLLM 経由に置き換え、Anthropic・OpenAI・Google・Ollama の 4 プロバイダーを UI から切り替えられるようにする。

**Architecture:** クリーンアーキテクチャの既存パターンに従い、`ILLMClient` 抽象インターフェースを domain 層に追加し LiteLLM 実装を infrastructure 層に置く。設定は `data/llm_config.json` に永続化し、フロントエンドの「データ管理」タブを「設定」タブに拡張してモデル選択 UI を追加する。

**Tech Stack:** Python / FastAPI / LiteLLM / dataclasses (backend)、TypeScript / React / Vite / Tailwind CSS (frontend)

---

## ファイルマップ

| 操作 | パス | 役割 |
|---|---|---|
| 新規 | `backend/src/domain/entities/llm_config.py` | LLMConfig, ProviderSettings エンティティ |
| 新規 | `backend/src/domain/repositories/llm_client.py` | ILLMClient ABC |
| 新規 | `backend/src/domain/repositories/llm_config_repository.py` | ILLMConfigRepository ABC |
| 新規 | `backend/src/infrastructure/external/litellm_client.py` | LiteLLMClient 実装 |
| 新規 | `backend/src/infrastructure/persistence/json_llm_config_repository.py` | JSON 永続化 |
| 新規 | `backend/src/presentation/routers/llm_config.py` | LLM 設定エンドポイント |
| 新規 | `backend/tests/test_llm_config.py` | エンティティテスト |
| 新規 | `backend/tests/test_json_llm_config_repository.py` | リポジトリテスト |
| 新規 | `backend/tests/test_litellm_client.py` | LiteLLMClient テスト |
| 変更 | `backend/pyproject.toml` | litellm 依存追加 |
| 変更 | `backend/src/application/use_cases/predict_use_case.py` | ILLMClient に差し替え |
| 変更 | `backend/src/presentation/routers/prediction.py` | LiteLLMClient 注入 |
| 変更 | `backend/src/main.py` | llm_config router 登録 |
| 変更 | `backend/tests/test_predict_use_case.py` | ILLMClient モックに更新 |
| 変更 | `backend/tests/test_routers.py` | prediction + llm-config テスト更新 |
| 変更 | `docker-compose.yml` | extra_hosts 追加 |
| 新規 | `frontend/src/domain/entities/llm_config.ts` | LLMConfig 型定義 |
| 新規 | `frontend/src/infrastructure/api/llmConfigApi.ts` | API クライアント |
| 新規 | `frontend/src/application/hooks/useLLMConfig.ts` | 設定管理フック |
| 新規 | `frontend/src/presentation/components/ModelSettings.tsx` | モデル設定 UI |
| 新規 | `frontend/src/presentation/pages/SettingsPage.tsx` | 設定ページ |
| 変更 | `frontend/src/App.tsx` | `'data'` → `'settings'` |
| 変更 | `frontend/src/presentation/components/Header.tsx` | ラベル変更 |
| 削除 | `frontend/src/presentation/pages/DataPage.tsx` | SettingsPage に統合 |

---

## Task 1: litellm 依存追加

**Files:**
- Modify: `backend/pyproject.toml`

- [ ] **Step 1: pyproject.toml に litellm を追加**

`backend/pyproject.toml` の `dependencies` を以下に置き換える:

```toml
[project]
name = "pokemon-champions-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi==0.115.0",
    "uvicorn[standard]==0.30.0",
    "python-multipart==0.0.9",
    "pydantic>=2.0",
    "opencv-python-headless==4.10.0.84",
    "numpy==1.26.4",
    "requests==2.32.3",
    "beautifulsoup4==4.12.3",
    "anthropic>=0.40.0",
    "litellm>=1.0.0",
]

[dependency-groups]
dev = [
    "pytest==8.3.2",
    "pytest-asyncio==0.23.8",
    "httpx==0.27.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
pythonpath = ["src"]
```

- [ ] **Step 2: Docker イメージをリビルド**

```bash
docker compose build backend
```

Expected: `Successfully built ...` でエラーなし

- [ ] **Step 3: litellm がインポートできることを確認**

```bash
docker compose run --rm backend python -c "import litellm; print(litellm.__version__)"
```

Expected: バージョン番号（例: `1.x.x`）が表示される

- [ ] **Step 4: Commit**

```bash
git add backend/pyproject.toml
git commit -m "feat: add litellm dependency"
```

---

## Task 2: LLMConfig エンティティ

**Files:**
- Create: `backend/src/domain/entities/llm_config.py`
- Create: `backend/tests/test_llm_config.py`

- [ ] **Step 1: テストを書く**

`backend/tests/test_llm_config.py` を新規作成:

```python
import pytest
from domain.entities.llm_config import LLMConfig, ProviderSettings


def test_provider_settings_is_immutable():
    s = ProviderSettings(model="claude-sonnet-4-6", base_url=None)
    with pytest.raises((AttributeError, TypeError)):
        s.model = "other"  # type: ignore[misc]


def test_provider_settings_allows_none_model():
    s = ProviderSettings(model=None, base_url="http://host.docker.internal:11434")
    assert s.model is None
    assert s.base_url == "http://host.docker.internal:11434"


def test_llm_config_holds_selected_provider():
    config = LLMConfig(
        selected_provider="anthropic",
        providers={
            "anthropic": ProviderSettings(model="claude-sonnet-4-6", base_url=None),
        },
    )
    assert config.selected_provider == "anthropic"
    assert config.providers["anthropic"].model == "claude-sonnet-4-6"


def test_llm_config_is_immutable():
    config = LLMConfig(
        selected_provider="anthropic",
        providers={"anthropic": ProviderSettings(model="claude-sonnet-4-6", base_url=None)},
    )
    with pytest.raises((AttributeError, TypeError)):
        config.selected_provider = "openai"  # type: ignore[misc]
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
docker compose run --rm backend pytest tests/test_llm_config.py -v
```

Expected: `ImportError` または `ModuleNotFoundError`

- [ ] **Step 3: エンティティを実装**

`backend/src/domain/entities/llm_config.py` を新規作成:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderSettings:
    model: str | None
    base_url: str | None


@dataclass(frozen=True)
class LLMConfig:
    selected_provider: str
    providers: dict[str, ProviderSettings]
```

- [ ] **Step 4: テストが通ることを確認**

```bash
docker compose run --rm backend pytest tests/test_llm_config.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add backend/src/domain/entities/llm_config.py backend/tests/test_llm_config.py
git commit -m "feat: add LLMConfig entity"
```

---

## Task 3: ILLMClient / ILLMConfigRepository インターフェース

**Files:**
- Create: `backend/src/domain/repositories/llm_client.py`
- Create: `backend/src/domain/repositories/llm_config_repository.py`

ABC そのものはテスト不要。実装クラスのテストで間接的に検証する。

- [ ] **Step 1: ILLMClient を作成**

`backend/src/domain/repositories/llm_client.py` を新規作成:

```python
from abc import ABC, abstractmethod


class ILLMClient(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str: ...
```

- [ ] **Step 2: ILLMConfigRepository を作成**

`backend/src/domain/repositories/llm_config_repository.py` を新規作成:

```python
from abc import ABC, abstractmethod
from domain.entities.llm_config import LLMConfig


class ILLMConfigRepository(ABC):
    @abstractmethod
    def get_config(self) -> LLMConfig: ...

    @abstractmethod
    def save_config(self, config: LLMConfig) -> None: ...
```

- [ ] **Step 3: import が通ることを確認**

```bash
docker compose run --rm backend python -c "
from domain.repositories.llm_client import ILLMClient
from domain.repositories.llm_config_repository import ILLMConfigRepository
print('OK')
"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add backend/src/domain/repositories/llm_client.py \
        backend/src/domain/repositories/llm_config_repository.py
git commit -m "feat: add ILLMClient and ILLMConfigRepository interfaces"
```

---

## Task 4: JsonLLMConfigRepository

**Files:**
- Create: `backend/src/infrastructure/persistence/json_llm_config_repository.py`
- Create: `backend/tests/test_json_llm_config_repository.py`

- [ ] **Step 1: テストを書く**

`backend/tests/test_json_llm_config_repository.py` を新規作成:

```python
import pytest
from infrastructure.persistence.json_llm_config_repository import JsonLLMConfigRepository
from domain.entities.llm_config import LLMConfig, ProviderSettings


def test_get_config_returns_default_when_no_file(tmp_path):
    repo = JsonLLMConfigRepository(data_dir=tmp_path)
    config = repo.get_config()
    assert config.selected_provider == "anthropic"
    assert config.providers["anthropic"].model == "claude-sonnet-4-6"
    assert config.providers["openai"].model == "gpt-4o"
    assert config.providers["google"].model == "gemini-2.0-flash"
    assert config.providers["ollama"].model is None
    assert config.providers["ollama"].base_url == "http://host.docker.internal:11434"


def test_save_and_get_config_roundtrip(tmp_path):
    repo = JsonLLMConfigRepository(data_dir=tmp_path)
    config = LLMConfig(
        selected_provider="openai",
        providers={
            "anthropic": ProviderSettings(model="claude-sonnet-4-6", base_url=None),
            "openai": ProviderSettings(model="gpt-4o-mini", base_url=None),
            "google": ProviderSettings(model="gemini-2.0-flash", base_url=None),
            "ollama": ProviderSettings(model=None, base_url="http://host.docker.internal:11434"),
        },
    )
    repo.save_config(config)
    loaded = repo.get_config()
    assert loaded.selected_provider == "openai"
    assert loaded.providers["openai"].model == "gpt-4o-mini"
    assert loaded.providers["ollama"].base_url == "http://host.docker.internal:11434"


def test_save_creates_json_file(tmp_path):
    repo = JsonLLMConfigRepository(data_dir=tmp_path)
    config = LLMConfig(
        selected_provider="anthropic",
        providers={"anthropic": ProviderSettings(model="claude-sonnet-4-6", base_url=None)},
    )
    repo.save_config(config)
    assert (tmp_path / "llm_config.json").exists()


def test_get_config_creates_data_dir_if_missing(tmp_path):
    nested = tmp_path / "nested" / "dir"
    repo = JsonLLMConfigRepository(data_dir=nested)
    config = repo.get_config()
    assert config.selected_provider == "anthropic"
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
docker compose run --rm backend pytest tests/test_json_llm_config_repository.py -v
```

Expected: `ImportError` または `ModuleNotFoundError`

- [ ] **Step 3: JsonLLMConfigRepository を実装**

`backend/src/infrastructure/persistence/json_llm_config_repository.py` を新規作成:

```python
import json
import dataclasses
from pathlib import Path
from domain.entities.llm_config import LLMConfig, ProviderSettings
from domain.repositories.llm_config_repository import ILLMConfigRepository

_DEFAULT_CONFIG: dict = {
    "selected_provider": "anthropic",
    "providers": {
        "anthropic": {"model": "claude-sonnet-4-6", "base_url": None},
        "openai": {"model": "gpt-4o", "base_url": None},
        "google": {"model": "gemini-2.0-flash", "base_url": None},
        "ollama": {"model": None, "base_url": "http://host.docker.internal:11434"},
    },
}


class JsonLLMConfigRepository(ILLMConfigRepository):
    def __init__(
        self,
        data_dir: Path | str = Path(__file__).parent.parent.parent.parent / "data",
    ) -> None:
        self._path = Path(data_dir) / "llm_config.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def get_config(self) -> LLMConfig:
        if not self._path.exists():
            return self._from_dict(_DEFAULT_CONFIG)
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return self._from_dict(data)

    def save_config(self, config: LLMConfig) -> None:
        self._path.write_text(
            json.dumps(dataclasses.asdict(config), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _from_dict(self, data: dict) -> LLMConfig:
        providers = {
            k: ProviderSettings(model=v["model"], base_url=v["base_url"])
            for k, v in data["providers"].items()
        }
        return LLMConfig(selected_provider=data["selected_provider"], providers=providers)
```

- [ ] **Step 4: テストが通ることを確認**

```bash
docker compose run --rm backend pytest tests/test_json_llm_config_repository.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add backend/src/infrastructure/persistence/json_llm_config_repository.py \
        backend/tests/test_json_llm_config_repository.py
git commit -m "feat: add JsonLLMConfigRepository"
```

---

## Task 5: LiteLLMClient

**Files:**
- Create: `backend/src/infrastructure/external/litellm_client.py`
- Create: `backend/tests/test_litellm_client.py`

- [ ] **Step 1: テストを書く**

`backend/tests/test_litellm_client.py` を新規作成:

```python
from unittest.mock import patch, MagicMock
from infrastructure.external.litellm_client import LiteLLMClient
from domain.entities.llm_config import LLMConfig, ProviderSettings


def _make_config(provider: str, model: str, base_url: str | None = None) -> LLMConfig:
    return LLMConfig(
        selected_provider=provider,
        providers={provider: ProviderSettings(model=model, base_url=base_url)},
    )


def _mock_response(text: str) -> MagicMock:
    return MagicMock(choices=[MagicMock(message=MagicMock(content=text))])


@patch("infrastructure.external.litellm_client.litellm.completion")
def test_generate_anthropic_uses_correct_prefix(mock_completion):
    mock_completion.return_value = _mock_response("result")
    client = LiteLLMClient(_make_config("anthropic", "claude-sonnet-4-6"))
    result = client.generate("system", "user")
    assert result == "result"
    assert mock_completion.call_args[1]["model"] == "anthropic/claude-sonnet-4-6"


@patch("infrastructure.external.litellm_client.litellm.completion")
def test_generate_openai_uses_correct_prefix(mock_completion):
    mock_completion.return_value = _mock_response("result")
    client = LiteLLMClient(_make_config("openai", "gpt-4o"))
    client.generate("system", "user")
    assert mock_completion.call_args[1]["model"] == "openai/gpt-4o"


@patch("infrastructure.external.litellm_client.litellm.completion")
def test_generate_google_uses_gemini_prefix(mock_completion):
    mock_completion.return_value = _mock_response("result")
    client = LiteLLMClient(_make_config("google", "gemini-2.0-flash"))
    client.generate("system", "user")
    assert mock_completion.call_args[1]["model"] == "gemini/gemini-2.0-flash"


@patch("infrastructure.external.litellm_client.litellm.completion")
def test_generate_ollama_passes_api_base(mock_completion):
    mock_completion.return_value = _mock_response("result")
    client = LiteLLMClient(
        _make_config("ollama", "llama3.2", "http://host.docker.internal:11434")
    )
    client.generate("system", "user")
    kwargs = mock_completion.call_args[1]
    assert kwargs["model"] == "ollama/llama3.2"
    assert kwargs["api_base"] == "http://host.docker.internal:11434"


@patch("infrastructure.external.litellm_client.litellm.completion")
def test_generate_passes_system_and_user_messages(mock_completion):
    mock_completion.return_value = _mock_response("response")
    client = LiteLLMClient(_make_config("anthropic", "claude-sonnet-4-6"))
    client.generate("my system", "my user prompt")
    messages = mock_completion.call_args[1]["messages"]
    assert messages[0] == {"role": "system", "content": "my system"}
    assert messages[1] == {"role": "user", "content": "my user prompt"}
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
docker compose run --rm backend pytest tests/test_litellm_client.py -v
```

Expected: `ImportError` または `ModuleNotFoundError`

- [ ] **Step 3: LiteLLMClient を実装**

`backend/src/infrastructure/external/litellm_client.py` を新規作成:

```python
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
        response = litellm.completion(**kwargs)
        return response.choices[0].message.content
```

- [ ] **Step 4: テストが通ることを確認**

```bash
docker compose run --rm backend pytest tests/test_litellm_client.py -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add backend/src/infrastructure/external/litellm_client.py \
        backend/tests/test_litellm_client.py
git commit -m "feat: add LiteLLMClient"
```

---

## Task 6: PredictUseCase リファクタリング

**Files:**
- Modify: `backend/src/application/use_cases/predict_use_case.py`
- Modify: `backend/tests/test_predict_use_case.py`

- [ ] **Step 1: テストを ILLMClient モックに更新**

`backend/tests/test_predict_use_case.py` を全文置き換え:

```python
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
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
docker compose run --rm backend pytest tests/test_predict_use_case.py -v
```

Expected: `TypeError` (コンストラクタが `api_key` を要求する)

- [ ] **Step 3: PredictUseCase を ILLMClient を使う形に書き換え**

`backend/src/application/use_cases/predict_use_case.py` を全文置き換え:

```python
import re
from domain.entities.pokemon import UsageData
from domain.entities.party import PredictionResult, PredictionPattern
from domain.repositories.llm_client import ILLMClient

SYSTEM_PROMPT = """あなたはポケモンチャンピオンズの対戦分析AIです。
与えられた情報をもとに、相手プレイヤーが選出しそうなポケモン3体のパターンを3つ予想してください。

回答は必ず以下の形式で出力してください：
パターン1: ポケモン名A, ポケモン名B, ポケモン名C
パターン2: ポケモン名D, ポケモン名E, ポケモン名F
パターン3: ポケモン名G, ポケモン名H, ポケモン名I

可能性が高い順に並べてください。確率の数値は不要です。"""


class PredictUseCase:
    def __init__(self, llm_client: ILLMClient) -> None:
        self._client = llm_client

    def predict(
        self,
        opponent_party: list[str],
        my_party: list[str],
        usage_data: UsageData,
    ) -> PredictionResult:
        prompt = self._build_prompt(opponent_party, my_party, usage_data)
        text = self._client.generate(SYSTEM_PROMPT, prompt)
        return self._parse_response(text)

    def _build_prompt(
        self,
        opponent_party: list[str],
        my_party: list[str],
        usage_data: UsageData,
    ) -> str:
        usage_summary = []
        for entry in usage_data.pokemons:
            if entry.name in opponent_party:
                top_moves = ", ".join(f"{m.name}({m.rate}%)" for m in entry.moves[:3])
                top_items = ", ".join(f"{i.name}({i.rate}%)" for i in entry.items[:2])
                usage_summary.append(f"- {entry.name}: わざ[{top_moves}] 持ち物[{top_items}]")

        usage_text = "\n".join(usage_summary) if usage_summary else "使用率データなし"

        return f"""【相手パーティ（6体）】
{", ".join(opponent_party)}

【自分のパーティ（6体）】
{", ".join(my_party)}

【相手パーティの使用率データ】
{usage_text}

シングルバトル3体選出です。相手が選出しそうな3体のパターンを3つ予想してください。"""

    def _parse_response(self, text: str) -> PredictionResult:
        patterns = []
        for line in text.strip().splitlines():
            m = re.match(r"パターン\d+[:：]\s*(.+)", line)
            if m:
                names = [n.strip() for n in m.group(1).split(",")][:3]
                while len(names) < 3:
                    names.append("")
                patterns.append(PredictionPattern(pokemons=names))
        while len(patterns) < 3:
            patterns.append(PredictionPattern(pokemons=["", "", ""]))
        return PredictionResult(patterns=patterns[:3])
```

- [ ] **Step 4: テストが通ることを確認**

```bash
docker compose run --rm backend pytest tests/test_predict_use_case.py -v
```

Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add backend/src/application/use_cases/predict_use_case.py \
        backend/tests/test_predict_use_case.py
git commit -m "refactor: replace anthropic SDK with ILLMClient in PredictUseCase"
```

---

## Task 7: prediction.py ルーター変更

**Files:**
- Modify: `backend/src/presentation/routers/prediction.py`
- Modify: `backend/tests/test_routers.py`

- [ ] **Step 1: test_routers.py の prediction テストを更新**

`backend/tests/test_routers.py` 内の `test_predict_uses_selected_date` と `test_predict_uses_latest_when_no_date_selected` を探して以下の 3 テストで置き換える（`test_predict_returns_400_when_model_not_set` を末尾に追加）:

```python
@pytest.mark.asyncio
async def test_predict_uses_selected_date(monkeypatch):
    import application.state.scraping_state as state
    monkeypatch.setattr(state, "selected_date", "2026-04-27")

    with patch("presentation.routers.prediction._usage_repo") as mock_repo:
        mock_repo.get_usage_data_by_date.return_value = MagicMock()
        with patch("presentation.routers.prediction._llm_config_repo") as mock_cfg:
            mock_cfg.get_config.return_value = MagicMock(
                selected_provider="anthropic",
                providers={"anthropic": MagicMock(model="claude-sonnet-4-6")},
            )
            with patch("presentation.routers.prediction.LiteLLMClient"):
                with patch("presentation.routers.prediction.PredictUseCase") as mock_uc:
                    mock_uc.return_value.predict.return_value = {"patterns": []}
                    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                        await client.post("/api/predict", json={
                            "opponent_party": ["リザードン"] * 6,
                            "my_party": ["カメックス"] * 6,
                        })

    mock_repo.get_usage_data_by_date.assert_called_once_with("2026-04-27")
    mock_repo.get_usage_data.assert_not_called()


@pytest.mark.asyncio
async def test_predict_uses_latest_when_no_date_selected():
    import application.state.scraping_state as state
    state.selected_date = None

    with patch("presentation.routers.prediction._usage_repo") as mock_repo:
        mock_repo.get_usage_data.return_value = MagicMock()
        with patch("presentation.routers.prediction._llm_config_repo") as mock_cfg:
            mock_cfg.get_config.return_value = MagicMock(
                selected_provider="anthropic",
                providers={"anthropic": MagicMock(model="claude-sonnet-4-6")},
            )
            with patch("presentation.routers.prediction.LiteLLMClient"):
                with patch("presentation.routers.prediction.PredictUseCase") as mock_uc:
                    mock_uc.return_value.predict.return_value = {"patterns": []}
                    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                        resp = await client.post("/api/predict", json={
                            "opponent_party": ["リザードン"] * 6,
                            "my_party": ["カメックス"] * 6,
                        })

    mock_repo.get_usage_data.assert_called_once()
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_predict_returns_400_when_model_not_set():
    import application.state.scraping_state as state
    state.selected_date = None

    with patch("presentation.routers.prediction._usage_repo") as mock_repo:
        mock_repo.get_usage_data.return_value = MagicMock()
        with patch("presentation.routers.prediction._llm_config_repo") as mock_cfg:
            mock_cfg.get_config.return_value = MagicMock(
                selected_provider="ollama",
                providers={"ollama": MagicMock(model=None)},
            )
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post("/api/predict", json={
                    "opponent_party": ["リザードン"] * 6,
                    "my_party": ["カメックス"] * 6,
                })

    assert resp.status_code == 400
    assert "モデルが設定されていません" in resp.json()["detail"]
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
docker compose run --rm backend pytest tests/test_routers.py::test_predict_uses_selected_date tests/test_routers.py::test_predict_uses_latest_when_no_date_selected tests/test_routers.py::test_predict_returns_400_when_model_not_set -v
```

Expected: prediction のテストが失敗（ルーターがまだ旧実装）

- [ ] **Step 3: prediction.py ルーターを全文置き換え**

`backend/src/presentation/routers/prediction.py` を全文置き換え:

```python
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
    provider_settings = config.providers.get(config.selected_provider)
    if provider_settings is None or provider_settings.model is None:
        raise HTTPException(
            status_code=400,
            detail="LLMのモデルが設定されていません。設定ページでモデルを選択してください。",
        )

    llm_client = LiteLLMClient(config)
    use_case = PredictUseCase(llm_client=llm_client)
    return use_case.predict(
        opponent_party=req.opponent_party,
        my_party=req.my_party,
        usage_data=usage_data,
    )
```

- [ ] **Step 4: テストが通ることを確認**

```bash
docker compose run --rm backend pytest tests/test_routers.py -v
```

Expected: 全テスト pass

- [ ] **Step 5: Commit**

```bash
git add backend/src/presentation/routers/prediction.py \
        backend/tests/test_routers.py
git commit -m "refactor: wire LiteLLMClient into prediction router"
```

---

## Task 8: llm_config ルーター新規作成と登録

**Files:**
- Create: `backend/src/presentation/routers/llm_config.py`
- Modify: `backend/src/main.py`
- Modify: `backend/tests/test_routers.py`

- [ ] **Step 1: llm-config エンドポイントのテストを test_routers.py 末尾に追記**

```python
@pytest.mark.asyncio
async def test_get_llm_config_returns_default():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/llm-config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["selected_provider"] == "anthropic"
    assert "providers" in data
    assert "anthropic" in data["providers"]
    assert "openai" in data["providers"]
    assert "google" in data["providers"]
    assert "ollama" in data["providers"]


@pytest.mark.asyncio
async def test_put_llm_config_saves_and_returns():
    payload = {
        "selected_provider": "openai",
        "providers": {
            "anthropic": {"model": "claude-sonnet-4-6", "base_url": None},
            "openai": {"model": "gpt-4o", "base_url": None},
            "google": {"model": "gemini-2.0-flash", "base_url": None},
            "ollama": {"model": None, "base_url": "http://host.docker.internal:11434"},
        },
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.put("/api/llm-config", json=payload)
    assert resp.status_code == 200
    assert resp.json()["selected_provider"] == "openai"


@pytest.mark.asyncio
async def test_get_ollama_models_returns_model_names():
    with patch("presentation.routers.llm_config.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "models": [{"name": "llama3.2"}, {"name": "mistral"}]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/ollama-models?base_url=http://localhost:11434")
    assert resp.status_code == 200
    assert resp.json()["models"] == ["llama3.2", "mistral"]


@pytest.mark.asyncio
async def test_get_ollama_models_returns_503_on_connection_error():
    with patch(
        "presentation.routers.llm_config.requests.get",
        side_effect=Exception("connection refused"),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/ollama-models?base_url=http://localhost:11434")
    assert resp.status_code == 503
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
docker compose run --rm backend pytest tests/test_routers.py::test_get_llm_config_returns_default -v
```

Expected: `404 Not Found`（エンドポイント未登録）

- [ ] **Step 3: llm_config.py ルーターを作成**

`backend/src/presentation/routers/llm_config.py` を新規作成:

```python
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
```

- [ ] **Step 4: main.py に llm_config router を登録**

`backend/src/main.py` を全文置き換え:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from presentation.routers import data, recognition, prediction, party, llm_config

app = FastAPI(title="Pokemon Champions Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(recognition.router)
app.include_router(prediction.router)
app.include_router(party.router)
app.include_router(llm_config.router)

sprites_dir = Path(__file__).parent.parent / "data" / "sprites"
sprites_dir.mkdir(parents=True, exist_ok=True)
app.mount("/sprites", StaticFiles(directory=str(sprites_dir)), name="sprites")


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: テストが通ることを確認**

```bash
docker compose run --rm backend pytest tests/test_routers.py -v
```

Expected: 全テスト pass（新規 4 件含む）

- [ ] **Step 6: 全バックエンドテストが通ることを確認**

```bash
docker compose run --rm backend pytest -v
```

Expected: 全テスト pass

- [ ] **Step 7: Commit**

```bash
git add backend/src/presentation/routers/llm_config.py \
        backend/src/main.py \
        backend/tests/test_routers.py
git commit -m "feat: add llm-config and ollama-models endpoints"
```

---

## Task 9: docker-compose.yml extra_hosts 追加

**Files:**
- Modify: `docker-compose.yml`

- [ ] **Step 1: docker-compose.yml を全文置き換え**

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/src:/app/src
      - ./backend/data:/app/data
      - ./backend/tests:/app/tests
      - ./backend/scripts:/app/scripts
    env_file:
      - path: .env
        required: false
    environment:
      - PYTHONUNBUFFERED=1
      - UV_SYSTEM_PYTHON=1
    extra_hosts:
      - "host.docker.internal:host-gateway"

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/index.html:/app/index.html
    depends_on:
      - backend
```

- [ ] **Step 2: コンテナが正常起動することを確認**

```bash
docker compose up -d backend
docker compose exec backend curl -s http://localhost:8000/api/health
```

Expected: `{"status":"ok"}`

```bash
docker compose down
```

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add extra_hosts for Ollama host access"
```

---

## Task 10: フロントエンド型定義

**Files:**
- Create: `frontend/src/domain/entities/llm_config.ts`

- [ ] **Step 1: llm_config.ts を作成**

`frontend/src/domain/entities/llm_config.ts` を新規作成:

```typescript
export type Provider = 'anthropic' | 'openai' | 'google' | 'ollama'

export interface ProviderSettings {
  model: string | null
  base_url: string | null
}

export interface LLMConfig {
  selected_provider: Provider
  providers: Record<Provider, ProviderSettings>
}

export const PROVIDER_LABELS: Record<Provider, string> = {
  anthropic: 'Anthropic',
  openai: 'OpenAI',
  google: 'Google',
  ollama: 'Ollama',
}

export const PROVIDER_MODELS: Record<Provider, string[]> = {
  anthropic: ['claude-opus-4-7', 'claude-sonnet-4-6', 'claude-haiku-4-5'],
  openai: ['gpt-4o', 'gpt-4o-mini', 'o1', 'o1-mini'],
  google: ['gemini-2.5-pro', 'gemini-2.0-flash', 'gemini-1.5-flash'],
  ollama: [],
}

export const PROVIDERS: Provider[] = ['anthropic', 'openai', 'google', 'ollama']
```

- [ ] **Step 2: TypeScript エラーがないことを確認**

```bash
docker compose run --rm frontend npx tsc --noEmit
```

Expected: エラーなし（または既存エラーのみ）

- [ ] **Step 3: Commit**

```bash
git add frontend/src/domain/entities/llm_config.ts
git commit -m "feat: add LLMConfig type definitions"
```

---

## Task 11: フロントエンド API クライアント

**Files:**
- Create: `frontend/src/infrastructure/api/llmConfigApi.ts`

- [ ] **Step 1: llmConfigApi.ts を作成**

`frontend/src/infrastructure/api/llmConfigApi.ts` を新規作成:

```typescript
import type { LLMConfig } from '../../domain/entities/llm_config'

const BASE = '/api'

export async function getLLMConfig(): Promise<LLMConfig> {
  const res = await fetch(`${BASE}/llm-config`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function saveLLMConfig(config: LLMConfig): Promise<LLMConfig> {
  const res = await fetch(`${BASE}/llm-config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getOllamaModels(baseUrl: string): Promise<string[]> {
  const res = await fetch(
    `${BASE}/ollama-models?base_url=${encodeURIComponent(baseUrl)}`
  )
  if (!res.ok) throw new Error(await res.text())
  const data = await res.json()
  return data.models as string[]
}
```

- [ ] **Step 2: TypeScript エラーがないことを確認**

```bash
docker compose run --rm frontend npx tsc --noEmit
```

Expected: エラーなし

- [ ] **Step 3: Commit**

```bash
git add frontend/src/infrastructure/api/llmConfigApi.ts
git commit -m "feat: add LLM config API client"
```

---

## Task 12: useLLMConfig フック

**Files:**
- Create: `frontend/src/application/hooks/useLLMConfig.ts`

- [ ] **Step 1: useLLMConfig.ts を作成**

`frontend/src/application/hooks/useLLMConfig.ts` を新規作成:

```typescript
import { useState, useEffect, useCallback } from 'react'
import type { LLMConfig, Provider } from '../../domain/entities/llm_config'
import { getLLMConfig, saveLLMConfig, getOllamaModels } from '../../infrastructure/api/llmConfigApi'

export function useLLMConfig() {
  const [config, setConfig] = useState<LLMConfig | null>(null)
  const [ollamaModels, setOllamaModels] = useState<string[]>([])
  const [isSaving, setIsSaving] = useState(false)
  const [isFetchingModels, setIsFetchingModels] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)

  useEffect(() => {
    getLLMConfig()
      .then(setConfig)
      .catch((e: unknown) => setError(String(e)))
  }, [])

  const updateProvider = useCallback(
    (provider: Provider) => {
      if (!config) return
      setConfig({ ...config, selected_provider: provider })
    },
    [config]
  )

  const updateModel = useCallback(
    (provider: Provider, model: string) => {
      if (!config) return
      setConfig({
        ...config,
        providers: {
          ...config.providers,
          [provider]: { ...config.providers[provider], model },
        },
      })
    },
    [config]
  )

  const updateOllamaBaseUrl = useCallback(
    (url: string) => {
      if (!config) return
      setConfig({
        ...config,
        providers: {
          ...config.providers,
          ollama: { ...config.providers.ollama, base_url: url },
        },
      })
    },
    [config]
  )

  const fetchOllamaModels = useCallback(async () => {
    if (!config?.providers.ollama.base_url) return
    setIsFetchingModels(true)
    setError(null)
    try {
      const models = await getOllamaModels(config.providers.ollama.base_url)
      setOllamaModels(models)
    } catch {
      setError('Ollamaへの接続に失敗しました')
    } finally {
      setIsFetchingModels(false)
    }
  }, [config])

  const save = useCallback(async () => {
    if (!config) return
    setIsSaving(true)
    setError(null)
    try {
      await saveLLMConfig(config)
      setSaveMessage('保存しました')
      setTimeout(() => setSaveMessage(null), 3000)
    } catch {
      setError('保存に失敗しました')
    } finally {
      setIsSaving(false)
    }
  }, [config])

  const isSelectedModelValid =
    config !== null &&
    (config.providers[config.selected_provider]?.model ?? null) !== null

  return {
    config,
    ollamaModels,
    isSaving,
    isFetchingModels,
    error,
    saveMessage,
    isSelectedModelValid,
    updateProvider,
    updateModel,
    updateOllamaBaseUrl,
    fetchOllamaModels,
    save,
  }
}
```

- [ ] **Step 2: TypeScript エラーがないことを確認**

```bash
docker compose run --rm frontend npx tsc --noEmit
```

Expected: エラーなし

- [ ] **Step 3: Commit**

```bash
git add frontend/src/application/hooks/useLLMConfig.ts
git commit -m "feat: add useLLMConfig hook"
```

---

## Task 13: App.tsx + Header.tsx リネーム

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/presentation/components/Header.tsx`

- [ ] **Step 1: Header.tsx を全文置き換え**

```typescript
import DarkModeToggle from './DarkModeToggle'

interface Props {
  dark: boolean
  onToggleDark: () => void
  page: 'prediction' | 'party' | 'settings'
  onChangePage: (p: 'prediction' | 'party' | 'settings') => void
}

export default function Header({ dark, onToggleDark, page, onChangePage }: Props) {
  return (
    <header className="border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <span className="font-bold text-lg">Pokemon Champions Tool</span>
        <nav className="flex gap-2">
          <button
            onClick={() => onChangePage('prediction')}
            className={`px-3 py-1 rounded text-sm ${page === 'prediction' ? 'bg-indigo-600 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            選出予想
          </button>
          <button
            onClick={() => onChangePage('party')}
            className={`px-3 py-1 rounded text-sm ${page === 'party' ? 'bg-indigo-600 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            パーティ登録
          </button>
          <button
            onClick={() => onChangePage('settings')}
            className={`px-3 py-1 rounded text-sm ${page === 'settings' ? 'bg-indigo-600 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            設定
          </button>
        </nav>
      </div>
      <DarkModeToggle dark={dark} onToggle={onToggleDark} />
    </header>
  )
}
```

- [ ] **Step 2: App.tsx を全文置き換え**

```typescript
import { useState } from 'react'
import { useDarkMode } from './presentation/hooks/useDarkMode'
import PredictionPage from './presentation/pages/PredictionPage'
import PartyPage from './presentation/pages/PartyPage'
import SettingsPage from './presentation/pages/SettingsPage'
import Header from './presentation/components/Header'

type Page = 'prediction' | 'party' | 'settings'

export default function App() {
  const { dark, toggle } = useDarkMode()
  const [page, setPage] = useState<Page>('prediction')

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <Header dark={dark} onToggleDark={toggle} page={page} onChangePage={setPage} />
      <main className="p-4">
        {page === 'prediction' && <PredictionPage />}
        {page === 'party' && <PartyPage />}
        {page === 'settings' && <SettingsPage />}
      </main>
    </div>
  )
}
```

- [ ] **Step 3: TypeScript エラーを確認（SettingsPage 未作成のためエラーが出る）**

```bash
docker compose run --rm frontend npx tsc --noEmit
```

Expected: `SettingsPage` が見つからないエラーのみ（次タスクで解消）

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.tsx \
        frontend/src/presentation/components/Header.tsx
git commit -m "refactor: rename data page to settings in App and Header"
```

---

## Task 14: ModelSettings.tsx コンポーネント

**Files:**
- Create: `frontend/src/presentation/components/ModelSettings.tsx`

- [ ] **Step 1: ModelSettings.tsx を作成**

`frontend/src/presentation/components/ModelSettings.tsx` を新規作成:

```typescript
import type { LLMConfig, Provider } from '../../domain/entities/llm_config'
import { PROVIDER_LABELS, PROVIDER_MODELS, PROVIDERS } from '../../domain/entities/llm_config'

interface Props {
  config: LLMConfig
  ollamaModels: string[]
  isSaving: boolean
  isFetchingModels: boolean
  error: string | null
  saveMessage: string | null
  isSelectedModelValid: boolean
  onSelectProvider: (p: Provider) => void
  onSelectModel: (p: Provider, model: string) => void
  onUpdateOllamaBaseUrl: (url: string) => void
  onFetchOllamaModels: () => void
  onSave: () => void
}

export default function ModelSettings({
  config,
  ollamaModels,
  isSaving,
  isFetchingModels,
  error,
  saveMessage,
  isSelectedModelValid,
  onSelectProvider,
  onSelectModel,
  onUpdateOllamaBaseUrl,
  onFetchOllamaModels,
  onSave,
}: Props) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">モデル設定</h2>

      <div className="space-y-3">
        {PROVIDERS.map((provider) => {
          const isSelected = config.selected_provider === provider
          const settings = config.providers[provider]
          const models =
            provider === 'ollama' ? ollamaModels : PROVIDER_MODELS[provider]

          return (
            <div
              key={provider}
              className={`border rounded-lg p-4 space-y-3 ${
                isSelected
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                  : 'border-gray-200 dark:border-gray-700'
              }`}
            >
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="provider"
                  value={provider}
                  checked={isSelected}
                  onChange={() => onSelectProvider(provider)}
                  className="accent-indigo-600"
                />
                <span className="font-medium">{PROVIDER_LABELS[provider]}</span>
              </label>

              {provider === 'ollama' ? (
                <div className="space-y-2 ml-6">
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600 dark:text-gray-400 w-28">
                      エンドポイント
                    </label>
                    <input
                      type="text"
                      value={settings.base_url ?? ''}
                      onChange={(e) => onUpdateOllamaBaseUrl(e.target.value)}
                      className="flex-1 px-2 py-1 text-sm border rounded dark:bg-gray-800 dark:border-gray-600"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600 dark:text-gray-400 w-28">
                      モデル
                    </label>
                    <select
                      value={settings.model ?? ''}
                      onChange={(e) => onSelectModel(provider, e.target.value)}
                      disabled={ollamaModels.length === 0}
                      className="flex-1 px-2 py-1 text-sm border rounded dark:bg-gray-800 dark:border-gray-600 disabled:opacity-50"
                    >
                      {ollamaModels.length === 0 ? (
                        <option value="">未取得</option>
                      ) : (
                        ollamaModels.map((m) => (
                          <option key={m} value={m}>
                            {m}
                          </option>
                        ))
                      )}
                    </select>
                    <button
                      onClick={onFetchOllamaModels}
                      disabled={isFetchingModels}
                      className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50"
                    >
                      {isFetchingModels ? '取得中...' : '一覧を取得'}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2 ml-6">
                  <label className="text-sm text-gray-600 dark:text-gray-400 w-28">
                    モデル
                  </label>
                  <select
                    value={settings.model ?? ''}
                    onChange={(e) => onSelectModel(provider, e.target.value)}
                    className="flex-1 px-2 py-1 text-sm border rounded dark:bg-gray-800 dark:border-gray-600"
                  >
                    {models.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}
      {saveMessage && <p className="text-sm text-green-600">{saveMessage}</p>}

      <button
        onClick={onSave}
        disabled={isSaving || !isSelectedModelValid}
        className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
      >
        {isSaving ? '保存中...' : '保存'}
      </button>
    </div>
  )
}
```

- [ ] **Step 2: TypeScript エラーがないことを確認（SettingsPage 未作成エラーはまだある）**

```bash
docker compose run --rm frontend npx tsc --noEmit
```

Expected: `SettingsPage` 関連エラーのみ

- [ ] **Step 3: Commit**

```bash
git add frontend/src/presentation/components/ModelSettings.tsx
git commit -m "feat: add ModelSettings component"
```

---

## Task 15: SettingsPage.tsx と DataPage 削除

**Files:**
- Create: `frontend/src/presentation/pages/SettingsPage.tsx`
- Delete: `frontend/src/presentation/pages/DataPage.tsx`

- [ ] **Step 1: SettingsPage.tsx を作成**

`frontend/src/presentation/pages/SettingsPage.tsx` を新規作成:

```typescript
import { useState } from 'react'
import { useDataManagement } from '../../application/hooks/useDataManagement'
import { useLLMConfig } from '../../application/hooks/useLLMConfig'
import DataCardList from '../components/DataCardList'
import PokemonPanelGrid from '../components/PokemonPanelGrid'
import ModelSettings from '../components/ModelSettings'

type DataTab = 'dates' | 'pokemons'

export default function SettingsPage() {
  const {
    status,
    pokemonList,
    isFetching,
    fetchMessage,
    error: dataError,
    triggerFetch,
    handleSelectDate,
  } = useDataManagement()

  const {
    config,
    ollamaModels,
    isSaving,
    isFetchingModels,
    error: llmError,
    saveMessage,
    isSelectedModelValid,
    updateProvider,
    updateModel,
    updateOllamaBaseUrl,
    fetchOllamaModels,
    save,
  } = useLLMConfig()

  const [dataTab, setDataTab] = useState<DataTab>('dates')

  const onSelectDate = async (date: string) => {
    await handleSelectDate(date)
    setDataTab('pokemons')
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <section className="space-y-4">
        <h1 className="text-xl font-bold">データ管理</h1>

        <div className="space-y-2">
          <div className="flex items-center gap-4">
            <button
              onClick={triggerFetch}
              disabled={isFetching}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
            >
              {isFetching ? '開始中...' : 'データ取得'}
            </button>
            {status?.scraping_in_progress && (
              <p className="text-sm text-yellow-500 animate-pulse">
                スクレイピング実行中...
              </p>
            )}
          </div>
          {fetchMessage && <p className="text-sm text-green-600">{fetchMessage}</p>}
          {dataError && <p className="text-sm text-red-500">{dataError}</p>}
        </div>

        {status === null ? (
          <p className="text-sm text-gray-500">読み込み中...</p>
        ) : (
          <>
            <div className="flex border-b dark:border-gray-700 sm:hidden">
              <button
                onClick={() => setDataTab('dates')}
                className={`flex-1 py-2 text-sm font-medium border-b-2 transition-colors ${
                  dataTab === 'dates'
                    ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                }`}
              >
                日付選択
              </button>
              <button
                onClick={() => setDataTab('pokemons')}
                className={`flex-1 py-2 text-sm font-medium border-b-2 transition-colors ${
                  dataTab === 'pokemons'
                    ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                }`}
              >
                ポケモン一覧
              </button>
            </div>

            <div className="sm:flex sm:gap-4 sm:items-stretch">
              <div
                className={`sm:block sm:w-64 sm:shrink-0 ${dataTab === 'dates' ? 'block' : 'hidden'}`}
              >
                <DataCardList
                  details={status.dates_detail}
                  selectedDate={status.selected_date}
                  onSelect={onSelectDate}
                />
              </div>
              <div className="hidden sm:block w-px bg-gray-300 dark:bg-gray-600 self-stretch" />
              <div
                className={`sm:block sm:flex-1 sm:min-w-0 ${dataTab === 'pokemons' ? 'block' : 'hidden'}`}
              >
                <PokemonPanelGrid pokemonList={pokemonList} />
              </div>
            </div>
          </>
        )}
      </section>

      <hr className="border-gray-200 dark:border-gray-700" />

      <section>
        {config === null ? (
          <p className="text-sm text-gray-500">読み込み中...</p>
        ) : (
          <ModelSettings
            config={config}
            ollamaModels={ollamaModels}
            isSaving={isSaving}
            isFetchingModels={isFetchingModels}
            error={llmError}
            saveMessage={saveMessage}
            isSelectedModelValid={isSelectedModelValid}
            onSelectProvider={updateProvider}
            onSelectModel={updateModel}
            onUpdateOllamaBaseUrl={updateOllamaBaseUrl}
            onFetchOllamaModels={fetchOllamaModels}
            onSave={save}
          />
        )}
      </section>
    </div>
  )
}
```

- [ ] **Step 2: TypeScript エラーがないことを確認**

```bash
docker compose run --rm frontend npx tsc --noEmit
```

Expected: エラーなし

- [ ] **Step 3: DataPage.tsx を削除**

```bash
rm frontend/src/presentation/pages/DataPage.tsx
```

- [ ] **Step 4: 削除後も TypeScript エラーがないことを確認**

```bash
docker compose run --rm frontend npx tsc --noEmit
```

Expected: エラーなし

- [ ] **Step 5: Commit**

```bash
git add frontend/src/presentation/pages/SettingsPage.tsx
git rm frontend/src/presentation/pages/DataPage.tsx
git commit -m "feat: add SettingsPage with data management and model settings sections"
```

---

## 最終確認

- [ ] **全バックエンドテストが通ることを確認**

```bash
docker compose run --rm backend pytest -v --tb=short
```

Expected: 全テスト pass

- [ ] **フロントエンドビルドエラーなし確認**

```bash
docker compose run --rm frontend npx tsc --noEmit
```

Expected: エラーなし

- [ ] **統合動作確認**

```bash
docker compose up -d
```

ブラウザで `http://localhost:5173` を開き以下を確認:

1. ヘッダーのタブが「選出予想」「パーティ登録」「設定」になっている
2. 「設定」タブに「データ管理」セクションと「モデル設定」セクションが表示される
3. モデル設定で Anthropic / OpenAI / Google / Ollama がカード形式で表示される
4. プロバイダー選択のラジオボタンが機能する
5. モデルのプルダウンが選択できる
6. 「保存」ボタンが機能し「保存しました」が表示される
7. 「選出予想」タブの選出予想が引き続き動作する（Anthropic 選択時）

```bash
docker compose down
```
