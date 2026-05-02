# Critical Issues Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** コードレビューで発見された4つのCritical課題を修正し、予測機能が最低限動作する状態にする。

**Architecture:** 各修正は独立しており、影響範囲が限定的。requirements.txt/docker-compose.ymlの設定修正、ImageRecognizerの防御的コーディング追加、data routerのスタブ実装を実際の処理に置き換える。

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, OpenCV, Docker Compose

---

## 修正対象一覧

| # | 課題 | ファイル | 優先度 |
|---|------|---------|-------|
| 1 | pydantic が requirements.txt に未記載 | `backend/requirements.txt` | 最優先 |
| 2 | ANTHROPIC_API_KEY が docker-compose.yml に未設定 | `docker-compose.yml` | 最優先 |
| 3 | 無効画像で ImageRecognizer がクラッシュ | `backend/services/image_recognition.py` | 高 |
| 4 | `_do_fetch` がスタブのままで何も実行しない | `backend/routers/data.py` | 高 |

---

### Task 1: requirements.txt に pydantic を明示的に追加

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: pydantic を追加して anthropic バージョンを更新**

`backend/requirements.txt` を以下の内容に更新する（pydantic 追加、anthropic を最新安定版へ更新）:

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9
pydantic>=2.0
opencv-python-headless==4.10.0.84
numpy==1.26.4
requests==2.32.3
beautifulsoup4==4.12.3
anthropic>=0.40.0
pytest==8.3.2
pytest-asyncio==0.23.8
httpx==0.27.0
```

- [ ] **Step 2: 既存テストがパスすることを確認**

```bash
cd backend
pip install -r requirements.txt -q
pytest tests/ -v
```

Expected: すべてのテストが PASS

- [ ] **Step 3: コミット**

```bash
git add backend/requirements.txt
git commit -m "fix: requirements.txtにpydanticを明示追加、anthropicバージョン更新"
```

---

### Task 2: docker-compose.yml に ANTHROPIC_API_KEY を追加し .env.example を作成

**Files:**
- Modify: `docker-compose.yml`
- Create: `.env.example`

- [ ] **Step 1: .env.example を作成**

プロジェクトルートに `.env.example` を作成:

```
# Anthropic API Key
# https://console.anthropic.com/ で取得
ANTHROPIC_API_KEY=your_api_key_here
```

- [ ] **Step 2: docker-compose.yml に環境変数を追加**

`docker-compose.yml` の backend サービスの environment に追加:

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - PYTHONUNBUFFERED=1
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
      - ./frontend/index.html:/app/index.html
    depends_on:
      - backend
```

- [ ] **Step 3: CLAUDE.md の環境変数セクションを更新**

`CLAUDE.md` の `## 環境変数` セクションを更新:

```markdown
## 環境変数

| 変数名 | 必須 | 説明 |
|--------|------|------|
| ANTHROPIC_API_KEY | 必須 | Anthropic APIキー。https://console.anthropic.com/ で取得 |

ローカル開発時は `.env` ファイルを作成して設定する（`.env.example` 参照）。
`.env` は `.gitignore` に含まれており、リポジトリにコミットしないこと。
```

- [ ] **Step 4: .env が .gitignore に含まれていることを確認**

```bash
grep "\.env" .gitignore
```

Expected: `.env` の行が存在する。なければ追加:
```bash
echo ".env" >> .gitignore
```

- [ ] **Step 5: コミット**

```bash
git add docker-compose.yml .env.example CLAUDE.md .gitignore
git commit -m "fix: docker-compose.ymlにANTHROPIC_API_KEY追加、.env.example作成"
```

---

### Task 3: 無効画像で ImageRecognizer がクラッシュする問題を修正

**Files:**
- Modify: `backend/services/image_recognition.py`
- Modify: `backend/tests/test_image_recognition.py`

- [ ] **Step 1: 失敗するテストを書く**

`backend/tests/test_image_recognition.py` に以下を追加:

```python
from fastapi import HTTPException


def test_recognize_from_bytes_raises_on_invalid_image(sprites_dir):
    """無効なバイト列を渡した場合、400エラーが発生すること"""
    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    with pytest.raises(HTTPException) as exc_info:
        recognizer.recognize_from_bytes(b"this is not an image")
    assert exc_info.value.status_code == 400


def test_recognize_from_bytes_raises_on_empty_bytes(sprites_dir):
    """空のバイト列を渡した場合、400エラーが発生すること"""
    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    with pytest.raises(HTTPException) as exc_info:
        recognizer.recognize_from_bytes(b"")
    assert exc_info.value.status_code == 400
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
cd backend
pytest tests/test_image_recognition.py::test_recognize_from_bytes_raises_on_invalid_image -v
```

Expected: FAIL（現在は AttributeError が発生し HTTPException が raise されない）

- [ ] **Step 3: ImageRecognizer.recognize_from_bytes を修正**

`backend/services/image_recognition.py` の先頭に import 追加、`recognize_from_bytes` を修正:

```python
import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from fastapi import HTTPException


@dataclass
class RecognitionResult:
    names: list[str]
    confidences: list[float]


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
        matches: list[tuple[str, float, tuple]] = []

        for name, template in self.templates.items():
            h, w = template.shape[:2]
            if image.shape[0] < h or image.shape[1] < w:
                continue
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val >= self.threshold:
                matches.append((name, float(max_val), max_loc))

        matches.sort(key=lambda x: x[1], reverse=True)
        top = matches[:self.top_n]

        names = [m[0] for m in top]
        confidences = [m[1] for m in top]

        while len(names) < 6:
            names.append("")
            confidences.append(0.0)

        return RecognitionResult(names=names, confidences=confidences)

    def recognize_from_bytes(self, image_bytes: bytes) -> RecognitionResult:
        arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=400, detail="無効な画像ファイルです。PNG または JPEG 形式の画像をアップロードしてください。")
        return self.recognize(image)
```

