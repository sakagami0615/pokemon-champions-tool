import numpy as np
import pytest
import cv2
from infrastructure.external.image_recognition import ImageRecognizer
from domain.repositories.image_recognizer import RecognitionResult, InvalidImageError, SelectionRecognitionResult


@pytest.fixture
def sprites_dir(tmp_path):
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
    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    with pytest.raises(InvalidImageError):
        recognizer.recognize_from_bytes(b"this is not an image")


def test_recognize_from_bytes_raises_on_empty_bytes(sprites_dir):
    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    with pytest.raises(InvalidImageError):
        recognizer.recognize_from_bytes(b"")


def test_recognize_selection_from_bytes_returns_both_parties(sprites_dir):
    bg = np.zeros((400, 1000, 3), dtype=np.uint8)
    charmander = cv2.imread(str(sprites_dir / "リザードン.png"))
    blastoise = cv2.imread(str(sprites_dir / "カメックス.png"))
    # 左リージョン（x=50 は 1000 の 5% < 40%）
    bg[50:82, 50:82] = charmander
    # 右リージョン（x=700 は 1000 の 70% > 65%）
    bg[50:82, 700:732] = blastoise

    recognizer = ImageRecognizer(sprites_dir=sprites_dir, top_n=1)
    encoded = cv2.imencode(".png", bg)[1].tobytes()
    result = recognizer.recognize_selection_from_bytes(encoded)

    assert isinstance(result, SelectionRecognitionResult)
    assert result.my_party.names[0] == "リザードン"
    assert result.opponent_party.names[0] == "カメックス"


def test_recognize_selection_from_bytes_raises_on_empty(sprites_dir):
    recognizer = ImageRecognizer(sprites_dir=sprites_dir)
    with pytest.raises(InvalidImageError):
        recognizer.recognize_selection_from_bytes(b"")
