from domain.repositories.image_recognizer import (
    IImageRecognizer,
    RecognitionResult,
    SelectionRecognitionResult,
)


class RecognitionUseCase:
    def __init__(self, recognizer: IImageRecognizer):
        self.recognizer = recognizer

    def recognize(self, image_bytes: bytes) -> RecognitionResult:
        return self.recognizer.recognize_from_bytes(image_bytes)

    def recognize_selection(self, image_bytes: bytes) -> SelectionRecognitionResult:
        return self.recognizer.recognize_selection_from_bytes(image_bytes)
