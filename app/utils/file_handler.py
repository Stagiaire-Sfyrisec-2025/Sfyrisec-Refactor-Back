import os
import shutil
import tempfile
from fastapi import UploadFile

async def save_upload_file_temporarily(file: UploadFile, destination_folder: str) -> str:
    os.makedirs(destination_folder, exist_ok=True)
    filename = os.path.basename(file.filename)
    file_path = os.path.join(destination_folder, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path