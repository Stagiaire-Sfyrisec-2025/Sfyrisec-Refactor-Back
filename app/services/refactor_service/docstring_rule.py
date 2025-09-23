import ast
from typing import List, Dict, Any


class DocstringRule(ast.NodeTransformer):
    """
    Ajoute des docstrings minimalistes aux fonctions, classes
    et au module lorsqu'ils sont absents.
    """

    def __init__(self, report_convention: List[Dict[str, Any]]):
        self.missing_functions = {
            item["line"]
            for item in report_convention
            if item["symbol"] == "missing-function-docstring"
        }
        self.missing_classes = {
            item["line"]
            for item in report_convention
            if item["symbol"] == "missing-class-docstring"
        }
        # True si le rapport mentionne l'absence de docstring de module
        self.missing_module = any(
            item.get("symbol") == "missing-module-docstring"
            for item in report_convention
        )
    # Module
    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Ajoute un docstring au module si nécessaire."""
        if self.missing_module and not ast.get_docstring(node):
            docstring_node = ast.Expr(
                value=ast.Constant(value="TODO: Describe this module.")
            )
            node.body.insert(0, docstring_node)
        return self.generic_visit(node)

    #Fonction
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        if node.lineno in self.missing_functions and not ast.get_docstring(node):
            docstring_node = ast.Expr(
                value=ast.Constant(value="TODO: Describe this function.")
            )
            node.body.insert(0, docstring_node)
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        if node.lineno in self.missing_functions and not ast.get_docstring(node):
            docstring_node = ast.Expr(
                value=ast.Constant(value="TODO: Describe this async function.")
            )
            node.body.insert(0, docstring_node)
        return self.generic_visit(node)

    #Classes
    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        if node.lineno in self.missing_classes and not ast.get_docstring(node):
            docstring_node = ast.Expr(
                value=ast.Constant(value=f"TODO: Describe class {node.name}.")
            )
            node.body.insert(0, docstring_node)
        return self.generic_visit(node)
