# UX改善（進捗表示・プロンプト管理・トースト通知）実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** データ取得中のプログレスバー表示・プロンプトのYAML設定ファイル管理・完了トースト通知を実装する

**Architecture:** バックエンドのスクレイパーにコールバック関数を伝搬してscraping_stateを更新し、フロントエンドがポーリングで進捗を取得してUIに反映する。プロンプトはYAMLファイルから毎回読み込みPredictUseCaseにDIする。完了通知はsonnerトーストとlocalStorageで管理する。

**Tech Stack:** Python/FastAPI, PyYAML, React/TypeScript/Tailwind, sonner

---

## ファイル構成

### 新規作成
- `backend/src/domain/entities/prompt_config.py` — PromptConfig データクラス
- `backend/src/domain/repositories/prompt_config_repository.py` — IPromptConfigRepository インターフェース
- `backend/src/infrastructure/persistence/yaml_prompt_config_repository.py` — YAML読み込み実装
- `backend/config/prompts.yaml` — プロンプト設定ファイル
- `backend/tests/test_yaml_prompt_config_repository.py` — リポジトリのテスト
- `frontend/src/presentation/components/ScrapeProgressBar.tsx` — プログレスバーコンポーネント

### 変更
- `backend/src/application/state/scraping_state.py` — progress/step/last_scraped_at 追加
- `backend/src/infrastructure/external/pokemon_list_scraper.py` — コールバック引数追加
- `backend/src/application/use_cases/scrape_pokemon_list_use_case.py` — コールバック伝搬
- `backend/src/application/use_cases/predict_use_case.py` — SYSTEM_PROMPT 削除、DI追加
- `backend/src/presentation/routers/data.py` — 進捗更新・last_scraped_at 記録
- `backend/src/presentation/routers/prediction.py` — YamlPromptConfigRepository 注入
- `backend/tests/test_predict_use_case.py` — prompt_config_repository 対応
- `backend/tests/test_scrape_pokemon_list_use_case.py` — コールバックテスト追加
- `frontend/src/infrastructure/api/dataApi.ts` — DataStatus 型に3フィールド追加
- `frontend/src/application/hooks/useDataManagement.ts` — トースト通知追加
- `frontend/src/presentation/pages/SettingsPage.tsx` — プログレスバー組み込み
- `frontend/src/App.tsx` — Toaster 追加

---

### Task 1: scraping_state.py にフィールドを追加

**Files:**
- Modify: `backend/src/application/state/scraping_state.py`

- [ ] **Step 1: フィールドを追加する**

`backend/src/application/state/scraping_state.py` を以下に書き換える：

```python
scraping_in_progress: bool = False
scraping_progress: int = 0
scraping_step: str = ""
last_scraped_at: str | None = None
selected_date: str | None = None
```

- [ ] **Step 2: コミット**

```bash
git add backend/src/application/state/scraping_state.py
git commit -m "feat: add progress, step, last_scraped_at fields to scraping_state"
```

---

### Task 2: PokemonListScraper._fetch_all にコールバックを追加

**Files:**
- Modify: `backend/src/infrastructure/external/pokemon_list_scraper.py`
- Test: `backend/tests/test_pokemon_list_scraper.py`

- [ ] **Step 1: テストを追加する**

`backend/tests/test_pokemon_list_scraper.py` の末尾に以下を追加する（既存テストはそのまま残す）：

```python
def test_fetch_all_invokes_progress_callback(tmp_path):
    scraper = PokemonListScraper(sprites_dir=tmp_path)
    calls: list[tuple[int, str]] = []

    def on_progress(progress: int, step: str) -> None:
        calls.append((progress, step))

    grouped = [
        (1, "フシギダネ", "http://example.com/1", "001.png"),
        (4, "ヒトカゲ", "http://example.com/4", "004.png"),
    ]

    with patch.object(scraper, '_fetch', return_value=MagicMock()), \
         patch.object(scraper, '_parse_detail_page', return_value=MagicMock()):
        scraper._fetch_all(
            grouped,
            on_progress=on_progress,
            progress_start=5,
            progress_end=45,
            step_label="通常ポケモン",
        )

    # i=1, total=2: 5 + int(1/2 * 40) = 25
    # i=2, total=2: 5 + int(2/2 * 40) = 45
    assert calls == [
        (25, "通常ポケモン取得中... (1/2)"),
        (45, "通常ポケモン取得中... (2/2)"),
    ]


def test_fetch_all_without_callback_does_not_raise(tmp_path):
    scraper = PokemonListScraper(sprites_dir=tmp_path)
    grouped = [(1, "フシギダネ", "http://example.com/1", "001.png")]

    with patch.object(scraper, '_fetch', return_value=MagicMock()), \
         patch.object(scraper, '_parse_detail_page', return_value=MagicMock()):
        result = scraper._fetch_all(grouped)

    assert len(result) == 1
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
docker compose run --rm backend pytest tests/test_pokemon_list_scraper.py::test_fetch_all_invokes_progress_callback -v
```

