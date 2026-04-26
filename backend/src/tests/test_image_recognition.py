import numpy as np
import pytest
import cv2
from pathlib import Path
from services.image_recognition import ImageRecognizer, RecognitionResult, InvalidImageError


@pytest.fixture
def sprites_dir(tmp_path):
    """テスト用スプライト画像（32x32 の単色PNG）を作成する"""
    for name, color in [
        ("リザードン", (0, 100, 255)),
        ("カメックス", (255, 100, 0)),
        ("フシギバナ", (0, 200, 0)),
    ]:
        img = np.full((32, 32, 3), color, dtype=np.uint8)
        cv2.imwrite(str(tmp_path / f"{name}.png"), img)
    return tmp_path


def test_recognizer_loads_sprites(sprites_dir):
    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    assert len(recognizer.templates) == 3
    assert "リザードン" in recognizer.templates


def test_recognize_returns_result_with_six_slots(sprites_dir):
    # 黒背景にリザードンスプライトを6箇所貼り付けたテスト画像を作成
    bg = np.zeros((400, 800, 3), dtype=np.uint8)
    sprite = cv2.imread(str(sprites_dir / "リザードン.png"))
    positions = [(50, 50), (150, 50), (250, 50), (350, 50), (450, 50), (550, 50)]
    for x, y in positions:
        bg[y:y+32, x:x+32] = sprite

    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    result = recognizer.recognize(bg)

    assert isinstance(result, RecognitionResult)
    assert len(result.names) == 6


def test_recognize_identifies_correct_pokemon(sprites_dir):
    bg = np.zeros((400, 800, 3), dtype=np.uint8)
    sprite = cv2.imread(str(sprites_dir / "リザードン.png"))
    bg[50:82, 50:82] = sprite

    recognizer = ImageRecognizer(sprites_dir=sprites_dir, top_n=1)
    result = recognizer.recognize(bg)

    assert result.names[0] == "リザードン"


def test_recognize_from_bytes_raises_on_invalid_image(sprites_dir):
    """無効なバイト列を渡した場合、InvalidImageError が発生すること"""
    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    with pytest.raises(InvalidImageError):
        recognizer.recognize_from_bytes(b"this is not an image")


def test_recognize_from_bytes_raises_on_empty_bytes(sprites_dir):
    """空のバイト列を渡した場合、InvalidImageError が発生すること"""
    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    with pytest.raises(InvalidImageError):
        recognizer.recognize_from_bytes(b"")
