# Pokemon Champions Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ポケモンチャンピオンズの対戦前に相手パーティを入力し、AIが選出予想3パターンと各ポケモンの型情報を表示するローカルWebアプリを構築する。

**Architecture:** FastAPIバックエンド（画像認識・スクレイピング・AI呼び出し）+ React/Viteフロントエンドの2プロセス構成。データはJSONファイルで永続化。

**Tech Stack:** Python 3.11+, FastAPI, OpenCV, BeautifulSoup4, Anthropic SDK, React 18, TypeScript, Vite, Tailwind CSS

---

## ファイル構成

```
pokemon-champions-tool/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── models/
│   │   ├── __init__.py
│   │   ├── pokemon.py        # PokemonInfo, MegaEvolution, UsageEntry, UsageData
│   │   └── party.py          # Party, PredictionPattern, PredictionResult
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── data.py           # POST /api/data/fetch
│   │   ├── recognition.py    # POST /api/recognize
│   │   ├── prediction.py     # POST /api/predict
│   │   └── party.py          # CRUD /api/party
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_manager.py   # JSON読み書き
│   │   ├── scraper.py        # GameWithスクレイピング
│   │   ├── image_recognition.py  # OpenCVテンプレートマッチング
│   │   └── ai_predictor.py   # Claude API呼び出し
│   ├── data/
│   │   ├── sprites/
│   │   ├── pokemon_list.json
│   │   ├── usage_rates/
│   │   └── parties.json
│   └── tests/
│       ├── conftest.py
│       ├── test_models.py
│       ├── test_data_manager.py
│       ├── test_scraper.py
│       ├── test_image_recognition.py
│       ├── test_ai_predictor.py
│       └── test_routers.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api/
        │   └── client.ts         # fetch wrapper
        ├── types/
        │   └── index.ts          # 共有型定義
        ├── hooks/
        │   └── useDarkMode.ts
        ├── pages/
        │   ├── PredictionPage.tsx
        │   └── PartyPage.tsx
        └── components/
            ├── Header.tsx
            ├── DarkModeToggle.tsx
            ├── PokemonSlot.tsx
            ├── PartyInput.tsx
            ├── PokemonCard.tsx
            ├── PatternCard.tsx
            └── PredictionResult.tsx
```

---

## Task 1: バックエンド プロジェクトセットアップ

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/routers/__init__.py`
- Create: `backend/services/__init__.py`
- Create: `backend/models/__init__.py`

- [ ] **Step 1: requirements.txt を作成する**

```
# backend/requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9
opencv-python==4.10.0.84
numpy==1.26.4
requests==2.32.3
beautifulsoup4==4.12.3
anthropic==0.34.0
pytest==8.3.2
pytest-asyncio==0.23.8
httpx==0.27.0
```

- [ ] **Step 2: 仮想環境を作成して依存関係をインストールする**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Expected: Successfully installed ... (エラーなし)

- [ ] **Step 3: main.py を作成する**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Pokemon Champions Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 4: サーバーが起動することを確認する**

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

Expected: `Application startup complete.` が表示される。ブラウザで http://localhost:8000/api/health にアクセスして `{"status":"ok"}` が返ること。

- [ ] **Step 5: `__init__.py` ファイルを作成する**

```bash
touch backend/models/__init__.py
touch backend/routers/__init__.py
touch backend/services/__init__.py
touch backend/tests/__init__.py
mkdir -p backend/data/sprites backend/data/usage_rates
```

- [ ] **Step 6: コミットする**

```bash
git add backend/
git commit -m "feat: バックエンドプロジェクト初期セットアップ"
```

---

## Task 2: データモデル定義

**Files:**
- Create: `backend/models/pokemon.py`
- Create: `backend/models/party.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: テストを書く**

```python
# backend/tests/test_models.py
from models.pokemon import PokemonInfo, MegaEvolution, BaseStats, RatedItem, EvSpread, UsageEntry, UsageData
from models.party import Party, PredictionPattern, PredictionResult


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

- [ ] **Step 2: テストが失敗することを確認する**

```bash
cd backend && source .venv/bin/activate
pytest tests/test_models.py -v
```

Expected: `ModuleNotFoundError: No module named 'models.pokemon'`

- [ ] **Step 3: pokemon.py を実装する**

```python
# backend/models/pokemon.py
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
    spread: dict[str, int]  # {"H": 0, "A": 0, "B": 0, "C": 252, "D": 4, "S": 252}
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

- [ ] **Step 4: party.py を実装する**

```python
# backend/models/party.py
from typing import Optional
from pydantic import BaseModel


class Party(BaseModel):
    id: str
    name: str
    pokemon: list[str]  # ポケモン名のリスト（6体）


class PartiesData(BaseModel):
    parties: list[Party]
    last_used_id: Optional[str] = None


class PredictionPattern(BaseModel):
    pokemon: list[str]  # 選出予想3体のポケモン名


class PredictionResult(BaseModel):
    patterns: list[PredictionPattern]  # 3パターン
```

※ `from typing import Optional` を party.py の先頭に追加すること。

- [ ] **Step 5: テストが通ることを確認する**

```bash
cd backend && source .venv/bin/activate
pytest tests/test_models.py -v
```

Expected: 全テスト PASSED

- [ ] **Step 6: コミットする**

```bash
git add backend/models/ backend/tests/test_models.py
git commit -m "feat: Pydanticデータモデル定義"
```

---

## Task 3: DataManager（JSONファイル読み書き）

**Files:**
- Create: `backend/services/data_manager.py`
- Create: `backend/tests/test_data_manager.py`

- [ ] **Step 1: テストを書く**

