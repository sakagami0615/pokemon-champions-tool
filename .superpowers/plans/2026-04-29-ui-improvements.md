# UI改善 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 選出予想・パーティ登録のボタンを入力条件が揃うまで無効化し、データ管理ページのレイアウトを刷新してデータを複数カードで表示・ラジオボタンで選択できるようにする。

**Architecture:** バックエンドの `/api/data/status` に `dates_detail` フィールドを追加して各日付ごとのポケモン数・上位3体を返す。フロントエンドは `DataCard` / `DataCardList` コンポーネントを新規作成し、`DataPage` を再構成する。ボタン無効化は各ページ内のローカルな条件計算で実現する。

**Tech Stack:** FastAPI (Python), React + TypeScript, Tailwind CSS, pytest, httpx

---

## ファイルマップ

| ファイル | 変更種別 | 責務 |
|----------|----------|------|
| `backend/src/presentation/routers/data.py` | 変更 | `/api/data/status` に `dates_detail` を追加 |
| `backend/tests/test_routers.py` | 変更 | `dates_detail` のテストを追加 |
| `frontend/src/infrastructure/api/dataApi.ts` | 変更 | `DataStatus` 型に `dates_detail` を追加、不要フィールドを削除 |
| `frontend/src/presentation/components/DataCard.tsx` | 新規 | 各日付カード（左右2カラム）コンポーネント |
| `frontend/src/presentation/components/DataCardList.tsx` | 新規 | スクロール可能な一覧コンテナコンポーネント |
| `frontend/src/presentation/pages/DataPage.tsx` | 変更 | 新レイアウト（ボタン上部・カード一覧下部）に再構成 |
| `frontend/src/presentation/pages/PartyPage.tsx` | 変更 | 登録ボタンに `isSaveable` 条件を追加 |
| `frontend/src/presentation/pages/PredictionPage.tsx` | 変更 | 選出予想ボタンに `isReady` 条件を追加 |
| `frontend/src/application/hooks/usePredict.ts` | 変更 | バリデーションしきい値の更新、エラーメッセージ削除 |

---

## Task 1: バックエンド `/api/data/status` に `dates_detail` を追加

**Files:**
- Modify: `backend/src/presentation/routers/data.py:137-149`
- Modify: `backend/tests/test_routers.py:107-115`

- [ ] **Step 1: 失敗するテストを追加**

`backend/tests/test_routers.py` の末尾に追加：

```python
@pytest.mark.asyncio
async def test_data_status_dates_detail_structure():
    from domain.entities.pokemon import UsageData, UsageEntry, PokemonList, PokemonInfo, BaseStats
    import presentation.routers.data as rd

    entry = UsageEntry(
        name="ピカチュウ",
        moves=[], items=[], abilities=[], natures=[], teammates=[], evs=[]
    )
    usage = UsageData(
        collected_at="2026-04-29T12:00:00",
        season=0, regulation="", source_updated_at="2026-04-29T12:00:00",
        pokemon=[entry]
    )
    plist = PokemonList(
        collected_at="2026-04-29T12:00:00",
        pokemon=[
            PokemonInfo(
                pokedex_id=25, name="ピカチュウ", types=["でんき"],
                base_stats=BaseStats(hp=35, attack=55, defense=40, sp_attack=50, sp_defense=50, speed=90),
                height_m=0.4, weight_kg=6.0, low_kick_power=20,
                abilities=["せいでんき"], weaknesses=["じめん"], resistances=["でんき"],
                sprite_path="sprites/ピカチュウ.png"
            )
        ]
    )
    rd._usage_repo.save_usage_data(usage)
    rd._usage_repo.save_pokemon_list(plist)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/data/status")

    assert resp.status_code == 200
    data = resp.json()
    assert "dates_detail" in data
    assert len(data["dates_detail"]) == 1
    detail = data["dates_detail"][0]
    assert detail["date"] == "2026-04-29"
    assert detail["pokemon_count"] == 1
    assert detail["top_pokemon"] == [{"name": "ピカチュウ"}]
```

また、既存の `test_data_status_includes_scraping_fields` に `dates_detail` のアサーションを追加：

```python
@pytest.mark.asyncio
async def test_data_status_includes_scraping_fields():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/data/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "scraping_in_progress" in data
    assert "selected_date" in data
    assert "available_dates" in data
    assert "dates_detail" in data
    assert isinstance(data["available_dates"], list)
    assert isinstance(data["dates_detail"], list)
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
docker compose run --rm backend pytest tests/test_routers.py::test_data_status_dates_detail_structure -v
```

期待: `FAILED` （`dates_detail` キーが存在しない）

- [ ] **Step 3: `data_status` 関数を実装**

`backend/src/presentation/routers/data.py` の `data_status()` 関数を以下に置き換え：

