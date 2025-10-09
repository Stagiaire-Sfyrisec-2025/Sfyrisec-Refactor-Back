from radon.complexity import cc_visit
from utils.constants import EXCLUDED_DIRS
import os
import subprocess
import json
from services.dead_code_ast import analyze_dead_code_ast

#analyse de complexite
def analyze_complexity(file_path):
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
        blocks = cc_visit(code)

        for block in blocks:
            results.append({
                "name": block.name,
                "complexity": block.complexity,
                "type": block.__class__.__name__,
                "lineno": block.lineno
            })
    return results

#analyse de convention non respecte
def analyze_convention(file_path):
    try:
        result = subprocess.run(
            ["pylint", file_path, "-f", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()
        if output:
            messages = json.loads(output)
        else:
            messages = []
        return {
            "file": file_path,
            "messages": [
                {
                    "type": msg.get("type"),
                    "symbol": msg.get("symbol"),
                    "message": msg.get("message"),
                    "line": msg.get("line"),
                    "column": msg.get("column")
                } for msg in messages
            ]
        }
    except subprocess.CalledProcessError as e:
        # Pylint peut retourner un status non-zéro même avec une sortie JSON valide
        # (par exemple, s'il trouve des erreurs), donc on essaie de parser stdout quand même.
        try:
            messages = json.loads(e.stdout) if e.stdout else []
            return {
                "file": file_path,
                "messages": messages,
                "error": f"Pylint exited with status {e.returncode}",
                "stderr": e.stderr
            }
        except json.JSONDecodeError:
            return {"error": f"Pylint failed with status {e.returncode} and invalid JSON output.", "file": file_path, "stderr": e.stderr}
    except Exception as e:
        return {"error": str(e), "file": file_path}

#Analyse d'un fichier .py
def full_analyze_script(file_path):
    return({
        "complexity": analyze_complexity(file_path),
        "convention": analyze_convention(file_path),
        "dead_code": analyze_dead_code(file_path)
    })

#Analyse d'un dossier .zip
def analyze_folder(folder_path):
    all_results = {}
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file == "__init__.py" or not file.endswith(".py"):
                continue
            file_path = os.path.join(root, file)
            result = full_analyze_script(file_path)
            all_results[file_path] = result
    return all_results
    
#analyse de code mort
def analyze_dead_code(file_path):
    """Utilise l'analyse AST fiable au lieu de Pylint"""
    return analyze_dead_code_ast(file_path)