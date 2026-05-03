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


class PokemonInfo(BaseModel):
    pokedex_id: int
    name: str
    types: list[str]
    base_stats: BaseStats
    height_m: float
    weight_kg: float
    low_kick_power: int
    abilities: list[str]
    no_effect_types: list[str]
    quarter_damage_types: list[str]
    half_damage_types: list[str]
    double_damage_types: list[str]
    quad_damage_types: list[str]
    sprite_path: str


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
    pokemons: list[UsageEntry]


class PokemonList(BaseModel):
    collected_at: str
    pokemons: list[PokemonInfo]
    mega_pokemons: list[PokemonInfo]
