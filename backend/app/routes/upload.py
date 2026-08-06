import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings

router = APIRouter(prefix="/api/upload", tags=["upload"])
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Seules les images sont acceptées")
    ext = Path(file.filename or "img.jpg").suffix or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    path = UPLOAD_DIR / filename
    path.write_bytes(await file.read())
    return {"url": f"/uploads/{filename}"}
