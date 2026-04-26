# pokemon-champions-tool

`pokemon-champions-tool` は、ポケモンチャンピオンズ向けの対戦補助ツールです。  
相手パーティ画像の認識、パーティ管理、使用率データを踏まえた選出予想を Web UI で行えます。

## 主な機能

- 画像認識: 相手パーティ画像（PNG/JPEG）から最大6体を推定
- パーティ管理: 自分のパーティを登録・編集・削除し、最終使用パーティを保持
- データ取得: GameWith から内定ポケモン一覧と使用率情報をスクレイピングして保存
- 選出予想: 使用率データ + 相手/自分のパーティ情報を使って AI が3パターンの選出を予想

## 技術スタック

- Frontend: React + TypeScript + Vite + Tailwind CSS
- Backend: FastAPI + Pydantic
- Image Recognition: OpenCV（テンプレートマッチング）
- AI: Anthropic API（`ANTHROPIC_API_KEY` を利用）
- Container: Docker / Docker Compose

## ディレクトリ構成

- `frontend/`: フロントエンド実装
- `backend/`: API、スクレイパー、画像認識、データ保存ロジック
- `backend/data/`: 取得データやスプライト画像の保存先（実行時に生成）

## セットアップ（Docker Compose）

1. `.env` を作成し、Anthropic APIキーを設定

```bash
cp .env.example .env
# .env の ANTHROPIC_API_KEY を実値に更新
```

2. コンテナ起動

```bash
docker compose up --build
```

3. アクセス

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Health Check: `GET http://localhost:8000/api/health`

## 主要 API

- `POST /api/recognize`: 相手パーティ画像からポケモン名を推定
- `POST /api/predict`: 選出予想（相手6体 + 自分6体）
- `GET/POST /api/party`: パーティ一覧取得・新規作成
- `PUT /api/party/{party_id}`: パーティ更新
- `DELETE /api/party/{party_id}`: パーティ削除
- `POST /api/party/last-used/{party_id}`: 最終使用パーティ設定
- `POST /api/data/fetch`: データ取得ジョブ開始（バックグラウンド）
- `GET /api/data/status`: データ有無の確認
- `GET /api/data/pokemon/names`: ポケモン名一覧（オートコンプリート用）

## テスト

バックエンドのテストを Docker コンテナ内で実行:

```bash
docker compose run --rm backend pytest
```

## 補足

- スクレイピングは対象サイトの HTML 構造に依存するため、必要に応じて `backend/services/scraper.py` のセレクタ調整が必要です。
- 現状、使用率データの `season` / `regulation` は固定値（`0` / `""`）で保存されます。
