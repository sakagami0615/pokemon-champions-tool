# クリーンアーキテクチャ整合リファクタリング 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** バックエンドとフロントエンドのフォルダ構成をクリーンアーキテクチャに統一し、各レイヤーの責務を明確に分離する。

**Architecture:** バックエンドは `domain/`・`application/`・`infrastructure/`・`presentation/` の4層構成に再編し、リポジトリインターフェースでインフラの詳細を抽象化する。フロントエンドは既存の `domain/`・`infrastructure/`・`presentation/` に加えて `application/hooks/` 層を追加し、ページコンポーネントをUI専用にする。

**Tech Stack:** Python 3.11 / FastAPI / Pydantic v2 / pytest / TypeScript / React / Vite / Tailwind CSS / Docker Compose

---

## ファイルマップ

### 作成するファイル（バックエンド）

| 新パス | 旧パス | 内容 |
|--------|--------|------|
| `backend/src/domain/entities/party.py` | `src/models/party.py` | Party, PartiesData, PredictionResult, PredictionPattern |
| `backend/src/domain/entities/pokemon.py` | `src/models/pokemon.py` | UsageData, PokemonList 等 |
| `backend/src/domain/repositories/party_repository.py` | なし（新規） | IPartyRepository (ABC) |
| `backend/src/domain/repositories/usage_repository.py` | なし（新規） | IUsageRepository (ABC) |
| `backend/src/infrastructure/persistence/json_party_repository.py` | `src/services/data_manager.py`（分割） | parties.json の読み書き |
| `backend/src/infrastructure/persistence/json_usage_repository.py` | `src/services/data_manager.py`（分割） | pokemon_list.json / usage_rates/ の読み書き |
| `backend/src/infrastructure/external/scraper.py` | `src/services/scraper.py` | Web スクレイピング |
| `backend/src/infrastructure/external/image_recognition.py` | `src/services/image_recognition.py` | テンプレートマッチング |
| `backend/src/application/use_cases/predict_use_case.py` | `src/services/ai_predictor.py` | Claude API 呼び出し |
| `backend/src/application/use_cases/recognition_use_case.py` | なし（新規） | ImageRecognizer のラッパー |
| `backend/src/presentation/routers/party.py` | `src/routers/party.py` | /api/party エンドポイント |
| `backend/src/presentation/routers/prediction.py` | `src/routers/prediction.py` | /api/predict エンドポイント |
| `backend/src/presentation/routers/recognition.py` | `src/routers/recognition.py` | /api/recognize エンドポイント |
| `backend/src/presentation/routers/data.py` | `src/routers/data.py` | /api/data エンドポイント |
| `backend/tests/conftest.py` | `src/tests/conftest.py` | テストフィクスチャ（import パス更新） |
| `backend/tests/test_json_party_repository.py` | なし（新規） | JsonPartyRepository のユニットテスト |
| `backend/tests/test_json_usage_repository.py` | なし（新規） | JsonUsageRepository のユニットテスト |
| `backend/tests/test_predict_use_case.py` | `src/tests/test_ai_predictor.py` | import パス更新 |
| `backend/tests/test_image_recognition.py` | `src/tests/test_image_recognition.py` | import パス更新 |
| `backend/tests/test_models.py` | `src/tests/test_models.py` | import パス更新 |
| `backend/tests/test_routers.py` | `src/tests/test_routers.py` | import パス更新 |
| `backend/tests/test_scraper.py` | `src/tests/test_scraper.py` | import パス更新 |

### 削除するファイル（バックエンド）

- `backend/src/models/` ディレクトリ全体
- `backend/src/services/` ディレクトリ全体
- `backend/src/routers/` ディレクトリ全体
- `backend/src/tests/` ディレクトリ全体

### 作成・更新するファイル（フロントエンド）

| パス | 内容 |
|------|------|
| `frontend/src/domain/entities/party.ts` | Party, PartiesData |
| `frontend/src/domain/entities/prediction.ts` | PredictionPattern, PredictionResult |
| `frontend/src/domain/entities/pokemon.ts` | RatedItem, EvSpread, UsageEntry |
| `frontend/src/infrastructure/api/partyApi.ts` | /api/party 系 |
| `frontend/src/infrastructure/api/predictionApi.ts` | /api/predict |
| `frontend/src/infrastructure/api/recognitionApi.ts` | /api/recognize |
| `frontend/src/infrastructure/api/dataApi.ts` | /api/data 系 |
| `frontend/src/application/hooks/useParty.ts` | パーティ状態管理 |
| `frontend/src/application/hooks/usePredict.ts` | 予想状態管理 |
| `frontend/src/application/hooks/usePokemonData.ts` | ポケモン名一覧取得 |
| `frontend/src/presentation/pages/PredictionPage.tsx` | UIのみ（フック呼び出し） |
| `frontend/src/presentation/pages/PartyPage.tsx` | UIのみ（フック呼び出し） |

### 削除するファイル（フロントエンド）

- `frontend/src/domain/entities/index.ts`
- `frontend/src/infrastructure/api/client.ts`
- `frontend/src/App.css`

---

## Task 1: バックエンド - domain/entities/ 作成

**Files:**
- Create: `backend/src/domain/__init__.py`
- Create: `backend/src/domain/entities/__init__.py`
- Create: `backend/src/domain/entities/party.py`
- Create: `backend/src/domain/entities/pokemon.py`

- [ ] **Step 1: ディレクトリと __init__.py を作成**

```bash
mkdir -p backend/src/domain/entities
touch backend/src/domain/__init__.py
touch backend/src/domain/entities/__init__.py
```

- [ ] **Step 2: domain/entities/party.py を作成**

`backend/src/domain/entities/party.py`:

```python
from typing import Optional
from pydantic import BaseModel


class Party(BaseModel):
    id: str
    name: str
    pokemon: list[str]


class PartiesData(BaseModel):
    parties: list[Party]
    last_used_id: Optional[str] = None


class PredictionPattern(BaseModel):
    pokemon: list[str]


class PredictionResult(BaseModel):
    patterns: list[PredictionPattern]
```

- [ ] **Step 3: domain/entities/pokemon.py を作成**

`backend/src/domain/entities/pokemon.py`:

```python
from pydantic import BaseModel
from typing import Optional


class BaseStats(BaseModel):
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int


class RatedItem(BaseModel):
    name: str
    rate: float


class EvSpread(BaseModel):
    spread: dict[str, int]
    rate: float


class MegaEvolution(BaseModel):
    name: str
    types: list[str]
    base_stats: BaseStats
    abilities: list[str]
    weaknesses: list[str]
    resistances: list[str]
    sprite_path: str


class PokemonInfo(BaseModel):
    pokedex_id: int
    name: str
    types: list[str]
    base_stats: BaseStats
    height_m: float
    weight_kg: float
    low_kick_power: int
    abilities: list[str]
    weaknesses: list[str]
    resistances: list[str]
    sprite_path: str
    mega_evolution: Optional[MegaEvolution] = None


class UsageEntry(BaseModel):
    name: str
    moves: list[RatedItem]
    items: list[RatedItem]
    abilities: list[RatedItem]
    natures: list[RatedItem]
    teammates: list[RatedItem]
    evs: list[EvSpread]
    ivs: Optional[dict[str, int]] = None


class UsageData(BaseModel):
    collected_at: str
    season: int
    regulation: str
    source_updated_at: str
    pokemon: list[UsageEntry]


class PokemonList(BaseModel):
    collected_at: str
    pokemon: list[PokemonInfo]
```

