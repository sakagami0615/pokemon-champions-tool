# アーキテクチャ

## 構成

```
[React フロントエンド (Vite)]
        ↕ HTTP / REST API
[FastAPI バックエンド (Python)]
        ├── 画像認識 (OpenCV)
        ├── データ取得 (requests + BeautifulSoup)
        ├── 選出予想 (Claude API)
        └── データ永続化 (JSON ファイル)
```

## 技術スタック

| レイヤー | 技術 |
|---|---|
| フロントエンド | React (Vite) + Tailwind CSS |
| バックエンド | Python + FastAPI |
| パッケージ管理 | UV |
| 画像認識 | OpenCV (テンプレートマッチング) |
| スクレイピング | requests + BeautifulSoup |
| AI選出予想 | LiteLLM (Anthropic / OpenAI / Google / Ollama) |
| データ保存 | JSON ファイル |

## 起動方法

```bash
# Docker Compose で起動（推奨）
docker compose up

# バックエンド単体（ローカル / UV使用）
cd backend
uv run uvicorn main:app --app-dir src --reload

# フロントエンド単体（ローカル）
cd frontend
npm run dev
```

## テスト実行

```bash
# Docker コンテナ内で実行
docker compose run --rm backend pytest
```

## デプロイ

ローカル専用。外部公開なし。
