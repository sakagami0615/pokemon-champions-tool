from domain.repositories.image_recognizer import (
    IImageRecognizer,
    SelectionRecognitionResult,
)


class RecognitionUseCase:
    def __init__(self, recognizer: IImageRecognizer):
        self.recognizer = recognizer

    def recognize_selection(self, image_bytes: bytes) -> SelectionRecognitionResult:
        return self.recognizer.recognize_selection_from_bytes(image_bytes)
