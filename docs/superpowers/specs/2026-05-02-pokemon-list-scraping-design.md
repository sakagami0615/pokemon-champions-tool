# 内定ポケモン一覧スクレイピング 設計書

## 概要

GameWith の内定ポケモン一覧ページをスクレイピングし、通常ポケモンとメガシンカポケモンを分けて `pokemon_list.json` に保存する機能を実装する。

---

## データ構造

### エンティティ変更（`domain/entities/pokemon.py`）

- `MegaEvolution` クラスを削除（メガポケモンはトップレベルリストへ移行）
- `PokemonInfo` の型相性フィールドを4区分に刷新し `mega_evolution` を削除
- `PokemonList` に `mega_pokemons` フィールドを追加

```python
class PokemonInfo(BaseModel):
    pokedex_id: int
    name: str
    types: list[str]
    base_stats: BaseStats
    height_m: float
    weight_kg: float
    low_kick_power: int
    abilities: list[str]
    no_effect_types: list[str]       # x0 (無効)
    quarter_damage_types: list[str]  # x0.25
    half_damage_types: list[str]     # x0.5
    double_damage_types: list[str]   # x2 (弱点)
    sprite_path: str

class PokemonList(BaseModel):
    collected_at: str
    pokemons: list[PokemonInfo]
    mega_pokemons: list[PokemonInfo]
```

通常ポケモンとメガシンカは同じ `PokemonInfo` 構造を共用する。

### `pokemon_list.json` のJSON構造

```json
{
  "collected_at": "2026-04-26T12:00:00",
  "pokemons": [
    {
      "pokedex_id": 3,
      "name": "フシギバナ",
      "types": ["くさ", "どく"],
      "base_stats": {
        "hp": 80, "attack": 82, "defense": 83,
        "sp_attack": 100, "sp_defense": 100, "speed": 80
      },
      "height_m": 2.0,
      "weight_kg": 100.0,
      "low_kick_power": 100,
      "abilities": ["しんりょく", "ようりょくそ"],
      "no_effect_types": [],
      "quarter_damage_types": ["くさ"],
      "half_damage_types": ["みず", "でんき", "かくとう", "フェアリー"],
      "double_damage_types": ["ほのお", "こおり", "ひこう", "エスパー"],
      "sprite_path": "sprites/003.png"
    }
  ],
  "mega_pokemons": [
    {
      "pokedex_id": 3,
      "name": "メガフシギバナ",
      "types": ["くさ", "どく"],
      "base_stats": {
        "hp": 80, "attack": 100, "defense": 123,
        "sp_attack": 122, "sp_defense": 120, "speed": 80
      },
      "height_m": 2.4,
      "weight_kg": 155.5,
      "low_kick_power": 120,
      "abilities": ["あついしぼう"],
      "no_effect_types": [],
      "quarter_damage_types": [],
      "half_damage_types": ["みず", "でんき", "くさ", "かくとう", "フェアリー"],
      "double_damage_types": ["ほのお", "こおり", "ひこう", "エスパー"],
      "sprite_path": "sprites/003-mega.png"
    }
  ]
}
```

### `usage_rates` / `parties.json` のキー変更

配列要素は複数形に統一する。

| ファイル | 変更前 | 変更後 |
|----------|--------|--------|
| `usage_rates/YYYY-MM-DD.json` | `pokemon` | `pokemons` |
| `parties.json` | `pokemon` | `pokemons` |

---

## ファイル構成

### 新規ファイル

```
backend/src/infrastructure/external/
├── constants.py                    # URL・ヘッダー・インターバルの定数を一元管理
├── base_scraper.py                 # BaseScraper: _fetch / _download_sprite の共通ロジック
└── pokemon_list_scraper.py         # PokemonListScraper: 内定ポケモン一覧スクレイピング

backend/src/domain/repositories/
└── pokemon_list_repository.py      # PokemonListRepository インターフェース

backend/src/application/use_cases/
└── scrape_pokemon_list_use_case.py # スクレイピング実行ユースケース

backend/src/infrastructure/persistence/
└── json_pokemon_list_repository.py # JSON読み書き実装

backend/tests/
├── test_pokemon_list_scraper.py    # スクレイパーのユニットテスト
├── test_json_pokemon_list_repository.py # リポジトリのユニットテスト
└── test_scrape_pokemon_list_use_case.py # ユースケースのユニットテスト
```

### 変更ファイル

