from pathlib import Path
from infrastructure.external.image_recognition import ImageRecognizer, RecognitionResult, InvalidImageError


class RecognitionUseCase:
    def __init__(self, sprites_dir: Path | str):
        self.recognizer = ImageRecognizer(sprites_dir=sprites_dir)

    def recognize(self, image_bytes: bytes) -> RecognitionResult:
        return self.recognizer.recognize_from_bytes(image_bytes)
