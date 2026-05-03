import logging
import re
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pathlib import Path
from pydantic import BaseModel, field_validator
from infrastructure.external.scraper import GameWithScraper
from infrastructure.external.pokemon_list_scraper import PokemonListScraper
from infrastructure.persistence.json_usage_repository import JsonUsageRepository
from infrastructure.persistence.json_pokemon_list_repository import JsonPokemonListRepository
from domain.entities.pokemon import UsageData, UsageEntry
from application.use_cases.scrape_pokemon_list_use_case import ScrapePokemonListUseCase
import application.state.scraping_state as _state

router = APIRouter(prefix="/api/data", tags=["data"])
_usage_repo = JsonUsageRepository()
_pokemon_list_repo = JsonPokemonListRepository()
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
            use_case = ScrapePokemonListUseCase(
                scraper=PokemonListScraper(sprites_dir=_sprites_dir),
                repository=_pokemon_list_repo,
            )
            use_case.execute()
            _logger.info("ポケモン一覧のスクレイピングが完了しました")
        except Exception:
            _logger.exception("ポケモン一覧スクレイピングでエラーが発生しました")

        try:
            scraper = GameWithScraper(sprites_dir=_sprites_dir)
        except Exception:
            _logger.exception("GameWithScraper の初期化に失敗しました")
            return
        _fetch_and_save_usage_data(scraper)
    finally:
        _state.scraping_in_progress = False


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
            pokemons=entries,
        )
        _usage_repo.save_usage_data(usage_data)
        _logger.info("使用率データを保存しました: %d件", len(entries))
    except Exception:
        _logger.exception("fetch_usage_ranking でエラーが発生しました")


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
    pokemon_list = _pokemon_list_repo.get_pokemon_list()
    available_dates = _usage_repo.get_available_dates()
    pokemon_count = (len(pokemon_list.pokemons) + len(pokemon_list.mega_pokemons)) if pokemon_list else 0

    dates_detail = []
    for date in available_dates:
        usage_data = _usage_repo.get_usage_data_by_date(date)
        if usage_data:
            top_pokemon = [{"name": p.name} for p in usage_data.pokemons[:3]]
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


@router.get("/dates")
def get_dates():
    return {"dates": _usage_repo.get_available_dates()}


@router.post("/select-date")
def select_date(req: SelectDateRequest):
    if _usage_repo.get_usage_data_by_date(req.date) is None:
        raise HTTPException(status_code=404, detail=f"{req.date} のデータが存在しません")
    _state.selected_date = req.date
    return {"selected_date": _state.selected_date}


@router.get("/pokemon/names")
def get_pokemon_names():
    if _state.selected_date:
        usage_data = _usage_repo.get_usage_data_by_date(_state.selected_date)
        if usage_data:
            return {"names": [p.name for p in usage_data.pokemons]}
    pokemon_list = _pokemon_list_repo.get_pokemon_list()
    if pokemon_list is None:
        return {"names": []}
    names = [p.name for p in pokemon_list.pokemons] + [p.name for p in pokemon_list.mega_pokemons]
    return {"names": names}
