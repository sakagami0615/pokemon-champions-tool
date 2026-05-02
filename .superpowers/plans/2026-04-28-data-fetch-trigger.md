# データ取得トリガー機能 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** フロントエンドにデータ管理ページを新設し、GameWithスクレイピングの起動トリガーUI・スクレイピング状態の管理・使用データ日付の選択機能を追加する。

**Architecture:** バックエンドにスクレイピング進行状態と選択日付をインメモリで管理するモジュールを追加し、既存リポジトリに日付別アクセスメソッドを追加する。フロントエンドは「データ管理」タブと新規ページを追加し、ポーリングでスクレイピング状態を監視する。

**Tech Stack:** Python / FastAPI / Pydantic v2 (backend), React 18 / TypeScript / Tailwind CSS (frontend), Docker Compose (test execution)

---

## ファイル構成

### バックエンド

| 操作 | ファイル | 変更内容 |
|------|----------|----------|
| 変更 | `backend/src/domain/repositories/usage_repository.py` | `get_available_dates`, `get_usage_data_by_date` 抽象メソッドを追加 |
| 変更 | `backend/src/infrastructure/persistence/json_usage_repository.py` | 上記2メソッドを実装 |
| 新規 | `backend/src/presentation/routers/_data_state.py` | スクレイピング状態・選択日付のインメモリ状態管理 |
| 変更 | `backend/src/presentation/routers/data.py` | フラグ管理・新エンドポイント追加・`/pokemon/names` 変更 |
| 変更 | `backend/src/presentation/routers/prediction.py` | `selected_date` を参照してデータ取得 |
| 変更 | `backend/tests/test_json_usage_repository.py` | 新メソッドのテスト追加 |
| 変更 | `backend/tests/test_routers.py` | 新エンドポイントのテスト追加 |

### フロントエンド

| 操作 | ファイル | 変更内容 |
|------|----------|----------|
| 変更 | `frontend/src/infrastructure/api/dataApi.ts` | `getAvailableDates`, `selectDate` 関数追加 |
| 新規 | `frontend/src/application/hooks/useDataManagement.ts` | データ管理ページ用フック |
| 新規 | `frontend/src/presentation/pages/DataPage.tsx` | データ管理ページコンポーネント |
| 変更 | `frontend/src/App.tsx` | `Page` 型に `'data'` 追加・DataPage レンダリング |
| 変更 | `frontend/src/presentation/components/Header.tsx` | 「データ管理」タブを追加 |

---

## Task 1: リポジトリインターフェースに日付別メソッドを追加

**Files:**
- Modify: `backend/src/domain/repositories/usage_repository.py`

- [ ] **Step 1: テストを書く**

`backend/tests/test_json_usage_repository.py` の末尾に以下を追加する：

```python
def test_get_available_dates_empty(repo):
    assert repo.get_available_dates() == []


def test_get_available_dates_returns_sorted_desc(repo):
    old = _make_usage_data().model_copy(update={"collected_at": "2026-04-25T00:00:00"})
    new = _make_usage_data()  # collected_at="2026-04-27T00:00:00"
    repo.save_usage_data(old)
    repo.save_usage_data(new)
    dates = repo.get_available_dates()
    assert dates == ["2026-04-27", "2026-04-25"]


def test_get_usage_data_by_date_returns_none_for_missing(repo):
    assert repo.get_usage_data_by_date("2026-04-27") is None


def test_get_usage_data_by_date_returns_correct_data(repo):
    data = _make_usage_data()  # collected_at="2026-04-27T00:00:00"
    repo.save_usage_data(data)
    loaded = repo.get_usage_data_by_date("2026-04-27")
    assert loaded is not None
    assert loaded.pokemon[0].name == "リザードン"
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
docker compose run --rm backend pytest tests/test_json_usage_repository.py::test_get_available_dates_empty -v
```

期待出力: `FAILED` （`get_available_dates` が未定義のため）

- [ ] **Step 3: インターフェースにメソッドを追加**

`backend/src/domain/repositories/usage_repository.py` を以下に書き換える：

