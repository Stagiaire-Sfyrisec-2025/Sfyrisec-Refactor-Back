from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os

from services.analyze_service import analyze_dead_code, analyze_convention, full_analyze_script
from services.refactor_service.pipeline import apply_refactors
from services.refactor_service.dead_code_rule import DeadCodeRefactor
from services.refactor_service.docstring_rule import DocstringRule
from services.refactor_service.format_rule import FormatRule

router = APIRouter()
BASE_SESSIONS_PATH = "/tmp/sessions"

@router.get("/{session_id}")
async def refactor_uploaded_file(session_id: str):
    session_path = os.path.join(BASE_SESSIONS_PATH, session_id)
    original_path = os.path.join(session_path, "original")

    if not os.path.exists(original_path):
        raise HTTPException(status_code=404, detail="Session non trouvée")

    # Cherche les fichiers Python
    files = os.listdir(original_path)
    py_files = [f for f in files if f.endswith(".py")]

    if not py_files:
        # Si c'est un projet complet → non supporté pour le moment
        extract_dir = os.path.join(original_path, "extracted")
        if os.path.exists(extract_dir):
            raise HTTPException(status_code=501, detail="Refactor de projet non encore supporté")
        raise HTTPException(status_code=404, detail="Aucun fichier à refactoriser trouvé")

    file_path = os.path.join(original_path, py_files[0])
    refactored_dir = os.path.join(session_path, "refactored")
    os.makedirs(refactored_dir, exist_ok=True)

    # Lire le code original
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_code = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Impossible de lire le fichier original")

    # Etape 1: Analyse et suppression du code mort
    dead_code_report = analyze_dead_code(file_path)
    intermediate_report = {"dead_code": dead_code_report, "convention": []}
    intermediate_path = apply_refactors(
        file_path,
        intermediate_report,
        rules=[DeadCodeRefactor],
        output_dir=refactored_dir
    )

    # Etape 2: Analyse des conventions (docstrings manquantes)
    convention_report_full = analyze_convention(intermediate_path)
    convention_report = convention_report_full.get("messages", [])

    # Etape 3: Application des règles Docstring + Formatage
    final_report = {"dead_code": {}, "convention": convention_report, "format": {}}
    output_path = apply_refactors(
        intermediate_path,
        final_report,
        rules=[DocstringRule, FormatRule],
        output_dir=refactored_dir
    )

    # Lire le code refactorisé final
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            refactored_code = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Impossible de lire le fichier refactorisé")

    # Analyse complète du code refactorisé pour la comparaison
    new_report_data = full_analyze_script(output_path)
    
    # Analyse du code original pour comparaison
    original_analysis = full_analyze_script(file_path)
    
    # Formatter le rapport amélioré
    enhanced_report = generate_enhanced_report(new_report_data, original_analysis, os.path.basename(output_path))
    
    # Déterminer ce qui a été réellement appliqué
    dead_code_applied = count_dead_code_applied(dead_code_report, original_code, refactored_code)
    docstrings_applied = count_docstrings_applied(original_code, refactored_code)

    # Retourner la comparaison complète
    response_data = {
        "analysis": enhanced_report,
        "originalCode": original_code,
        "refactoredCode": refactored_code,
        "refactoringSteps": [
            {
                "name": "Suppression du code mort",
                "description": "Élimination des fonctions, variables et imports non utilisés",
                "changesCount": dead_code_applied["count"],
                "status": "completed" if dead_code_applied["count"] > 0 else "skipped",
                "details": dead_code_applied["details"],
                "notes": dead_code_applied["notes"]
            },
            {
                "name": "Ajout des docstrings",
                "description": "Ajout de documentation aux fonctions et classes manquantes",
                "changesCount": docstrings_applied["count"],
                "status": "completed" if docstrings_applied["count"] > 0 else "skipped",
                "details": docstrings_applied["details"],
                "notes": docstrings_applied["notes"]
            },
            {
                "name": "Formatage du code",
                "description": "Application des standards PEP8 et amélioration de la lisibilité",
                "changesCount": "Automatique",
                "status": "completed",
                "details": ["Application du style PEP8", "Correction des guillemets", "Formatage cohérent"]
            }
        ]
    }
    
    return JSONResponse(content=response_data, status_code=200)