- [ ] **Step 4: 既存テストがまだ通ることを確認（旧 models/ はまだ残っている）**

```bash
docker compose run --rm backend pytest src/tests/ -q
```

期待: 全テスト PASS

- [ ] **Step 5: コミット**

```bash
git add backend/src/domain/
git commit -m "refactor: domain/entities レイヤー作成"
```

---

## Task 2: バックエンド - domain/repositories/ 作成

**Files:**
- Create: `backend/src/domain/repositories/__init__.py`
- Create: `backend/src/domain/repositories/party_repository.py`
- Create: `backend/src/domain/repositories/usage_repository.py`

- [ ] **Step 1: ディレクトリを作成**

```bash
mkdir -p backend/src/domain/repositories
touch backend/src/domain/repositories/__init__.py
```

- [ ] **Step 2: party_repository.py を作成**

`backend/src/domain/repositories/party_repository.py`:

```python
from abc import ABC, abstractmethod
from domain.entities.party import PartiesData


class IPartyRepository(ABC):
    @abstractmethod
    def get_all(self) -> PartiesData: ...

    @abstractmethod
    def save(self, data: PartiesData) -> None: ...
```

- [ ] **Step 3: usage_repository.py を作成**

`backend/src/domain/repositories/usage_repository.py`:

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
```

- [ ] **Step 4: コミット**

```bash
git add backend/src/domain/repositories/
git commit -m "refactor: domain/repositories インターフェース追加"
```

---

## Task 3: バックエンド - infrastructure/persistence/ 作成（TDD）

**Files:**
- Create: `backend/src/infrastructure/__init__.py`
- Create: `backend/src/infrastructure/persistence/__init__.py`
- Create: `backend/src/infrastructure/persistence/json_party_repository.py`
- Create: `backend/src/infrastructure/persistence/json_usage_repository.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_json_party_repository.py`
- Create: `backend/tests/test_json_usage_repository.py`

- [ ] **Step 1: ディレクトリを作成**

```bash
mkdir -p backend/src/infrastructure/persistence
touch backend/src/infrastructure/__init__.py
touch backend/src/infrastructure/persistence/__init__.py
mkdir -p backend/tests
touch backend/tests/__init__.py
```

- [ ] **Step 2: test_json_party_repository.py を作成**

`backend/tests/test_json_party_repository.py`:

```python
import pytest
from pathlib import Path
from domain.entities.party import Party, PartiesData
from infrastructure.persistence.json_party_repository import JsonPartyRepository


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "sprites").mkdir()
    (tmp_path / "usage_rates").mkdir()
    return JsonPartyRepository(data_dir=tmp_path)


def test_get_all_returns_empty_when_no_file(repo):
    result = repo.get_all()
    assert result.parties == []
    assert result.last_used_id is None


def test_save_and_get_all(repo):
    data = PartiesData(
        parties=[Party(id="p1", name="テスト", pokemon=["リザードン", "カメックス"])],
        last_used_id="p1",
    )
    repo.save(data)
    loaded = repo.get_all()
    assert loaded.parties[0].name == "テスト"
    assert loaded.last_used_id == "p1"


def test_save_overwrites_existing(repo):
    data1 = PartiesData(parties=[Party(id="p1", name="最初", pokemon=[])])
    repo.save(data1)
    data2 = PartiesData(parties=[Party(id="p2", name="更新後", pokemon=[])])
    repo.save(data2)
    loaded = repo.get_all()
    assert len(loaded.parties) == 1
    assert loaded.parties[0].name == "更新後"
```

- [ ] **Step 3: テストが失敗することを確認**

```bash
docker compose run --rm backend pytest tests/test_json_party_repository.py -v
```

期待: `ImportError` または `ModuleNotFoundError` で FAIL

- [ ] **Step 4: json_party_repository.py を実装**

`backend/src/infrastructure/persistence/json_party_repository.py`:

```python
from pathlib import Path
from domain.entities.party import PartiesData
from domain.repositories.party_repository import IPartyRepository


class JsonPartyRepository(IPartyRepository):
    def __init__(self, data_dir: Path | str = Path(__file__).parent.parent.parent.parent / "data"):
        self._path = Path(data_dir) / "parties.json"

    def get_all(self) -> PartiesData:
        if not self._path.exists():
            return PartiesData(parties=[])
        return PartiesData.model_validate_json(self._path.read_text(encoding="utf-8"))

    def save(self, data: PartiesData) -> None:
        self._path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
```

- [ ] **Step 5: テストが通ることを確認**

```bash
docker compose run --rm backend pytest tests/test_json_party_repository.py -v
```

期待: 3 passed

- [ ] **Step 6: test_json_usage_repository.py を作成**

`backend/tests/test_json_usage_repository.py`:

```python
import pytest
from pathlib import Path
from domain.entities.pokemon import (
    PokemonList, PokemonInfo, BaseStats,
    UsageData, UsageEntry, RatedItem, EvSpread,
)
from infrastructure.persistence.json_usage_repository import JsonUsageRepository


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "usage_rates").mkdir()
    return JsonUsageRepository(data_dir=tmp_path)


def _make_pokemon_list():
    return PokemonList(
        collected_at="2026-04-27T00:00:00",
        pokemon=[
            PokemonInfo(
                pokedex_id=6, name="リザードン", types=["ほのお"],
                sprite_path="sprites/006.png",
                base_stats=BaseStats(hp=78, attack=84, defense=78,
                                     sp_attack=109, sp_defense=85, speed=100),
                height_m=1.7, weight_kg=90.5, low_kick_power=100,
                abilities=["もうか"], weaknesses=["いわ"], resistances=["くさ"],
            )
        ],
    )


def _make_usage_data():
    return UsageData(
        collected_at="2026-04-27T00:00:00",
        season=1,
        regulation="レギュレーションA",
        source_updated_at="2026-04-26",
        pokemon=[
            UsageEntry(
                name="リザードン",
                moves=[RatedItem(name="かえんほうしゃ", rate=78)],
                items=[RatedItem(name="いのちのたま", rate=61)],
                abilities=[RatedItem(name="もうか", rate=82)],
                natures=[RatedItem(name="ひかえめ", rate=67)],
                teammates=[],
                evs=[EvSpread(spread={"C": 252, "S": 252, "H": 0, "A": 0, "B": 0, "D": 4}, rate=52)],
            )
        ],
    )


def test_get_pokemon_list_returns_none_when_missing(repo):
    assert repo.get_pokemon_list() is None


