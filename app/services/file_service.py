import uuid
import os
import zipfile
import tarfile
from fastapi.responses import JSONResponse
from utils.file_handler import save_upload_file_temporarily
from services.language_detector import detect_language_script, detect_languages_in_folder

UPLOAD_BASE_PATH = "/tmp/sessions/"

async def handle_upload(file):
    filename = file.filename.lower()
    session_id = str(uuid.uuid4())

    # Cree structure /tmp/sessions/<session_id>/original/
    session_path = os.path.join(UPLOAD_BASE_PATH, session_id)
    original_path = os.path.join(session_path, "original")
    os.makedirs(original_path, exist_ok=True)

    #Sauvegarder le fichier uploader
    file_path = await save_upload_file_temporarily(file, original_path)

    #Fichier python unique(.py)
    if filename.endswith(".py"):
            language = detect_language_script(file_path)
            return JSONResponse(content={
                "status": "uploaded",
                "session_id": session_id,
                "type": "script",
                "filename": file.filename,
                "saved_to": file_path,
                "language": language,
            })

    #Projet compresse(.zip ou .tar.gz)    
    elif filename.endswith(".zip") or filename.endswith(".tar.gz"):
            #Repertoire temporaire pour extraction
            extract_dir = os.path.join(original_path, "extracted")
            os.makedirs(extract_dir, exist_ok=True)

            #Extraction
            if filename.endswith(".zip"):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif filename.endswith(".tar.gz"):
                with tarfile.open(file_path, 'r:gz') as tar:
                    tar.extractall(extract_dir)
        
            languages = detect_languages_in_folder(extract_dir)
            return JSONResponse(content={
                "status": "uploaded",
                "session_id": session_id,
                "type": "project",
                "filename": file.filename,
                "extracted_to": extract_dir,
                "languages_detected": languages
            })