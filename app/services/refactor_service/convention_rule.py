import ast
import logging
from typing import Dict, Any

import re

def to_snake_case(name: str) -> str:
    """Convertit un nom en snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class ConventionRefactor(ast.NodeTransformer):
    """
    Une règle de refactorisation pour corriger les problèmes de convention de nommage.
    """
    def __init__(self, convention_report: Dict[str, Any]):
        """
        Initialise la règle avec le rapport de convention.

        Args:
            convention_report (Dict[str, Any]): Le rapport généré par `analyze_convention`.
        """
        self.report = convention_report
        self.violations = {
            item['line']: item['message']
            for item in self.report.get('messages', [])
            if 'snake_case' in item['message']
        }
        logging.info(f"Convention violations to fix: {self.violations}")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """
        Visite les définitions de fonctions et les renomme si nécessaire.
        """
        if node.lineno in self.violations:
            original_name = node.name
            new_name = to_snake_case(original_name)
            logging.info(f"Renaming function '{original_name}' to '{new_name}'")
            node.name = new_name

        self.generic_visit(node)
        return node