```python
# backend/tests/test_data_manager.py
import json
import pytest
from pathlib import Path
from services.data_manager import DataManager
from models.pokemon import PokemonList, PokemonInfo, BaseStats, UsageData, UsageEntry, RatedItem, EvSpread
from models.party import PartiesData, Party


@pytest.fixture
def data_dir(tmp_path):
    (tmp_path / "sprites").mkdir()
    (tmp_path / "usage_rates").mkdir()
    return tmp_path


@pytest.fixture
def manager(data_dir):
    return DataManager(data_dir=data_dir)


def test_save_and_load_pokemon_list(manager, data_dir):
    pl = PokemonList(
        collected_at="2026-04-26T12:00:00",
        pokemon=[
            PokemonInfo(
                pokedex_id=6, name="リザードン", types=["ほのお"], sprite_path="sprites/006.png",
                base_stats=BaseStats(hp=78, attack=84, defense=78, sp_attack=109, sp_defense=85, speed=100),
                height_m=1.7, weight_kg=90.5, low_kick_power=100,
                abilities=["もうか"], weaknesses=["いわ"], resistances=["くさ"],
            )
        ],
    )
    manager.save_pokemon_list(pl)
    loaded = manager.load_pokemon_list()
    assert loaded.pokemon[0].name == "リザードン"
    assert loaded.pokemon[0].base_stats.hp == 78


def test_load_pokemon_list_returns_none_when_missing(manager):
    assert manager.load_pokemon_list() is None


def test_save_and_load_parties(manager):
    data = PartiesData(
        parties=[Party(id="p1", name="テスト", pokemon=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "ゲンガー", "カビゴン"])],
        last_used_id="p1",
    )
    manager.save_parties(data)
    loaded = manager.load_parties()
    assert loaded.parties[0].name == "テスト"
    assert loaded.last_used_id == "p1"


def test_load_parties_returns_empty_when_missing(manager):
    data = manager.load_parties()
    assert data.parties == []


def test_save_and_load_usage_data(manager):
    usage = UsageData(
        collected_at="2026-04-26T12:00:00",
        season=1,
        regulation="レギュレーションA",
        source_updated_at="2026-04-25",
        pokemon=[
            UsageEntry(
                name="リザードン",
                moves=[RatedItem(name="かえんほうしゃ", rate=78)],
                items=[RatedItem(name="いのちのたま", rate=61)],
                abilities=[RatedItem(name="もうか", rate=82)],
                natures=[RatedItem(name="ひかえめ", rate=67)],
                teammates=[],
                evs=[EvSpread(spread={"H": 0, "A": 0, "B": 0, "C": 252, "D": 4, "S": 252}, rate=52)],
            )
        ],
    )
    manager.save_usage_data(usage)
    loaded = manager.load_latest_usage_data()
    assert loaded.pokemon[0].name == "リザードン"
    assert loaded.season == 1


def test_load_usage_data_returns_none_when_missing(manager):
    assert manager.load_latest_usage_data() is None
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
pytest tests/test_data_manager.py -v
```

Expected: `ModuleNotFoundError: No module named 'services.data_manager'`

- [ ] **Step 3: data_manager.py を実装する**

```python
# backend/services/data_manager.py
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from models.pokemon import PokemonList, UsageData
from models.party import PartiesData, Party


class DataManager:
    def __init__(self, data_dir: Path | str = Path(__file__).parent.parent / "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "sprites").mkdir(exist_ok=True)
        (self.data_dir / "usage_rates").mkdir(exist_ok=True)

    def save_pokemon_list(self, data: PokemonList) -> None:
        path = self.data_dir / "pokemon_list.json"
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    def load_pokemon_list(self) -> Optional[PokemonList]:
        path = self.data_dir / "pokemon_list.json"
        if not path.exists():
            return None
        return PokemonList.model_validate_json(path.read_text(encoding="utf-8"))

    def save_parties(self, data: PartiesData) -> None:
        path = self.data_dir / "parties.json"
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    def load_parties(self) -> PartiesData:
        path = self.data_dir / "parties.json"
        if not path.exists():
            return PartiesData(parties=[])
        return PartiesData.model_validate_json(path.read_text(encoding="utf-8"))

    def save_usage_data(self, data: UsageData) -> None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        path = self.data_dir / "usage_rates" / f"{date_str}.json"
        path.write_text(data.model_dump_json(indent=2), encoding="utf-8")

    def load_latest_usage_data(self) -> Optional[UsageData]:
        rate_dir = self.data_dir / "usage_rates"
        files = sorted(rate_dir.glob("*.json"), reverse=True)
        if not files:
            return None
        return UsageData.model_validate_json(files[0].read_text(encoding="utf-8"))
```

- [ ] **Step 4: テストが通ることを確認する**

```bash
pytest tests/test_data_manager.py -v
```

Expected: 全テスト PASSED

- [ ] **Step 5: コミットする**

```bash
git add backend/services/data_manager.py backend/tests/test_data_manager.py
git commit -m "feat: DataManager JSONファイル読み書き実装"
```

---

## Task 4: GameWithスクレイパー

**Files:**
- Create: `backend/services/scraper.py`
- Create: `backend/tests/test_scraper.py`

- [ ] **Step 1: テストを書く（モック使用）**

```python
# backend/tests/test_scraper.py
from unittest.mock import patch, MagicMock
import pytest
from services.scraper import GameWithScraper


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


@patch("services.scraper.requests.get")
def test_fetch_with_rate_limit(mock_get, tmp_path):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html></html>"
    mock_get.return_value = mock_resp

    scraper = GameWithScraper(sprites_dir=tmp_path, request_interval=0)
    scraper._fetch("https://example.com")
    mock_get.assert_called_once()
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
pytest tests/test_scraper.py -v
```

Expected: `ModuleNotFoundError: No module named 'services.scraper'`

- [ ] **Step 3: scraper.py を実装する**