Expected: FAIL（`_fetch_all` が `on_progress` 引数を受け付けない）

- [ ] **Step 3: `_fetch_all` と `fetch_pokemon_list` を更新する**

`backend/src/infrastructure/external/pokemon_list_scraper.py` の import 直後に型エイリアスを追加し、メソッドを書き換える：

```python
import logging
import re
from typing import Callable
from bs4 import BeautifulSoup
from domain.entities.pokemon import PokemonInfo, BaseStats
from infrastructure.external.base_scraper import BaseScraper
from infrastructure.external.constants import POKEMON_LIST_URL

_logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, str], None]

# ... _STAT_KEY_MAP, _TYPE_ATTR_MAP はそのまま残す ...

class PokemonListScraper(BaseScraper):
    def fetch_pokemon_list(
        self,
        on_progress: ProgressCallback | None = None,
    ) -> tuple[list[PokemonInfo], list[PokemonInfo]]:
        _logger.info("内定ポケモン一覧ページを取得中...")
        if on_progress:
            on_progress(0, "ポケモン一覧ページを取得中...")
        list_soup = self._fetch(POKEMON_LIST_URL)
        entries = self._parse_list_page(list_soup)
        normals, megas = self._group_entries(entries)
        _logger.info("一覧取得完了: 通常 %d 体 / メガ %d 体", len(normals), len(megas))
        _logger.info("通常ポケモンの詳細を取得中...")
        normal_list = self._fetch_all(
            normals,
            on_progress=on_progress,
            progress_start=5,
            progress_end=45,
            step_label="通常ポケモン",
        )
        _logger.info("メガシンカポケモンの詳細を取得中...")
        mega_list = self._fetch_all(
            megas,
            on_progress=on_progress,
            progress_start=45,
            progress_end=50,
            step_label="メガポケモン",
        )
        return normal_list, mega_list

    def _fetch_all(
        self,
        grouped: list[tuple[int, str, str, str]],
        on_progress: ProgressCallback | None = None,
        progress_start: int = 0,
        progress_end: int = 100,
        step_label: str = "ポケモン",
    ) -> list[PokemonInfo]:
        total = len(grouped)
        result: list[PokemonInfo] = []
        for i, (pokedex_id, name, url, sprite_filename) in enumerate(grouped, 1):
            _logger.info("[%3d/%3d] %s を取得中...", i, total, name)
            detail_soup = self._fetch(url)
            info = self._parse_detail_page(
                detail_soup,
                pokedex_id=pokedex_id,
                name=name,
                sprite_filename=sprite_filename,
            )
            result.append(info)
            if on_progress is not None and total > 0:
                progress = progress_start + int((i / total) * (progress_end - progress_start))
                on_progress(progress, f"{step_label}取得中... ({i}/{total})")
        return result
```

`_parse_list_page`, `_group_entries`, `_parse_detail_page` はそのまま残す。

- [ ] **Step 4: テストが通ることを確認する**

```bash
docker compose run --rm backend pytest tests/test_pokemon_list_scraper.py -v
```

Expected: PASS

- [ ] **Step 5: コミット**

```bash
git add backend/src/infrastructure/external/pokemon_list_scraper.py backend/tests/test_pokemon_list_scraper.py
git commit -m "feat: add progress callback to PokemonListScraper._fetch_all"
```

---

### Task 3: ScrapePokemonListUseCase にコールバックを伝搬

**Files:**
- Modify: `backend/src/application/use_cases/scrape_pokemon_list_use_case.py`
- Test: `backend/tests/test_scrape_pokemon_list_use_case.py`

- [ ] **Step 1: テストを追加する**

`backend/tests/test_scrape_pokemon_list_use_case.py` の末尾に以下を追加する：

