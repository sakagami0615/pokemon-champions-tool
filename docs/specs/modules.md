# モジュール設計

## バックエンド

クリーンアーキテクチャを採用。ソースコードは `src/` 配下に、データは `data/` 配下に分離する。

```
backend/
├── src/          # ソースコード
│   ├── main.py              # FastAPI エントリーポイント
│   ├── routers/
│   │   ├── recognition.py   # 画像認識エンドポイント
│   │   ├── prediction.py    # 選出予想エンドポイント
│   │   ├── party.py         # 自分パーティ CRUD
│   │   └── data.py          # データ取得トリガー
│   ├── services/
│   │   ├── image_recognition.py  # OpenCV テンプレートマッチング
│   │   ├── scraper.py            # GameWith スクレイピング
│   │   ├── ai_predictor.py       # Claude API 呼び出し
│   │   └── data_manager.py       # JSON ファイル読み書き
│   ├── models/
│   │   ├── pokemon.py       # ポケモン関連モデル
│   │   └── party.py         # パーティ関連モデル
│   └── tests/               # テストコード
│       ├── conftest.py
│       ├── test_ai_predictor.py
│       ├── test_data_manager.py
│       ├── test_image_recognition.py
│       ├── test_models.py
│       ├── test_routers.py
│       └── test_scraper.py
├── data/                    # 永続化データ（バージョン管理外）
│   ├── sprites/             # ポケモンスプライト画像
│   ├── pokemon_list.json    # 内定ポケモン一覧
│   ├── usage_rates/         # 使用率データ（日付ごと）
│   │   └── YYYY-MM-DD.json
│   └── parties.json         # 自分のパーティ登録データ
├── pyproject.toml           # UV パッケージ管理
└── Dockerfile
```

パッケージ管理には UV を使用する。依存関係は `pyproject.toml` で管理し、開発依存（pytest 等）は `[dependency-groups] dev` に分離する。

## フロントエンド

クリーンアーキテクチャを採用。`frontend/src/` をレイヤー別に構成する。

```
frontend/src/
├── domain/
│   └── entities/
│       └── index.ts             # ビジネスエンティティの型定義
├── infrastructure/
│   └── api/
│       └── client.ts            # バックエンド API クライアント（fetch）
├── presentation/
│   ├── components/
│   │   ├── DarkModeToggle.tsx   # ダークモード切り替えボタン
│   │   ├── Header.tsx           # ヘッダー（ナビゲーション込み）
│   │   ├── PartyInput.tsx       # 相手パーティ入力（6枠）
│   │   ├── PatternCard.tsx      # 選出パターン1枚分のカード
│   │   ├── PokemonCard.tsx      # ポケモン1体の型情報カード
│   │   ├── PokemonSlot.tsx      # 1枠：スプライト＋名前選択
│   │   └── PredictionResult.tsx # 選出予想パターン一覧表示
│   ├── pages/
│   │   ├── PredictionPage.tsx   # 選出予想メイン画面
│   │   └── PartyPage.tsx        # 自分パーティ登録画面
│   └── hooks/
│       └── useDarkMode.ts       # ダークモード状態管理
├── App.tsx
├── main.tsx
├── App.css
├── index.css
└── vite-env.d.ts
```

### レイヤー定義

| レイヤー | 役割 | 依存 |
|---|---|---|
| `domain/entities/` | ビジネスエンティティの型定義 | なし |
| `infrastructure/api/` | バックエンド API との HTTP 通信 | domain |
| `presentation/` | React コンポーネント・ページ・UI フック | domain, infrastructure |

将来的に UseCases を導入する場合は `application/useCases/` を追加する。

### ファイル管理方針

- `.gitignore` はリポジトリ最上位の `.gitignore` で一元管理する
- `.dockerignore` は Docker ビルドコンテキストが `./frontend` であるため `frontend/.dockerignore` に配置する（ルートへの移動は不可）
- `public/` フォルダは使用しない（デフォルトの `vite.svg` は不要なため削除済み）