def test_save_and_get_pokemon_list(repo):
    repo.save_pokemon_list(_make_pokemon_list())
    loaded = repo.get_pokemon_list()
    assert loaded.pokemon[0].name == "リザードン"


def test_get_usage_data_returns_none_when_missing(repo):
    assert repo.get_usage_data() is None


def test_save_and_get_usage_data(repo):
    repo.save_usage_data(_make_usage_data())
    loaded = repo.get_usage_data()
    assert loaded.pokemon[0].name == "リザードン"
    assert loaded.season == 1


def test_get_usage_data_returns_latest(repo):
    data1 = _make_usage_data()
    data1_copy = data1.model_copy(update={"collected_at": "2026-04-25T00:00:00"})
    data2 = _make_usage_data()
    repo.save_usage_data(data1_copy)
    repo.save_usage_data(data2)
    loaded = repo.get_usage_data()
    assert loaded is not None
```

- [ ] **Step 7: テストが失敗することを確認**

```bash
docker compose run --rm backend pytest tests/test_json_usage_repository.py -v
```

期待: `ImportError` で FAIL

- [ ] **Step 8: json_usage_repository.py を実装**

`backend/src/infrastructure/persistence/json_usage_repository.py`:

```python
from datetime import datetime
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
        date_str = datetime.now().strftime("%Y-%m-%d")
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
```

- [ ] **Step 9: テストが通ることを確認**

```bash
docker compose run --rm backend pytest tests/test_json_usage_repository.py -v
```

期待: 5 passed

- [ ] **Step 10: コミット**

```bash
git add backend/src/infrastructure/ backend/tests/test_json_party_repository.py backend/tests/test_json_usage_repository.py
git commit -m "refactor: infrastructure/persistence レイヤー作成（TDD）"
```

---

## Task 4: バックエンド - infrastructure/external/ 作成

**Files:**
- Create: `backend/src/infrastructure/external/__init__.py`
- Create: `backend/src/infrastructure/external/scraper.py`
- Create: `backend/src/infrastructure/external/image_recognition.py`

- [ ] **Step 1: ディレクトリを作成**

```bash
mkdir -p backend/src/infrastructure/external
touch backend/src/infrastructure/external/__init__.py
```

- [ ] **Step 2: scraper.py をコピーして import パスを更新**

`backend/src/services/scraper.py` の内容を `backend/src/infrastructure/external/scraper.py` にコピーする。import パスは変更不要（外部ライブラリのみ使用）。

```bash
cp backend/src/services/scraper.py backend/src/infrastructure/external/scraper.py
```

- [ ] **Step 3: image_recognition.py をコピー**

import パスは変更不要（標準ライブラリ・opencv のみ使用）。

```bash
cp backend/src/services/image_recognition.py backend/src/infrastructure/external/image_recognition.py
```

- [ ] **Step 4: コミット**

```bash
git add backend/src/infrastructure/external/
git commit -m "refactor: infrastructure/external レイヤー作成"
```

---

## Task 5: バックエンド - application/use_cases/ 作成

**Files:**
- Create: `backend/src/application/__init__.py`
- Create: `backend/src/application/use_cases/__init__.py`
- Create: `backend/src/application/use_cases/predict_use_case.py`
- Create: `backend/src/application/use_cases/recognition_use_case.py`

- [ ] **Step 1: ディレクトリを作成**

```bash
mkdir -p backend/src/application/use_cases
touch backend/src/application/__init__.py
touch backend/src/application/use_cases/__init__.py
```

- [ ] **Step 2: predict_use_case.py を作成（ai_predictor.py から移植、import パス更新）**

`backend/src/application/use_cases/predict_use_case.py`:

```python
import re
import anthropic
from domain.entities.pokemon import UsageData
from domain.entities.party import PredictionResult, PredictionPattern

SYSTEM_PROMPT = """あなたはポケモンチャンピオンズの対戦分析AIです。
与えられた情報をもとに、相手プレイヤーが選出しそうなポケモン3体のパターンを3つ予想してください。

回答は必ず以下の形式で出力してください：
パターン1: ポケモン名A, ポケモン名B, ポケモン名C
パターン2: ポケモン名D, ポケモン名E, ポケモン名F
パターン3: ポケモン名G, ポケモン名H, ポケモン名I

可能性が高い順に並べてください。確率の数値は不要です。"""


class PredictUseCase:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def predict(
        self,
        opponent_party: list[str],
        my_party: list[str],
        usage_data: UsageData,
    ) -> PredictionResult:
        prompt = self._build_prompt(opponent_party, my_party, usage_data)
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_response(response.content[0].text)

    def _build_prompt(
        self,
        opponent_party: list[str],
        my_party: list[str],
        usage_data: UsageData,
    ) -> str:
        usage_summary = []
        for entry in usage_data.pokemon:
            if entry.name in opponent_party:
                top_moves = ", ".join(f"{m.name}({m.rate}%)" for m in entry.moves[:3])
                top_items = ", ".join(f"{i.name}({i.rate}%)" for i in entry.items[:2])
                usage_summary.append(f"- {entry.name}: わざ[{top_moves}] 持ち物[{top_items}]")

        usage_text = "\n".join(usage_summary) if usage_summary else "使用率データなし"

        return f"""【相手パーティ（6体）】
{", ".join(opponent_party)}

【自分のパーティ（6体）】
{", ".join(my_party)}

【相手パーティの使用率データ】
{usage_text}

シングルバトル3体選出です。相手が選出しそうな3体のパターンを3つ予想してください。"""

    def _parse_response(self, text: str) -> PredictionResult:
        patterns = []
        for line in text.strip().splitlines():
            m = re.match(r"パターン\d+[:：]\s*(.+)", line)
            if m:
                names = [n.strip() for n in m.group(1).split(",")][:3]
                while len(names) < 3:
                    names.append("")
                patterns.append(PredictionPattern(pokemon=names))
        while len(patterns) < 3:
            patterns.append(PredictionPattern(pokemon=["", "", ""]))
        return PredictionResult(patterns=patterns[:3])
```

- [ ] **Step 3: recognition_use_case.py を作成**

`backend/src/application/use_cases/recognition_use_case.py`:

```python
from pathlib import Path
from infrastructure.external.image_recognition import ImageRecognizer, RecognitionResult, InvalidImageError


class RecognitionUseCase:
    def __init__(self, sprites_dir: Path | str):
        self.recognizer = ImageRecognizer(sprites_dir=sprites_dir)

    def recognize(self, image_bytes: bytes) -> RecognitionResult:
        return self.recognizer.recognize_from_bytes(image_bytes)
