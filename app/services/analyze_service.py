from radon.complexity import cc_visit, cc_rank
from utils.constants import EXCLUDED_DIRS
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List
import os
import hashlib
import ast
from services.dead_code_ast import analyze_dead_code_ast

#analyse de complexite
def analyze_complexity(file_path, code=None):
    try:
        if code is None:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        blocks = cc_visit(code)
        return [
            {
                "file": file_path,
                "name": block.name,
                "complexity": block.complexity,
                "rank": cc_rank(block.complexity),
                "type": block.__class__.__name__,
                "lineno": block.lineno
            }
        for block in blocks]
    except Exception as e:
        return [{"file": file_path, "error": str(e)}]

#analyse de redondance
def hash_ast_node(node: ast.AST) -> str:
    node_dump = ast.dump(node, annotate_fields=True, include_attributes=False)
    return hashlib.md5(node_dump.encode("utf-8")).hexdigest()

def analyze_redundancy_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Analyse un fichier Python pour détecter les fonctions/classes redondantes
    """
    duplicates = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        hash_map = {}

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                node_hash = hash_ast_node(node)
                if node_hash in hash_map:
                    duplicates.append({
                        "type": "function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "class",
                        "name": node.name,
                        "line": node.lineno,
                        "duplicate_of": hash_map[node_hash]
                    })
                else:
                    hash_map[node_hash] = f"{file_path}:{node.lineno}"
    except Exception as e:
        duplicates.append({"error": str(e), "file": file_path})
    return duplicates

def analyze_redundancy_folder(folder_path: str) -> Dict[str, Any]:
    """
    Analyse tous les fichiers Python d'un dossier pour détecter les doublons
    """
    all_duplicates = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(root, file)
                result = analyze_redundancy_file(file_path)
                if result:
                    all_duplicates[file_path] = result
    return all_duplicates

#analyse de convention non respecte
def analyze_convention(file_path, timeout=30, rcfile=None):
    """
    Analyse le style/conformite
    """
    cmd = ["pylint", file_path, "-f", "json"]
    if rcfile:
        cmd.extend(["--rcfile", rcfile])

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )

        output = result.stdout.strip()
        messages = json.loads(output) if output else []

        return {
            "file": file_path,
            "messages": [
                {
                    "type": msg.get("type"),
                    "symbol": msg.get("symbol"),
                    "message": msg.get("message"),
                    "line": msg.get("line"),
                    "column": msg.get("column")
                }
                for msg in messages
            ],
            "stderr": result.stderr.strip() or None,
            "returncode": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "file": file_path,
            "error": f"Timeout after {timeout}s"
        }
    except Exception as e:
        return {
            "file": file_path,
            "error": str(e)
        }
    
#analyse de code mort pour un simple script
def analyze_dead_code(file_path):
    return analyze_dead_code_ast(file_path)

#analyse de code mort pour un projet .zip
def analyze_dead_code_project(folder_path: str) -> Dict[str, Any]:
    """
    Analyse globale du code mort pour tous les fichiers Python dans un dossier.
    """
    folder = Path(folder_path)
    py_files = [f for f in folder.rglob("*.py") if f.name != "__init__.py"]

    all_functions_defined: Dict[str, str] = {}
    all_variables_defined: Dict[str, str] = {}
    all_functions_called: set = set()
    all_variables_used: set = set()
    file_results: Dict[str, Any] = {}

    for file_path in py_files:
        result = analyze_dead_code_ast(str(file_path))
        file_results[str(file_path)] = result

        for name in result.get("functions_defined", {}):
            all_functions_defined[name] = str(file_path)
        for name in result.get("variables_defined", set()):
            all_variables_defined[name] = str(file_path)

        all_functions_called.update(result.get("functions_called", set()))
        all_variables_used.update(result.get("variables_used", set()))

    # filtrer les faux positifs globaux
    for file_path, result in file_results.items():
        dead_filtered = []
        for warning in result["dead_code"]:
            symbol = warning["symbol"]
            name = warning["message"].split("'")[1]
            if symbol == "unused-function" and name in all_functions_called:
                continue
            if symbol == "unused-variable" and name in all_variables_used:
                continue
            dead_filtered.append(warning)
        file_results[file_path]["dead_code"] = dead_filtered

        # Mettre a jour les stats
        file_results[file_path]["stats"]["unused_functions"] = sum(
            1 for w in dead_filtered if w["symbol"] == "unused-function")
        file_results[file_path]["stats"]["unused_variables"] = sum(
            1 for w in dead_filtered if w["symbol"] == "unused-variable")
        file_results[file_path]["stats"]["unused_imports"] = sum(
            1 for w in dead_filtered if w["symbol"] == "unused-import")

    return file_results

#Analyse complet d'un fichier .py
def full_analyze_script(file_path):
    return({
        "complexity": analyze_complexity(file_path),
        "redundancy": analyze_redundancy_file(file_path),
        "convention": analyze_convention(file_path),
        "dead_code": analyze_dead_code(file_path)
    })

#Analyse d'un dossier .zip
def analyze_folder(folder_path):
    all_results = {}
    #Analyse fichier par fichier
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if file == "__init__.py" or not file.endswith(".py"):
                continue
            file_path = os.path.join(root, file)
            result = full_analyze_script(file_path)  # complexité + convention + dead code fichier
            all_results[file_path] = result

    #Analyse redondance
    redundancy_results = analyze_redundancy_folder(folder_path)
    for file_path, duplicates in redundancy_results.items():
        if file_path in all_results:
            all_results[file_path]["redundancy"] = duplicates
        else:
            all_results[file_path] = {"redundancy": duplicates}

    # Analyse code mort global
    dead_code_results = analyze_dead_code_project(folder_path)
    for file_path, dead_result in dead_code_results.items():
        if file_path in all_results:
            all_results[file_path]["dead_code"] = dead_result["dead_code"]
            all_results[file_path]["stats"] = dead_result["stats"]

    return all_results