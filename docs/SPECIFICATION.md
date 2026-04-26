# ポケモンチャンピオンズ対戦支援ツール 仕様書

## 概要

ポケモンチャンピオンズの対戦前に、相手パーティをもとにAIが選出予想を生成し、各ポケモンの型情報（技・持ち物・特性・性格・個体値・能力ポイント）を表示する個人利用ツール。

## 機能仕様

### 1. 相手パーティ入力

**デフォルト表示**: 6枠の手動入力フォーム

各枠の動作:
- テキスト入力 or 候補リストからポケモンを選択
- 選択完了後、枠内にスプライト画像＋ポケモン名を表示

**画像アップロードボタン**:
- 撮影した選出画面の写真をアップロード
- OpenCV テンプレートマッチングで6体を認識
- 認識結果を6枠に自動入力
- 間違いがあればそのまま各枠を手動で修正可能

### 2. 選出予想

入力:
- 相手パーティ6体
- 自分パーティ（登録済み）
- 使用率データ（最新の取得済みデータ）

処理:
- 上記をコンテキストとして Claude API に渡す
- 3パターンの選出予想を返させる

出力:
- 3パターンを常時全展開表示
- 各パターン内に3体のポケモンカードを横並び
- 各ポケモンカードに以下を表示:
  - スプライト画像 ＋ ポケモン名
  - わざ（上位3件 ＋ 使用率%）
  - 持ち物（上位2件 ＋ 使用率%）
  - 特性（上位2件 ＋ 使用率%）
  - 性格（上位2件 ＋ 使用率%）
  - 個体値（H/A/B/C/D/S）※GameWithに記載がある場合はその値、ない場合は競技標準値（全31、特殊アタッカーのAは0）を表示
  - 能力ポイント（上位2件のEV配分 ＋ 使用率%）

### 3. 自分パーティ登録

- 複数パーティを登録・保存できる
- パーティ名をつけて切り替え可能
- 各パーティにポケモン6体を登録（スプライト＋名前表示）
- 選出予想画面を開いたとき、前回使用したパーティを自動で読み込む

### 4. 使用率データ取得

- 手動トリガーボタンで実行
- GameWith の以下ページをスクレイピング:
  - 内定ポケモン一覧ページ → スプライト画像 ＋ ポケモン基本情報
  - 使用率ランキング TOP30 ページ → 各ポケモンの詳細バトルデータ
- 取得データは `data/usage_rates/YYYY-MM-DD.json` として日付管理
- TOP30 外のポケモンは内定ポケモン一覧データで補間、使用率は「ランキング外」とする

## UI / UX 設計

### レスポンシブレイアウト

**横長（PC・横向きスマホ）**:
- ポケモンカード内: 画像 左 ／ 型情報 右

**縦長（スマホ縦向き）**:
- ポケモンカード内: 画像 上 ／ 型情報 下

### ダークモード

- ヘッダーに手動トグルボタンを配置
- Tailwind CSS の `dark:` クラスで実装
- 設定は localStorage に保存（リロード後も維持）

### UX 原則

- 対戦前の短時間で使えること
- 認識ミスはすぐ修正できること（入力枠を直接編集）
- 出力は直感的に判断できる形（全パターン常時展開）

## アーキテクチャ

### 構成

```
[React フロントエンド (Vite)]
        ↕ HTTP / REST API
[FastAPI バックエンド (Python)]
        ├── 画像認識 (OpenCV)
        ├── データ取得 (requests + BeautifulSoup)
        ├── 選出予想 (Claude API)
        └── データ永続化 (JSON ファイル)
```

### 技術スタック

| レイヤー | 技術 |
|---|---|
| フロントエンド | React (Vite) + Tailwind CSS |
| バックエンド | Python + FastAPI |
| パッケージ管理 | UV |
| 画像認識 | OpenCV (テンプレートマッチング) |
| スクレイピング | requests + BeautifulSoup |
| AI選出予想 | Claude API (claude-sonnet-4-6) |
| データ保存 | JSON ファイル |

### 起動方法

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