```

- [ ] **Step 4: コミット**

```bash
git add backend/src/application/
git commit -m "refactor: application/use_cases レイヤー作成"
```

---

## Task 6: バックエンド - presentation/routers/ 作成

**Files:**
- Create: `backend/src/presentation/__init__.py`
- Create: `backend/src/presentation/routers/__init__.py`
- Create: `backend/src/presentation/routers/party.py`
- Create: `backend/src/presentation/routers/prediction.py`
- Create: `backend/src/presentation/routers/recognition.py`
- Create: `backend/src/presentation/routers/data.py`

- [ ] **Step 1: ディレクトリを作成**

```bash
mkdir -p backend/src/presentation/routers
touch backend/src/presentation/__init__.py
touch backend/src/presentation/routers/__init__.py
```

- [ ] **Step 2: presentation/routers/party.py を作成**

`backend/src/presentation/routers/party.py`:

```python
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from domain.entities.party import Party, PartiesData
from infrastructure.persistence.json_party_repository import JsonPartyRepository

router = APIRouter(prefix="/api/party", tags=["party"])
_repo = JsonPartyRepository()


class PartyCreateRequest(BaseModel):
    name: str
    pokemon: list[str]


@router.get("")
def list_parties() -> PartiesData:
    return _repo.get_all()


@router.post("")
def create_party(req: PartyCreateRequest) -> Party:
    data = _repo.get_all()
    party = Party(id=str(uuid.uuid4()), name=req.name, pokemon=req.pokemon)
    updated = PartiesData(parties=[*data.parties, party], last_used_id=data.last_used_id)
    _repo.save(updated)
    return party


@router.put("/{party_id}")
def update_party(party_id: str, req: PartyCreateRequest) -> Party:
    data = _repo.get_all()
    parties = data.parties
    for i, p in enumerate(parties):
        if p.id == party_id:
            updated_party = Party(id=party_id, name=req.name, pokemon=req.pokemon)
            new_parties = [*parties[:i], updated_party, *parties[i + 1:]]
            _repo.save(PartiesData(parties=new_parties, last_used_id=data.last_used_id))
            return updated_party
    raise HTTPException(status_code=404, detail="Party not found")


@router.delete("/{party_id}")
def delete_party(party_id: str):
    data = _repo.get_all()
    new_parties = [p for p in data.parties if p.id != party_id]
    _repo.save(PartiesData(parties=new_parties, last_used_id=data.last_used_id))
    return {"ok": True}


@router.post("/last-used/{party_id}")
def set_last_used(party_id: str):
    data = _repo.get_all()
    _repo.save(PartiesData(parties=data.parties, last_used_id=party_id))
    return {"ok": True}
```

- [ ] **Step 3: presentation/routers/prediction.py を作成**

`backend/src/presentation/routers/prediction.py`:

```python
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from application.use_cases.predict_use_case import PredictUseCase
from infrastructure.persistence.json_usage_repository import JsonUsageRepository

router = APIRouter(prefix="/api", tags=["prediction"])
_usage_repo = JsonUsageRepository()


class PredictRequest(BaseModel):
    opponent_party: list[str]
    my_party: list[str]


@router.post("/predict")
def predict(req: PredictRequest):
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

- [ ] **Step 4: presentation/routers/recognition.py を作成**

`backend/src/presentation/routers/recognition.py`:

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from application.use_cases.recognition_use_case import RecognitionUseCase
from infrastructure.external.image_recognition import InvalidImageError

router = APIRouter(prefix="/api", tags=["recognition"])
_sprites_dir = Path(__file__).parent.parent.parent.parent / "data" / "sprites"
recognizer = RecognitionUseCase(sprites_dir=_sprites_dir)


@router.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    image_bytes = await file.read()
    try:
        result = recognizer.recognize(image_bytes)
    except InvalidImageError:
        raise HTTPException(status_code=400, detail="無効な画像ファイルです。PNG または JPEG 形式の画像をアップロードしてください。")
    return {"names": result.names, "confidences": result.confidences}
```

- [ ] **Step 5: presentation/routers/data.py を作成**

`backend/src/presentation/routers/data.py`:

```python
import logging
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks
from pathlib import Path
from infrastructure.external.scraper import GameWithScraper
from infrastructure.persistence.json_usage_repository import JsonUsageRepository
from domain.entities.pokemon import PokemonList, UsageData, UsageEntry, PokemonInfo, BaseStats

router = APIRouter(prefix="/api/data", tags=["data"])
_usage_repo = JsonUsageRepository()
_sprites_dir = Path(__file__).parent.parent.parent.parent / "data" / "sprites"
_logger = logging.getLogger(__name__)


@router.post("/fetch")
def fetch_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(_do_fetch)
    return {"status": "started"}


def _do_fetch() -> None:
    try:
        scraper = GameWithScraper(sprites_dir=_sprites_dir)
    except Exception:
        _logger.exception("GameWithScraper の初期化に失敗しました")
        return
    _fetch_and_save_pokemon_list(scraper)
    _fetch_and_save_usage_data(scraper)


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
        _logger.info("season と regulation はスクレイパー未対応のため 0/\"\" のままです。HTMLセレクタ実装後に修正が必要です。")
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
    return {
        "pokemon_list_available": pokemon_list is not None,
        "usage_data_available": usage_data is not None,
        "usage_data_date": usage_data.collected_at if usage_data else None,
    }


@router.get("/pokemon/names")
def get_pokemon_names():
    pokemon_list = _usage_repo.get_pokemon_list()
    if pokemon_list is None:
        return {"names": []}
    names = [p.name for p in pokemon_list.pokemon]
    for p in pokemon_list.pokemon:
        if p.mega_evolution:
            names.append(p.mega_evolution.name)
    return {"names": names}
```

- [ ] **Step 6: main.py の import パスを更新**

`backend/src/main.py` を以下に書き換える:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from presentation.routers import data, recognition, prediction, party

app = FastAPI(title="Pokemon Champions Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(recognition.router)
app.include_router(prediction.router)
app.include_router(party.router)

sprites_dir = Path(__file__).parent.parent / "data" / "sprites"
sprites_dir.mkdir(parents=True, exist_ok=True)
app.mount("/sprites", StaticFiles(directory=str(sprites_dir)), name="sprites")


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 7: コミット**

```bash
git add backend/src/presentation/ backend/src/main.py
git commit -m "refactor: presentation/routers レイヤー作成・main.py 更新"
```

---

## Task 7: バックエンド - テスト移動・conftest 更新・pyproject.toml 更新

**Files:**
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_predict_use_case.py`
- Create: `backend/tests/test_image_recognition.py`
- Create: `backend/tests/test_models.py`
- Create: `backend/tests/test_routers.py`
- Create: `backend/tests/test_scraper.py`
- Modify: `backend/pyproject.toml`

- [ ] **Step 1: conftest.py を新パスで作成（import パス更新）**

`backend/tests/conftest.py`:

