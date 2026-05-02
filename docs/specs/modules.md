# モジュール設計

## バックエンド

クリーンアーキテクチャを採用。ソースコードは `src/` 配下に、データは `data/` 配下に分離する。

```
backend/
├── src/          # ソースコード
│   ├── main.py                        # FastAPI エントリーポイント
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── party.py               # パーティエンティティ
│   │   │   └── pokemon.py             # ポケモンエンティティ
│   │   └── repositories/
│   │       ├── image_recognizer.py    # 画像認識リポジトリインターフェース
│   │       ├── party_repository.py    # パーティリポジトリインターフェース
│   │       └── usage_repository.py    # 使用率データリポジトリインターフェース
│   ├── application/
│   │   ├── state/
│   │   │   └── scraping_state.py      # スクレイピング実行状態（インメモリ）
│   │   └── use_cases/
│   │       ├── predict_use_case.py    # 選出予想ユースケース
│   │       └── recognition_use_case.py # 画像認識ユースケース
│   ├── infrastructure/
│   │   ├── external/
│   │   │   ├── image_recognition.py   # OpenCV テンプレートマッチング実装
│   │   │   └── scraper.py             # GameWith スクレイピング実装
│   │   └── persistence/
│   │       ├── json_party_repository.py  # パーティ JSON 永続化実装
│   │       └── json_usage_repository.py  # 使用率データ JSON 永続化実装
│   └── presentation/
│       └── routers/
│           ├── data.py                # データ取得・ステータス・日付選択エンドポイント
│           ├── party.py               # 自分パーティ CRUD
│           ├── prediction.py          # 選出予想エンドポイント
│           └── recognition.py         # 画像認識エンドポイント
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
│       ├── party.ts             # パーティエンティティ型定義
│       ├── pokemon.ts           # ポケモンエンティティ型定義
│       └── prediction.ts        # 選出予想エンティティ型定義
├── infrastructure/
│   └── api/
│       ├── dataApi.ts           # データ管理 API クライアント
│       ├── partyApi.ts          # パーティ API クライアント
│       ├── predictionApi.ts     # 選出予想 API クライアント
│       └── recognitionApi.ts    # 画像認識 API クライアント
├── application/
│   └── hooks/
│       ├── useDataManagement.ts # データ管理状態・操作
│       ├── useParty.ts          # パーティ CRUD 操作
│       ├── usePokemonData.ts    # ポケモンデータ取得
│       ├── usePredict.ts        # 選出予想実行
│       └── useRecognition.ts    # 画像認識実行
├── presentation/
│   ├── components/
│   │   ├── DataCard.tsx         # データ管理：日付カード（1件分）
│   │   ├── DataCardList.tsx     # データ管理：日付カード一覧（スクロール可）
│   │   ├── DarkModeToggle.tsx   # ダークモード切り替えボタン
│   │   ├── Header.tsx           # ヘッダー（ナビゲーション込み）
│   │   ├── PartyInput.tsx       # 相手パーティ入力（6枠）
│   │   ├── PatternCard.tsx      # 選出パターン1枚分のカード
│   │   ├── PokemonCard.tsx      # ポケモン1体の型情報カード
│   │   ├── PokemonSlot.tsx      # 1枠：スプライト＋名前選択
│   │   └── PredictionResult.tsx # 選出予想パターン一覧表示
│   ├── pages/
│   │   ├── DataPage.tsx         # データ管理画面
│   │   ├── PartyPage.tsx        # 自分パーティ登録画面
│   │   └── PredictionPage.tsx   # 選出予想メイン画面
│   └── hooks/
│       └── useDarkMode.ts       # ダークモード状態管理
├── App.tsx
├── main.tsx
├── index.css
└── vite-env.d.ts
```

### レイヤー定義

| レイヤー | 役割 | 依存 |
|---|---|---|
| `domain/entities/` | ビジネスエンティティの型定義 | なし |
| `infrastructure/api/` | バックエンド API との HTTP 通信 | domain |
| `application/hooks/` | ビジネスロジックを持つカスタムフック | domain, infrastructure |
| `presentation/` | React コンポーネント・ページ・UI フック | domain, infrastructure, application |

### ファイル管理方針

- `.gitignore` はリポジトリ最上位の `.gitignore` で一元管理する
- `.dockerignore` は Docker ビルドコンテキストが `./frontend` であるため `frontend/.dockerignore` に配置する（ルートへの移動は不可）
- `public/` フォルダは使用しない（デフォルトの `vite.svg` は不要なため削除済み）
