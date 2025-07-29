from radon.complexity import cc_visit
from utils.constants import EXCLUDED_DIRS, ALLOWED_EXTENSIONS
import os
import subprocess
import json

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

#analyse de redondance
def sanitize_dict(d):
    """Convertir les sets en listes pour eviter les erreurs JSON"""
    return {
        k: list(v) if isinstance(v, set) else v
        for k, v in d.items()
    }

def analyze_redundancy(file_path):
    try:
        result = subprocess.run(
            ["pylint", file_path, "-f", "json", "--disable=all", "--enable=W0611,W0612,R0801"],
            capture_output=True,
            text=True
        )

        output = result.stdout.strip()

        if not output:
            return [] #Aucune probleme detectee
        
        try:
            messages = json.loads(output)
        except json.JSONDecodeError as e:
            return [{"error": f"JSON decode failed: {str(e)}", "raw_output": output}]

        redundancy_issues = []
        for msg in messages:
                redundancy_issues.append(sanitize_dict({
                    "type": msg.get("symbol"),
                    "line": msg.get("line"),
                    "message": msg.get("message"),
                    "path": msg.get("path"),
                    "message_id": msg.get("message_id")
                }))

        return redundancy_issues
    
    except Exception as e:
        return [{"error": str(e)}]

#analyse de convention non respecte
def analyze_convention(file_path):
    try:
        result = subprocess.run(
            ["pylint", file_path, "-f", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
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
    except Exception as e:
        return {"error": str(e), "file": file_path}

#analyse de code mort
def analyze_dead_code(file_path):
    try:
        result = subprocess.run(
            ["pylint", file_path, "-f", "json", "--disable=all", "--enable=unused-import,unused-variable,unused-wildcard-import,function-redefined"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output = result.stdout.strip()
        if not output:
            return{"file": file_path, "dead_code": []}
        
        messages = json.loads(output)

        dead_code_warning = [
            {
                "line": msg.get("line"),
                "symbol": msg.get("symbol"),
                "message": msg.get("mesage")
            } 
            for msg in messages
        ]

        return {"file": file_path, "dead_code":dead_code_warning}
    except Exception as e:
        return {"error": str(e), "file": file_path}

#Analyse d'un fichier .py
def full_analyze_script(file_path):
    return({
        "complexity": analyze_complexity(file_path),
        "redundancy": analyze_redundancy(file_path),
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
