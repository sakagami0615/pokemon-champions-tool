from fastapi import APIRouter, UploadFile, File
from services.image_recognition import ImageRecognizer
from pathlib import Path

router = APIRouter(prefix="/api", tags=["recognition"])
_sprites_dir = Path(__file__).parent.parent / "data" / "sprites"
recognizer = ImageRecognizer(sprites_dir=_sprites_dir)


@router.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = recognizer.recognize_from_bytes(image_bytes)
    return {"names": result.names, "confidences": result.confidences}