```python
# backend/services/scraper.py
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup

POKEMON_LIST_URL = "https://gamewith.jp/pokemon-champions/546414"
USAGE_RANKING_URL = "https://gamewith.jp/pokemon-champions/555373"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PokemonChampionsTool/1.0)"}


class GameWithScraper:
    def __init__(self, sprites_dir: Path, request_interval: float = 2.0):
        self.sprites_dir = Path(sprites_dir)
        self.request_interval = request_interval

    def _fetch(self, url: str) -> BeautifulSoup:
        time.sleep(self.request_interval)
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")

    def _download_sprite(self, url: str, filename: str) -> str:
        """スプライト画像をダウンロードして保存パスを返す"""
        time.sleep(self.request_interval)
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        path = self.sprites_dir / filename
        path.write_bytes(resp.content)
        return str(path.relative_to(self.sprites_dir.parent))

    def fetch_pokemon_list(self) -> list[dict]:
        """
        内定ポケモン一覧ページをスクレイピングして各ポケモンの基本情報を返す。
        実際のHTMLの構造に応じてselectorを調整すること。
        返り値: PokemonInfo に変換可能なdictのリスト
        """
        soup = self._fetch(POKEMON_LIST_URL)
        results = []
        # NOTE: GameWithの実際のHTML構造に合わせてセレクタを調整する
        # 以下は骨格実装 — 実ページ確認後に修正が必要
        for row in soup.select("table.pokemon-table tr.pokemon-row"):
            try:
                name = row.select_one(".pokemon-name").get_text(strip=True)
                sprite_url = row.select_one("img.pokemon-sprite")["src"]
                sprite_filename = f"{name}.png"
                sprite_path = self._download_sprite(sprite_url, sprite_filename)

                results.append({
                    "name": name,
                    "sprite_path": sprite_path,
                    # 残フィールドは実ページのHTML構造を確認して実装
                })
            except (AttributeError, KeyError):
                continue
        return results

    def fetch_usage_ranking(self) -> list[dict]:
        """
        使用率ランキングTOP30ページをスクレイピングして各ポケモンの詳細を返す。
        返り値: UsageEntry に変換可能なdictのリスト
        """
        soup = self._fetch(USAGE_RANKING_URL)
        results = []
        # NOTE: 各ポケモンの詳細ページURLを取得して順に巡回する
        detail_links = soup.select("a.pokemon-detail-link")[:30]
        for link in detail_links:
            detail_url = link["href"]
            if not detail_url.startswith("http"):
                detail_url = f"https://gamewith.jp{detail_url}"
            detail = self._fetch_pokemon_detail(detail_url)
            if detail:
                results.append(detail)
        return results

    def _fetch_pokemon_detail(self, url: str) -> dict | None:
        """ポケモン詳細ページから型情報を取得する"""
        soup = self._fetch(url)
        try:
            name = soup.select_one("h1.pokemon-name").get_text(strip=True)
            # NOTE: 実ページのHTML構造を確認して各フィールドのセレクタを実装
            return {"name": name}
        except AttributeError:
            return None
```

- [ ] **Step 4: テストが通ることを確認する**

```bash
pytest tests/test_scraper.py -v
```

Expected: 全テスト PASSED

- [ ] **Step 5: コミットする**

```bash
git add backend/services/scraper.py backend/tests/test_scraper.py
git commit -m "feat: GameWithスクレイパー骨格実装"
```

> **注意:** `fetch_pokemon_list` と `fetch_pokemon_detail` のセレクタは、実際のGameWithページのHTMLを `requests.get` で取得して確認しながら実装する。セレクタは仕様変更で壊れやすいため、取得後すぐに `pokemon_list.json` へ保存してキャッシュとして使う。

---

## Task 5: 画像認識（OpenCVテンプレートマッチング）

**Files:**
- Create: `backend/services/image_recognition.py`
- Create: `backend/tests/test_image_recognition.py`
- Create: `backend/tests/fixtures/` (テスト用画像を置くディレクトリ)

- [ ] **Step 1: テストを書く**

```python
# backend/tests/test_image_recognition.py
import numpy as np
import pytest
import cv2
from pathlib import Path
from services.image_recognition import ImageRecognizer, RecognitionResult


@pytest.fixture
def sprites_dir(tmp_path):
    """テスト用スプライト画像（32x32 の単色PNG）を作成する"""
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
    # 黒背景にリザードンスプライトを6箇所貼り付けたテスト画像を作成
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
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
pytest tests/test_image_recognition.py -v
```

Expected: `ModuleNotFoundError: No module named 'services.image_recognition'`

- [ ] **Step 3: image_recognition.py を実装する**

```python
# backend/services/image_recognition.py
import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RecognitionResult:
    names: list[str]          # 認識されたポケモン名（6体分）
    confidences: list[float]  # 各スロットの一致スコア（0〜1）


class ImageRecognizer:
    def __init__(self, sprites_dir: Path | str, top_n: int = 6, threshold: float = 0.6):
        self.sprites_dir = Path(sprites_dir)
        self.top_n = top_n
        self.threshold = threshold
        self.templates: dict[str, np.ndarray] = self._load_templates()

    def _load_templates(self) -> dict[str, np.ndarray]:
        templates = {}
        for path in self.sprites_dir.glob("*.png"):
            img = cv2.imread(str(path))
            if img is not None:
                templates[path.stem] = img
        return templates

    def recognize(self, image: np.ndarray) -> RecognitionResult:
        """
        画像中からテンプレートマッチングで上位 top_n 体のポケモンを検出する。
        見つかったポケモンが top_n 未満の場合は空文字で埋める。
        """
        matches: list[tuple[str, float, tuple]] = []

        for name, template in self.templates.items():
            h, w = template.shape[:2]
            if image.shape[0] < h or image.shape[1] < w:
                continue
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val >= self.threshold:
                matches.append((name, float(max_val), max_loc))

        # スコア降順に並べてtop_n個取得
        matches.sort(key=lambda x: x[1], reverse=True)
        top = matches[:self.top_n]

        names = [m[0] for m in top]
        confidences = [m[1] for m in top]

        # 6体に満たない場合は空文字で埋める
        while len(names) < 6:
            names.append("")
            confidences.append(0.0)

        return RecognitionResult(names=names, confidences=confidences)

    @classmethod
    def from_bytes(cls, image_bytes: bytes, **kwargs) -> "ImageRecognizer":
        """バイト列からImageRecognizerを生成するファクトリ（ルーターから使う）"""
        return cls(**kwargs)

    def recognize_from_bytes(self, image_bytes: bytes) -> RecognitionResult:
        arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return self.recognize(image)
```

- [ ] **Step 4: テストが通ることを確認する**

```bash
pytest tests/test_image_recognition.py -v
```

Expected: 全テスト PASSED

- [ ] **Step 5: コミットする**

```bash
git add backend/services/image_recognition.py backend/tests/test_image_recognition.py
git commit -m "feat: OpenCVテンプレートマッチング画像認識実装"
```

---

## Task 6: AI選出予想（Claude API）

**Files:**
- Create: `backend/services/ai_predictor.py`
- Create: `backend/tests/test_ai_predictor.py`

- [ ] **Step 1: テストを書く（Claude APIをモック）**

