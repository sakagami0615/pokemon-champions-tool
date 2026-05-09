from abc import ABC, abstractmethod
from dataclasses import dataclass


class InvalidImageError(ValueError):
    pass


@dataclass
class RecognitionResult:
    names: list[str]
    confidences: list[float]


@dataclass
class SelectionRecognitionResult:
    my_party: RecognitionResult
    opponent_party: RecognitionResult


class IImageRecognizer(ABC):
    @abstractmethod
    def recognize_from_bytes(self, image_bytes: bytes) -> RecognitionResult: ...

    @abstractmethod
    def recognize_selection_from_bytes(self, image_bytes: bytes) -> SelectionRecognitionResult: ...