```python
def test_execute_passes_callback_to_scraper():
    mock_scraper = MagicMock()
    mock_scraper.fetch_pokemon_list.return_value = ([], [])
    mock_repo = MagicMock()
    use_case = ScrapePokemonListUseCase(scraper=mock_scraper, repository=mock_repo)
    callback = MagicMock()

    use_case.execute(on_progress=callback)

    mock_scraper.fetch_pokemon_list.assert_called_once_with(on_progress=callback)


def test_execute_without_callback_does_not_raise():
    mock_scraper = MagicMock()
    mock_scraper.fetch_pokemon_list.return_value = ([], [])
    mock_repo = MagicMock()
    use_case = ScrapePokemonListUseCase(scraper=mock_scraper, repository=mock_repo)

    use_case.execute()
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
docker compose run --rm backend pytest tests/test_scrape_pokemon_list_use_case.py::test_execute_passes_callback_to_scraper -v
```

Expected: FAIL（`execute` が `on_progress` 引数を受け付けない）

- [ ] **Step 3: `execute` を更新する**

`backend/src/application/use_cases/scrape_pokemon_list_use_case.py` を以下に書き換える：

```python
from datetime import datetime
from typing import Callable
from domain.entities.pokemon import PokemonList
from domain.repositories.pokemon_list_repository import IPokemonListRepository
from infrastructure.external.pokemon_list_scraper import PokemonListScraper

ProgressCallback = Callable[[int, str], None]


class ScrapePokemonListUseCase:
    def __init__(self, scraper: PokemonListScraper, repository: IPokemonListRepository):
        self._scraper = scraper
        self._repository = repository

    def execute(self, on_progress: ProgressCallback | None = None) -> None:
        pokemons, mega_pokemons = self._scraper.fetch_pokemon_list(on_progress=on_progress)
        data = PokemonList(
            collected_at=datetime.now().isoformat(),
            pokemons=pokemons,
            mega_pokemons=mega_pokemons,
        )
        self._repository.save_pokemon_list(data)
```

- [ ] **Step 4: テストが通ることを確認する**

```bash
docker compose run --rm backend pytest tests/test_scrape_pokemon_list_use_case.py -v
```

Expected: PASS

- [ ] **Step 5: コミット**

```bash
git add backend/src/application/use_cases/scrape_pokemon_list_use_case.py backend/tests/test_scrape_pokemon_list_use_case.py
git commit -m "feat: propagate progress callback through ScrapePokemonListUseCase"
```

---

### Task 4: data.py の `_do_fetch` と `data_status` を更新

**Files:**
- Modify: `backend/src/presentation/routers/data.py`

- [ ] **Step 1: `_do_fetch` を書き換える**

`backend/src/presentation/routers/data.py` の `_do_fetch` 関数を以下に置き換える（他の部分はそのまま）：

```python
def _do_fetch() -> None:
    _state.scraping_in_progress = True
    _state.scraping_progress = 0
    _state.scraping_step = "ポケモン一覧ページを取得中..."

    def on_progress(progress: int, step: str) -> None:
        _state.scraping_progress = progress
        _state.scraping_step = step

    try:
        try:
            use_case = ScrapePokemonListUseCase(
                scraper=PokemonListScraper(sprites_dir=_sprites_dir),
                repository=_pokemon_list_repo,
            )
            use_case.execute(on_progress=on_progress)
            _logger.info("ポケモン一覧のスクレイピングが完了しました")
        except Exception:
            _logger.exception("ポケモン一覧スクレイピングでエラーが発生しました")

        _state.scraping_progress = 50
        _state.scraping_step = "使用率データ取得中..."

        try:
            scraper = GameWithScraper(sprites_dir=_sprites_dir)
        except Exception:
            _logger.exception("GameWithScraper の初期化に失敗しました")
            return
        _fetch_and_save_usage_data(scraper)

        _state.scraping_progress = 100
        _state.scraping_step = ""
        _state.last_scraped_at = datetime.now().isoformat()
    finally:
        _state.scraping_in_progress = False
```

- [ ] **Step 2: `data_status` を書き換える**

同ファイルの `data_status` 関数を以下に置き換える：

```python
@router.get("/status")
def data_status():
    pokemon_list = _pokemon_list_repo.get_pokemon_list()
    available_dates = _usage_repo.get_available_dates()
    pokemon_count = (len(pokemon_list.pokemons) + len(pokemon_list.mega_pokemons)) if pokemon_list else 0

    dates_detail = []
    for date in available_dates:
        usage_data = _usage_repo.get_usage_data_by_date(date)
        top_pokemon = [{"name": p.name} for p in usage_data.pokemons[:3]] if usage_data else []
        dates_detail.append({
            "date": date,
            "pokemon_count": pokemon_count,
            "top_pokemon": top_pokemon,
        })

    return {
        "scraping_in_progress": _state.scraping_in_progress,
        "scraping_progress": _state.scraping_progress,
        "scraping_step": _state.scraping_step,
        "last_scraped_at": _state.last_scraped_at,
        "selected_date": _state.selected_date,
        "available_dates": available_dates,
        "dates_detail": dates_detail,
    }
```