```python
@router.get("/status")
def data_status():
    pokemon_list = _usage_repo.get_pokemon_list()
    available_dates = _usage_repo.get_available_dates()
    pokemon_count = len(pokemon_list.pokemon) if pokemon_list else 0

    dates_detail = []
    for date in available_dates:
        usage_data = _usage_repo.get_usage_data_by_date(date)
        if usage_data:
            top_pokemon = [{"name": p.name} for p in usage_data.pokemon[:3]]
        else:
            top_pokemon = []
        dates_detail.append({
            "date": date,
            "pokemon_count": pokemon_count,
            "top_pokemon": top_pokemon,
        })

    return {
        "scraping_in_progress": _state.scraping_in_progress,
        "selected_date": _state.selected_date,
        "available_dates": available_dates,
        "dates_detail": dates_detail,
    }
```

- [ ] **Step 4: テストが通ることを確認**

```bash
docker compose run --rm backend pytest tests/test_routers.py -v
```

期待: 全テスト `PASSED`

- [ ] **Step 5: コミット**

```bash
git add backend/src/presentation/routers/data.py backend/tests/test_routers.py
git commit -m "feat: data_status API に dates_detail フィールドを追加"
```

---

## Task 2: フロントエンド型定義更新（`dataApi.ts`）

**Files:**
- Modify: `frontend/src/infrastructure/api/dataApi.ts:1-10`

- [ ] **Step 1: `DataStatus` 型を更新**

`frontend/src/infrastructure/api/dataApi.ts` の先頭部分を以下に置き換え：

```typescript
const BASE = '/api'

export interface TopPokemon {
  name: string
}

export interface DateDetail {
  date: string
  pokemon_count: number
  top_pokemon: TopPokemon[]
}

export interface DataStatus {
  scraping_in_progress: boolean
  selected_date: string | null
  available_dates: string[]
  dates_detail: DateDetail[]
}
```

（`pokemon_list_available`, `usage_data_available`, `usage_data_date` は削除する。以降の関数定義はそのまま保持。）

- [ ] **Step 2: コミット**

```bash
git add frontend/src/infrastructure/api/dataApi.ts
git commit -m "feat: DataStatus 型に dates_detail を追加、旧フィールドを削除"
```

---

## Task 3: `DataCard.tsx` 新規作成

**Files:**
- Create: `frontend/src/presentation/components/DataCard.tsx`

- [ ] **Step 1: コンポーネントを作成**

`frontend/src/presentation/components/DataCard.tsx` を新規作成：

```tsx
import type { DateDetail } from '../../infrastructure/api/dataApi'

interface Props {
  detail: DateDetail
  selected: boolean
  onSelect: (date: string) => void
}

export default function DataCard({ detail, selected, onSelect }: Props) {
  return (
    <label className="flex items-start gap-3 border rounded-lg p-4 cursor-pointer dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
      <input
        type="radio"
        name="selected-date"
        checked={selected}
        onChange={() => onSelect(detail.date)}
        className="mt-1 shrink-0"
      />
      <div className="flex flex-1 gap-4">
        <div className="flex-1">
          <p className="font-bold text-sm">{detail.date}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">内定ポケモン: {detail.pokemon_count}体</p>
        </div>
        {detail.top_pokemon.length > 0 && (
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">使用ポケモン上位3位</p>
            <div className="flex gap-2">
              {detail.top_pokemon.map((p) => (
                <div key={p.name} className="text-center">
                  <img
                    src={`/sprites/${p.name}.png`}
                    alt={p.name}
                    className="w-10 h-10 object-contain mx-auto"
                    onError={(e) => {
                      ;(e.target as HTMLImageElement).style.display = 'none'
                    }}
                  />
                  <p className="text-xs">{p.name}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </label>
  )
}
```

- [ ] **Step 2: コミット**

```bash
git add frontend/src/presentation/components/DataCard.tsx
git commit -m "feat: DataCard コンポーネントを新規作成"
```

---

## Task 4: `DataCardList.tsx` 新規作成

**Files:**
- Create: `frontend/src/presentation/components/DataCardList.tsx`

- [ ] **Step 1: コンポーネントを作成**

`frontend/src/presentation/components/DataCardList.tsx` を新規作成：

```tsx
import type { DateDetail } from '../../infrastructure/api/dataApi'
import DataCard from './DataCard'

interface Props {
  details: DateDetail[]
  selectedDate: string | null
  onSelect: (date: string) => void
}

export default function DataCardList({ details, selectedDate, onSelect }: Props) {
  if (details.length === 0) {
    return <p className="text-sm text-gray-500">取得済みデータがありません</p>
  }

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-y-auto max-h-96 space-y-2 p-2">
      {details.map((detail) => (
        <DataCard
          key={detail.date}
          detail={detail}
          selected={selectedDate === detail.date}
          onSelect={onSelect}
        />
      ))}
    </div>
  )
}
```

