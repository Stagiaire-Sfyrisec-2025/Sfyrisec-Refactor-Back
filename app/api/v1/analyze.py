from fastapi import APIRouter, HTTPException
from services.analyze_service import full_analyze_script, analyze_folder
import os

router = APIRouter()
BASE_SESSIONS_PATH = "/tmp/sessions"

@router.get("/{session_id}")
async def analyze_uploaded_file(session_id: str):
    session_path = os.path.join(BASE_SESSIONS_PATH, session_id)
    original_path = os.path.join(session_path, "original")

    if not os.path.exists(original_path):
        raise HTTPException(status_code=404, detail="Session non trouvee")
    
    # Cas fichier .py
    files = os.listdir(original_path)
    py_files = [f for f in files if f.endswith(".py")]

    if py_files:
        file_path = os.path.join(original_path, py_files[0])
        result = full_analyze_script(file_path)
        return{
            "status": "analyzed",
            "type": "script",
            "session_id": session_id,
            "result": result
        }
    
    # Cas projet extrait
    extract_dir = os.path.join(original_path, "extracted")
    if os.path.exists(extract_dir):
        results = analyze_folder(extract_dir)
        return {
            "status": "analyzed",
            "type": "project",
            "session_id": session_id,
            "results": results
        }
    
    raise HTTPException(status_code=404, detail="Aucun fichier ou dossier analysable trouve")