```python
from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.pokemon import UsageData, PokemonList


class IUsageRepository(ABC):
    @abstractmethod
    def get_usage_data(self) -> Optional[UsageData]: ...

    @abstractmethod
    def save_usage_data(self, data: UsageData) -> None: ...

    @abstractmethod
    def get_pokemon_list(self) -> Optional[PokemonList]: ...

    @abstractmethod
    def save_pokemon_list(self, data: PokemonList) -> None: ...

    @abstractmethod
    def get_available_dates(self) -> list[str]: ...

    @abstractmethod
    def get_usage_data_by_date(self, date: str) -> Optional[UsageData]: ...
```

- [ ] **Step 4: JsonUsageRepository に実装を追加**

`backend/src/infrastructure/persistence/json_usage_repository.py` を以下に書き換える：

```python
from pathlib import Path
from typing import Optional
from domain.entities.pokemon import UsageData, PokemonList
from domain.repositories.usage_repository import IUsageRepository


class JsonUsageRepository(IUsageRepository):
    def __init__(self, data_dir: Path | str = Path(__file__).parent.parent.parent.parent / "data"):
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        (self._data_dir / "usage_rates").mkdir(exist_ok=True)

    def get_usage_data(self) -> Optional[UsageData]:
        rate_dir = self._data_dir / "usage_rates"
        files = sorted(rate_dir.glob("*.json"), reverse=True)
        if not files:
            return None
        return UsageData.model_validate_json(files[0].read_text(encoding="utf-8"))

    def save_usage_data(self, data: UsageData) -> None:
        date_str = data.collected_at[:10]
        path = self._data_dir / "usage_rates" / f"{date_str}.json"
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    def get_pokemon_list(self) -> Optional[PokemonList]:
        path = self._data_dir / "pokemon_list.json"
        if not path.exists():
            return None
        return PokemonList.model_validate_json(path.read_text(encoding="utf-8"))

    def save_pokemon_list(self, data: PokemonList) -> None:
        path = self._data_dir / "pokemon_list.json"
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    def get_available_dates(self) -> list[str]:
        rate_dir = self._data_dir / "usage_rates"
        files = sorted(rate_dir.glob("*.json"), reverse=True)
        return [f.stem for f in files]

    def get_usage_data_by_date(self, date: str) -> Optional[UsageData]:
        path = self._data_dir / "usage_rates" / f"{date}.json"
        if not path.exists():
            return None
        return UsageData.model_validate_json(path.read_text(encoding="utf-8"))
```

- [ ] **Step 5: テストがパスすることを確認**

```bash
docker compose run --rm backend pytest tests/test_json_usage_repository.py -v
```

期待出力: 全テスト `PASSED`

- [ ] **Step 6: コミット**

```bash
git add backend/src/domain/repositories/usage_repository.py \
        backend/src/infrastructure/persistence/json_usage_repository.py \
        backend/tests/test_json_usage_repository.py
git commit -m "feat: リポジトリに日付別アクセスメソッドを追加"
```

---

## Task 2: インメモリ状態管理モジュールを作成

**Files:**
- Create: `backend/src/presentation/routers/_data_state.py`

- [ ] **Step 1: 状態モジュールを作成**

`backend/src/presentation/routers/_data_state.py` を以下の内容で新規作成する：

```python
scraping_in_progress: bool = False
selected_date: str | None = None
```

- [ ] **Step 2: コミット**

```bash
git add backend/src/presentation/routers/_data_state.py
git commit -m "feat: スクレイピング状態管理モジュールを追加"
```

---

## Task 3: data.py ルーターを更新

**Files:**
- Modify: `backend/src/presentation/routers/data.py`
- Modify: `backend/tests/test_routers.py`

- [ ] **Step 1: 新エンドポイントのテストを書く**

`backend/tests/test_routers.py` の末尾に以下を追加する：

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
    assert isinstance(data["available_dates"], list)


@pytest.mark.asyncio
async def test_get_dates_returns_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/data/dates")
    assert resp.status_code == 200
    assert "dates" in resp.json()
    assert isinstance(resp.json()["dates"], list)