- [ ] **Step 3: テストが通ることを確認する**

```bash
docker compose run --rm backend pytest tests/test_routers.py -v
```

Expected: PASS（既存テストが壊れていないこと）

- [ ] **Step 4: コミット**

```bash
git add backend/src/presentation/routers/data.py
git commit -m "feat: update _do_fetch to report progress and record last_scraped_at"
```

---

### Task 5: フロントエンド DataStatus 型を更新

**Files:**
- Modify: `frontend/src/infrastructure/api/dataApi.ts`

- [ ] **Step 1: DataStatus インターフェースを更新する**

`frontend/src/infrastructure/api/dataApi.ts` の `DataStatus` インターフェースを以下に書き換える：

```typescript
export interface DataStatus {
  scraping_in_progress: boolean
  scraping_progress: number
  scraping_step: string
  last_scraped_at: string | null
  selected_date: string | null
  available_dates: string[]
  dates_detail: DateDetail[]
}
```

- [ ] **Step 2: コミット**

```bash
git add frontend/src/infrastructure/api/dataApi.ts
git commit -m "feat: add scraping_progress, scraping_step, last_scraped_at to DataStatus"
```

---

### Task 6: ScrapeProgressBar コンポーネントを作成

**Files:**
- Create: `frontend/src/presentation/components/ScrapeProgressBar.tsx`

- [ ] **Step 1: コンポーネントを新規作成する**

`frontend/src/presentation/components/ScrapeProgressBar.tsx` を作成する：

```tsx
interface Props {
  progress: number
  step: string
}

export default function ScrapeProgressBar({ progress, step }: Props) {
  return (
    <div className="space-y-1">
      {step && (
        <p className="text-sm text-gray-600 dark:text-gray-400">{step}</p>
      )}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
        <div
          className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="text-sm text-gray-500">{progress}%</p>
    </div>
  )
}
```

- [ ] **Step 2: コミット**

```bash
git add frontend/src/presentation/components/ScrapeProgressBar.tsx
git commit -m "feat: add ScrapeProgressBar component"
```

---

### Task 7: SettingsPage.tsx にプログレスバーを組み込む

**Files:**
- Modify: `frontend/src/presentation/pages/SettingsPage.tsx`

- [ ] **Step 1: import を追加する**

`frontend/src/presentation/pages/SettingsPage.tsx` の import 末尾に追加する：

```typescript
import ScrapeProgressBar from '../components/ScrapeProgressBar'
```

- [ ] **Step 2: 「スクレイピング実行中...」テキストをプログレスバーに置き換える**

以下の部分を：

```tsx
{status?.scraping_in_progress && (
  <p className="text-sm text-yellow-500 animate-pulse">
    スクレイピング実行中...
  </p>
)}
```

以下に置き換える：

```tsx
{status?.scraping_in_progress && (
  <ScrapeProgressBar
    progress={status.scraping_progress}
    step={status.scraping_step}
  />
)}
```

- [ ] **Step 3: 動作確認する**

```bash
docker compose up
```

ブラウザで `http://localhost:5173` の設定ページを開き、「データ取得」ボタンを押してプログレスバーが表示されることを確認する。

- [ ] **Step 4: コミット**

```bash
git add frontend/src/presentation/pages/SettingsPage.tsx
git commit -m "feat: replace scraping status text with ScrapeProgressBar"
```

---

### Task 8: sonner を導入して Toaster を追加

**Files:**
- Modify: `frontend/package.json`（npm install で自動更新）
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: sonner をインストールする**

```bash
docker compose run --rm frontend npm install sonner
```

- [ ] **Step 2: App.tsx に Toaster を追加する**

`frontend/src/App.tsx` の import 末尾に追加する：

```typescript
import { Toaster } from 'sonner'
```

App コンポーネントの return 内のルート要素の直下（他の要素の前）に追加する：

```tsx
<Toaster position="top-right" richColors />
```

- [ ] **Step 3: コミット**

```bash
git add frontend/package.json frontend/package-lock.json frontend/src/App.tsx
git commit -m "feat: install sonner and add Toaster to App"
```

---

### Task 9: useDataManagement にトースト通知を追加

**Files:**
- Modify: `frontend/src/application/hooks/useDataManagement.ts`

