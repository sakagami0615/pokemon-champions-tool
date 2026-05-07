from abc import ABC, abstractmethod

from domain.entities.prompt_config import PromptConfig


class IPromptConfigRepository(ABC):
    @abstractmethod
    def get_config(self) -> PromptConfig: ...