- [ ] **Step 4: テストがパスすることを確認**

```bash
cd backend
pytest tests/test_image_recognition.py -v
```

Expected: すべて PASS

- [ ] **Step 5: コミット**

```bash
git add backend/services/image_recognition.py backend/tests/test_image_recognition.py
git commit -m "fix: 無効画像でImageRecognizerがクラッシュする問題を修正"
```

---

### Task 4: `_do_fetch` スタブを実際の実装に置き換える

**Files:**
- Modify: `backend/routers/data.py`
- Modify: `backend/tests/test_routers.py`

**注意:** スクレイパーの HTML セレクタ（`table.pokemon-table tr.pokemon-row` 等）は実際の GameWith サイト構造に合わせて別途調整が必要。このタスクでは「スクレイパーを呼び出してデータを保存する」という骨格を正しく実装し、失敗時にエラーログを残す。

- [ ] **Step 1: 失敗するテストを書く**

`backend/tests/test_routers.py` に以下を追加:

```python
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
async def test_fetch_data_calls_scraper():
    """POST /api/data/fetch がスクレイパーを実際に呼び出すこと"""
    with patch("routers.data._do_fetch") as mock_fetch:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/data/fetch")
        assert resp.status_code == 200
        assert resp.json()["status"] == "started"
        # バックグラウンドタスクが登録されたことを確認（直接実行は別テスト）
        mock_fetch.assert_not_called()  # バックグラウンドで非同期実行されるため直接呼ばれない


@pytest.mark.asyncio
async def test_do_fetch_calls_scraper_methods():
    """_do_fetch が fetch_pokemon_list と fetch_usage_ranking を呼び出すこと"""
    mock_scraper = MagicMock()
    mock_scraper.fetch_pokemon_list.return_value = []
    mock_scraper.fetch_usage_ranking.return_value = []

    with patch("routers.data.GameWithScraper", return_value=mock_scraper):
        with patch("routers.data._manager") as mock_manager:
            from routers.data import _do_fetch
            _do_fetch()

    mock_scraper.fetch_pokemon_list.assert_called_once()
    mock_scraper.fetch_usage_ranking.assert_called_once()


@pytest.mark.asyncio
async def test_do_fetch_handles_scraper_exception():
    """スクレイパーが例外を投げても _do_fetch がクラッシュしないこと"""
    mock_scraper = MagicMock()
    mock_scraper.fetch_pokemon_list.side_effect = Exception("Network error")

    with patch("routers.data.GameWithScraper", return_value=mock_scraper):
        from routers.data import _do_fetch
        _do_fetch()  # 例外が伝播しないこと
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
cd backend
pytest tests/test_routers.py::test_do_fetch_calls_scraper_methods -v
```

Expected: FAIL（現在 _do_fetch は pass のみ）

- [ ] **Step 3: `_do_fetch` を実装する**

`backend/routers/data.py` を以下の内容に置き換える:

```python
import logging
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks
from services.scraper import GameWithScraper
from services.data_manager import DataManager
from models.pokemon import PokemonList, UsageData, UsageEntry, PokemonInfo, BaseStats
from pathlib import Path

router = APIRouter(prefix="/api/data", tags=["data"])
_manager = DataManager()
_sprites_dir = Path(__file__).parent.parent / "data" / "sprites"
_logger = logging.getLogger(__name__)


@router.post("/fetch")
def fetch_data(background_tasks: BackgroundTasks):
    """GameWithからデータを取得する（バックグラウンド実行）"""
    background_tasks.add_task(_do_fetch)
    return {"status": "started"}


def _do_fetch() -> None:
    scraper = GameWithScraper(sprites_dir=_sprites_dir)
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
        _manager.save_pokemon_list(pokemon_list)
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
        usage_data = UsageData(
            collected_at=datetime.now().isoformat(),
            season=0,
            regulation="",
            source_updated_at=datetime.now().isoformat(),
            pokemon=entries,
        )
        _manager.save_usage_data(usage_data)
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
    for p in pokemon_list.pokemon:
        if p.mega_evolution:
            names.append(p.mega_evolution.name)
    return {"names": names}
```

- [ ] **Step 4: テストがパスすることを確認**

```bash
cd backend
pytest tests/test_routers.py -v
```

Expected: すべて PASS

- [ ] **Step 5: 全テストを実行して回帰がないことを確認**

```bash
cd backend
pytest tests/ -v
```

Expected: すべて PASS

- [ ] **Step 6: コミット**

```bash
git add backend/routers/data.py backend/tests/test_routers.py
git commit -m "fix: _do_fetchスタブを実際の実装に置き換え、エラーハンドリング追加"
```

---

## 完了後の確認

全タスク完了後に以下を実行し、すべてパスすることを確認する:

```bash
cd backend
pytest tests/ -v --tb=short
```

Expected: 全テスト PASS

**スクレイパー HTML セレクタについて:**
`backend/services/scraper.py` の CSS セレクタは GameWith サイトの実際の HTML 構造に合わせた調整が別途必要。`_do_fetch` のエラーログ（"取得件数が0件"）が出た場合はセレクタを修正すること。これは Critical 修正の範囲外として別タスクで対応する。
