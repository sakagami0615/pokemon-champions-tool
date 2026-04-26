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