### テスト実行

```bash
# Docker コンテナ内で実行
docker compose run --rm backend pytest
```

### デプロイ

ローカル専用。外部公開なし。

## モジュール設計

### バックエンド

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

### フロントエンド

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

#### レイヤー定義

| レイヤー | 役割 | 依存 |
|---|---|---|
| `domain/entities/` | ビジネスエンティティの型定義 | なし |
| `infrastructure/api/` | バックエンド API との HTTP 通信 | domain |
| `presentation/` | React コンポーネント・ページ・UI フック | domain, infrastructure |

将来的に UseCases を導入する場合は `application/useCases/` を追加する。

#### ファイル管理方針

- `.gitignore` はリポジトリ最上位の `.gitignore` で一元管理する
- `.dockerignore` は Docker ビルドコンテキストが `./frontend` であるため `frontend/.dockerignore` に配置する（ルートへの移動は不可）
- `public/` フォルダは使用しない（デフォルトの `vite.svg` は不要なため削除済み）

## データ設計

### 使用率データ（usage_rates/YYYY-MM-DD.json）

```json
{
  "collected_at": "2026-04-26T12:00:00",
  "season": 1,
  "regulation": "レギュレーションA",
  "source_updated_at": "2026-04-25",
  "pokemon": [
    {
      "name": "リザードン",
      "moves": [{"name": "かえんほうしゃ", "rate": 78}],
      "items": [{"name": "いのちのたま", "rate": 61}],
      "abilities": [{"name": "もうか", "rate": 82}],
      "natures": [{"name": "ひかえめ", "rate": 67}],
      "teammates": [],
      "evs": [
        {"spread": {"H": 0, "A": 0, "B": 0, "C": 252, "D": 4, "S": 252}, "rate": 52}
      ],
      "ivs": {"H": 31, "A": 0, "B": 31, "C": 31, "D": 31, "S": 31}
    }
  ]
}
```

`ivs` は GameWith に記載がある場合は実値、ない場合は `null`（表示時に競技標準値で補完）。

### 内定ポケモン一覧（pokemon_list.json）

```json
{
  "collected_at": "2026-04-26T12:00:00",
  "pokemon": [
    {
      "pokedex_id": 6,
      "name": "リザードン",
      "types": ["ほのお", "ひこう"],
      "base_stats": {
        "hp": 78, "attack": 84, "defense": 78,
        "sp_attack": 109, "sp_defense": 85, "speed": 100
      },
      "height_m": 1.7,
      "weight_kg": 90.5,
      "low_kick_power": 100,
      "abilities": ["もうか", "サンパワー"],
      "weaknesses": ["いわ", "みず", "でんき"],
      "resistances": ["くさ", "かくとう", "むし", "はがね", "ほのお", "フェアリー"],
      "sprite_path": "sprites/006.png",
      "mega_evolution": null
    }
  ]
}
```

`mega_evolution` はメガシンカしないポケモンは `null`。

### パーティデータ（parties.json）

```json
{
  "parties": [
    {
      "id": "party-1",
      "name": "メインパーティ",
      "pokemon": ["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "ゲンガー", "カビゴン"]
    }
  ]
}
```

## 外部サービス利用方針

### GameWith スクレイピング

- 禁止事項（GameWith 利用規約）に抵触しない範囲で利用
- 手動トリガーのみ（定期自動取得なし）でサーバー負荷を最小化
- リクエスト間に適切なインターバルを設ける

### Claude API

- 初期実装は外部 API（claude-sonnet-4-6）を使用し精度を検証する
- プロンプトキャッシュを活用してコスト削減
- ポケモン一覧・使用率データをキャッシュ対象とする
- 精度・コストの問題が生じた場合はローカル LLM（Ollama + Llama / Gemma 等）への切り替えを検討する
- 切り替えに備え、AI 呼び出しは `ai_predictor.py` に集約してインターフェースを統一しておく

## 将来拡張（対象外）

- 対戦中の再推定
- パーティ分析機能
- ダメージ計算
- RAG 連携
- 外部デプロイ
