from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound
import os
from utils.constants import EXCLUDED_DIRS

#detection pour des lignes de codes
def detect_language_code(code: str) -> str:
    try:
        lexer = guess_lexer(code)
        return lexer.name
    except ClassNotFound:
        return "Unknown"

#detection pour les fichiers simple
def detect_language_script(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        return detect_language_code(code)
    except Exception:
        return "Unknown"
    
#detection pour le projet complet
def detect_languages_in_folder(folder_path: str) -> list[str]:
    languages = set ()
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file.endswith(('.py', '.js', '.java', '.cpp', '.ts', '.cs', '.rb', '.go', '.php', '.html', '.css')):
                lang = detect_language_script(os.path.join(root, file))
                if lang != "Unknown":
                    languages.add(lang)
    return list(languages)