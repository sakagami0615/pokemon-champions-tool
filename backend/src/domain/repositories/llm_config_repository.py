from abc import ABC, abstractmethod
from domain.entities.llm_config import LLMConfig


class ILLMConfigRepository(ABC):
    @abstractmethod
    def get_config(self) -> LLMConfig: ...

    @abstractmethod
    def save_config(self, config: LLMConfig) -> None: ...
