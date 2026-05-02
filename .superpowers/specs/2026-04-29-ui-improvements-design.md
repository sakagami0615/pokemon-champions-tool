# UI改善設計書

## 概要

選出予想・パーティ登録のボタン無効化、およびデータ管理ページのレイアウト刷新を行う。

---

## 1. ボタン無効化

### 1-1. 選出予想ページ（`PredictionPage.tsx`）

**有効化条件:**
- 相手パーティに3体以上のポケモンが入力されている
- 自分のパーティが選択済み

**実装方針:**

```tsx
const isReady =
  opponentParty.filter(Boolean).length >= 3 &&
  !!myParty && myParty.length > 0

<button disabled={loading || !isReady} ...>
```

- `usePredict` 内のエラーメッセージ表示は削除する（ボタンが押せないため不要）
- `handlePredict` 内のバリデーションガードはそのまま残す（防御的コード）

### 1-2. パーティ登録ページ（`PartyPage.tsx`）

**有効化条件:**
- パーティ名が1文字以上入力されている
- ポケモンが3体以上選択されている

**実装方針:**

```tsx
const isSaveable =
  name.trim().length > 0 &&
  pokemon.filter(Boolean).length >= 3

<button disabled={!isSaveable} ...>
```

- `save` 関数内の `if (!name) return` ガードはそのまま残す（防御的コード）

---

## 2. データ管理ページ（`DataPage.tsx`）

### 2-1. レイアウト構成

```
[データ管理]

[データ取得ボタン]  [スクレイピング中インジケーター（表示中のみ）]
[完了メッセージ / エラーメッセージ（表示中のみ）]

┌───────────────────────────────────────────────────────┐
│ 取得済みデータ一覧（固定高さ・内部スクロール）               │
│                                                       │
│ ┌─────────────────────────────────────────────────┐  │
│ │ ○  2026-04-29          │ 使用ポケモン上位3位        │  │
│ │    内定ポケモン: 150体   │ [画像] [画像] [画像]      │  │
│ │                        │ ピカチュウ カイオーガ ...   │  │
│ └─────────────────────────────────────────────────┘  │
│                                                       │
│ ┌─────────────────────────────────────────────────┐  │
│ │ ○  2026-04-22          │ 使用ポケモン上位3位        │  │
│ │    内定ポケモン: 148体   │ [画像] [画像] [画像]      │  │
│ │                        │ ...                       │  │
│ └─────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

**詳細:**
- データ取得ボタンは枠（border）なし、ページ上部に常時表示
- 一覧コンテナは固定高さ（`max-h-96` 程度）でオーバーフロー時に内部スクロール
- 各カードを左右2カラムに分割
  - 左側：ラジオボタン + 日付 + 内定ポケモン数
  - 右側：「使用ポケモン上位3位」ラベル + 3体の画像・ポケモン名
- ラジオボタンで選択したデータが `selected_date` に反映される
- ポケモン画像は `/sprites/${name}.png` を使用

### 2-2. バックエンドAPI変更

**変更対象:** `GET /api/data/status`

レスポンスに `dates_detail` フィールドを追加する。

```python
# 追加フィールド
"dates_detail": [
  {
    "date": "2026-04-29",
    "pokemon_count": 150,       # PokemonList のポケモン総数（全日付共通）
    "top_pokemon": [            # UsageData の先頭3件
      {"name": "ピカチュウ", "sprite_path": "sprites/ピカチュウ.png"},
      {"name": "カイオーガ", "sprite_path": "sprites/カイオーガ.png"},
      {"name": "ルカリオ",   "sprite_path": "sprites/ルカリオ.png"},
    ]
  },
  ...  # available_dates と同じ順序（降順）
]
```

**実装方針:**
- `data_status()` ルーター関数内で `available_dates` をループし、各日付の `UsageData` から先頭3件を取得
- `PokemonList` のポケモン総数は1回だけ取得して全日付に使い回す
- `UsageData` が存在しない日付（異常系）は `top_pokemon: []`, `pokemon_count: 0` とする

**フロントエンド型定義変更（`dataApi.ts`）:**

```typescript
export interface DateDetail {
  date: string
  pokemon_count: number
  top_pokemon: { name: string; sprite_path: string }[]
}

export interface DataStatus {
  scraping_in_progress: boolean
  selected_date: string | null
  available_dates: string[]
  dates_detail: DateDetail[]
  // 削除: pokemon_list_available, usage_data_available, usage_data_date
}
```

既存の `pokemon_list_available`, `usage_data_available`, `usage_data_date` フィールドは `dates_detail` で代替できるため削除する。

### 2-3. フロントエンドコンポーネント構成

- `DataPage.tsx`：ページ全体の構成（ボタン + 一覧）
- `DataCardList.tsx`（新規）：スクロール可能な一覧コンテナ
- `DataCard.tsx`（新規）：各日付カード（左右2カラム）

---

## 影響範囲まとめ

| ファイル | 変更種別 |
|----------|----------|
| `frontend/src/presentation/pages/PredictionPage.tsx` | 変更 |
| `frontend/src/presentation/pages/PartyPage.tsx` | 変更 |
| `frontend/src/presentation/pages/DataPage.tsx` | 変更 |
| `frontend/src/presentation/components/DataCardList.tsx` | 新規 |
| `frontend/src/presentation/components/DataCard.tsx` | 新規 |
| `frontend/src/infrastructure/api/dataApi.ts` | 変更 |
| `frontend/src/application/hooks/useDataManagement.ts` | 変更 |
| `backend/src/presentation/routers/data.py` | 変更 |
