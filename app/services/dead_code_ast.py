from typing import Dict, List, Any, Set
import ast

# ANALYSE AVEC AST
def analyze_dead_code_ast(file_path: str) -> Dict[str, Any]:
    """
    Analyse fiable du code mort avec AST
    Détecte les fonctions, variables et imports non utilisés
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Collections pour le tracking
        functions_defined: Dict[str, int] = {}
        variables_defined: Set[str] = set()
        imports_defined: Dict[str, int] = {}
        
        functions_called: Set[str] = set()
        variables_used: Set[str] = set()
        
        # Visiteur AST
        class DeadCodeVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                if not node.name.startswith("_dynamic_"):
                    functions_defined[node.name] = node.lineno
                self.generic_visit(node)


            
            def visit_Import(self, node):
                for alias in node.names:
                    imports_defined[alias.name] = node.lineno
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                module = node.module or ""
                for alias in node.names:
                    full_name = f"{module}.{alias.name}" if module else alias.name
                    imports_defined[full_name] = node.lineno
                self.generic_visit(node)
            
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    variables_defined.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    variables_used.add(node.id)
                self.generic_visit(node)
            
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    functions_called.add(node.func.id)
                self.generic_visit(node)
        
        visitor = DeadCodeVisitor()
        visitor.visit(tree)
        
        # Identifier le code mort
        unused_functions = {
            name: line 
            for name, line in functions_defined.items() 
            if name not in functions_called and not name.startswith('__')
        }
        
        unused_variables = variables_defined - variables_used
        unused_imports = {
            imp: line 
            for imp, line in imports_defined.items() 
            if imp.split('.')[-1] not in functions_called and 
               imp.split('.')[-1] not in variables_used
        }
        
        # Formater les résultats
        dead_code_warnings = []
        
        for name, line in unused_functions.items():
            dead_code_warnings.append({
                "line": line,
                "symbol": "unused-function",
                "message": f"Function '{name}' is defined but never used"
            })
        
        for var in unused_variables:
            dead_code_warnings.append({
                "line": 0,  # Ligne approximative
                "symbol": "unused-variable", 
                "message": f"Variable '{var}' is defined but never used"
            })
        
        for imp, line in unused_imports.items():
            dead_code_warnings.append({
                "line": line,
                "symbol": "unused-import",
                "message": f"Import '{imp}' is not used"
            })
        
        return {
            "file": file_path,
            "dead_code": dead_code_warnings,
            "stats": {
                "total_functions": len(functions_defined),
                "unused_functions": len(unused_functions),
                "total_variables": len(variables_defined),
                "unused_variables": len(unused_variables),
                "total_imports": len(imports_defined),
                "unused_imports": len(unused_imports)
            }
        }
        
    except Exception as e:
        return {"error": str(e), "file": file_path}