from domain.repositories.image_recognizer import IImageRecognizer, RecognitionResult


class RecognitionUseCase:
    def __init__(self, recognizer: IImageRecognizer):
        self.recognizer = recognizer

    def recognize(self, image_bytes: bytes) -> RecognitionResult:
        return self.recognizer.recognize_from_bytes(image_bytes)