```python
import pytest
from pathlib import Path
from infrastructure.persistence.json_party_repository import JsonPartyRepository
from infrastructure.persistence.json_usage_repository import JsonUsageRepository


@pytest.fixture(autouse=True)
def use_temp_data_dir(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "sprites").mkdir()
    (data_dir / "usage_rates").mkdir()

    temp_party_repo = JsonPartyRepository(data_dir=data_dir)
    temp_usage_repo = JsonUsageRepository(data_dir=data_dir)

    import presentation.routers.party as rp
    import presentation.routers.prediction as rpred
    import presentation.routers.data as rd

    original_party = rp._repo
    original_pred_usage = rpred._usage_repo
    original_data_usage = rd._usage_repo

    rp._repo = temp_party_repo
    rpred._usage_repo = temp_usage_repo
    rd._usage_repo = temp_usage_repo

    yield

    rp._repo = original_party
    rpred._usage_repo = original_pred_usage
    rd._usage_repo = original_data_usage
```

- [ ] **Step 2: test_predict_use_case.py を作成（旧 test_ai_predictor.py から移植）**

`backend/tests/test_predict_use_case.py`:

```python
from unittest.mock import MagicMock, patch
from application.use_cases.predict_use_case import PredictUseCase
from domain.entities.pokemon import UsageData, UsageEntry, RatedItem, EvSpread
from domain.entities.party import PredictionResult


MOCK_CLAUDE_RESPONSE = """
パターン1: リザードン, カメックス, フシギバナ
パターン2: ピカチュウ, リザードン, イワーク
パターン3: フシギバナ, カメックス, ゲンガー
"""


def _make_usage_data():
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
        pokemon=[entry],
    )


@patch("application.use_cases.predict_use_case.anthropic.Anthropic")
def test_predict_returns_three_patterns(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=MOCK_CLAUDE_RESPONSE)]
    )

    use_case = PredictUseCase(api_key="test-key")
    result = use_case.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )

    assert isinstance(result, PredictionResult)
    assert len(result.patterns) == 3
    assert len(result.patterns[0].pokemon) == 3
    assert result.patterns[0].pokemon[0] == "リザードン"


@patch("application.use_cases.predict_use_case.anthropic.Anthropic")
def test_predict_calls_api_with_both_parties(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=MOCK_CLAUDE_RESPONSE)]
    )

    use_case = PredictUseCase(api_key="test-key")
    use_case.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )

    call_kwargs = mock_client.messages.create.call_args
    prompt_text = str(call_kwargs)
    assert "リザードン" in prompt_text
    assert "カビゴン" in prompt_text
```

- [ ] **Step 3: test_models.py を作成（import パス更新）**

`backend/tests/test_models.py`:

```python
from domain.entities.pokemon import PokemonInfo, MegaEvolution, BaseStats, RatedItem, EvSpread, UsageEntry, UsageData
from domain.entities.party import Party, PredictionPattern, PredictionResult


def test_pokemon_info_with_mega():
    mega = MegaEvolution(
        name="メガリザードンX",
        types=["ほのお", "ドラゴン"],
        base_stats=BaseStats(hp=78, attack=130, defense=111, sp_attack=130, sp_defense=85, speed=100),
        abilities=["かたいツメ"],
        weaknesses=["じめん", "いわ", "ドラゴン"],
        resistances=["ほのお", "くさ"],
        sprite_path="sprites/006-mega-x.png",
    )
    p = PokemonInfo(
        pokedex_id=6,
        name="リザードン",
        types=["ほのお", "ひこう"],
        base_stats=BaseStats(hp=78, attack=84, defense=78, sp_attack=109, sp_defense=85, speed=100),
        height_m=1.7,
        weight_kg=90.5,
        low_kick_power=100,
        abilities=["もうか", "サンパワー"],
        weaknesses=["いわ", "みず", "でんき"],
        resistances=["くさ", "かくとう"],
        sprite_path="sprites/006.png",
        mega_evolution=mega,
    )
    assert p.name == "リザードン"
    assert p.mega_evolution.name == "メガリザードンX"


def test_pokemon_info_without_mega():
    p = PokemonInfo(
        pokedex_id=1,
        name="フシギダネ",
        types=["くさ", "どく"],
        base_stats=BaseStats(hp=45, attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45),
        height_m=0.7,
        weight_kg=6.9,
        low_kick_power=20,
        abilities=["しんりょく"],
        weaknesses=["ほのお", "ひこう"],
        resistances=["くさ", "みず"],
        sprite_path="sprites/001.png",
        mega_evolution=None,
    )
    assert p.mega_evolution is None


def test_usage_entry():
    entry = UsageEntry(
        name="リザードン",
        moves=[RatedItem(name="かえんほうしゃ", rate=78), RatedItem(name="だいもんじ", rate=54)],
        items=[RatedItem(name="いのちのたま", rate=61)],
        abilities=[RatedItem(name="もうか", rate=82)],
        natures=[RatedItem(name="ひかえめ", rate=67)],
        teammates=[RatedItem(name="カメックス", rate=45)],
        evs=[EvSpread(spread={"H": 0, "A": 0, "B": 0, "C": 252, "D": 4, "S": 252}, rate=52)],
        ivs={"H": 31, "A": 0, "B": 31, "C": 31, "D": 31, "S": 31},
    )
    assert entry.moves[0].rate == 78
    assert entry.ivs["A"] == 0


def test_prediction_pattern():
    pattern = PredictionPattern(pokemon=["リザードン", "カメックス", "フシギバナ"])
    assert len(pattern.pokemon) == 3


def test_party():
    party = Party(id="p1", name="メインパーティ", pokemon=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "ゲンガー", "カビゴン"])
    assert len(party.pokemon) == 6
```

- [ ] **Step 4: test_image_recognition.py を作成（import パス更新）**

`backend/tests/test_image_recognition.py`:

```python
import numpy as np
import pytest
import cv2
from infrastructure.external.image_recognition import ImageRecognizer, RecognitionResult, InvalidImageError


@pytest.fixture
def sprites_dir(tmp_path):
    for name, color in [
        ("リザードン", (0, 100, 255)),
        ("カメックス", (255, 100, 0)),
        ("フシギバナ", (0, 200, 0)),
    ]:
        img = np.full((32, 32, 3), color, dtype=np.uint8)
        cv2.imwrite(str(tmp_path / f"{name}.png"), img)
    return tmp_path


def test_recognizer_loads_sprites(sprites_dir):
    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    assert len(recognizer.templates) == 3
    assert "リザードン" in recognizer.templates


def test_recognize_returns_result_with_six_slots(sprites_dir):
    bg = np.zeros((400, 800, 3), dtype=np.uint8)
    sprite = cv2.imread(str(sprites_dir / "リザードン.png"))
    positions = [(50, 50), (150, 50), (250, 50), (350, 50), (450, 50), (550, 50)]
    for x, y in positions:
        bg[y:y+32, x:x+32] = sprite

    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    result = recognizer.recognize(bg)

    assert isinstance(result, RecognitionResult)
    assert len(result.names) == 6


def test_recognize_identifies_correct_pokemon(sprites_dir):
    bg = np.zeros((400, 800, 3), dtype=np.uint8)
    sprite = cv2.imread(str(sprites_dir / "リザードン.png"))
    bg[50:82, 50:82] = sprite

    recognizer = ImageRecognizer(sprites_dir=sprites_dir, top_n=1)
    result = recognizer.recognize(bg)

    assert result.names[0] == "リザードン"


def test_recognize_from_bytes_raises_on_invalid_image(sprites_dir):
    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    with pytest.raises(InvalidImageError):
        recognizer.recognize_from_bytes(b"this is not an image")


def test_recognize_from_bytes_raises_on_empty_bytes(sprites_dir):
    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    with pytest.raises(InvalidImageError):
        recognizer.recognize_from_bytes(b"")
```

