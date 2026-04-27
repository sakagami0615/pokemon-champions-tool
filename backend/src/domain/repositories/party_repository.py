from abc import ABC, abstractmethod
from domain.entities.party import PartiesData


class IPartyRepository(ABC):
    @abstractmethod
    def get_all(self) -> PartiesData: ...

    @abstractmethod
    def save(self, data: PartiesData) -> None: ...
