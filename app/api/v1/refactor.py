from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os

from services.analyze_service import full_analyze_script
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

        # Analyse complète avant refactor
        # Note: `apply_refactors` utilise un rapport partiel, nous continuons de l'utiliser
        # pour la logique de refactorisation, mais nous ferons une analyse complète après.
        initial_analysis_for_refactor = full_analyze_script(file_path)

        # Appliquer le refactor
        refactored_dir = os.path.join(session_path, "refactored")
        os.makedirs(refactored_dir, exist_ok=True)

        # `apply_refactors` n'a besoin que du rapport de code mort.
        # Nous utilisons une analyse ciblée pour cela.
        from services.analyze_service import analyze_dead_code
        dead_code_report = analyze_dead_code(file_path)


        output_path = apply_refactors(file_path, {"dead_code": dead_code_report}, output_dir=refactored_dir)

        # Réanalyser le fichier refactorisé avec une analyse complète
        new_report_data = full_analyze_script(output_path)

        # Formatter le rapport pour correspondre à ce que le frontend attend
        new_report = {
            os.path.basename(output_path): new_report_data
        }


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
