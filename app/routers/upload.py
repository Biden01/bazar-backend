import os
import uuid

import aiofiles
from fastapi import APIRouter, UploadFile, File

from app.dependencies import CurrentUser

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("")
async def upload_file(user: CurrentUser, file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    async with aiofiles.open(path, "wb") as f:
        content = await file.read()
        await f.write(content)

    url = f"/uploads/{filename}"
    return {"id": filename, "url": url}
