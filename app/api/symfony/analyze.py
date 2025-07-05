from fastapi import APIRouter, HTTPException, Query
from schemas.analysis import AnalysisResponse
from services.symfony.analyzer import symfony_analyze
from utils.file_handler import save_uploaded_file
from fastapi import UploadFile, File

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(file: UploadFile = File(...), version: str = Query("6", description="Symfony version (e.g., 6)")):
    if not file.filename.endswith(".php"):
        raise HTTPException(status_code=400, detail="Only PHP files are accepted")
    
    temp_file_path = await save_uploaded_file(file)
    try:
        analysis_result = symfony_analyze(temp_file_path, version)
        return {"analysis": analysis_result, "framework": "symfony", "version": version}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")