```python
# backend/tests/test_ai_predictor.py
from unittest.mock import MagicMock, patch
import pytest
from services.ai_predictor import AIPredictor
from models.pokemon import UsageData, UsageEntry, RatedItem, EvSpread
from models.party import PredictionResult


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
        collected_at="2026-04-26T12:00:00",
        season=1,
        regulation="レギュレーションA",
        source_updated_at="2026-04-25",
        pokemon=[entry],
    )


@patch("services.ai_predictor.anthropic.Anthropic")
def test_predict_returns_three_patterns(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=MOCK_CLAUDE_RESPONSE)]
    )

    predictor = AIPredictor(api_key="test-key")
    result = predictor.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )

    assert isinstance(result, PredictionResult)
    assert len(result.patterns) == 3
    assert len(result.patterns[0].pokemon) == 3
    assert result.patterns[0].pokemon[0] == "リザードン"


@patch("services.ai_predictor.anthropic.Anthropic")
def test_predict_calls_api_with_both_parties(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=MOCK_CLAUDE_RESPONSE)]
    )

    predictor = AIPredictor(api_key="test-key")
    predictor.predict(
        opponent_party=["リザードン", "カメックス", "フシギバナ", "ピカチュウ", "イワーク", "ゲンガー"],
        my_party=["カビゴン", "ラプラス", "サンダー", "ゲンガー", "フシギバナ", "ストライク"],
        usage_data=_make_usage_data(),
    )

    call_kwargs = mock_client.messages.create.call_args
    prompt_text = str(call_kwargs)
    assert "リザードン" in prompt_text
    assert "カビゴン" in prompt_text
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
pytest tests/test_ai_predictor.py -v
```

Expected: `ModuleNotFoundError: No module named 'services.ai_predictor'`

- [ ] **Step 3: ai_predictor.py を実装する**

```python
# backend/services/ai_predictor.py
import json
import re
import anthropic
from models.pokemon import UsageData
from models.party import PredictionResult, PredictionPattern

SYSTEM_PROMPT = """あなたはポケモンチャンピオンズの対戦分析AIです。
与えられた情報をもとに、相手プレイヤーが選出しそうなポケモン3体のパターンを3つ予想してください。

回答は必ず以下の形式で出力してください：
パターン1: ポケモン名A, ポケモン名B, ポケモン名C
パターン2: ポケモン名D, ポケモン名E, ポケモン名F
パターン3: ポケモン名G, ポケモン名H, ポケモン名I

可能性が高い順に並べてください。確率の数値は不要です。"""


class AIPredictor:
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

- [ ] **Step 4: テストが通ることを確認する**

```bash
pytest tests/test_ai_predictor.py -v
```

Expected: 全テスト PASSED

- [ ] **Step 5: コミットする**

```bash
git add backend/services/ai_predictor.py backend/tests/test_ai_predictor.py
git commit -m "feat: Claude API選出予想実装"
```

---

## Task 7: FastAPI ルーター

**Files:**
- Create: `backend/routers/data.py`
- Create: `backend/routers/recognition.py`
- Create: `backend/routers/prediction.py`
- Create: `backend/routers/party.py`
- Modify: `backend/main.py`
- Create: `backend/tests/test_routers.py`

- [ ] **Step 1: テストを書く**

```python
# backend/tests/test_routers.py
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

    with patch("routers.recognition.recognizer") as mock_rec:
        mock_rec.recognize_from_bytes.return_value = mock_result
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/recognize",
                files={"file": ("test.jpg", b"fake-image-data", "image/jpeg")},
            )
    assert resp.status_code == 200
    assert len(resp.json()["names"]) == 6
```

- [ ] **Step 2: テストが失敗することを確認する**

```bash
pytest tests/test_routers.py -v
```

Expected: `ImportError` または `404`

- [ ] **Step 3: party.py ルーターを実装する**

```python
# backend/routers/party.py
import uuid
from fastapi import APIRouter
from services.data_manager import DataManager
from models.party import Party, PartiesData
from pydantic import BaseModel

router = APIRouter(prefix="/api/party", tags=["party"])
_manager = DataManager()


class PartyCreateRequest(BaseModel):
    name: str
    pokemon: list[str]


@router.get("")
def list_parties():
    return _manager.load_parties()


@router.post("")
def create_party(req: PartyCreateRequest):
    data = _manager.load_parties()
    party = Party(id=str(uuid.uuid4()), name=req.name, pokemon=req.pokemon)
    data.parties.append(party)
    _manager.save_parties(data)
    return party


@router.put("/{party_id}")
def update_party(party_id: str, req: PartyCreateRequest):
    data = _manager.load_parties()
    for i, p in enumerate(data.parties):
        if p.id == party_id:
            data.parties[i] = Party(id=party_id, name=req.name, pokemon=req.pokemon)
            _manager.save_parties(data)
            return data.parties[i]
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Party not found")


@router.delete("/{party_id}")
def delete_party(party_id: str):
    data = _manager.load_parties()
    data.parties = [p for p in data.parties if p.id != party_id]
    _manager.save_parties(data)
    return {"ok": True}


@router.post("/last-used/{party_id}")
def set_last_used(party_id: str):
    data = _manager.load_parties()
    data.last_used_id = party_id
    _manager.save_parties(data)
    return {"ok": True}
```

- [ ] **Step 4: recognition.py ルーターを実装する**

```python
# backend/routers/recognition.py
from fastapi import APIRouter, UploadFile, File
from services.image_recognition import ImageRecognizer
from pathlib import Path

router = APIRouter(prefix="/api", tags=["recognition"])
_sprites_dir = Path(__file__).parent.parent / "data" / "sprites"
recognizer = ImageRecognizer(sprites_dir=_sprites_dir)


@router.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = recognizer.recognize_from_bytes(image_bytes)
    return {"names": result.names, "confidences": result.confidences}
```

- [ ] **Step 5: prediction.py ルーターを実装する**

```python
# backend/routers/prediction.py
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.ai_predictor import AIPredictor
from services.data_manager import DataManager

router = APIRouter(prefix="/api", tags=["prediction"])
_manager = DataManager()


class PredictRequest(BaseModel):
    opponent_party: list[str]
    my_party: list[str]


@router.post("/predict")
def predict(req: PredictRequest):
    usage_data = _manager.load_latest_usage_data()
    if usage_data is None:
        raise HTTPException(status_code=400, detail="使用率データがありません。先にデータを取得してください。")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY が設定されていません。")

    predictor = AIPredictor(api_key=api_key)
    result = predictor.predict(
        opponent_party=req.opponent_party,
        my_party=req.my_party,
        usage_data=usage_data,
    )
    return result
```

- [ ] **Step 6: data.py ルーターを実装する**

```python
# backend/routers/data.py
from fastapi import APIRouter, BackgroundTasks
from services.scraper import GameWithScraper
from services.data_manager import DataManager
from models.pokemon import PokemonList, UsageData
from pathlib import Path

router = APIRouter(prefix="/api/data", tags=["data"])
_manager = DataManager()
_sprites_dir = Path(__file__).parent.parent / "data" / "sprites"


