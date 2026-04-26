from fastapi import APIRouter, BackgroundTasks
from services.scraper import GameWithScraper
from services.data_manager import DataManager
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
    for p in pokemon_list.pokemon:
        if p.mega_evolution:
            names.append(p.mega_evolution.name)
    return {"names": names}
