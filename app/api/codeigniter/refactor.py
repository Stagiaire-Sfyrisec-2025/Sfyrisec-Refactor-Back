from fastapi import APIRouter, HTTPException, Query
from schemas.refactor import RefactorResponse
from services.codeigniter.refactor import codeigniter_refactor
from utils.file_handler import save_uploaded_file
from fastapi import UploadFile, File

router = APIRouter()

@router.post("/refactor", response_model=RefactorResponse)
async def refactor(file: UploadFile = File(...), version: str = Query("4", description="Target CodeIgniter version (e.g., 4)")):
    if not file.filename.endswith(".php"):
        raise HTTPException(status_code=400, detail="Only PHP files are accepted")
    
    temp_file_path = await save_uploaded_file(file)
    try:
        refactored_code, logs = codeigniter_refactor菜
        return {"refactored_code": refactored_code, "logs": logs, "framework": "codeigniter", "version": version}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refactoring error: {str(e)}")