トースト表示のロジック：
- `triggerFetch()` 実行時に `localStorage` の `SCRAPING_PENDING_KEY` を `'true'` にセット
- 通常セッション（リロードなし）: `wasScrapingRef` が `true` → `scraping_in_progress` が `false` になった瞬間にトーストを表示
- リロード後: `loadStatus()` で `scraping_in_progress: false` かつ `SCRAPING_PENDING_KEY === 'true'` かつ `last_scraped_at > last_notified_at` の場合にトーストを表示
- トースト表示後は `LAST_NOTIFIED_KEY` を更新して重複表示を防ぐ

- [ ] **Step 1: useDataManagement.ts を書き換える**

`frontend/src/application/hooks/useDataManagement.ts` を以下に書き換える：

```typescript
import { useState, useEffect, useRef, useCallback } from 'react'
import { toast } from 'sonner'
import { fetchData, getDataStatus, selectDate, getPokemonList, DataStatus } from '../../infrastructure/api/dataApi'
import type { PokemonListEntry } from '../../domain/entities/pokemon'

const SCRAPING_PENDING_KEY = 'pokemon_tool_scraping_pending'
const LAST_NOTIFIED_KEY = 'pokemon_tool_last_notified_at'

interface UseDataManagementReturn {
  status: DataStatus | null
  pokemonList: PokemonListEntry[]
  isFetching: boolean
  fetchMessage: string | null
  error: string | null
  triggerFetch: () => Promise<void>
  handleSelectDate: (date: string) => Promise<void>
}

export function useDataManagement(): UseDataManagementReturn {
  const [status, setStatus] = useState<DataStatus | null>(null)
  const [pokemonList, setPokemonList] = useState<PokemonListEntry[]>([])
  const [isFetching, setIsFetching] = useState(false)
  const [fetchMessage, setFetchMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const wasScrapingRef = useRef(false)

  const showCompletionToast = useCallback((lastScrapedAt: string) => {
    const lastNotified = localStorage.getItem(LAST_NOTIFIED_KEY)
    if (!lastNotified || lastScrapedAt > lastNotified) {
      toast.success('データ取得が完了しました')
      localStorage.setItem(LAST_NOTIFIED_KEY, lastScrapedAt)
    }
    localStorage.removeItem(SCRAPING_PENDING_KEY)
  }, [])

  const loadStatus = useCallback(async () => {
    try {
      const s = await getDataStatus()
      setStatus(s)

      if (
        !s.scraping_in_progress &&
        s.last_scraped_at &&
        localStorage.getItem(SCRAPING_PENDING_KEY) === 'true'
      ) {
        showCompletionToast(s.last_scraped_at)
      }
    } catch {
    }
  }, [showCompletionToast])

  const loadPokemonList = useCallback(async () => {
    try {
      const res = await getPokemonList()
      setPokemonList([...res.pokemons, ...res.mega_pokemons])
    } catch {
    }
  }, [])

  useEffect(() => {
    loadStatus()
    loadPokemonList()
  }, [loadStatus, loadPokemonList])

  useEffect(() => {
    if (status?.scraping_in_progress) {
      wasScrapingRef.current = true
      pollingRef.current = setInterval(loadStatus, 3000)
    } else {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
      if (wasScrapingRef.current) {
        wasScrapingRef.current = false
        loadPokemonList()
        if (status?.last_scraped_at) {
          showCompletionToast(status.last_scraped_at)
        }
      }
    }
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
  }, [status?.scraping_in_progress, status?.last_scraped_at, loadStatus, loadPokemonList, showCompletionToast])

  const triggerFetch = useCallback(async () => {
    setIsFetching(true)
    setError(null)
    setFetchMessage(null)
    try {
      await fetchData()
      localStorage.setItem(SCRAPING_PENDING_KEY, 'true')
      setFetchMessage('データ取得を開始しました')
      await loadStatus()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'データ取得の開始に失敗しました')
    } finally {
      setIsFetching(false)
    }
  }, [loadStatus])

  const handleSelectDate = useCallback(async (date: string) => {
    setError(null)
    const previous = status?.selected_date ?? null
    setStatus((prev) => prev ? { ...prev, selected_date: date } : prev)
    try {
      await selectDate(date)
      await loadPokemonList()
    } catch (e) {
      setStatus((prev) => prev ? { ...prev, selected_date: previous } : prev)
      setError(e instanceof Error ? e.message : '日付の選択に失敗しました')
    }
  }, [status?.selected_date, loadPokemonList])

  return { status, pokemonList, isFetching, fetchMessage, error, triggerFetch, handleSelectDate }
}
```

