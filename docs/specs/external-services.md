# 外部サービス利用方針

## GameWith スクレイピング

- 禁止事項（GameWith 利用規約）に抵触しない範囲で利用
- 手動トリガーのみ（定期自動取得なし）でサーバー負荷を最小化
- リクエスト間に適切なインターバルを設ける

## LLM プロバイダー（LiteLLM 経由）

LiteLLM を介して複数の LLM プロバイダーに対応する。使用するプロバイダーとモデルは設定画面から選択できる。

### 対応プロバイダー

| プロバイダー | LiteLLM モデル名 | APIキー |
|---|---|---|
| Anthropic | `anthropic/claude-sonnet-4-6` | 設定画面から入力 |
| OpenAI | `openai/gpt-4o` | 設定画面から入力 |
| Google | `gemini/gemini-2.0-flash` | 設定画面から入力 |
| Ollama（ローカル） | `ollama/<model>` | 不要（ローカル接続） |

### APIキー管理

APIキーはアプリの設定ページ（モデル設定セクション）から入力する。入力されたキーは `data/llm_config.json` に保存される。

### Ollama（ローカル LLM）

Ollama はホスト PC 上で起動し、Docker コンテナ内のバックエンドから `host.docker.internal:11434` で接続する。`docker-compose.yml` の `extra_hosts` 設定が必要。

### AI 呼び出しの抽象化

AI 呼び出しは `ILLMClient` インターフェースに集約し、`LiteLLMClient` が実装する。プロバイダーの切り替えはインターフェースを通じて行い、ユースケース層はプロバイダーの詳細を知らない。

## 将来拡張（対象外）

- 対戦中の再推定
- パーティ分析機能
- ダメージ計算
- RAG 連携
- 外部デプロイ