@router.post("/fetch")
def fetch_data(background_tasks: BackgroundTasks):
    """GameWithからデータを取得する（バックグラウンド実行）"""
    background_tasks.add_task(_do_fetch)
    return {"status": "started"}


def _do_fetch():
    scraper = GameWithScraper(sprites_dir=_sprites_dir)
    # pokemon_list取得（スクレイパー実装後に有効化）
    # pokemon_data = scraper.fetch_pokemon_list()
    # usage_data = scraper.fetch_usage_ranking()
    # _manager.save_pokemon_list(...)
    # _manager.save_usage_data(...)
    pass


@router.get("/status")
def data_status():
    pokemon_list = _manager.load_pokemon_list()
    usage_data = _manager.load_latest_usage_data()
    return {
        "pokemon_list_available": pokemon_list is not None,
        "usage_data_available": usage_data is not None,
        "usage_data_date": usage_data.collected_at if usage_data else None,
    }


@router.get("/pokemon/names")
def get_pokemon_names():
    """フロントエンドのオートコンプリート用にポケモン名一覧を返す"""
    pokemon_list = _manager.load_pokemon_list()
    if pokemon_list is None:
        return {"names": []}
    names = [p.name for p in pokemon_list.pokemon]
    # メガシンカ名も含める
    for p in pokemon_list.pokemon:
        if p.mega_evolution:
            names.append(p.mega_evolution.name)
    return {"names": names}
```

- [ ] **Step 7: main.py にルーターを登録する**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from routers import data, recognition, prediction, party

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

sprites_dir = Path(__file__).parent / "data" / "sprites"
sprites_dir.mkdir(parents=True, exist_ok=True)
app.mount("/sprites", StaticFiles(directory=str(sprites_dir)), name="sprites")


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 8: テストが通ることを確認する**

```bash
pytest tests/test_routers.py -v
```

Expected: 全テスト PASSED

- [ ] **Step 9: コミットする**

```bash
git add backend/routers/ backend/main.py backend/tests/test_routers.py
git commit -m "feat: FastAPIルーター実装"
```

---

## Task 8: フロントエンド プロジェクトセットアップ

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`

- [ ] **Step 1: Vite + React + TypeScript プロジェクトを作成する**