| ファイル | 変更内容 |
|----------|----------|
| `infrastructure/external/scraper.py` | 定数参照を `constants.py` に移行 |
| `domain/entities/pokemon.py` | `PokemonInfo` / `PokemonList` を更新、`MegaEvolution` を削除 |
| `infrastructure/persistence/json_usage_repository.py` | `pokemon` → `pokemons` キー対応 |
| `domain/repositories/usage_repository.py` | 型定義の更新（必要に応じて） |
| `docs/specs/data.md` | JSON構造のドキュメント更新 |

### `constants.py` の内容

```python
POKEMON_LIST_URL = "https://gamewith.jp/pokemon-champions/546414"
USAGE_RANKING_URL = "https://gamewith.jp/pokemon-champions/555373"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PokemonChampionsTool/1.0)"}
REQUEST_INTERVAL: float = 1.0  # 秒
```

---

## スクレイピングロジック

### スクレイピング対象

| ページ | URL |
|--------|-----|
| 内定ポケモン一覧 | `https://gamewith.jp/pokemon-champions/546414` |
| 個別ポケモン詳細 | `https://gamewith.jp/pokemon-champions/{id}` |

### 一覧ページの取得フロー

1. `ol.w-pokemon-list` 内の全 `li.w-pokemon-list-element` を取得
2. 各 `li` から以下を抽出：
   - 図鑑番号：`span._no` のテキスト（`"No.0003"` → `3`）
   - ポケモン名：`a._name` のテキスト
   - 詳細ページURL：`a._name` の `href`
3. 図鑑番号でグルーピング：
   - 各No.の最初のエントリ → `pokemons`
   - 2件目以降のエントリ → `mega_pokemons`

### 詳細ページの取得内容

| 項目 | セレクター |
|------|-----------|
| 種族値 | `table._pokechamp_pkm_status` 内の `div._num` |
| タイプ | `div._type > img[alt]` |
| 身長・体重 | `td._height_weight`（`"2.0m / 100.0kg"` 形式） |
| けたぐり威力 | `td._sex`（`"けたぐり・くさむすびの威力：100"` 形式） |
| 特性 | `table._pokechamp_ability > tbody > tr` |
| タイプ相性 | `ol._pokechamp_pkm_typechart > li[data-attr]` |
| スプライト | 詳細ページの画像をダウンロード保存 |

### タイプ相性の取得

```python
ATTR_TO_FIELD = {
    "x0":    "no_effect_types",
    "x0.25": "quarter_damage_types",
    "x0.5":  "half_damage_types",
    "x2":    "double_damage_types",
}
for li in soup.select("ol._pokechamp_pkm_typechart li"):
    attr = li.get("data-attr")
    field = ATTR_TO_FIELD.get(attr)
    if field:
        types = [img["alt"] for img in li.select("img[alt]")]
        type_chart[field] = types
```

### リクエストインターバル

全HTTPリクエスト（ページ取得・画像ダウンロード）に `REQUEST_INTERVAL = 1.0` 秒の待機を挿入し、サーバー負荷を抑える。

---

## テスト戦略

### `test_pokemon_list_scraper.py`（ユニットテスト）

実HTTPリクエストは行わず、HTMLフィクスチャを使ってパースロジックを検証する。

- 通常ポケモンとメガシンカが図鑑番号で正しく分類されること
- 種族値・タイプ・特性・体重・タイプ相性4区分が正しくパースされること
- 同じ図鑑番号が複数ある場合にメガシンカとして扱われること

### `test_json_pokemon_list_repository.py`（ユニットテスト）

一時ディレクトリを使ってJSONの読み書きを検証する。

- `pokemons` / `mega_pokemons` が正しくシリアライズ・デシリアライズされること

### `test_scrape_pokemon_list_use_case.py`（ユニットテスト）

スクレイパーとリポジトリをモックしてユースケースの制御フローを検証する。

- スクレイピング結果がリポジトリに保存されること
- エラー時にステータスが適切に更新されること

---

## アーキテクチャレイヤー整理

```
presentation/
  └── （既存の data.py ルーターからユースケースを呼び出す）

application/
  └── scrape_pokemon_list_use_case.py
        └── PokemonListScraper（infrastructure/external）を呼び出す
        └── PokemonListRepository（domain）経由で保存

domain/
  └── entities/pokemon.py       （PokemonInfo / PokemonList）
  └── repositories/pokemon_list_repository.py （インターフェース）

infrastructure/
  ├── external/
  │   ├── constants.py
  │   ├── base_scraper.py
  │   └── pokemon_list_scraper.py
  └── persistence/
      └── json_pokemon_list_repository.py
```
