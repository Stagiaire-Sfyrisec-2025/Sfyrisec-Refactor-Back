from fastapi import APIRouter, UploadFile, File, HTTPException
from services.file_service import handle_upload

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename.lower()

    if filename.endswith(".py") or filename.endswith(".zip") or filename.endswith(".tar.gz"):
        return await handle_upload(file)
    
    raise HTTPException(status_code=404, detail="Extension non supporte: .py, .zip ou tar.gz uniquement")