- [ ] **Step 5: test_scraper.py を作成（import パス更新）**

`backend/tests/test_scraper.py`:

```python
from unittest.mock import patch, MagicMock
import pytest
from infrastructure.external.scraper import GameWithScraper


MOCK_POKEMON_LIST_HTML = """
<html><body>
  <div class="pokemon-item">
    <img src="https://img.gamewith.jp/sprites/006.png" alt="リザードン">
    <span class="pokemon-name">リザードン</span>
    <span class="pokemon-type">ほのお/ひこう</span>
    <td class="hp">78</td><td class="attack">84</td><td class="defense">78</td>
    <td class="sp-attack">109</td><td class="sp-defense">85</td><td class="speed">100</td>
    <span class="height">1.7m</span><span class="weight">90.5kg</span>
    <span class="ability">もうか</span>
  </div>
</body></html>
"""


def test_scraper_initializes(tmp_path):
    scraper = GameWithScraper(sprites_dir=tmp_path)
    assert scraper.sprites_dir == tmp_path


@patch("infrastructure.external.scraper.requests.get")
def test_fetch_with_rate_limit(mock_get, tmp_path):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html></html>"
    mock_get.return_value = mock_resp

    scraper = GameWithScraper(sprites_dir=tmp_path, request_interval=0)
    scraper._fetch("https://example.com")
    mock_get.assert_called_once()
```

- [ ] **Step 6: test_routers.py を作成（import パス更新）**

`backend/tests/test_routers.py`:

```python
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_parties_empty():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/party")
    assert resp.status_code == 200
    assert resp.json()["parties"] == []


@pytest.mark.asyncio
async def test_create_party():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/party", json={
            "name": "テストパーティ",
            "pokemon": ["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "ゲンガー", "カビゴン"]
        })
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "テストパーティ"
    assert "id" in data


@pytest.mark.asyncio
async def test_recognize_returns_six_names():
    mock_result = MagicMock()
    mock_result.names = ["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "ゲンガー", "カビゴン"]
    mock_result.confidences = [0.9] * 6

    with patch("presentation.routers.recognition.recognizer") as mock_rec:
        mock_rec.recognize.return_value = mock_result
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/recognize",
                files={"file": ("test.jpg", b"fake-image-data", "image/jpeg")},
            )
    assert resp.status_code == 200
    assert len(resp.json()["names"]) == 6


@pytest.mark.asyncio
async def test_recognize_returns_400_on_invalid_image():
    from infrastructure.external.image_recognition import InvalidImageError
    with patch("presentation.routers.recognition.recognizer") as mock_rec:
        mock_rec.recognize.side_effect = InvalidImageError("bad image")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/recognize",
                files={"file": ("bad.png", b"not an image", "image/png")},
            )
    assert resp.status_code == 400


def test_do_fetch_calls_scraper_methods():
    mock_scraper = MagicMock()
    mock_scraper.fetch_pokemon_list.return_value = []
    mock_scraper.fetch_usage_ranking.return_value = []

    with patch("presentation.routers.data.GameWithScraper", return_value=mock_scraper):
        with patch("presentation.routers.data._usage_repo"):
            from presentation.routers.data import _do_fetch
            _do_fetch()

    mock_scraper.fetch_pokemon_list.assert_called_once()
    mock_scraper.fetch_usage_ranking.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_data_endpoint_returns_started():
    with patch("presentation.routers.data._do_fetch"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/data/fetch")
    assert resp.status_code == 200
    assert resp.json()["status"] == "started"


def test_do_fetch_handles_scraper_init_exception():
    with patch("presentation.routers.data.GameWithScraper", side_effect=Exception("init error")):
        from presentation.routers.data import _do_fetch
        _do_fetch()


def test_do_fetch_handles_scraper_exception():
    mock_scraper = MagicMock()
    mock_scraper.fetch_pokemon_list.side_effect = Exception("Network error")
    mock_scraper.fetch_usage_ranking.return_value = []

    with patch("presentation.routers.data.GameWithScraper", return_value=mock_scraper):
        from presentation.routers.data import _do_fetch
        _do_fetch()

    mock_scraper.fetch_usage_ranking.assert_called_once()
```

- [ ] **Step 7: pyproject.toml の testpaths と pythonpath を更新**

`backend/pyproject.toml` の `[tool.pytest.ini_options]` を以下に変更:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
asyncio_mode = "auto"
```

- [ ] **Step 8: 新テストスイートが通ることを確認**

```bash
docker compose run --rm backend pytest tests/ -v
```

期待: 全テスト PASS

- [ ] **Step 9: コミット**

```bash
git add backend/tests/ backend/pyproject.toml
git commit -m "refactor: テストを backend/tests/ に移動・import パス更新"
```

---

## Task 8: バックエンド - 旧ファイル削除

**Files:**
- Delete: `backend/src/models/`
- Delete: `backend/src/services/`
- Delete: `backend/src/routers/`
- Delete: `backend/src/tests/`

- [ ] **Step 1: 旧ディレクトリを削除**

```bash
rm -rf backend/src/models backend/src/services backend/src/routers backend/src/tests
```

- [ ] **Step 2: 全テストが通ることを確認**

```bash
docker compose run --rm backend pytest tests/ -v
```

期待: 全テスト PASS

- [ ] **Step 3: コミット**

```bash
git add -A
git commit -m "refactor: 旧 models/services/routers/tests ディレクトリ削除"
```

---

## Task 9: フロントエンド - domain/entities/ 分割

**Files:**
- Create: `frontend/src/domain/entities/party.ts`
- Create: `frontend/src/domain/entities/prediction.ts`
- Create: `frontend/src/domain/entities/pokemon.ts`
- Delete: `frontend/src/domain/entities/index.ts`

- [ ] **Step 1: party.ts を作成**

`frontend/src/domain/entities/party.ts`:

```typescript
export interface Party {
  id: string
  name: string
  pokemon: string[]
}

export interface PartiesData {
  parties: Party[]
  last_used_id: string | null
}
```

- [ ] **Step 2: prediction.ts を作成**

`frontend/src/domain/entities/prediction.ts`:

```typescript
export interface PredictionPattern {
  pokemon: string[]
}

export interface PredictionResult {
  patterns: PredictionPattern[]
}
```

- [ ] **Step 3: pokemon.ts を作成**

`frontend/src/domain/entities/pokemon.ts`:

```typescript
export interface RatedItem {
  name: string
  rate: number
}

export interface EvSpread {
  spread: Record<string, number>
  rate: number
}

