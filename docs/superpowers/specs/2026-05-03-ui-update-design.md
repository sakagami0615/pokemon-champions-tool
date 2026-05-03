# UI更新 設計ドキュメント

## 概要

ui-ux.md の更新内容をフロントエンド・バックエンドに反映する。主な変更は以下の5点。

1. `GET /api/data/pokemon-list` エンドポイントをバックエンドに追加
2. フロントエンドのデータ層にポケモン一覧型・API関数・フック拡張を追加
3. `PokemonSlot` をオートコンプリートからプルダウンに変更
4. `PokemonCard` の個体値表示を種族値表示に変更
5. `DataPage` を左ペイン+中央ペインの2カラムレイアウトに変更
6. データ未取得時のガードを `PredictionPage` / `PartyPage` に追加

---

## セクション1：バックエンド変更

### 変更ファイル
- `backend/src/presentation/routers/data.py`

### 追加エンドポイント

```
GET /api/data/pokemon-list
```

- `JsonPokemonListRepository.get_pokemon_list()` で取得した `pokemon_list.json` の内容をそのまま返す
- レスポンス: `{ pokemons: [...], mega_pokemons: [...] }`
- 各エントリには `name`, `sprite_path`, `base_stats`（hp/attack/defense/sp_attack/sp_defense/speed）を含む
- データが存在しない場合は `{ pokemons: [], mega_pokemons: [] }` を返す

---

## セクション2：フロントエンドのデータ層

### 2-1. ドメインエンティティ追加

**変更ファイル**: `frontend/src/domain/entities/pokemon.ts`

```typescript
export interface BaseStats {
  hp: number
  attack: number
  defense: number
  sp_attack: number
  sp_defense: number
  speed: number
}

export interface PokemonListEntry {
  name: string
  sprite_path: string
  base_stats: BaseStats
}
```

### 2-2. APIクライアント追加

**変更ファイル**: `frontend/src/infrastructure/api/dataApi.ts`

```typescript
export interface PokemonListResponse {
  pokemons: PokemonListEntry[]
  mega_pokemons: PokemonListEntry[]
}

export async function getPokemonList(): Promise<PokemonListResponse>
```

`GET /api/data/pokemon-list` を呼び出し、`PokemonListResponse` を返す。

### 2-3. usePokemonData フック拡張

**変更ファイル**: `frontend/src/application/hooks/usePokemonData.ts`

- 既存の `pokemonNames: string[]` に加えて `pokemonList: PokemonListEntry[]` も返す
- `getPokemonList()` を初期化時に呼び出し、`pokemons` と `mega_pokemons` を結合して保持する
- 名前→種族値のルックアップ用に `getBaseStats(name: string): BaseStats | null` ヘルパーも返す

---

## セクション3：コンポーネント変更

### 3-1. PokemonSlot.tsx（プルダウンに変更）

**変更ファイル**: `frontend/src/presentation/components/PokemonSlot.tsx`

- テキスト入力+オートコンプリートを廃止し `<select>` に置き換える
- 未選択時: `<select>` を表示（先頭に空の選択肢「---」）
- 選択済み時: スプライト画像+ポケモン名を表示。クリックでリセット（`<select>` に戻る）
- `pokemonNames: string[]` のプロップはそのまま使用（変更不要）

### 3-2. PokemonCard.tsx（種族値表示に変更）

**変更ファイル**: `frontend/src/presentation/components/PokemonCard.tsx`

- `ivs` の表示を削除
- props として `pokemonList: PokemonListEntry[]` を受け取り、`name` で種族値を引いて `H/A/B/C/D/S` の形式で表示
- `pokemonList` は `PredictionPage` → `PatternCard` → `PokemonCard` の順で props として渡す
- `PredictionPage` は `usePokemonData()` から `pokemonList` を取得する
- 種族値が取得できない場合は該当行を非表示にする

### 3-3. DataPage.tsx（2カラムレイアウトに変更）

**変更ファイル**: `frontend/src/presentation/pages/DataPage.tsx`

**レイアウト**:
```
[ データ取得ボタン + ステータス ]
[ 左ペイン              | 中央ペイン                    ]
[ ラジオ + 日付 + 数   | ポケモンパネルグリッド         ]
```

- 左ペイン: 既存の `DataCardList` / `DataCard` を流用。日付・ポケモン数・ラジオボタンのみ表示（上位3体のスプライトは不要になる）
- 中央ペイン: 新コンポーネント `PokemonPanelGrid.tsx` を追加
  - `GET /api/data/pokemon-list` で取得したポケモン一覧をパネル形式で表示
  - 各パネル: スプライト画像 + ポケモン名
  - 表示順: 使用率ランキングがあるポケモンを使用率順に先頭、それ以外をPokedex No順（`pokedex_id` 昇順）
- ポケモン一覧の取得タイミング: `DataPage` 初期表示時、および日付選択（`handleSelectDate` 完了後）のたびに `getPokemonList()` を再取得する
- `useDataManagement` フックに `pokemonList: PokemonListEntry[]` の状態を追加し、上記タイミングで更新する

**変更コンポーネント**:
- `DataCard.tsx`: 上位3体スプライト表示を削除
- `DataCardList.tsx`: 変更なし（左ペインの幅制限のみ調整）
- 新規: `PokemonPanelGrid.tsx`

### 3-4. PredictionPage.tsx / PartyPage.tsx（データガード追加）

**変更ファイル**:
- `frontend/src/presentation/pages/PredictionPage.tsx`
- `frontend/src/presentation/pages/PartyPage.tsx`

- `useDataManagement` の `status` を取得する
- データが存在しない条件: `status` が null、または `status.available_dates` が空配列
- 条件を満たす場合:
  - 主要ボタン（予想実行・パーティ保存）を `disabled` にする
  - 「データが取得されていません。データ管理ページからデータを取得してください。」というメッセージを表示

---

## データフロー

```
バックエンド
  GET /api/data/pokemon-list
        ↓
  dataApi.getPokemonList()
        ↓
  usePokemonData (pokemonList, getBaseStats)
        ↓
  PokemonCard (種族値表示)
  PokemonSlot (プルダウン選択肢)
  PokemonPanelGrid (データ管理画面中央ペイン)
```

---

## テスト方針

- `GET /api/data/pokemon-list` のルーターテストを追加（`test_routers.py`）
- `PokemonSlot` はプルダウン選択でポケモンが選択できること
- `PokemonCard` は種族値が表示されること（ivs は表示しない）
- `DataPage` は左ペインで日付選択すると中央ペインのポケモン一覧が更新されること
- データ未取得時に `PredictionPage` / `PartyPage` のボタンが無効化されること
