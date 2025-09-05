from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os

from services.analyze_service import analyze_dead_code
from services.refactor_service.pipeline import apply_refactors

router = APIRouter()
BASE_SESSIONS_PATH = "/tmp/sessions"

@router.get("/{session_id}")
async def refactor_uploaded_file(session_id: str):
    session_path = os.path.join(BASE_SESSIONS_PATH, session_id)
    original_path = os.path.join(session_path, "original")

    if not os.path.exists(original_path):
        raise HTTPException(status_code=404, detail="Session non trouvée")

    # Chercher les fichiers Python
    files = os.listdir(original_path)
    py_files = [f for f in files if f.endswith(".py")]

    if py_files:
        file_path = os.path.join(original_path, py_files[0])

        # Analyse du code mort avant refactor
        report = analyze_dead_code(file_path)

        # Appliquer le refactor
        refactored_dir = os.path.join(session_path, "refactored")
        os.makedirs(refactored_dir, exist_ok=True)

        output_path = apply_refactors(file_path, report, output_dir=refactored_dir)

        # Réanalyser le fichier refactorisé
        new_report = analyze_dead_code(output_path)

        # Lire le contenu des fichiers
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_code = f.read()
            with open(output_path, "r", encoding="utf-8") as f:
                refactored_code = f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Impossible de lire les fichiers de code")

        # Retourner la nouvelle analyse et le code
        response_data = {
            "analysis": new_report,
            "originalCode": original_code,
            "refactoredCode": refactored_code,
        }
        return JSONResponse(content=response_data, status_code=200)

    # Si c’est un projet complet → non supporté
    extract_dir = os.path.join(original_path, "extracted")
    if os.path.exists(extract_dir):
        raise HTTPException(status_code=501, detail="Refactor de projet non encore supporté")

    raise HTTPException(status_code=404, detail="Aucun fichier ou dossier à refactoriser trouvé")
