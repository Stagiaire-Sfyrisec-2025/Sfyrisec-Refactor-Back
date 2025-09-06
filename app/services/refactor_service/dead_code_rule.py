import ast
import logging
import re
from typing import Dict, Any, Set

logging.basicConfig(level=logging.INFO)

class DeadCodeRefactor(ast.NodeTransformer):
    def __init__(self, dead_code_report: Dict[str, Any]):
        self.dead_code_report = dead_code_report
        self._parse_dead_code_messages()
    
    def _parse_dead_code_messages(self):
        self.unused_funcs: Set[str] = set()
        self.unused_vars: Set[str] = set()
        self.unused_imports: Set[str] = set()
        self.unused_classes: Set[str] = set()
        
        for message in self.dead_code_report.get("dead_code", []):
            # Fonctions - pattern: "Function 'nom' is defined but never used"
            if "Function" in message and "'" in message:
                match = re.search(r"Function '([^']+)'", message)
                if match:
                    self.unused_funcs.add(match.group(1))
            
            # Variables - pattern: "Variable 'nom' is defined but never used"  
            elif "variable" in message.lower() and "'" in message:
                match = re.search(r"Variable '([^']+)'", message, re.IGNORECASE)
                if match:
                    self.unused_vars.add(match.group(1))
            
            # Imports - pattern: "Import 'nom' is not used"
            elif "import" in message.lower() and "'" in message:
                match = re.search(r"Import '([^']+)'", message, re.IGNORECASE)
                if match:
                    self.unused_imports.add(match.group(1))
            
            # Classes - pattern: "Class 'nom' is defined but never used"
            elif "Class" in message and "'" in message:
                match = re.search(r"Class '([^']+)'", message)
                if match:
                    self.unused_classes.add(match.group(1))
        
        logging.info(f"Unused functions: {self.unused_funcs}")
        logging.info(f"Unused variables: {self.unused_vars}")
        logging.info(f"Unused imports: {self.unused_imports}")
        logging.info(f"Unused classes: {self.unused_classes}")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        """Supprime les fonctions non utilisées"""
        if node.name in self.unused_funcs:
            logging.info(f"Removing unused function: {node.name}")
            return None
        return self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        """Supprime les classes non utilisées"""
        if node.name in self.unused_classes:
            logging.info(f"Removing unused class: {node.name}")
            return None
        return self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> Any:
        """Nettoie les imports simples non utilisés"""
        original_count = len(node.names)
        node.names = [
            alias for alias in node.names
            if alias.name not in self.unused_imports
        ]
        
        if len(node.names) < original_count:
            removed = original_count - len(node.names)
            logging.info(f"Removed {removed} unused import(s)")
        
        if not node.names:
            logging.info(f"Removing entire import line")
            return None
            
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        """Nettoie les imports from non utilisés"""
        module_name = node.module or ""
        original_count = len(node.names)
        
        new_names = []
        for alias in node.names:
            # Vérifier si l'import est utilisé
            full_import_name = f"{module_name}.{alias.name}" if module_name else alias.name
            alias_name = alias.asname or alias.name
            
            if full_import_name not in self.unused_imports and alias_name not in self.unused_imports:
                new_names.append(alias)
            else:
                logging.info(f"Removing unused import: {alias.name}")
        
        node.names = new_names
        
        if len(node.names) < original_count:
            removed = original_count - len(node.names)
            logging.info(f"Removed {removed} import(s) from {module_name}")
        
        if not node.names:
            logging.info(f"Removing entire import from: {module_name}")
            return None
            
        return node

    def visit_Assign(self, node: ast.Assign) -> Any:
        """
        ATTENTION: La suppression des assignations est dangereuse !
        """
        return node