# Fonctions pour améliorer le rapport
def generate_enhanced_report(new_report, original_report, file_name):
    """Génère un rapport amélioré avec résumé et catégorisation"""
    all_issues = extract_all_issues(new_report)
    total_issues = len(all_issues)
    
    return {
        "file_name": file_name,
        "summary": {
            "total_issues": total_issues,
            "quality_score": calculate_quality_score(total_issues),
            "by_category": categorize_issues_count(new_report),
            "by_priority": categorize_issues_by_priority_count(all_issues)
        },
        "issues_by_priority": categorize_issues_by_priority(all_issues),
        "recommendations": generate_recommendations(new_report),
        "detailed_analysis": new_report  # Garder l'analyse détaillée originale
    }

def calculate_quality_score(total_issues):
    """Calcule un score de qualité basé sur le nombre d'issues"""
    if total_issues == 0:
        return "Excellent"
    elif total_issues <= 5:
        return "Très bon"
    elif total_issues <= 10:
        return "Bon"
    elif total_issues <= 15:
        return "Moyen"
    else:
        return "À améliorer"

def extract_all_issues(report):
    """Extrait toutes les issues de tous les types d'analyse"""
    issues = []
    
    # Issues de complexité
    if 'complexity' in report:
        issues.extend(report['complexity'])
    
    # Issues de convention
    if 'convention' in report and 'messages' in report['convention']:
        issues.extend(report['convention']['messages'])
    
    # Issues de code mort
    if 'dead_code' in report and 'dead_code' in report['dead_code']:
        issues.extend(report['dead_code']['dead_code'])
    
    # Issues de redondance
    if 'redundancy' in report:
        issues.extend(report['redundancy'])
    
    return issues

def categorize_issues_count(report):
    """Compte les issues par catégorie"""
    return {
        "complexity": len(report.get('complexity', [])),
        "convention": len(report.get('convention', {}).get('messages', [])),
        "dead_code": len(report.get('dead_code', {}).get('dead_code', [])),
        "redundancy": len(report.get('redundancy', []))
    }

def categorize_issues_by_priority_count(issues):
    """Compte les issues par priorité"""
    critical = 0
    warning = 0
    info = 0
    
    for issue in issues:
        if is_critical_issue(issue):
            critical += 1
        elif is_warning_issue(issue):
            warning += 1
        else:
            info += 1
    
    return {"critical": critical, "warning": warning, "info": info}

def categorize_issues_by_priority(issues):
    """Catégorise les issues par priorité"""
    critical = []
    warning = []
    info = []
    
    for issue in issues:
        if is_critical_issue(issue):
            critical.append(issue)
        elif is_warning_issue(issue):
            warning.append(issue)
        else:
            info.append(issue)
    
    return {"critical": critical, "warning": warning, "info": info}

def is_critical_issue(issue):
    """Détermine si une issue est critique"""
    if isinstance(issue, dict):
        # Issues de code mort
        if issue.get('symbol') in ['unused-function', 'unused-variable', 'unused-import']:
            return True
        # Issues de sécurité
        if 'security' in str(issue.get('message', '')).lower():
            return True
    return False

def is_warning_issue(issue):
    """Détermine si une issue est un avertissement"""
    if isinstance(issue, dict):
        # Issues de complexité élevée
        if issue.get('type') == 'Function' and issue.get('complexity', 0) > 5:
            return True
        # Issues de convention importantes
        if issue.get('symbol') in ['missing-function-docstring', 'missing-class-docstring']:
            return True
    return False

