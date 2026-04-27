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