@pytest.mark.asyncio
async def test_select_date_sets_and_returns_date():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/data/select-date", json={"date": "2026-04-27"})
    assert resp.status_code == 200
    assert resp.json()["selected_date"] == "2026-04-27"


@pytest.mark.asyncio
async def test_select_date_validates_format():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/data/select-date", json={"date": "not-a-date"})
    assert resp.status_code == 422


def test_do_fetch_sets_scraping_flag():
    import presentation.routers._data_state as state
    original = state.scraping_in_progress

    mock_scraper = MagicMock()
    mock_scraper.fetch_pokemon_list.return_value = []
    mock_scraper.fetch_usage_ranking.return_value = []

    with patch("presentation.routers.data.GameWithScraper", return_value=mock_scraper):
        with patch("presentation.routers.data._usage_repo"):
            from presentation.routers.data import _do_fetch
            _do_fetch()

    assert state.scraping_in_progress is False  # 完了後は False に戻る
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
docker compose run --rm backend pytest tests/test_routers.py::test_data_status_includes_scraping_fields -v
```

期待出力: `FAILED`

- [ ] **Step 3: data.py を更新**

`backend/src/presentation/routers/data.py` を以下に書き換える：

```python
import logging
import re
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks
from fastapi.exceptions import RequestValidationError
from pathlib import Path
from pydantic import BaseModel, field_validator
from infrastructure.external.scraper import GameWithScraper
from infrastructure.persistence.json_usage_repository import JsonUsageRepository
from domain.entities.pokemon import PokemonList, UsageData, UsageEntry, PokemonInfo, BaseStats
import presentation.routers._data_state as _state

router = APIRouter(prefix="/api/data", tags=["data"])
_usage_repo = JsonUsageRepository()
_sprites_dir = Path(__file__).parent.parent.parent.parent / "data" / "sprites"
_logger = logging.getLogger(__name__)


class SelectDateRequest(BaseModel):
    date: str

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            raise ValueError("date must be in YYYY-MM-DD format")
        return v


@router.post("/fetch")
def fetch_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(_do_fetch)
    return {"status": "started"}


def _do_fetch() -> None:
    _state.scraping_in_progress = True
    try:
        try:
            scraper = GameWithScraper(sprites_dir=_sprites_dir)
        except Exception:
            _logger.exception("GameWithScraper の初期化に失敗しました")
            return
        _fetch_and_save_pokemon_list(scraper)
        _fetch_and_save_usage_data(scraper)
    finally:
        _state.scraping_in_progress = False


def _fetch_and_save_pokemon_list(scraper: GameWithScraper) -> None:
    try:
        raw_list = scraper.fetch_pokemon_list()
        if not raw_list:
            _logger.warning("fetch_pokemon_list: 取得件数が0件でした。HTMLセレクタを確認してください。")
            return
        pokemon_infos = [_raw_to_pokemon_info(p) for p in raw_list if _is_valid_pokemon_info(p)]
        if not pokemon_infos:
            _logger.warning("fetch_pokemon_list: 有効なポケモン情報が取得できませんでした。")
            return
        pokemon_list = PokemonList(
            collected_at=datetime.now().isoformat(),
            pokemon=pokemon_infos,
        )
        _usage_repo.save_pokemon_list(pokemon_list)
        _logger.info("ポケモン一覧を保存しました: %d件", len(pokemon_infos))
    except Exception:
        _logger.exception("fetch_pokemon_list でエラーが発生しました")


def _fetch_and_save_usage_data(scraper: GameWithScraper) -> None:
    try:
        raw_usage = scraper.fetch_usage_ranking()
        if not raw_usage:
            _logger.warning("fetch_usage_ranking: 取得件数が0件でした。HTMLセレクタを確認してください。")
            return
        entries = [_raw_to_usage_entry(u) for u in raw_usage if _is_valid_usage_entry(u)]
        if not entries:
            _logger.warning("fetch_usage_ranking: 有効な使用率データが取得できませんでした。")
            return
        now = datetime.now().isoformat()
        usage_data = UsageData(
            collected_at=now,
            season=0,
            regulation="",
            source_updated_at=now,
            pokemon=entries,
        )
        _usage_repo.save_usage_data(usage_data)
        _logger.info("使用率データを保存しました: %d件", len(entries))
    except Exception:
        _logger.exception("fetch_usage_ranking でエラーが発生しました")