- [ ] **Step 2: コミット**

```bash
git add frontend/src/presentation/components/DataCardList.tsx
git commit -m "feat: DataCardList コンポーネントを新規作成"
```

---

## Task 5: `DataPage.tsx` 更新

**Files:**
- Modify: `frontend/src/presentation/pages/DataPage.tsx`

- [ ] **Step 1: DataPage を新レイアウトに書き換え**

`frontend/src/presentation/pages/DataPage.tsx` の全内容を以下に置き換え：

```tsx
import { useDataManagement } from '../../application/hooks/useDataManagement'
import DataCardList from '../components/DataCardList'

export default function DataPage() {
  const { status, isFetching, fetchMessage, error, triggerFetch, handleSelectDate } = useDataManagement()

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-xl font-bold">データ管理</h1>

      <div className="space-y-2">
        <div className="flex items-center gap-4">
          <button
            onClick={triggerFetch}
            disabled={isFetching}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
          >
            {isFetching ? '開始中...' : 'データ取得'}
          </button>
          {status?.scraping_in_progress && (
            <p className="text-sm text-yellow-500 animate-pulse">スクレイピング実行中...</p>
          )}
        </div>
        {fetchMessage && <p className="text-sm text-green-600">{fetchMessage}</p>}
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>

      {status === null ? (
        <p className="text-sm text-gray-500">読み込み中...</p>
      ) : (
        <DataCardList
          details={status.dates_detail}
          selectedDate={status.selected_date}
          onSelect={handleSelectDate}
        />
      )}
    </div>
  )
}
```

- [ ] **Step 2: コミット**

```bash
git add frontend/src/presentation/pages/DataPage.tsx
git commit -m "feat: DataPage を新レイアウト（ボタン上部・カード一覧下部）に刷新"
```

---

## Task 6: `PartyPage.tsx` ボタン無効化

**Files:**
- Modify: `frontend/src/presentation/pages/PartyPage.tsx:65-79`

- [ ] **Step 1: `isSaveable` 条件を追加**

`PartyPage.tsx` の `remove` 関数の後、`return` 文の直前に以下を追加し、ボタンに `disabled` を設定する。

`remove` 関数の後（`return` 文の直前）に追加：

```tsx
const isSaveable = name.trim().length > 0 && pokemon.filter(Boolean).length >= 3
```

ボタン部分を以下に変更（`disabled` プロパティと `disabled:opacity-50` クラスを追加）：

```tsx
<button
  onClick={save}
  disabled={!isSaveable}
  className="px-4 py-2 rounded bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold disabled:opacity-50"
>
  {editing ? '更新' : '登録'}
</button>
```

- [ ] **Step 2: コミット**

```bash
git add frontend/src/presentation/pages/PartyPage.tsx
git commit -m "feat: パーティ登録ボタンを条件未満の場合に無効化"
```

---

## Task 7: `PredictionPage.tsx` ボタン無効化・`usePredict.ts` 更新

**Files:**
- Modify: `frontend/src/presentation/pages/PredictionPage.tsx:9-47`
- Modify: `frontend/src/application/hooks/usePredict.ts:17-28`

- [ ] **Step 1: `usePredict.ts` のバリデーションを更新**

`frontend/src/application/hooks/usePredict.ts` の `handlePredict` 関数内の早期リターン部分を以下に変更：

変更前：
```typescript
if (opponent.length < 6) {
  setError('相手パーティを6体入力してください')
  return
}
if (my.length < 6) {
  setError('自分のパーティを6体入力してください')
  return
}
```

変更後：
```typescript
if (opponent.length < 3) return
if (my.length === 0) return
```

- [ ] **Step 2: `PredictionPage.tsx` に `isReady` 条件を追加**

`PredictionPage.tsx` の `return` 文の直前に以下を追加：

```tsx
const isReady =
  opponentParty.filter(Boolean).length >= 3 &&
  selectedPartyId !== null
```

ボタン部分を以下に変更：

```tsx
<button
  onClick={() => handlePredict(opponentParty, myParty)}
  disabled={loading || !isReady}
  className="w-full py-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
>
  {loading ? '予想中...' : '選出予想する'}
</button>
```

また、エラー表示の直前にある `{error && ...}` の行はそのまま残す（API エラーは引き続き表示する）。

- [ ] **Step 3: コミット**

```bash
git add frontend/src/application/hooks/usePredict.ts frontend/src/presentation/pages/PredictionPage.tsx
git commit -m "feat: 選出予想ボタンを条件未満の場合に無効化"
```