- [ ] **Step 2: 動作確認する**

ブラウザで `http://localhost:5173` の設定ページを開き、「データ取得」ボタンを押す。スクレイピング完了後に右上にトーストが表示されることを確認する。ページをリロードしてもトーストが再表示されないことを確認する。

- [ ] **Step 3: コミット**

```bash
git add frontend/src/application/hooks/useDataManagement.ts
git commit -m "feat: add completion toast with localStorage dedup to useDataManagement"
```

---

### Task 10: PromptConfig エンティティと IPromptConfigRepository を作成

**Files:**
- Create: `backend/src/domain/entities/prompt_config.py`
- Create: `backend/src/domain/repositories/prompt_config_repository.py`

- [ ] **Step 1: PromptConfig エンティティを作成する**

`backend/src/domain/entities/prompt_config.py` を新規作成する：

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PromptConfig:
    system_prompt: str
    user_prompt_template: str
```

- [ ] **Step 2: IPromptConfigRepository インターフェースを作成する**

`backend/src/domain/repositories/prompt_config_repository.py` を新規作成する：

```python
from abc import ABC, abstractmethod
from domain.entities.prompt_config import PromptConfig


class IPromptConfigRepository(ABC):
    @abstractmethod
    def get_prompt_config(self) -> PromptConfig:
        ...
```

- [ ] **Step 3: コミット**

```bash
git add backend/src/domain/entities/prompt_config.py backend/src/domain/repositories/prompt_config_repository.py
git commit -m "feat: add PromptConfig entity and IPromptConfigRepository interface"
```

---

### Task 11: YamlPromptConfigRepository を実装

**Files:**
- Create: `backend/src/infrastructure/persistence/yaml_prompt_config_repository.py`
- Create: `backend/tests/test_yaml_prompt_config_repository.py`

- [ ] **Step 1: テストファイルを作成する**

`backend/tests/test_yaml_prompt_config_repository.py` を新規作成する：

```python
import pytest
from pathlib import Path
from infrastructure.persistence.yaml_prompt_config_repository import YamlPromptConfigRepository


def test_get_prompt_config_loads_system_and_user_prompt(tmp_path):
    config_file = tmp_path / "prompts.yaml"
    config_file.write_text(
        "system_prompt: 'システムプロンプト'\n"
        "user_prompt_template: 'ユーザー {opponent_party}'\n",
        encoding="utf-8",
    )
    repo = YamlPromptConfigRepository(config_path=config_file)
    config = repo.get_prompt_config()

    assert config.system_prompt == "システムプロンプト"
    assert config.user_prompt_template == "ユーザー {opponent_party}"


def test_get_prompt_config_reloads_on_each_call(tmp_path):
    config_file = tmp_path / "prompts.yaml"
    config_file.write_text(
        "system_prompt: '初期'\nuser_prompt_template: 'template'\n",
        encoding="utf-8",
    )
    repo = YamlPromptConfigRepository(config_path=config_file)
    assert repo.get_prompt_config().system_prompt == "初期"

    config_file.write_text(
        "system_prompt: '更新後'\nuser_prompt_template: 'template'\n",
        encoding="utf-8",
    )
    assert repo.get_prompt_config().system_prompt == "更新後"


def test_get_prompt_config_raises_when_file_missing(tmp_path):
    repo = YamlPromptConfigRepository(config_path=tmp_path / "missing.yaml")
    with pytest.raises(FileNotFoundError):
        repo.get_prompt_config()
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
docker compose run --rm backend pytest tests/test_yaml_prompt_config_repository.py -v
```

Expected: FAIL（モジュールが存在しない）

- [ ] **Step 3: YamlPromptConfigRepository を実装する**

`backend/src/infrastructure/persistence/yaml_prompt_config_repository.py` を新規作成する：

```python
from pathlib import Path
import yaml
from domain.entities.prompt_config import PromptConfig
from domain.repositories.prompt_config_repository import IPromptConfigRepository


class YamlPromptConfigRepository(IPromptConfigRepository):
    def __init__(self, config_path: Path | str):
        self._config_path = Path(config_path)

    def get_prompt_config(self) -> PromptConfig:
        if not self._config_path.exists():
            raise FileNotFoundError(
                f"プロンプト設定ファイルが見つかりません: {self._config_path}"
            )
        with self._config_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return PromptConfig(
            system_prompt=data["system_prompt"],
            user_prompt_template=data["user_prompt_template"],
        )
