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
from .docstring_rule import DocstringRule
from .format_rule import FormatRule

def apply_refactors(file_path, report, rules=None, output_dir="refactored", in_place=False):
    """
    Applique les règles de refactorisation sur un fichier Python.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise ValueError(f"Erreur de parsing du fichier {file_path}: {e}")

    # Regles par défaut : suppression code mort + docstrings
    if rules is None:
        rules = [DeadCodeRefactor, DocstringRule]

    # Separation des regles AST des regles de formatage
    ast_rules = []
    format_rules = []
    
    for RuleClass in rules:
        if RuleClass.__name__ == "FormatRule":
            format_rules.append(RuleClass)
        else:
            ast_rules.append(RuleClass)

    # Appliquer les regles AST
    for RuleClass in ast_rules:
        if RuleClass is DeadCodeRefactor:
            sub_report = report.get("dead_code", {})
        elif RuleClass is DocstringRule:
            sub_report = report.get("convention", [])
        else:
            sub_report = report

        rule = RuleClass(sub_report)
        tree = rule.visit(tree)
        ast.fix_missing_locations(tree)

    new_code = to_source(tree)

    if in_place:
        output_path = file_path
    else:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(file_path)
        output_path = os.path.join(output_dir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_code)

    # Appliquer le formatage a la fin
    for FormatRuleClass in format_rules:
        rule = FormatRuleClass(report.get("format", {}))
        output_path = rule.visit_file(output_path)

    logging.info(f"Refactoring terminé : {file_path} -> {output_path}")
    return output_path