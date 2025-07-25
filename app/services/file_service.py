from fastapi.responses import JSONResponse
from utils.file_handler import save_upload_file_temporarily
import tempfile
import os
import zipfile
import tarfile
from services.language_detector import detect_language_script, detect_languages_in_folder
from services.analyze_service import analyze_complexity, analyze_complexity_folder, analyze_redundancy, analyze_redundancy_folder, analyze_convention, analyze_convention_folder, analyze_dead_code, analyze_dead_code_folder

async def handle_upload(file):
    filename = file.filename.lower()
    #Fichier python unique(.py)
    if filename.endswith(".py"):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = await save_upload_file_temporarily(file, temp_dir)

            language = detect_language_script(file_path)
            result = analyze_complexity(file_path)
            result_redundancy = analyze_redundancy(file_path)
            result_convention = analyze_convention(file_path)
            result_dead_code = analyze_dead_code(file_path)
            return JSONResponse(content={
                "status": "success",
                "type": "script",
                "filename": file.filename,
                "saved_to": file_path,
                "language": language,
                "complexity": result,
                "redondancy": result_redundancy,
                "convention": result_convention,
                "dead code": result_dead_code
            })

    #Projet compresse(.zip ou .tar.gz)    
    elif filename.endswith(".zip") or filename.endswith(".tar.gz"):
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = await save_upload_file_temporarily(file, temp_dir)

            #Repertoire temporaire pour extraction
            extract_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)

            #Extraction
            if filename.endswith(".zip"):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif filename.endswith(".tar.gz"):
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(extract_dir)
        
            languages = detect_languages_in_folder(extract_dir)
            results = analyze_complexity_folder(extract_dir)
            results_redundancy = analyze_redundancy_folder(extract_dir)
            results_convention = analyze_convention_folder(extract_dir)
            results_dead_code = analyze_dead_code_folder(extract_dir)
            return JSONResponse(content={
                "status": "success",
                "type": "project",
                "filename": file.filename,
                "extracted_to": extract_dir,
                "languages_detected": languages,
                "complexity": results,
                "redundancy": results_redundancy,
                "convention": results_convention,
                "dead code": results_dead_code
            })