export interface UsageEntry {
  name: string
  moves: RatedItem[]
  items: RatedItem[]
  abilities: RatedItem[]
  natures: RatedItem[]
  teammates: RatedItem[]
  evs: EvSpread[]
  ivs: Record<string, number> | null
}
```

- [ ] **Step 4: 旧 index.ts を削除**

```bash
rm frontend/src/domain/entities/index.ts
```

- [ ] **Step 5: コミット**

```bash
git add frontend/src/domain/entities/
git commit -m "refactor: frontend domain/entities を分割"
```

---

## Task 10: フロントエンド - infrastructure/api/ 分割

**Files:**
- Create: `frontend/src/infrastructure/api/partyApi.ts`
- Create: `frontend/src/infrastructure/api/predictionApi.ts`
- Create: `frontend/src/infrastructure/api/recognitionApi.ts`
- Create: `frontend/src/infrastructure/api/dataApi.ts`
- Delete: `frontend/src/infrastructure/api/client.ts`

- [ ] **Step 1: partyApi.ts を作成**

`frontend/src/infrastructure/api/partyApi.ts`:

```typescript
import type { Party, PartiesData } from '../../domain/entities/party'

const BASE = '/api'

export async function getParties(): Promise<PartiesData> {
  const res = await fetch(`${BASE}/party`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function createParty(name: string, pokemon: string[]): Promise<Party> {
  const res = await fetch(`${BASE}/party`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, pokemon }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function updateParty(id: string, name: string, pokemon: string[]): Promise<Party> {
  const res = await fetch(`${BASE}/party/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, pokemon }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function deleteParty(id: string): Promise<void> {
  await fetch(`${BASE}/party/${id}`, { method: 'DELETE' })
}

export async function setLastUsedParty(id: string): Promise<void> {
  await fetch(`${BASE}/party/last-used/${id}`, { method: 'POST' })
}
```

- [ ] **Step 2: predictionApi.ts を作成**

`frontend/src/infrastructure/api/predictionApi.ts`:

```typescript
import type { PredictionResult } from '../../domain/entities/prediction'

const BASE = '/api'

export async function predict(
  opponentParty: string[],
  myParty: string[],
): Promise<PredictionResult> {
  const res = await fetch(`${BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ opponent_party: opponentParty, my_party: myParty }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
```

- [ ] **Step 3: recognitionApi.ts を作成**

`frontend/src/infrastructure/api/recognitionApi.ts`:

```typescript
const BASE = '/api'

export async function recognize(
  file: File,
): Promise<{ names: string[]; confidences: number[] }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/recognize`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
```

- [ ] **Step 4: dataApi.ts を作成**

`frontend/src/infrastructure/api/dataApi.ts`:

```typescript
const BASE = '/api'

export async function fetchData(): Promise<{ status: string }> {
  const res = await fetch(`${BASE}/data/fetch`, { method: 'POST' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getDataStatus(): Promise<{
  pokemon_list_available: boolean
  usage_data_available: boolean
  usage_data_date: string | null
}> {
  const res = await fetch(`${BASE}/data/status`)
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

- [ ] **Step 5: 旧 client.ts を削除**

```bash
rm frontend/src/infrastructure/api/client.ts
```

- [ ] **Step 6: コミット**

```bash
git add frontend/src/infrastructure/api/
git commit -m "refactor: frontend infrastructure/api をドメイン別に分割"
```

---

## Task 11: フロントエンド - application/hooks/ 作成

**Files:**
- Create: `frontend/src/application/hooks/useParty.ts`
- Create: `frontend/src/application/hooks/usePredict.ts`
- Create: `frontend/src/application/hooks/usePokemonData.ts`

- [ ] **Step 1: useParty.ts を作成**

`frontend/src/application/hooks/useParty.ts`:

```typescript
import { useState, useEffect } from 'react'
import type { Party } from '../../domain/entities/party'
import {
  getParties,
  createParty,
  updateParty,
  deleteParty,
  setLastUsedParty,
} from '../../infrastructure/api/partyApi'

export interface UsePartyReturn {
  parties: Party[]
  selectedPartyId: string | null
  myParty: string[]
  selectParty: (party: Party) => Promise<void>
  createNewParty: (name: string, pokemon: string[]) => Promise<void>
  updateExistingParty: (id: string, name: string, pokemon: string[]) => Promise<void>
  removeParty: (id: string) => Promise<void>
  setMyParty: (pokemon: string[]) => void
  reload: () => void
}

export function useParty(): UsePartyReturn {
  const [parties, setParties] = useState<Party[]>([])
  const [selectedPartyId, setSelectedPartyId] = useState<string | null>(null)
  const [myParty, setMyParty] = useState<string[]>(Array(6).fill(''))

  const reload = () => {
    getParties().then((data) => {
      setParties(data.parties)
      if (data.last_used_id) {
        const last = data.parties.find((p) => p.id === data.last_used_id)
        if (last) {
          setMyParty([...last.pokemon, ...Array(6).fill('')].slice(0, 6))
          setSelectedPartyId(last.id)
        }
      }
    })
  }

  useEffect(() => {
    reload()
  }, [])

  const selectParty = async (party: Party) => {
    setMyParty([...party.pokemon, ...Array(6).fill('')].slice(0, 6))
    setSelectedPartyId(party.id)
    await setLastUsedParty(party.id)
  }

  const createNewParty = async (name: string, pokemon: string[]) => {
    await createParty(name, pokemon)
    reload()
  }

  const updateExistingParty = async (id: string, name: string, pokemon: string[]) => {
    await updateParty(id, name, pokemon)
    reload()
  }

  const removeParty = async (id: string) => {
    await deleteParty(id)
    reload()
  }

  return {
    parties,
    selectedPartyId,
    myParty,
    selectParty,
    createNewParty,
    updateExistingParty,
    removeParty,
    setMyParty,
    reload,
  }
}
```

- [ ] **Step 2: usePredict.ts を作成**

`frontend/src/application/hooks/usePredict.ts`:

```typescript
import { useState } from 'react'
import type { PredictionResult } from '../../domain/entities/prediction'
import { predict } from '../../infrastructure/api/predictionApi'

export interface UsePredictReturn {
  result: PredictionResult | null
  loading: boolean
  error: string | null
  handlePredict: (opponentParty: string[], myParty: string[]) => Promise<void>
}

export function usePredict(): UsePredictReturn {
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handlePredict = async (opponentParty: string[], myParty: string[]) => {
    const opponent = opponentParty.filter(Boolean)
    const my = myParty.filter(Boolean)
    if (opponent.length < 6) {
      setError('相手パーティを6体入力してください')
      return
    }
    if (my.length < 6) {
      setError('自分のパーティを6体入力してください')
      return
    }
    setError(null)
    setLoading(true)
    try {
      const res = await predict(opponent, my)
      setResult(res)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  return { result, loading, error, handlePredict }
}
```

- [ ] **Step 3: usePokemonData.ts を作成**

`frontend/src/application/hooks/usePokemonData.ts`:

```typescript
import { useState, useEffect } from 'react'
import { getPokemonNames } from '../../infrastructure/api/dataApi'

export interface UsePokemonDataReturn {
  pokemonNames: string[]
}

export function usePokemonData(): UsePokemonDataReturn {
  const [pokemonNames, setPokemonNames] = useState<string[]>([])

  useEffect(() => {
    getPokemonNames().then(setPokemonNames)
  }, [])

  return { pokemonNames }
}
```

- [ ] **Step 4: コミット**

```bash
git add frontend/src/application/
git commit -m "refactor: frontend application/hooks レイヤー作成"
```

---

## Task 12: フロントエンド - PredictionPage / PartyPage 更新

**Files:**
- Modify: `frontend/src/presentation/pages/PredictionPage.tsx`
- Modify: `frontend/src/presentation/pages/PartyPage.tsx`

- [ ] **Step 1: PredictionPage.tsx を更新**

`frontend/src/presentation/pages/PredictionPage.tsx`:

```typescript
import { useState } from 'react'
import PartyInput from '../components/PartyInput'
import PredictionResultView from '../components/PredictionResult'
import { usePredict } from '../../application/hooks/usePredict'
import { useParty } from '../../application/hooks/useParty'
import { usePokemonData } from '../../application/hooks/usePokemonData'

export default function PredictionPage() {
  const [opponentParty, setOpponentParty] = useState<string[]>(Array(6).fill(''))
  const { result, loading, error, handlePredict } = usePredict()
  const { parties, selectedPartyId, myParty, selectParty } = useParty()
  const { pokemonNames } = usePokemonData()

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <PartyInput party={opponentParty} onChange={setOpponentParty} pokemonNames={pokemonNames} />

      <div>
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400 mb-2">自分のパーティ</h2>
        <div className="flex gap-2 flex-wrap">
          {parties.map((p) => (
            <button
              key={p.id}
              onClick={() => selectParty(p)}
              className={`px-3 py-1 rounded text-sm border ${
                selectedPartyId === p.id
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        onClick={() => handlePredict(opponentParty, myParty)}
        disabled={loading}
        className="w-full py-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
      >
        {loading ? '予想中...' : '選出予想する'}
      </button>

      {result && <PredictionResultView result={result} />}
    </div>
  )
}
```

- [ ] **Step 2: PartyPage.tsx を更新**

`frontend/src/presentation/pages/PartyPage.tsx`:

```typescript
import { useState } from 'react'
import PokemonSlot from '../components/PokemonSlot'
import { useParty } from '../../application/hooks/useParty'
import { usePokemonData } from '../../application/hooks/usePokemonData'
import type { Party } from '../../domain/entities/party'

export default function PartyPage() {
  const { parties, createNewParty, updateExistingParty, removeParty } = useParty()
  const { pokemonNames } = usePokemonData()
  const [editing, setEditing] = useState<Party | null>(null)
  const [name, setName] = useState('')
  const [pokemon, setPokemon] = useState<string[]>(Array(6).fill(''))

  const startNew = () => {
    setEditing(null)
    setName('')
    setPokemon(Array(6).fill(''))
  }

  const startEdit = (p: Party) => {
    setEditing(p)
    setName(p.name)
    setPokemon([...p.pokemon, ...Array(6).fill('')].slice(0, 6))
  }

  const save = async () => {
    if (!name) return
    const filled = pokemon.filter(Boolean)
    if (editing) {
      await updateExistingParty(editing.id, name, filled)
    } else {
      await createNewParty(name, filled)
    }
    startNew()
  }

  const remove = async (id: string) => {
    if (!confirm('削除しますか？')) return
    await removeParty(id)
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="font-bold text-xl">パーティ登録</h1>

      <div className="border rounded-xl p-4 space-y-4 dark:border-gray-700">
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400">
          {editing ? `編集中: ${editing.name}` : '新規パーティ'}
        </h2>
        <input
          className="w-full border rounded px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600"
          placeholder="パーティ名"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
          {pokemon.map((p, i) => (
            <PokemonSlot
              key={i}
              value={p}
              onChange={(v) => {
                const next = [...pokemon]
                next[i] = v
                setPokemon(next)
              }}
              pokemonNames={pokemonNames}
            />
          ))}
        </div>
        <div className="flex gap-2">
          <button
            onClick={save}
            className="px-4 py-2 rounded bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold"
          >
            {editing ? '更新' : '登録'}
          </button>
          {editing && (
            <button
              onClick={startNew}
              className="px-4 py-2 rounded border dark:border-gray-600 text-sm"
            >
              キャンセル
            </button>
          )}
        </div>
      </div>

      <div className="space-y-3">
        {parties.map((p) => (
          <div key={p.id} className="border rounded-xl p-4 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold">{p.name}</span>
              <div className="flex gap-2">
                <button onClick={() => startEdit(p)} className="text-sm text-indigo-600 hover:underline">
                  編集
                </button>
                <button onClick={() => remove(p.id)} className="text-sm text-red-500 hover:underline">
                  削除
                </button>
              </div>
            </div>
            <div className="flex gap-2 flex-wrap">
              {p.pokemon.map((pname, i) => (
                <div key={i} className="text-center">
                  <img
                    src={`/sprites/${pname}.png`}
                    alt={pname}
                    className="w-10 h-10 object-contain mx-auto"
                    onError={(e) => {
                      ;(e.target as HTMLImageElement).style.display = 'none'
                    }}
                  />
                  <div className="text-xs">{pname}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: ビルドが通ることを確認**

```bash
cd frontend && npm run build
```

期待: `dist/` が生成されエラーなし

- [ ] **Step 4: コミット**

```bash
git add frontend/src/presentation/pages/
git commit -m "refactor: PredictionPage / PartyPage を application/hooks 経由に更新"
```

---

## Task 13: フロントエンド - App.css 削除・最終確認

**Files:**
- Delete: `frontend/src/App.css`

- [ ] **Step 1: App.css の使用箇所がないことを確認**

```bash
grep -r "App.css" frontend/src/
```

期待: 出力なし（未使用）

- [ ] **Step 2: App.css を削除**

```bash
rm frontend/src/App.css
```

- [ ] **Step 3: ビルドが通ることを最終確認**

```bash
cd frontend && npm run build
```

期待: エラーなし

- [ ] **Step 4: バックエンドの全テストも最終確認**

```bash
docker compose run --rm backend pytest tests/ -v
```

期待: 全テスト PASS

- [ ] **Step 5: 逆方向 import がないことを確認（バックエンド）**

```bash
grep -r "from presentation" backend/src/domain backend/src/application backend/src/infrastructure 2>/dev/null
grep -r "from application" backend/src/domain backend/src/infrastructure 2>/dev/null
grep -r "from infrastructure" backend/src/domain 2>/dev/null
```

期待: 全て出力なし

- [ ] **Step 6: 最終コミット**

```bash
git add -A
git commit -m "refactor: App.css 削除・クリーンアーキテクチャ整合完了"
```
