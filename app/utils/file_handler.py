from fastapi import UploadFile, HTTPException
from core.config import settings
import tempfile
import os

async def save_uploaded_file(file: UploadFile) -> str:
    file_size = file.size
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds {settings.MAX_FILE_SIZE} bytes")
    
    if not file.filename.endswith(".php"):
        raise HTTPException(status_code=400, detail="Only PHP files are accepted")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".php") as temp_file:
        content = await file.read()
        temp_file.write(content)
        return temp_file.name