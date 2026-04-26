import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from fastapi import HTTPException


@dataclass
class RecognitionResult:
    names: list[str]
    confidences: list[float]


class ImageRecognizer:
    def __init__(self, sprites_dir: Path | str, top_n: int = 6, threshold: float = 0.6):
        self.sprites_dir = Path(sprites_dir)
        self.top_n = top_n
        self.threshold = threshold
        self.templates: dict[str, np.ndarray] = self._load_templates()

    def _load_templates(self) -> dict[str, np.ndarray]:
        templates = {}
        for path in self.sprites_dir.glob("*.png"):
            img = cv2.imread(str(path))
            if img is not None:
                templates[path.stem] = img
        return templates

    def recognize(self, image: np.ndarray) -> RecognitionResult:
        matches: list[tuple[str, float, tuple]] = []

        for name, template in self.templates.items():
            h, w = template.shape[:2]
            if image.shape[0] < h or image.shape[1] < w:
                continue
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val >= self.threshold:
                matches.append((name, float(max_val), max_loc))

        matches.sort(key=lambda x: x[1], reverse=True)
        top = matches[:self.top_n]

        names = [m[0] for m in top]
        confidences = [m[1] for m in top]

        while len(names) < 6:
            names.append("")
            confidences.append(0.0)

        return RecognitionResult(names=names, confidences=confidences)

    def recognize_from_bytes(self, image_bytes: bytes) -> RecognitionResult:
        if not image_bytes:
            raise HTTPException(status_code=400, detail="無効な画像ファイルです。PNG または JPEG 形式の画像をアップロードしてください。")
        arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=400, detail="無効な画像ファイルです。PNG または JPEG 形式の画像をアップロードしてください。")
        return self.recognize(image)