```bash
cd /path/to/pokemon-champions-tool
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

- [ ] **Step 2: Tailwind を設定する**

```js
// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: { extend: {} },
  plugins: [],
}
```

```css
/* frontend/src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 3: vite.config.ts にプロキシを設定する（CORS回避）**

```ts
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/sprites': 'http://localhost:8000',
    },
  },
})
```

- [ ] **Step 4: 型定義ファイルを作成する**

```ts
// frontend/src/types/index.ts
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

export interface PredictionPattern {
  pokemon: string[]
}

export interface PredictionResult {
  patterns: PredictionPattern[]
}

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

- [ ] **Step 5: APIクライアントを作成する**

```ts
// frontend/src/api/client.ts
const BASE = '/api'

export async function recognize(file: File): Promise<{ names: string[]; confidences: number[] }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/recognize`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function predict(opponentParty: string[], myParty: string[]) {
  const res = await fetch(`${BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ opponent_party: opponentParty, my_party: myParty }),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getParties() {
  const res = await fetch(`${BASE}/party`)
  return res.json()
}

export async function createParty(name: string, pokemon: string[]) {
  const res = await fetch(`${BASE}/party`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, pokemon }),
  })
  return res.json()
}

export async function updateParty(id: string, name: string, pokemon: string[]) {
  const res = await fetch(`${BASE}/party/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, pokemon }),
  })
  return res.json()
}

export async function deleteParty(id: string) {
  await fetch(`${BASE}/party/${id}`, { method: 'DELETE' })
}

export async function setLastUsedParty(id: string) {
  await fetch(`${BASE}/party/last-used/${id}`, { method: 'POST' })
}

export async function fetchData() {
  const res = await fetch(`${BASE}/data/fetch`, { method: 'POST' })
  return res.json()
}

export async function getDataStatus() {
  const res = await fetch(`${BASE}/data/status`)
  return res.json()
}

export async function getPokemonNames(): Promise<string[]> {
  const res = await fetch(`${BASE}/data/pokemon/names`)
  const data = await res.json()
  return data.names as string[]
}
```

- [ ] **Step 6: useDarkMode フックを作成する**

```ts
// frontend/src/hooks/useDarkMode.ts
import { useEffect, useState } from 'react'

export function useDarkMode() {
  const [dark, setDark] = useState(() => localStorage.getItem('dark-mode') === 'true')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('dark-mode', String(dark))
  }, [dark])

  return { dark, toggle: () => setDark(d => !d) }
}
```

- [ ] **Step 7: App.tsx を作成する**

```tsx
// frontend/src/App.tsx
import { useState } from 'react'
import { useDarkMode } from './hooks/useDarkMode'
import PredictionPage from './pages/PredictionPage'
import PartyPage from './pages/PartyPage'
import Header from './components/Header'

type Page = 'prediction' | 'party'

export default function App() {
  const { dark, toggle } = useDarkMode()
  const [page, setPage] = useState<Page>('prediction')

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <Header dark={dark} onToggleDark={toggle} page={page} onChangePage={setPage} />
      <main className="p-4">
        {page === 'prediction' ? <PredictionPage /> : <PartyPage />}
      </main>
    </div>
  )
}
```

- [ ] **Step 8: Header + DarkModeToggle を作成する**

```tsx
// frontend/src/components/DarkModeToggle.tsx
interface Props { dark: boolean; onToggle: () => void }

export default function DarkModeToggle({ dark, onToggle }: Props) {
  return (
    <button
      onClick={onToggle}
      className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 text-sm"
      aria-label="ダークモード切り替え"
    >
      {dark ? '☀️ ライト' : '🌙 ダーク'}
    </button>
  )
}
```

```tsx
// frontend/src/components/Header.tsx
import DarkModeToggle from './DarkModeToggle'

interface Props {
  dark: boolean
  onToggleDark: () => void
  page: 'prediction' | 'party'
  onChangePage: (p: 'prediction' | 'party') => void
}

export default function Header({ dark, onToggleDark, page, onChangePage }: Props) {
  return (
    <header className="border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <span className="font-bold text-lg">🎮 ポケチャン支援ツール</span>
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
        </nav>
      </div>
      <DarkModeToggle dark={dark} onToggle={onToggleDark} />
    </header>
  )
}
```

- [ ] **Step 9: 空のページコンポーネントを作成する（後のタスクで実装）**

```tsx
// frontend/src/pages/PredictionPage.tsx
export default function PredictionPage() {
  return <div className="text-center py-8">選出予想ページ（実装中）</div>
}
```

```tsx
// frontend/src/pages/PartyPage.tsx
export default function PartyPage() {
  return <div className="text-center py-8">パーティ登録ページ（実装中）</div>
}
```

- [ ] **Step 10: フロントエンドが起動することを確認する**

```bash
cd frontend && npm run dev
```

Expected: http://localhost:5173 でヘッダーとダークモードトグルが表示される。

- [ ] **Step 11: コミットする**

```bash
git add frontend/
git commit -m "feat: フロントエンドプロジェクトセットアップ + ダークモード"
```

---

## Task 9: PokemonSlot コンポーネント（入力枠）

**Files:**
- Create: `frontend/src/components/PokemonSlot.tsx`

- [ ] **Step 1: PokemonSlot を実装する**

ポケモン名をテキスト検索で選択でき、選択後はスプライト画像と名前を表示する1枠コンポーネント。

```tsx
// frontend/src/components/PokemonSlot.tsx
import { useState, useEffect, useRef } from 'react'

interface Props {
  value: string
  onChange: (name: string) => void
  pokemonNames: string[]  // 候補リスト（内定ポケモン一覧）
}

export default function PokemonSlot({ value, onChange, pokemonNames }: Props) {
  const [query, setQuery] = useState(value)
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => { setQuery(value) }, [value])

  // クリック外でドロップダウンを閉じる
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const filtered = query
    ? pokemonNames.filter(n => n.includes(query)).slice(0, 8)
    : pokemonNames.slice(0, 8)

  const select = (name: string) => {
    onChange(name)
    setQuery(name)
    setOpen(false)
  }

  return (
    <div ref={ref} className="relative">
      {value ? (
        // 選択済み: スプライト+名前表示
        <div
          className="flex flex-col items-center gap-1 p-2 rounded-lg border-2 border-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 cursor-pointer"
          onClick={() => { onChange(''); setQuery('') }}
          title="クリックでリセット"
        >
          <img
            src={`/sprites/${value}.png`}
            alt={value}
            className="w-12 h-12 object-contain"
            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
          />
          <span className="text-xs font-bold">{value}</span>
        </div>
      ) : (
        // 未選択: テキスト入力+ドロップダウン
        <div className="rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 p-2">
          <input
            className="w-full text-sm bg-transparent outline-none placeholder-gray-400"
            placeholder="ポケモン名..."
            value={query}
            onChange={e => { setQuery(e.target.value); setOpen(true) }}
            onFocus={() => setOpen(true)}
          />
          {open && filtered.length > 0 && (
            <ul className="absolute z-10 top-full left-0 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
              {filtered.map(name => (
                <li
                  key={name}
                  className="flex items-center gap-2 px-3 py-2 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 cursor-pointer text-sm"
                  onMouseDown={() => select(name)}
                >
                  <img
                    src={`/sprites/${name}.png`}
                    alt={name}
                    className="w-8 h-8 object-contain"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                  />
                  {name}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: ブラウザで動作確認する**

バックエンドを起動した状態で http://localhost:5173 を開き、PokemonSlot が正しく描画されることを後続のタスクで確認する（現時点ではページに組み込まれていない）。

- [ ] **Step 3: コミットする**

```bash
git add frontend/src/components/PokemonSlot.tsx
git commit -m "feat: PokemonSlotコンポーネント（テキスト検索・スプライト表示）"
```

---

## Task 10: PartyInput と PredictionPage

**Files:**
- Create: `frontend/src/components/PartyInput.tsx`
- Modify: `frontend/src/pages/PredictionPage.tsx`

- [ ] **Step 1: PartyInput を実装する**

```tsx
// frontend/src/components/PartyInput.tsx
import { useRef } from 'react'
import PokemonSlot from './PokemonSlot'
import { recognize } from '../api/client'

interface Props {
  party: string[]             // 6体のポケモン名（空文字は未入力）
  onChange: (party: string[]) => void
  pokemonNames: string[]
}

export default function PartyInput({ party, onChange, pokemonNames }: Props) {
  const fileRef = useRef<HTMLInputElement>(null)

  const update = (index: number, name: string) => {
    const next = [...party]
    next[index] = name
    onChange(next)
  }

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const result = await recognize(file)
      onChange(result.names.slice(0, 6))
    } catch (err) {
      alert(`画像認識に失敗しました: ${err}`)
    } finally {
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400">相手パーティ（6体）</h2>
        <button
          onClick={() => fileRef.current?.click()}
          className="text-xs px-3 py-1 rounded bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600"
        >
          📷 画像から入力
        </button>
        <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleImageUpload} />
      </div>
      <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
        {party.map((name, i) => (
          <PokemonSlot key={i} value={name} onChange={v => update(i, v)} pokemonNames={pokemonNames} />
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: PredictionPage を実装する**

```tsx
// frontend/src/pages/PredictionPage.tsx
import { useState, useEffect } from 'react'
import PartyInput from '../components/PartyInput'
import PredictionResult from '../components/PredictionResult'
import { predict, getParties, setLastUsedParty, getPokemonNames } from '../api/client'
import type { PredictionResult as PredResult, Party, PartiesData } from '../types'

export default function PredictionPage() {
  const [opponentParty, setOpponentParty] = useState<string[]>(Array(6).fill(''))
  const [myParty, setMyParty] = useState<string[]>(Array(6).fill(''))
  const [parties, setParties] = useState<Party[]>([])
  const [selectedPartyId, setSelectedPartyId] = useState<string | null>(null)
  const [result, setResult] = useState<PredResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pokemonNames, setPokemonNames] = useState<string[]>([])

  // ポケモン名一覧とパーティを初期ロード
  useEffect(() => {
    getPokemonNames().then(setPokemonNames)
    getParties().then((data: PartiesData) => {
      setParties(data.parties)
      if (data.last_used_id) {
        const last = data.parties.find(p => p.id === data.last_used_id)
        if (last) {
          setMyParty([...last.pokemon, ...Array(6).fill('')].slice(0, 6))
          setSelectedPartyId(last.id)
        }
      }
    })
  }, [])

  const handlePartySelect = async (party: Party) => {
    setMyParty([...party.pokemon, ...Array(6).fill('')].slice(0, 6))
    setSelectedPartyId(party.id)
    await setLastUsedParty(party.id)
  }

  const handlePredict = async () => {
    const opponent = opponentParty.filter(Boolean)
    const my = myParty.filter(Boolean)
    if (opponent.length < 6) { setError('相手パーティを6体入力してください'); return }
    if (my.length < 6) { setError('自分のパーティを6体入力してください'); return }
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

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <PartyInput party={opponentParty} onChange={setOpponentParty} pokemonNames={pokemonNames} />

      {/* 自分のパーティ選択 */}
      <div>
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400 mb-2">自分のパーティ</h2>
        <div className="flex gap-2 flex-wrap">
          {parties.map(p => (
            <button
              key={p.id}
              onClick={() => handlePartySelect(p)}
              className={`px-3 py-1 rounded text-sm border ${selectedPartyId === p.id ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'}`}
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        onClick={handlePredict}
        disabled={loading}
        className="w-full py-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-bold disabled:opacity-50"
      >
        {loading ? '予想中...' : '🔮 選出予想する'}
      </button>

      {result && <PredictionResult result={result} />}
    </div>
  )
}
```

- [ ] **Step 3: コミットする**

```bash
git add frontend/src/components/PartyInput.tsx frontend/src/pages/PredictionPage.tsx
git commit -m "feat: PartyInput（画像アップロード対応）とPredictionPage実装"
```

---

## Task 11: 選出予想結果 UI（PokemonCard / PatternCard / PredictionResult）

**Files:**
- Create: `frontend/src/components/PokemonCard.tsx`
- Create: `frontend/src/components/PatternCard.tsx`
- Create: `frontend/src/components/PredictionResult.tsx`

- [ ] **Step 1: PokemonCard を実装する**

横長: 画像左・型情報右 / 縦長: 画像上・型情報下 のレスポンシブ対応。

```tsx
// frontend/src/components/PokemonCard.tsx
import type { UsageEntry } from '../types'

interface Props {
  name: string
  usage: UsageEntry | null
}

function StatRow({ label, items }: { label: string; items: { name: string; rate: number }[] }) {
  return (
    <div className="mb-1">
      <span className="text-xs font-bold" style={{ color: labelColor(label) }}>{label}</span>
      {items.map((item, i) => (
        <div key={i} className="flex justify-between text-xs">
          <span>{item.name}</span>
          <span className={`font-bold ${i === 0 ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500'}`}>
            {item.rate}%
          </span>
        </div>
      ))}
    </div>
  )
}

function labelColor(label: string) {
  const map: Record<string, string> = {
    'わざ': '#7c3aed', '持ち物': '#0369a1', '特性': '#065f46', '性格': '#92400e',
    '個体値': '#be185d', '能力ポイント': '#b45309',
  }
  return map[label] ?? '#374151'
}

export default function PokemonCard({ name, usage }: Props) {
  const ivText = usage?.ivs
    ? Object.entries(usage.ivs).map(([k, v]) => `${k}${v}`).join(' ')
    : 'H31 A31 B31 C31 D31 S31'

  return (
    <div className="flex-1 rounded-lg p-3 bg-gray-50 dark:bg-gray-800 min-w-0">
      {/* レスポンシブ: sm以上で横並び、sm未満で縦並び */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* 画像 + 名前 */}
        <div className="flex-shrink-0 text-center">
          <img
            src={`/sprites/${name}.png`}
            alt={name}
            className="w-14 h-14 object-contain mx-auto"
            onError={(e) => { (e.target as HTMLImageElement).src = '/sprites/unknown.png' }}
          />
          <div className="text-xs font-bold mt-1">{name}</div>
        </div>
        {/* 型情報 */}
        <div className="flex-1 min-w-0 text-xs">
          {usage ? (
            <>
              <StatRow label="わざ" items={usage.moves.slice(0, 3)} />
              <StatRow label="持ち物" items={usage.items.slice(0, 2)} />
              <StatRow label="特性" items={usage.abilities.slice(0, 2)} />
              <StatRow label="性格" items={usage.natures.slice(0, 2)} />
              <div className="mb-1">
                <span className="text-xs font-bold" style={{ color: '#be185d' }}>個体値</span>
                <div className="text-xs font-mono bg-pink-50 dark:bg-pink-900/20 rounded px-1 py-0.5">{ivText}</div>
              </div>
              <div className="mb-1">
                <span className="text-xs font-bold" style={{ color: '#b45309' }}>能力ポイント</span>
                {usage.evs.slice(0, 2).map((ev, i) => (
                  <div key={i} className="flex justify-between text-xs">
                    <span className="font-mono bg-yellow-50 dark:bg-yellow-900/20 rounded px-1 text-xs">
                      {Object.entries(ev.spread).filter(([, v]) => v > 0).map(([k, v]) => `${k}${v}`).join(' ')}
                    </span>
                    <span className={`font-bold ${i === 0 ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500'}`}>
                      {ev.rate}%
                    </span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <span className="text-gray-400">使用率データなし</span>
          )}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: PatternCard を実装する**

```tsx
// frontend/src/components/PatternCard.tsx
import PokemonCard from './PokemonCard'
import type { PredictionPattern, UsageEntry } from '../types'

interface Props {
  pattern: PredictionPattern
  index: number
  usageMap: Record<string, UsageEntry>
}

export default function PatternCard({ pattern, index, usageMap }: Props) {
  const isTop = index === 0
  return (
    <div className={`rounded-xl p-4 border-2 ${isTop ? 'border-indigo-500' : 'border-gray-200 dark:border-gray-700'}`}>
      <div className={`font-bold text-sm mb-3 ${isTop ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500'}`}>
        {isTop ? '🏆 ' : ''}パターン{index + 1}{isTop ? '（最有力）' : ''}
      </div>
      <div className="flex gap-2">
        {pattern.pokemon.map((name, i) => (
          <PokemonCard key={i} name={name} usage={usageMap[name] ?? null} />
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: PredictionResult を実装する**

```tsx
// frontend/src/components/PredictionResult.tsx
import PatternCard from './PatternCard'
import type { PredictionResult, UsageEntry } from '../types'

interface Props {
  result: PredictionResult
  usageEntries?: UsageEntry[]
}

export default function PredictionResultView({ result, usageEntries = [] }: Props) {
  const usageMap: Record<string, UsageEntry> = Object.fromEntries(
    usageEntries.map(e => [e.name, e])
  )

  return (
    <div className="space-y-4">
      <h2 className="font-bold text-lg">選出予想</h2>
      {result.patterns.map((pattern, i) => (
        <PatternCard key={i} pattern={pattern} index={i} usageMap={usageMap} />
      ))}
    </div>
  )
}
```

- [ ] **Step 4: PredictionPage に usageEntries を渡すよう修正する**

`PredictionPage.tsx` の `predict` 呼び出し後に usageData も取得し、`PredictionResult` へ渡す：

```tsx
// PredictionPage.tsx 内のhandlePredictを修正
const handlePredict = async () => {
  // ... (既存の検証コード)
  setLoading(true)
  try {
    const [predRes, statusRes] = await Promise.all([
      predict(opponent, my),
      fetch('/api/data/status').then(r => r.json()),
    ])
    setResult(predRes)
  } catch (e) {
    setError(String(e))
  } finally {
    setLoading(false)
  }
}
```

また、PredictionResult コンポーネントの呼び出し部分に `usageEntries` を渡す（使用率データはAPIから別途取得して state で保持する）。

- [ ] **Step 5: コミットする**

```bash
git add frontend/src/components/PokemonCard.tsx frontend/src/components/PatternCard.tsx frontend/src/components/PredictionResult.tsx
git commit -m "feat: 選出予想結果UI（PokemonCard/PatternCard/PredictionResult）"
```

---

## Task 12: PartyPage（パーティ登録）

**Files:**
- Modify: `frontend/src/pages/PartyPage.tsx`

- [ ] **Step 1: PartyPage を実装する**

```tsx
// frontend/src/pages/PartyPage.tsx
import { useState, useEffect } from 'react'
import PokemonSlot from '../components/PokemonSlot'
import { getParties, createParty, updateParty, deleteParty, getPokemonNames } from '../api/client'
import type { Party } from '../types'

export default function PartyPage() {
  const [parties, setParties] = useState<Party[]>([])
  const [editing, setEditing] = useState<Party | null>(null)
  const [name, setName] = useState('')
  const [pokemon, setPokemon] = useState<string[]>(Array(6).fill(''))
  const [pokemonNames, setPokemonNames] = useState<string[]>([])

  useEffect(() => {
    reload()
    getPokemonNames().then(setPokemonNames)
  }, [])

  const reload = () => getParties().then(d => setParties(d.parties))

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
      await updateParty(editing.id, name, filled)
    } else {
      await createParty(name, filled)
    }
    startNew()
    reload()
  }

  const remove = async (id: string) => {
    if (!confirm('削除しますか？')) return
    await deleteParty(id)
    reload()
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="font-bold text-xl">パーティ登録</h1>

      {/* 登録フォーム */}
      <div className="border rounded-xl p-4 space-y-4 dark:border-gray-700">
        <h2 className="font-bold text-sm text-gray-600 dark:text-gray-400">
          {editing ? `編集中: ${editing.name}` : '新規パーティ'}
        </h2>
        <input
          className="w-full border rounded px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600"
          placeholder="パーティ名"
          value={name}
          onChange={e => setName(e.target.value)}
        />
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
          {pokemon.map((p, i) => (
            <PokemonSlot
              key={i}
              value={p}
              onChange={v => { const next = [...pokemon]; next[i] = v; setPokemon(next) }}
              pokemonNames={pokemonNames}
            />
          ))}
        </div>
        <div className="flex gap-2">
          <button onClick={save} className="px-4 py-2 rounded bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold">
            {editing ? '更新' : '登録'}
          </button>
          {editing && (
            <button onClick={startNew} className="px-4 py-2 rounded border dark:border-gray-600 text-sm">
              キャンセル
            </button>
          )}
        </div>
      </div>

      {/* 登録済みパーティ一覧 */}
      <div className="space-y-3">
        {parties.map(p => (
          <div key={p.id} className="border rounded-xl p-4 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold">{p.name}</span>
              <div className="flex gap-2">
                <button onClick={() => startEdit(p)} className="text-sm text-indigo-600 hover:underline">編集</button>
                <button onClick={() => remove(p.id)} className="text-sm text-red-500 hover:underline">削除</button>
              </div>
            </div>
            <div className="flex gap-2">
              {p.pokemon.map((name, i) => (
                <div key={i} className="text-center">
                  <img
                    src={`/sprites/${name}.png`}
                    alt={name}
                    className="w-10 h-10 object-contain mx-auto"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                  />
                  <div className="text-xs">{name}</div>
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

- [ ] **Step 2: ブラウザでパーティ登録・編集・削除を確認する**

1. http://localhost:5173 でパーティ登録ページに移動
2. パーティ名を入力し6体を選択して登録
3. 登録済みパーティが一覧に表示されること
4. 編集・削除が動作すること
5. 選出予想ページでパーティが選択できること

- [ ] **Step 3: コミットする**

```bash
git add frontend/src/pages/PartyPage.tsx
git commit -m "feat: パーティ登録ページ実装"
```

---

## Task 13: E2Eフロー動作確認

このタスクはコードの変更ではなく手動での動作確認です。

- [ ] **Step 1: バックエンドとフロントエンドを起動する**

```bash
# ターミナル1
cd backend && source .venv/bin/activate && uvicorn main:app --reload

# ターミナル2
cd frontend && npm run dev
```

- [ ] **Step 2: データ取得が動作することを確認する**

```bash
curl -X POST http://localhost:8000/api/data/fetch
curl http://localhost:8000/api/data/status
```

Expected: `{"pokemon_list_available": true, "usage_data_available": true, ...}`

> スクレイパーのセレクタが未実装の場合は、`backend/data/pokemon_list.json` と `backend/data/usage_rates/YYYY-MM-DD.json` をダミーデータで手動作成して先に進む。

- [ ] **Step 3: 選出予想のE2Eフローを確認する**

1. パーティ登録ページで自分のパーティを登録する
2. 選出予想ページで相手パーティを6体入力する
3. 「選出予想する」ボタンをクリックする
4. 3パターンの予想結果が表示されることを確認する
5. 各ポケモンカードにわざ・持ち物・特性・性格・個体値・能力ポイントが表示されることを確認する

- [ ] **Step 4: レスポンシブレイアウトを確認する**

ブラウザの幅を変えて以下を確認:
- 横長: ポケモンカード内で画像左・型情報右
- 縦長（600px以下）: 画像上・型情報下

- [ ] **Step 5: ダークモードを確認する**

ヘッダーのトグルボタンでダークモードに切り替え、すべての要素が見やすく表示されることを確認する。リロード後もダークモードが維持されることを確認する。

- [ ] **Step 6: 最終コミットをする**

```bash
git add -A
git commit -m "feat: 全機能実装完了"
```
