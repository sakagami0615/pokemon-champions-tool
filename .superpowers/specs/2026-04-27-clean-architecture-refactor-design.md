# クリーンアーキテクチャ整合リファクタリング 設計書

## 目的

バックエンド・フロントエンド双方のフォルダ構成をクリーンアーキテクチャに統一し、レイヤー間の責務を明確化する。

## スコープ

- バックエンド: フォルダ構成の再編 + リポジトリ抽象化の追加
- フロントエンド: `application/hooks/` 層の追加 + ファイル分割

## バックエンド設計

### ディレクトリ構成

```
backend/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── party.py          # Party, PartiesData, PredictionResult, PredictionPattern
│   │   │   └── pokemon.py        # UsageData, UsageEntry, RatedItem
│   │   └── repositories/
│   │       ├── party_repository.py   # IPartyRepository (ABC)
│   │       └── usage_repository.py   # IUsageRepository (ABC)
│   ├── application/
│   │   └── use_cases/
│   │       ├── predict_use_case.py       # AIPredictor ロジック
│   │       └── recognition_use_case.py  # 画像認識ロジック
│   ├── infrastructure/
│   │   ├── persistence/
│   │   │   └── json_party_repository.py  # IPartyRepository の JSON 実装
│   │   └── external/
│   │       ├── scraper.py                # 使用率データのスクレイピング
│   │       └── image_recognition.py      # 画像認識 (外部 API/モデル)
│   ├── presentation/
│   │   └── routers/
│   │       ├── party.py
│   │       ├── prediction.py
│   │       ├── recognition.py
│   │       └── data.py
│   └── main.py
└── tests/
    ├── conftest.py
    ├── test_predict_use_case.py
    ├── test_recognition_use_case.py
    ├── test_json_party_repository.py
    ├── test_json_usage_repository.py
    ├── test_scraper.py
    ├── test_image_recognition.py
    ├── test_models.py
    └── test_routers.py
```

### レイヤー間の依存方向

```
presentation → application → domain
                           ↑
             infrastructure → domain
```

- `domain` は他のレイヤーに依存しない
- `application/use_cases` は `domain/entities` と `domain/repositories` のみ参照
- `infrastructure` は `domain/repositories` の抽象を実装する
- `presentation/routers` は `application/use_cases` を呼び出す

### リポジトリ抽象化

**IPartyRepository** — `parties.json` の読み書きを抽象化:

```python
class IPartyRepository(ABC):
    @abstractmethod
    def get_all(self) -> PartiesData: ...

    @abstractmethod
    def save(self, data: PartiesData) -> None: ...
```

**IUsageRepository** — 使用率データ（`pokemon_list.json`, `usage_rates/*.json`）の読み取りを抽象化:

```python
class IUsageRepository(ABC):
    @abstractmethod
    def get_usage_data(self) -> UsageData: ...

    @abstractmethod
    def get_pokemon_names(self) -> list[str]: ...
```

現在の `data_manager.py` は `infrastructure/persistence/` 配下の2ファイルに分割する:
- `json_party_repository.py` — `IPartyRepository` の実装（parties.json の読み書き）
- `json_usage_repository.py` — `IUsageRepository` の実装（pokemon_list.json / usage_rates/ の読み書き）

`predict_use_case.py` は `IUsageRepository` のインターフェースのみを参照し、ファイルI/Oの詳細を知らない。

### テスト移動

`backend/src/tests/` → `backend/tests/` に移動。`pyproject.toml` の `testpaths` を更新する。

## フロントエンド設計

### ディレクトリ構成

```
frontend/src/
├── domain/
│   └── entities/
│       ├── party.ts         # Party, PartiesData
│       ├── prediction.ts    # PredictionPattern, PredictionResult
│       └── pokemon.ts       # RatedItem, EvSpread, UsageEntry
├── application/
│   └── hooks/
│       ├── useParty.ts       # パーティ CRUD・最終使用パーティ管理
│       ├── usePredict.ts     # 選出予想の状態・APIコール・バリデーション
│       └── usePokemonData.ts # ポケモン名一覧の取得
├── infrastructure/
│   └── api/
│       ├── partyApi.ts       # /api/party 系エンドポイント
│       ├── predictionApi.ts  # /api/predict
│       ├── recognitionApi.ts # /api/recognize
│       └── dataApi.ts        # /api/data 系エンドポイント
└── presentation/
    ├── components/           # 変更なし
    ├── hooks/
    │   └── useDarkMode.ts    # プレゼンテーション固有フックのみ残す
    └── pages/
        ├── PredictionPage.tsx  # UIのみ (usePredict, useParty を呼ぶ)
        └── PartyPage.tsx       # UIのみ (useParty を呼ぶ)
```

### レイヤー間の依存方向

```
presentation → application → infrastructure → domain
(pages/components) (hooks)    (api/)        (entities)
```

### application/hooks の責務

各フックはページコンポーネントに対して状態と操作を提供する。

**usePredict**
- 状態: `opponentParty`, `result`, `loading`, `error`
- 操作: `handlePredict(opponentParty, myParty)` — バリデーション + `predictionApi.predict()` 呼び出し

**useParty**
- 状態: `parties`, `selectedPartyId`, `myParty`
- 操作: `selectParty`, `createParty`, `updateParty`, `deleteParty`

**usePokemonData**
- 状態: `pokemonNames`
- 初回マウント時に `dataApi.getPokemonNames()` を呼んでキャッシュ

### 削除対象

- `frontend/src/App.css` — 未使用のため削除

## 変更しないもの

- `docker-compose.yml`
- `frontend/src/App.tsx`
- `frontend/src/main.tsx`
- `frontend/src/presentation/components/` 配下の全コンポーネント
- `frontend/src/presentation/hooks/useDarkMode.ts`
- バックエンドの `main.py` のルーター登録部分（import パスのみ更新）

## 完了基準

- 既存のすべてのテストがDocker内で通過する
- `docker compose run --rm backend pytest` がエラーなく完了する
- フロントエンドのビルドが通る (`npm run build`)
- 各レイヤーが上位レイヤーに依存していない（逆方向のimportがない）
