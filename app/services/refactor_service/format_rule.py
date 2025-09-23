import subprocess
import logging

logging.basicConfig(level=logging.INFO)

class FormatRule:
    """
    Applique le tri des imports (isort) et le formatage du code (black)
    """

    def __init__(self, _report=None):
        pass

    def visit_file(self, file_path):
        """Applique le formatage directement sur le fichier"""
        try:
            logging.info(f"Tri des imports avec isort : {file_path}")
            subprocess.run(["isort", file_path], check=True, capture_output=True)
            
            logging.info(f"Formatage du code avec black : {file_path}")
            subprocess.run(["black", file_path], check=True, capture_output=True)
            
            return file_path
        except subprocess.CalledProcessError as e:
            logging.error(f"Erreur lors du formatage: {e}")
            return file_path
        except FileNotFoundError as e:
            logging.error(f"Outil de formatage non trouvé: {e}")
            return file_path