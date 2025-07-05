from fastapi import APIRouter, HTTPException, Query
from schemas.refactor import RefactorResponse
from services.symfony.refactor import symfony_refactor
from utils.file_handler import save_uploaded_file
from fastapi import UploadFile, File

router = APIRouter()

@router.post("/refactor", response_model=RefactorResponse)
async def refactor(file: UploadFile = File(...), version: str = Query("6", description="Target Symfony version (e.g., 6)")):
    if not file.filename.endswith(".php"):
        raise HTTPException(status_code=400, detail="Only PHP files are accepted")
    
    temp_file_path = await save_uploaded_file(file)
    try:
        refactored_code, logs = symfony_refactor(temp_file_path, version)
        return {"refactored_code": refactored_code, "logs": logs, "framework": "symfony", "version": version}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refactoring error: {str(e)}")