def generate_recommendations(report):
    """Génère des recommandations basées sur l'analyse"""
    recommendations = []
    
    # Recommandations pour le code mort
    dead_code_issues = report.get('dead_code', {}).get('dead_code', [])
    if dead_code_issues:
        functions = [issue for issue in dead_code_issues if 'function' in issue.get('symbol', '')]
        variables = [issue for issue in dead_code_issues if 'variable' in issue.get('symbol', '')]
        imports = [issue for issue in dead_code_issues if 'import' in issue.get('symbol', '')]
        
        description_parts = []
        if functions:
            description_parts.append(f"{len(functions)} fonction(s)")
        if variables:
            description_parts.append(f"{len(variables)} variable(s)")
        if imports:
            description_parts.append(f"{len(imports)} import(s)")
        
        recommendations.append({
            "priority": "high",
            "category": "dead_code",
            "title": "Code non utilisé détecté",
            "description": f"{', '.join(description_parts)} non utilisé(s)",
            "suggestion": "Supprimer le code mort pour améliorer la maintenabilité"
        })
    
    # Recommandations pour les docstrings
    convention_issues = report.get('convention', {}).get('messages', [])
    docstring_issues = [issue for issue in convention_issues if 'docstring' in str(issue.get('message', '')).lower()]
    
    if docstring_issues:
        module_docs = [issue for issue in docstring_issues if 'module' in str(issue.get('message', '')).lower()]
        function_docs = [issue for issue in docstring_issues if 'function' in str(issue.get('message', '')).lower()]
        
        description_parts = []
        if module_docs:
            description_parts.append("module")
        if function_docs:
            description_parts.append(f"{len(function_docs)} fonction(s)")
        
        recommendations.append({
            "priority": "medium",
            "category": "documentation",
            "title": "Documentation manquante",
            "description": f"Docstring manquante pour le {', '.join(description_parts)}",
            "suggestion": "Compléter les docstrings pour une meilleure documentation"
        })
    
    # Recommandations pour le style de nommage
    naming_issues = [issue for issue in convention_issues if 'invalid-name' in str(issue.get('symbol', ''))]
    if naming_issues:
        recommendations.append({
            "priority": "low",
            "category": "convention",
            "title": "Problèmes de nommage",
            "description": f"{len(naming_issues)} nom(s) ne respectant pas les conventions",
            "suggestion": "Suivre les conventions PEP8 pour les noms de variables"
        })
    
    # Recommandations pour la complexité
    complexity_issues = report.get('complexity', [])
    high_complexity = [issue for issue in complexity_issues if issue.get('complexity', 0) > 5]
    if high_complexity:
        recommendations.append({
            "priority": "medium",
            "category": "complexity",
            "title": "Fonctions trop complexes",
            "description": f"{len(high_complexity)} fonction(s) avec une complexité élevée",
            "suggestion": "Refactoriser les fonctions complexes en sous-fonctions"
        })
    
    return recommendations

# Fonction pour savoir ce qui a ete applique reelement
def count_dead_code_applied(dead_code_report, original_code, refactored_code):
    """Détermine ce qui a été réellement supprimé du code mort"""
    dead_code_issues = dead_code_report.get('dead_code', [])
    
    # Analyser les différences entre le code original et refactorisé
    applied_count = 0
    applied_details = []
    notes = []
    
    # Vérifier les imports supprimés
    imports_removed = check_imports_removed(original_code, refactored_code)
    if imports_removed:
        applied_count += len(imports_removed)
        applied_details.append(f"{len(imports_removed)} import(s) supprimé(s)")
        applied_details.extend(imports_removed[:3])  # Limiter à 3 exemples
    
    # Vérifier les fonctions supprimées (basique)
    functions_removed = check_functions_removed(original_code, refactored_code, dead_code_issues)
    if functions_removed["count"] > 0:
        applied_count += functions_removed["count"]
        applied_details.append(f"{functions_removed['count']} fonction(s) supprimée(s)")
        notes.append(f"Fonctions non supprimées: {functions_removed['remaining']}")
    
    # Vérifier les variables supprimées (basique)
    variables_removed = check_variables_removed(original_code, refactored_code, dead_code_issues)
    if variables_removed["count"] > 0:
        applied_count += variables_removed["count"]
        applied_details.append(f"{variables_removed['count']} variable(s) supprimée(s)")
        notes.append(f"Variables non supprimées: {variables_removed['remaining']}")
    
    # Si rien n'a été appliqué mais qu'il y a des problèmes détectés
    if applied_count == 0 and dead_code_issues:
        notes.append("Détection activée mais suppression désactivée dans les paramètres")
        # Montrer ce qui aurait pu être supprimé
        functions = [issue for issue in dead_code_issues if 'function' in issue.get('symbol', '')]
        variables = [issue for issue in dead_code_issues if 'variable' in issue.get('symbol', '')]
        imports = [issue for issue in dead_code_issues if 'import' in issue.get('symbol', '')]
        
        potential_details = []
        if functions:
            potential_details.append(f"{len(functions)} fonction(s) détectée(s)")
        if variables:
            potential_details.append(f"{len(variables)} variable(s) détectée(s)")
        if imports:
            potential_details.append(f"{len(imports)} import(s) détecté(s)")
        
        applied_details = potential_details
    
    return {
        "count": applied_count,
        "details": applied_details if applied_details else ["Aucune suppression appliquée"],
        "notes": notes
    }

