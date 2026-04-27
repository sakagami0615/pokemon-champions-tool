from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from application.use_cases.recognition_use_case import RecognitionUseCase
from domain.repositories.image_recognizer import InvalidImageError
from infrastructure.external.image_recognition import ImageRecognizer

router = APIRouter(prefix="/api", tags=["recognition"])
_sprites_dir = Path(__file__).parent.parent.parent.parent / "data" / "sprites"
recognizer = RecognitionUseCase(recognizer=ImageRecognizer(sprites_dir=_sprites_dir))


@router.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    image_bytes = await file.read()
    try:
        result = recognizer.recognize(image_bytes)
    except InvalidImageError:
        raise HTTPException(status_code=400, detail="無効な画像ファイルです。PNG または JPEG 形式の画像をアップロードしてください。")
    return {"names": result.names, "confidences": result.confidences}
