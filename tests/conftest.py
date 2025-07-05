import pytest
import os
import tempfile
from unittest.mock import patch
from app.utils.tool_runner import run_tool

@pytest.fixture
def temp_file():
    """Crée un fichier temporaire pour les tests."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".php") as temp:
        yield temp.name
    if os.path.exists(temp.name):
        os.unlink(temp.name)

@pytest.fixture
def mock_run_tool():
    """Mock de la fonction run_tool pour simuler l'exécution de Rector."""
    with patch("app.utils.tool_runner.run_tool") as mock:
        yield mock