def _is_valid_pokemon_info(raw: dict) -> bool:
    return bool(raw.get("name")) and bool(raw.get("sprite_path"))


def _raw_to_pokemon_info(raw: dict) -> PokemonInfo:
    return PokemonInfo(
        pokedex_id=raw.get("pokedex_id", 0),
        name=raw["name"],
        types=raw.get("types", []),
        base_stats=BaseStats(
            hp=raw.get("hp", 0),
            attack=raw.get("attack", 0),
            defense=raw.get("defense", 0),
            sp_attack=raw.get("sp_attack", 0),
            sp_defense=raw.get("sp_defense", 0),
            speed=raw.get("speed", 0),
        ),
        height_m=raw.get("height_m", 0.0),
        weight_kg=raw.get("weight_kg", 0.0),
        low_kick_power=raw.get("low_kick_power", 0),
        abilities=raw.get("abilities", []),
        weaknesses=raw.get("weaknesses", []),
        resistances=raw.get("resistances", []),
        sprite_path=raw.get("sprite_path", ""),
    )


def _is_valid_usage_entry(raw: dict) -> bool:
    return bool(raw.get("name"))


def _raw_to_usage_entry(raw: dict) -> UsageEntry:
    return UsageEntry(
        name=raw["name"],
        moves=raw.get("moves", []),
        items=raw.get("items", []),
        abilities=raw.get("abilities", []),
        natures=raw.get("natures", []),
        teammates=raw.get("teammates", []),
        evs=raw.get("evs", []),
        ivs=raw.get("ivs"),
    )


@router.get("/status")
def data_status():
    pokemon_list = _usage_repo.get_pokemon_list()
    usage_data = _usage_repo.get_usage_data()
    available_dates = _usage_repo.get_available_dates()
    return {
        "pokemon_list_available": pokemon_list is not None,
        "usage_data_available": usage_data is not None,
        "usage_data_date": usage_data.collected_at if usage_data else None,
        "scraping_in_progress": _state.scraping_in_progress,
        "selected_date": _state.selected_date,
        "available_dates": available_dates,
    }


@router.get("/dates")
def get_dates():
    return {"dates": _usage_repo.get_available_dates()}


@router.post("/select-date")
def select_date(req: SelectDateRequest):
    _state.selected_date = req.date
    return {"selected_date": _state.selected_date}


@router.get("/pokemon/names")
def get_pokemon_names():
    if _state.selected_date:
        usage_data = _usage_repo.get_usage_data_by_date(_state.selected_date)
        if usage_data:
            return {"names": [p.name for p in usage_data.pokemon]}
    pokemon_list = _usage_repo.get_pokemon_list()
    if pokemon_list is None:
        return {"names": []}
    names = [p.name for p in pokemon_list.pokemon]
    for p in pokemon_list.pokemon:
        if p.mega_evolution:
            names.append(p.mega_evolution.name)
    return {"names": names}
```

- [ ] **Step 4: テストがパスすることを確認**

```bash
docker compose run --rm backend pytest tests/test_routers.py -v
```

期待出力: 全テスト `PASSED`

- [ ] **Step 5: コミット**

```bash
git add backend/src/presentation/routers/data.py \
        backend/tests/test_routers.py