```

- [ ] **Step 4: テストが通ることを確認する**

```bash
docker compose run --rm backend pytest tests/test_yaml_prompt_config_repository.py -v
```

Expected: PASS

- [ ] **Step 5: コミット**

```bash
git add backend/src/infrastructure/persistence/yaml_prompt_config_repository.py backend/tests/test_yaml_prompt_config_repository.py
git commit -m "feat: implement YamlPromptConfigRepository"
```

---

### Task 12: prompts.yaml を作成

**Files:**
- Create: `backend/config/prompts.yaml`

- [ ] **Step 1: config ディレクトリと prompts.yaml を作成する**

```bash
mkdir -p backend/config
```

`backend/config/prompts.yaml` を新規作成する（現行の `predict_use_case.py` のプロンプトをそのまま移植）：

```yaml
system_prompt: |
  あなたはポケモンチャンピオンズの対戦分析AIです。
  与えられた情報をもとに、相手プレイヤーが選出しそうなポケモン3体のパターンを3つ予想してください。

  回答は必ず以下の形式で出力してください：
  パターン1: ポケモン名A, ポケモン名B, ポケモン名C
  パターン2: ポケモン名D, ポケモン名E, ポケモン名F
  パターン3: ポケモン名G, ポケモン名H, ポケモン名I

  可能性が高い順に並べてください。確率の数値は不要です。

user_prompt_template: |
  【相手パーティ（6体）】
  {opponent_party}

  【自分のパーティ（6体）】
  {my_party}

  【相手パーティの使用率データ】
  {usage_text}

  シングルバトル3体選出です。相手が選出しそうな3体のパターンを3つ予想してください。
```

- [ ] **Step 2: コミット**

```bash
git add backend/config/prompts.yaml
git commit -m "feat: add prompts.yaml with system and user prompt templates"
```

---

### Task 13: PredictUseCase を IPromptConfigRepository に対応させる

**Files:**
- Modify: `backend/src/application/use_cases/predict_use_case.py`
- Modify: `backend/src/presentation/routers/prediction.py`
- Modify: `backend/tests/test_predict_use_case.py`

- [ ] **Step 1: テストを更新する**

`backend/tests/test_predict_use_case.py` を以下に書き換える：

```python
from unittest.mock import MagicMock
from application.use_cases.predict_use_case import PredictUseCase
from domain.entities.pokemon import UsageData, UsageEntry, RatedItem, EvSpread
from domain.entities.party import PredictionResult
from domain.entities.prompt_config import PromptConfig
from domain.repositories.llm_client import ILLMClient


MOCK_LLM_RESPONSE = """
パターン1: リザードン, カメックス, フシギバナ
パターン2: ピカチュウ, リザードン, イワーク
パターン3: フシギバナ, カメックス, ゲンガー
"""

MOCK_PROMPT_CONFIG = PromptConfig(
    system_prompt="テスト用システムプロンプト",
    user_prompt_template=(
        "相手: {opponent_party}\n"
        "自分: {my_party}\n"
        "データ: {usage_text}"
    ),
)


def _make_usage_data() -> UsageData:
    entry = UsageEntry(
        name="リザードン",
        moves=[RatedItem(name="かえんほうしゃ", rate=78)],
        items=[RatedItem(name="いのちのたま", rate=61)],
        abilities=[RatedItem(name="もうか", rate=82)],
        natures=[RatedItem(name="ひかえめ", rate=67)],
        teammates=[],
        evs=[EvSpread(spread={"H": 0, "A": 0, "B": 0, "C": 252, "D": 4, "S": 252}, rate=52)],
    )
    return UsageData(
        collected_at="2026-04-27T12:00:00",
        season=1,
        regulation="レギュレーションA",
        source_updated_at="2026-04-26",
        pokemons=[entry],
    )


def _make_mock_client(response: str = MOCK_LLM_RESPONSE) -> ILLMClient:
    mock = MagicMock(spec=ILLMClient)
    mock.generate.return_value = response
    return mock


def _make_mock_prompt_repo() -> MagicMock:
    mock = MagicMock()
    mock.get_prompt_config.return_value = MOCK_PROMPT_CONFIG
    return mock


def test_predict_returns_three_patterns():
    use_case = PredictUseCase(
        llm_client=_make_mock_client(),
        prompt_config_repository=_make_mock_prompt_repo(),
    )
    result = use_case.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )
    assert isinstance(result, PredictionResult)
    assert len(result.patterns) == 3
    assert len(result.patterns[0].pokemons) == 3
    assert result.patterns[0].pokemons[0] == "リザードン"


