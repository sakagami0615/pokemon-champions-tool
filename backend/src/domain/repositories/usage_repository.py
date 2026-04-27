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