git commit -m "feat: data ルーターにスクレイピング状態管理と日付選択エンドポイントを追加"
```

---

## Task 4: prediction.py で selected_date を参照

**Files:**
- Modify: `backend/src/presentation/routers/prediction.py`
- Modify: `backend/tests/test_routers.py`

- [ ] **Step 1: テストを追加**

`backend/tests/test_routers.py` の末尾に以下を追加する：

```python
@pytest.mark.asyncio
async def test_predict_uses_selected_date():
    import presentation.routers._data_state as state
    state.selected_date = "2026-04-27"

    with patch("presentation.routers.prediction._usage_repo") as mock_repo:
        mock_usage = MagicMock()
        mock_repo.get_usage_data_by_date.return_value = mock_usage
        mock_repo.get_usage_data.return_value = mock_usage

        with patch("presentation.routers.prediction.PredictUseCase") as mock_uc:
            mock_uc.return_value.predict.return_value = {"patterns": []}
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post("/api/predict", json={
                    "opponent_party": ["リザードン"] * 6,
                    "my_party": ["カメックス"] * 6,
                })

        mock_repo.get_usage_data_by_date.assert_called_once_with("2026-04-27")
        mock_repo.get_usage_data.assert_not_called()

    state.selected_date = None  # テスト後にリセット


@pytest.mark.asyncio
async def test_predict_uses_latest_when_no_date_selected():
    import presentation.routers._data_state as state
    state.selected_date = None

    with patch("presentation.routers.prediction._usage_repo") as mock_repo:
        mock_usage = MagicMock()
        mock_repo.get_usage_data.return_value = mock_usage

        with patch("presentation.routers.prediction.PredictUseCase") as mock_uc:
            mock_uc.return_value.predict.return_value = {"patterns": []}
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post("/api/predict", json={
                    "opponent_party": ["リザードン"] * 6,
                    "my_party": ["カメックス"] * 6,
                })

        mock_repo.get_usage_data.assert_called_once()
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
docker compose run --rm backend pytest tests/test_routers.py::test_predict_uses_selected_date -v
```

期待出力: `FAILED`

- [ ] **Step 3: prediction.py を更新**

`backend/src/presentation/routers/prediction.py` を以下に書き換える：

```python
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from application.use_cases.predict_use_case import PredictUseCase
from infrastructure.persistence.json_usage_repository import JsonUsageRepository
import presentation.routers._data_state as _state

router = APIRouter(prefix="/api", tags=["prediction"])
_usage_repo = JsonUsageRepository()


class PredictRequest(BaseModel):
    opponent_party: list[str]
    my_party: list[str]


@router.post("/predict")
def predict(req: PredictRequest):
    if _state.selected_date:
        usage_data = _usage_repo.get_usage_data_by_date(_state.selected_date)
    else:
        usage_data = _usage_repo.get_usage_data()

    if usage_data is None:
        raise HTTPException(status_code=400, detail="使用率データがありません。先にデータを取得してください。")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY が設定されていません。")

    use_case = PredictUseCase(api_key=api_key)
    return use_case.predict(
        opponent_party=req.opponent_party,
        my_party=req.my_party,
        usage_data=usage_data,
    )
```

- [ ] **Step 4: テストがパスすることを確認**

```bash
docker compose run --rm backend pytest tests/test_routers.py -v
```

期待出力: 全テスト `PASSED`

- [ ] **Step 5: バックエンド全テストを通す**

```bash
docker compose run --rm backend pytest -v
```

期待出力: 全テスト `PASSED`

- [ ] **Step 6: コミット**

```bash
git add backend/src/presentation/routers/prediction.py \
        backend/tests/test_routers.py
git commit -m "feat: 予測ルーターが selected_date のデータを使用するよう変更"
```

---

## Task 5: フロントエンド API 層を更新

**Files:**
- Modify: `frontend/src/infrastructure/api/dataApi.ts`

- [ ] **Step 1: dataApi.ts に新関数を追加**

`frontend/src/infrastructure/api/dataApi.ts` を以下に書き換える：

```typescript
const BASE = '/api'

export interface DataStatus {
  pokemon_list_available: boolean
  usage_data_available: boolean
  usage_data_date: string | null
  scraping_in_progress: boolean
  selected_date: string | null
  available_dates: string[]
}

