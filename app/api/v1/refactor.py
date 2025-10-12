from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import subprocess
import sys

from services.analyze_service import full_analyze_script, analyze_folder

router = APIRouter()
BASE_SESSIONS_PATH = "/tmp/sessions"


def refactor_codebase(path: str):
    """
    Applique isort et autopep8 récursivement à un dossier ou fichier Python,
    en excluant automatiquement les environnements virtuels (venv) et autres répertoires inutiles.
    """
    python_executable = sys.executable

    if not os.path.exists(path):
        print(f"⚠️ Chemin introuvable : {path}")
        return

    try:
        # 1️⃣ Trier les imports sur tout le projet, sauf dans le venv
        subprocess.run(
            [
                python_executable, "-m", "isort",
                path, "--recursive", "--skip", "venv"
            ],
            check=True,
            capture_output=True,
            text=True
        )

        # 2️⃣ Appliquer autopep8 sur tout le projet, en excluant le dossier venv
        subprocess.run(
            [
                python_executable, "-m", "autopep8",
                "--in-place", "--recursive", "--aggressive", "--aggressive",
                "--exclude", "venv",
                path
            ],
            check=True,
            capture_output=True,
            text=True
        )

        print(f"✅ Refactoring terminé pour {path}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur durant le refactoring : {e.stderr}")
        raise
    except Exception as e:
        print(f"⚠️ Exception inattendue : {e}")
        raise


@router.get("/{session_id}")
async def refactor_uploaded_file(session_id: str):
    """
    Endpoint principal : refactorise le fichier ou projet uploadé, puis renvoie les analyses avant/après.
    """
    session_path = os.path.join(BASE_SESSIONS_PATH, session_id)
    original_path = os.path.join(session_path, "original")
    refactored_path = os.path.join(session_path, "refactored")

    if not os.path.exists(original_path):
        raise HTTPException(status_code=404, detail="Session non trouvée")

    # Nettoyage/refabrication du dossier refactored
    if os.path.exists(refactored_path):
        shutil.rmtree(refactored_path)
    os.makedirs(refactored_path, exist_ok=True)

    # ✅ Cas 1 : fichier Python unique
    py_files = [f for f in os.listdir(original_path) if f.endswith(".py")]
    if py_files:
        original_file_path = os.path.join(original_path, py_files[0])
        refactored_file_path = os.path.join(refactored_path, py_files[0])
        shutil.copy2(original_file_path, refactored_file_path)

        initial_analysis = full_analyze_script(original_file_path)

        try:
            refactor_codebase(refactored_file_path)
            final_analysis = full_analyze_script(refactored_file_path)

            with open(original_file_path, "r", encoding="utf-8") as f:
                original_code = f.read()
            with open(refactored_file_path, "r", encoding="utf-8") as f:
                refactored_code = f.read()

            return JSONResponse(
                content={
                   "analysis": {os.path.basename(refactored_file_path): final_analysis or {}},
    "originalCode": original_code,
    "refactoredCode": refactored_code,
                },
                status_code=200
            )

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            error_detail = e.stderr if isinstance(e, subprocess.CalledProcessError) else str(e)
            raise HTTPException(status_code=500, detail=f"Erreur durant le refactoring: {error_detail}")

    # ✅ Cas 2 : projet complet
    extract_dir = os.path.join(original_path, "extracted")
    if os.path.exists(extract_dir):
        initial_analysis = analyze_folder(extract_dir)

        shutil.copytree(extract_dir, refactored_path, dirs_exist_ok=True)

        if not any(fname.endswith(".py") for _, _, files in os.walk(refactored_path) for fname in files):
            raise HTTPException(status_code=400, detail="Le projet ne contient aucun fichier Python.")

        try:
            refactor_codebase(refactored_path)
            final_analysis = analyze_folder(refactored_path)

            # Lecture des contenus de fichiers
            original_codes = {}
            for root, _, files in os.walk(extract_dir):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, extract_dir)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                original_codes[relative_path] = f.read()
                        except Exception:
                            original_codes[relative_path] = "# Impossible de lire le fichier"

            refactored_codes = {}
            for root, _, files in os.walk(refactored_path):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, refactored_path)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                refactored_codes[relative_path] = f.read()
                        except Exception:
                            refactored_codes[relative_path] = "# Impossible de lire le fichier"

            # Combinaison des données
            files_data = {
                file: {
                    "originalCode": original_codes.get(file, ""),
                    "refactoredCode": refactored_codes.get(file, "")
                }
                for file in original_codes
            }

            return JSONResponse(
                content={
                    "status": "refactored",
                    "session_id": session_id,
                    "type": "project",
                    "initial_analysis": initial_analysis,
                    "final_analysis": final_analysis,
                    "files": files_data
                },
                status_code=200
            )

        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Erreur durant le refactoring du projet: {e.stderr}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Une erreur inattendue est survenue: {str(e)}")

    raise HTTPException(status_code=404, detail="Aucun fichier ou dossier à refactoriser trouvé")
