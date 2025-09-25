import os
import ast
import logging

logging.basicConfig(level=logging.INFO)

try:
    from ast import unparse as to_source
except ImportError:
    import astor
    to_source = astor.to_source

from .dead_code_rule import DeadCodeRefactor
from .convention_rule import ConventionRefactor

def apply_refactors(file_path, report, rules=None, output_dir="refactored", in_place=False):
    """
    Applique les règles de refactorisation sur un fichier.
    - file_path : chemin du fichier original
    - report : résultat de l'analyse (ex. analyze_dead_code)
    - rules : liste de classes de règles
    - output_dir : dossier de sortie (si in_place=False)
    - in_place : bool, si True écrase le fichier original
    """
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise ValueError(f"Erreur de parsing du fichier {file_path}: {e}")

    # Le rapport complet est maintenant passé.
    # Le rapport de code mort est sous la clé "dead_code".
    dead_code_report = report.get("dead_code", {})

    if rules is None:
        rules = [
            (DeadCodeRefactor, dead_code_report),
            (ConventionRefactor, report.get("convention", {})),
        ]

    for RuleClass, rule_report in rules:
        if rule_report:
            rule = RuleClass(rule_report)
            tree = rule.visit(tree)

    new_code = to_source(tree)

    if in_place:
        output_path = file_path
    else:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(file_path)
        output_path = os.path.join(output_dir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_code)

    logging.info(f"Refactoring terminé : {file_path} -> {output_path}")
    return output_path