export async function fetchData(): Promise<{ status: string }> {
  const res = await fetch(`${BASE}/data/fetch`, { method: 'POST' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getDataStatus(): Promise<DataStatus> {
  const res = await fetch(`${BASE}/data/status`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getAvailableDates(): Promise<string[]> {
  const res = await fetch(`${BASE}/data/dates`)
  if (!res.ok) throw new Error(await res.text())
  const data = await res.json()
  return data.dates as string[]
}

export async function selectDate(date: string): Promise<{ selected_date: string }> {
  const res = await fetch(`${BASE}/data/select-date`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ date }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getPokemonNames(): Promise<string[]> {
  const res = await fetch(`${BASE}/data/pokemon/names`)
  if (!res.ok) throw new Error(await res.text())
  const data = await res.json()
  return data.names as string[]
}
```

- [ ] **Step 2: コミット**

```bash
git add frontend/src/infrastructure/api/dataApi.ts
git commit -m "feat: dataApi に getAvailableDates・selectDate 関数を追加"
```

---

## Task 6: useDataManagement フックを作成

**Files:**
- Create: `frontend/src/application/hooks/useDataManagement.ts`

- [ ] **Step 1: フックを作成**

`frontend/src/application/hooks/useDataManagement.ts` を以下の内容で新規作成する：

```typescript
import { useState, useEffect, useRef, useCallback } from 'react'
import { fetchData, getDataStatus, selectDate, DataStatus } from '../../infrastructure/api/dataApi'

interface UseDataManagementReturn {
  status: DataStatus | null
  isFetching: boolean
  fetchMessage: string | null
  error: string | null
  triggerFetch: () => Promise<void>
  handleSelectDate: (date: string) => Promise<void>
}

export function useDataManagement(): UseDataManagementReturn {
  const [status, setStatus] = useState<DataStatus | null>(null)
  const [isFetching, setIsFetching] = useState(false)
  const [fetchMessage, setFetchMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const loadStatus = useCallback(async () => {
    try {
      const s = await getDataStatus()
      setStatus(s)
    } catch {
      // ポーリング失敗は無視して次回に再試行
    }
  }, [])

  useEffect(() => {
    loadStatus()
  }, [loadStatus])

  useEffect(() => {
    if (status?.scraping_in_progress) {
      pollingRef.current = setInterval(loadStatus, 3000)
    } else {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
  }, [status?.scraping_in_progress, loadStatus])

  const triggerFetch = useCallback(async () => {
    setIsFetching(true)
    setError(null)
    setFetchMessage(null)
    try {
      await fetchData()
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
    } catch (e) {
      setStatus((prev) => prev ? { ...prev, selected_date: previous } : prev)
      setError(e instanceof Error ? e.message : '日付の選択に失敗しました')
    }
  }, [status?.selected_date])

  return { status, isFetching, fetchMessage, error, triggerFetch, handleSelectDate }
}
```

- [ ] **Step 2: コミット**

```bash
git add frontend/src/application/hooks/useDataManagement.ts
git commit -m "feat: useDataManagement フックを追加"
```

---

## Task 7: DataPage コンポーネントを作成

**Files:**
- Create: `frontend/src/presentation/pages/DataPage.tsx`

- [ ] **Step 1: DataPage を作成**

`frontend/src/presentation/pages/DataPage.tsx` を以下の内容で新規作成する：

```typescript
import { useDataManagement } from '../../application/hooks/useDataManagement'

export default function DataPage() {
  const { status, isFetching, fetchMessage, error, triggerFetch, handleSelectDate } = useDataManagement()

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-xl font-bold">データ管理</h1>

      <section className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-2">
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400">データ取得状況</h2>
        {status === null ? (
          <p className="text-sm text-gray-500">読み込み中...</p>
        ) : (
          <>
            <p className="text-sm">
              ポケモン一覧：
              <span className={status.pokemon_list_available ? 'text-green-600' : 'text-red-500'}>
                {status.pokemon_list_available ? '取得済み' : '未取得'}
              </span>
            </p>
            <p className="text-sm">
              使用率データ：
              <span className={status.usage_data_available ? 'text-green-600' : 'text-red-500'}>
                {status.usage_data_available
                  ? `取得済み（${status.usage_data_date?.slice(0, 10) ?? ''}）`
                  : '未取得'}
              </span>
            </p>
            {status.scraping_in_progress && (
              <p className="text-sm text-yellow-500 animate-pulse">スクレイピング実行中...</p>
            )}
          </>
        )}
      </section>

      <section className="space-y-2">
        <button
          onClick={triggerFetch}
          disabled={isFetching}
          className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
        >
          {isFetching ? '開始中...' : 'データ取得'}
        </button>
        {fetchMessage && <p className="text-sm text-green-600">{fetchMessage}</p>}
        {error && <p className="text-sm text-red-500">{error}</p>}
      </section>

      {status && status.available_dates.length > 0 && (
        <section className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-2">
          <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400">使用するデータを選択</h2>
          <select
            value={status.selected_date ?? ''}
            onChange={(e) => handleSelectDate(e.target.value)}
            className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-800 text-sm"
          >
            <option value="" disabled>日付を選択してください</option>
            {status.available_dates.map((date) => (
              <option key={date} value={date}>{date}</option>
            ))}
          </select>
          {status.selected_date && (
            <p className="text-sm text-gray-500">
              選択中：{status.selected_date}
            </p>
          )}
        </section>
      )}
    </div>
  )
}
```

- [ ] **Step 2: コミット**

```bash
git add frontend/src/presentation/pages/DataPage.tsx
git commit -m "feat: DataPage コンポーネントを追加"
```

---

## Task 8: App.tsx と Header.tsx にデータ管理タブを追加

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/presentation/components/Header.tsx`

- [ ] **Step 1: App.tsx を更新**

`frontend/src/App.tsx` を以下に書き換える：

```typescript
import { useState } from 'react'
import { useDarkMode } from './presentation/hooks/useDarkMode'
import PredictionPage from './presentation/pages/PredictionPage'
import PartyPage from './presentation/pages/PartyPage'
import DataPage from './presentation/pages/DataPage'
import Header from './presentation/components/Header'

type Page = 'prediction' | 'party' | 'data'

export default function App() {
  const { dark, toggle } = useDarkMode()
  const [page, setPage] = useState<Page>('prediction')

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <Header dark={dark} onToggleDark={toggle} page={page} onChangePage={setPage} />
      <main className="p-4">
        {page === 'prediction' && <PredictionPage />}
        {page === 'party' && <PartyPage />}
        {page === 'data' && <DataPage />}
      </main>
    </div>
  )
}
```

- [ ] **Step 2: Header.tsx を更新**

`frontend/src/presentation/components/Header.tsx` を以下に書き換える：

```typescript
import DarkModeToggle from './DarkModeToggle'

interface Props {
  dark: boolean
  onToggleDark: () => void
  page: 'prediction' | 'party' | 'data'
  onChangePage: (p: 'prediction' | 'party' | 'data') => void
}

export default function Header({ dark, onToggleDark, page, onChangePage }: Props) {
  return (
    <header className="border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <span className="font-bold text-lg">Pokemon Champions Tool</span>
        <nav className="flex gap-2">
          <button
            onClick={() => onChangePage('prediction')}
            className={`px-3 py-1 rounded text-sm ${page === 'prediction' ? 'bg-indigo-600 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            選出予想
          </button>
          <button
            onClick={() => onChangePage('party')}
            className={`px-3 py-1 rounded text-sm ${page === 'party' ? 'bg-indigo-600 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            パーティ登録
          </button>
          <button
            onClick={() => onChangePage('data')}
            className={`px-3 py-1 rounded text-sm ${page === 'data' ? 'bg-indigo-600 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}`}
          >
            データ管理
          </button>
        </nav>
      </div>
      <DarkModeToggle dark={dark} onToggle={onToggleDark} />
    </header>
  )
}
```

- [ ] **Step 3: バックエンド全テストを最終確認**

```bash
docker compose run --rm backend pytest -v
```

期待出力: 全テスト `PASSED`

- [ ] **Step 4: コミット**

```bash
git add frontend/src/App.tsx \
        frontend/src/presentation/components/Header.tsx
git commit -m "feat: ヘッダーとルーティングにデータ管理ページを追加"
```
