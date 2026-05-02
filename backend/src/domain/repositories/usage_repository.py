from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.pokemon import UsageData


class IUsageRepository(ABC):
    @abstractmethod
    def get_usage_data(self) -> Optional[UsageData]: ...

    @abstractmethod
    def save_usage_data(self, data: UsageData) -> None: ...

    @abstractmethod
    def get_available_dates(self) -> list[str]: ...

    @abstractmethod
    def get_usage_data_by_date(self, date: str) -> Optional[UsageData]: ...