def count_docstrings_applied(original_code, refactored_code):
    """Détermine combien de docstrings ont été ajoutées"""
    # Compter les docstrings dans le code original
    original_docstrings = original_code.count('"""') + original_code.count("'''")
    
    # Compter les docstrings dans le code refactorisé
    refactored_docstrings = refactored_code.count('"""') + refactored_code.count("'''")
    
    docstrings_added = refactored_docstrings - original_docstrings
    
    details = []
    if docstrings_added > 0:
        details.append(f"{docstrings_added} docstring(s) ajoutée(s)")
    else:
        details.append("Aucune docstring ajoutée")
    
    return {
        "count": docstrings_added,
        "details": details,
        "notes": []
    }

def check_imports_removed(original_code, refactored_code):
    """Détecte les imports qui ont été supprimés"""
    removed_imports = []
    
    # Extraire les imports du code original
    original_imports = extract_imports(original_code)
    refactored_imports = extract_imports(refactored_code)
    
    # Trouver les imports manquants dans le code refactorisé
    for imp in original_imports:
        if imp not in refactored_imports:
            removed_imports.append(f"Import supprimé: {imp}")
    
    return removed_imports

def extract_imports(code):
    """Extrait les lignes d'import d'un code Python"""
    imports = []
    lines = code.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('import ') or line.startswith('from '):
            imports.append(line)
    return imports

def check_functions_removed(original_code, refactored_code, dead_code_issues):
    """Détecte les fonctions qui ont été supprimées (version basique)"""
    # Extraire les noms de fonctions du code original
    original_functions = extract_function_names(original_code)
    refactored_functions = extract_function_names(refactored_code)
    
    # Fonctions manquantes dans le code refactorisé
    missing_functions = [f for f in original_functions if f not in refactored_functions]
    
    # Fonctions détectées comme mortes mais toujours présentes
    dead_functions = [issue for issue in dead_code_issues if 'function' in issue.get('symbol', '')]
    remaining_functions = [issue.get('message', '') for issue in dead_functions 
                          if extract_function_name_from_message(issue.get('message', '')) in refactored_functions]
    
    return {
        "count": len(missing_functions),
        "remaining": len(remaining_functions)
    }

def check_variables_removed(original_code, refactored_code, dead_code_issues):
    """Détecte les variables qui ont été supprimées (version basique)"""
    # Version simplifiée
    original_vars = extract_global_variables(original_code)
    refactored_vars = extract_global_variables(refactored_code)
    
    missing_vars = [v for v in original_vars if v not in refactored_vars]
    
    # Variables détectées comme mortes mais toujours présentes
    dead_variables = [issue for issue in dead_code_issues if 'variable' in issue.get('symbol', '')]
    remaining_variables = len(dead_variables) - len(missing_vars)
    
    return {
        "count": len(missing_vars),
        "remaining": max(0, remaining_variables)
    }

def extract_function_names(code):
    """Extrait les noms de fonctions d'un code Python (version basique)"""
    functions = []
    lines = code.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('def '):
            # Extraire le nom de la fonction
            func_name = line[4:].split('(')[0].strip()
            functions.append(func_name)
    return functions

def extract_function_name_from_message(message):
    """Extrait le nom de fonction d'un message d'erreur"""
    if "'" in message:
        return message.split("'")[1]
    return ""

def extract_global_variables(code):
    """Extrait les variables globales (version basique)"""
    variables = []
    lines = code.split('\n')
    for line in lines:
        line = line.strip()
        # Détection basique des assignments de variables
        if ' = ' in line and not line.startswith('def ') and not line.startswith('class '):
            var_name = line.split(' = ')[0].strip()
            if var_name and not var_name.startswith('#'):
                variables.append(var_name)
    return variables