def test_predict_uses_system_prompt_from_repository():
    mock_client = _make_mock_client()
    use_case = PredictUseCase(
        llm_client=mock_client,
        prompt_config_repository=_make_mock_prompt_repo(),
    )
    use_case.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )
    mock_client.generate.assert_called_once()
    system, user = mock_client.generate.call_args[0]
    assert system == "テスト用システムプロンプト"
    assert "リザードン" in user
    assert "カビゴン" in user


def test_predict_loads_prompt_from_repository_each_call():
    mock_prompt_repo = _make_mock_prompt_repo()
    use_case = PredictUseCase(
        llm_client=_make_mock_client(),
        prompt_config_repository=mock_prompt_repo,
    )
    use_case.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )
    mock_prompt_repo.get_prompt_config.assert_called_once()
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
docker compose run --rm backend pytest tests/test_predict_use_case.py -v
```

Expected: FAIL（`PredictUseCase` が `prompt_config_repository` を受け付けない）

- [ ] **Step 3: PredictUseCase を書き換える**

`backend/src/application/use_cases/predict_use_case.py` を以下に書き換える：

```python
import re
from domain.entities.pokemon import UsageData
from domain.entities.party import PredictionResult, PredictionPattern
from domain.repositories.llm_client import ILLMClient
from domain.repositories.prompt_config_repository import IPromptConfigRepository


class PredictUseCase:
    def __init__(
        self,
        llm_client: ILLMClient,
        prompt_config_repository: IPromptConfigRepository,
    ) -> None:
        self._client = llm_client
        self._prompt_config_repository = prompt_config_repository

    def predict(
        self,
        opponent_party: list[str],
        my_party: list[str],
        usage_data: UsageData,
    ) -> PredictionResult:
        config = self._prompt_config_repository.get_prompt_config()
        prompt = self._build_prompt(
            opponent_party, my_party, usage_data, config.user_prompt_template
        )
        text = self._client.generate(config.system_prompt, prompt)
        return self._parse_response(text)

    def _build_prompt(
        self,
        opponent_party: list[str],
        my_party: list[str],
        usage_data: UsageData,
        user_prompt_template: str,
    ) -> str:
        usage_summary = []
        for entry in usage_data.pokemons:
            if entry.name in opponent_party:
                top_moves = ", ".join(f"{m.name}({m.rate}%)" for m in entry.moves[:3])
                top_items = ", ".join(f"{i.name}({i.rate}%)" for i in entry.items[:2])
                usage_summary.append(f"- {entry.name}: わざ[{top_moves}] 持ち物[{top_items}]")

        usage_text = "\n".join(usage_summary) if usage_summary else "使用率データなし"

        return user_prompt_template.format(
            opponent_party=", ".join(opponent_party),
            my_party=", ".join(my_party),
            usage_text=usage_text,
        )

    def _parse_response(self, text: str) -> PredictionResult:
        patterns = []
        for line in text.strip().splitlines():
            m = re.match(r"パターン\d+[:：]\s*(.+)", line)
            if m:
                names = [n.strip() for n in m.group(1).split(",")][:3]
                while len(names) < 3:
                    names.append("")
                patterns.append(PredictionPattern(pokemons=names))
        while len(patterns) < 3:
            patterns.append(PredictionPattern(pokemons=["", "", ""]))
        return PredictionResult(patterns=patterns[:3])
```

- [ ] **Step 4: prediction.py ルーターを更新する**

`backend/src/presentation/routers/prediction.py` の import 末尾に追加する：

```python
from pathlib import Path
from infrastructure.persistence.yaml_prompt_config_repository import YamlPromptConfigRepository
```

モジュールレベルの定数（`_llm_config_repo` の直後）に追加する：

```python
_prompts_config_path = Path(__file__).parent.parent.parent.parent / "config" / "prompts.yaml"
_prompt_config_repo = YamlPromptConfigRepository(config_path=_prompts_config_path)
```

`predict` 関数内の `use_case` 初期化を以下に変更する：

```python
use_case = PredictUseCase(
    llm_client=llm_client,
    prompt_config_repository=_prompt_config_repo,
)
```

- [ ] **Step 5: テストが通ることを確認する**

```bash
docker compose run --rm backend pytest tests/test_predict_use_case.py tests/test_routers.py -v
```

Expected: PASS

- [ ] **Step 6: コミット**

```bash
git add backend/src/application/use_cases/predict_use_case.py \
        backend/src/presentation/routers/prediction.py \
        backend/tests/test_predict_use_case.py
git commit -m "feat: inject IPromptConfigRepository into PredictUseCase, load prompts from YAML"
```
