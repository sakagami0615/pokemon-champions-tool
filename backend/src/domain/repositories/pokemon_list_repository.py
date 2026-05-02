from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.pokemon import PokemonList


class IPokemonListRepository(ABC):
    @abstractmethod
    def get_pokemon_list(self) -> Optional[PokemonList]: ...

    @abstractmethod
    def save_pokemon_list(self, data: PokemonList) -> None: ...
