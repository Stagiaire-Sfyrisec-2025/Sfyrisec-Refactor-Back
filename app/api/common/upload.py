from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.file_handler import save_uploaded_file

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".php"):
        raise HTTPException(status_code=400, detail="Only PHP files are accepted")
    
    temp_file_path = await save_uploaded_file(file)
    return {"file_path": temp_file_path}