# LiteLLM マルチプロバイダー対応 設計書

## 概要

選出予想機能で使用するLLMを、Anthropic SDKに直接依存する現状の実装からLiteLLMを介した抽象化に置き換える。
ユーザーはAnthropic・OpenAI・Google・Ollamaの中から使用するプロバイダーとモデルを設定ページから選択できる。

## 要件

- LiteLLMを使用して複数のLLMプロバイダーに対応する
- 対応プロバイダー: Anthropic、OpenAI、Google、Ollama（ローカルLLM）
- プロバイダーとモデルはUIから設定できる
- 設定はバックエンドのJSONファイルで永続化する
- APIキーは引き続き環境変数で管理する（UIには露出しない）
- OllamaはDockerコンテナからホストPCのOllamaに接続する

## アーキテクチャ

クリーンアーキテクチャの既存パターンに従い、以下の層に変更・追加を行う。

```
domain/
  entities/
    llm_config.py          # 新規: LLM設定エンティティ
  repositories/
    llm_client.py          # 新規: ILLMClient 抽象インターフェース
    llm_config_repository.py  # 新規: ILLMConfigRepository 抽象インターフェース

infrastructure/
  external/
    litellm_client.py      # 新規: ILLMClient の LiteLLM 実装
  persistence/
    json_llm_config_repository.py  # 新規: ILLMConfigRepository の JSON実装

application/
  use_cases/
    predict_use_case.py    # 変更: anthropic SDK を ILLMClient に差し替え

presentation/
  routers/
    prediction.py          # 変更: LiteLLMClient を組み立てて注入
    llm_config.py          # 新規: 設定取得・保存・Ollamaモデル一覧エンドポイント
```

## ドメインエンティティ

### LLMConfig

```python
@dataclass(frozen=True)
class ProviderSettings:
    model: str | None  # None = 未設定
    base_url: str | None  # Ollamaのみ使用

@dataclass(frozen=True)
class LLMConfig:
    selected_provider: str  # "anthropic" | "openai" | "google" | "ollama"
    providers: dict[str, ProviderSettings]
```

## ドメインインターフェース

### ILLMClient

```python
class ILLMClient(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str: ...
```

### ILLMConfigRepository

```python
class ILLMConfigRepository(ABC):
    @abstractmethod
    def get_config(self) -> LLMConfig: ...

    @abstractmethod
    def save_config(self, config: LLMConfig) -> None: ...
```

## インフラ実装

### LiteLLMClient

- `ILLMClient` を実装する
- コンストラクタで `LLMConfig` を受け取り、`generate()` 呼び出し時に `litellm.completion()` を呼び出す
- プロバイダーごとにLiteLLM形式のモデル名に変換する
  - anthropic: `anthropic/claude-sonnet-4-6`
  - openai: `openai/gpt-4o`
  - google: `gemini/gemini-2.0-flash`
  - ollama: `ollama/llama3.2`（`base_url` を `api_base` に渡す）
- 各プロバイダーのAPIキーは環境変数からLiteLLMが自動読み込みする
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY`
  - `GEMINI_API_KEY`

### JsonLLMConfigRepository

- `data/llm_config.json` に設定を保存・読み込みする
- ファイルが存在しない場合は以下のデフォルト設定を返す

```json
{
  "selected_provider": "anthropic",
  "providers": {
    "anthropic": { "model": "claude-sonnet-4-6", "base_url": null },
    "openai":    { "model": "gpt-4o",            "base_url": null },
    "google":    { "model": "gemini-2.0-flash",  "base_url": null },
    "ollama":    { "model": null,                 "base_url": "http://host.docker.internal:11434" }
  }
}
```

## APIエンドポイント

### 既存エンドポイントの変更

**POST /api/predict**
- `ANTHROPIC_API_KEY` の直接参照を削除
- `JsonLLMConfigRepository` から設定を読み込み `LiteLLMClient` を生成して `PredictUseCase` に注入する
- 選択中プロバイダーのモデルが `null` の場合は400エラーを返す

### 新規エンドポイント

**GET /api/llm-config**
- 現在の `LLMConfig` をJSONで返す

**PUT /api/llm-config**
- リクエストボディで `LLMConfig` を受け取り保存する

**GET /api/ollama-models**
- クエリパラメータ `base_url` で指定されたOllamaエンドポイントに問い合わせる
- `{base_url}/api/tags` を叩いてインストール済みモデル名のリストを返す
- 接続失敗時は適切なエラーメッセージを返す

## フロントエンド設計

### タブ名変更

「データ管理」→「設定」

### 設定ページのレイアウト

```
[設定]
  ├─ [データ管理] セクション  ← 既存のUIをそのまま移動
  └─ [モデル設定] セクション  ← 新規追加
```

### モデル設定セクションのUI

各プロバイダーをカード形式で縦に並べ、ラジオボタンで選択する。

```
[モデル設定]

● Anthropic
  モデル: [claude-sonnet-4-6 ▼]

○ OpenAI
  モデル: [gpt-4o ▼]

○ Google
  モデル: [gemini-2.0-flash ▼]

○ Ollama
  エンドポイント: [http://host.docker.internal:11434]
  モデル:         [未取得 ▼]  [一覧を取得]

[保存]
```

### プルダウンの選択肢（フロントエンド固定定義）

| プロバイダー | モデル候補 |
|---|---|
| Anthropic | claude-opus-4-7、claude-sonnet-4-6、claude-haiku-4-5 |
| OpenAI | gpt-4o、gpt-4o-mini、o1、o1-mini |
| Google | gemini-2.5-pro、gemini-2.0-flash、gemini-1.5-flash |
| Ollama | 「一覧を取得」ボタンでエンドポイントから動的取得 |

### Ollamaのインタラクション

1. ユーザーがエンドポイントURLを入力する
2. 「一覧を取得」ボタンを押す
3. `GET /api/ollama-models?base_url=...` を呼び出す
4. 取得成功時: モデルのプルダウンに結果を表示する
5. 取得失敗時: エラーメッセージを表示する（Ollamaが起動していない等）

### バリデーション

- 選択中のプロバイダーのモデルが未設定（null）の場合、「保存」ボタンを無効化する
- Ollamaでモデルが「未取得」のまま選択した場合も同様に無効化する

## Docker設定の変更

`docker-compose.yml` のbackendサービスに以下を追加し、コンテナからホストのOllamaに接続できるようにする。

```yaml
services:
  backend:
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

## 依存パッケージの追加

`backend/pyproject.toml` に以下を追加する。

```toml
dependencies = [
    ...
    "litellm>=1.0.0",
]
```

`anthropic>=0.40.0` はLiteLLMの依存として引き続き使用されるため、削除不要。

## テスト方針

- `ILLMClient` をモックに差し替えて `PredictUseCase` の単体テストを行う
- `JsonLLMConfigRepository` の単体テスト（保存・読み込み・デフォルト値）
- `LiteLLMClient` の統合テスト（LiteLLMのモック機能を使用）
- `GET /api/llm-config`・`PUT /api/llm-config`・`GET /api/ollama-models` のAPIテスト
