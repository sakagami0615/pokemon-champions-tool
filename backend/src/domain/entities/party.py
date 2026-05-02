from typing import Optional
from pydantic import BaseModel


class Party(BaseModel):
    id: str
    name: str
    pokemons: list[str]


class PartiesData(BaseModel):
    parties: list[Party]
    last_used_id: Optional[str] = None


class PredictionPattern(BaseModel):
    pokemons: list[str]


class PredictionResult(BaseModel):
    patterns: list[PredictionPattern]
