import pytest
import os
from app.services.codeigniter.refactor import codeigniter_refactor

@pytest.mark.asyncio
async def test_codeigniter_helper_refactor(temp_file, mock_run_tool):
    """Teste la migration des helpers CodeIgniter."""
    input_code = """<?php
class Welcome extends CI_Controller {
    public function index() {
        $this->load->helper('form');
    }
}
"""
    expected_code = """<?php
use CodeIgniter\CodeIgniter;
class Welcome extends \\CodeIgniter\\Controller {
    public function index() {
        helper('form');
    }
}
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored helper", "")
    
    refactored_code, logs = codeigniter_refactor(temp_file, version="4")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored helper" in logs

@pytest.mark.asyncio
async def test_codeigniter_session_refactor(temp_file, mock_run_tool):
    """Teste la migration des sessions CodeIgniter."""
    input_code = """<?php
class Welcome extends CI_Controller {
    public function index() {
        $this->session->set_userdata('user_id', 123);
    }
}
"""
    expected_code = """<?php
use CodeIgniter\Session\Session;
class Welcome extends \\CodeIgniter\\Controller {
    public function index() {
        session()->set('user_id', 123);
    }
}
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored session", "")
    
    refactored_code, logs = codeigniter_refactor(temp_file, version="4")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored session" in logs

@pytest.mark.asyncio
async def test_codeigniter_route_refactor(temp_file, mock_run_tool):
    """Teste la migration des routes CodeIgniter."""
    input_code = """<?php
$route['default_controller'] = 'Welcome';
"""
    expected_code = """<?php
Routes::add('default_controller', 'Welcome');
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored route", "")
    
    refactored_code, logs = codeigniter_refactor(temp_file, version="4")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored route" in logs

@pytest.mark.asyncio
async def test_codeigniter_model_refactor(temp_file, mock_run_tool):
    """Teste la migration des modèles CodeIgniter."""
    input_code = """<?php
class User_model extends CI_Model {
}
"""
    expected_code = """<?php
class User_model extends \CodeIgniter\Model {
}
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored model", "")
    
    refactored_code, logs = codeigniter_refactor(temp_file, version="4")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored model" in logs

@pytest.mark.asyncio
async def test_codeigniter_config_refactor(temp_file, mock_run_tool):
    """Teste la migration des configurations CodeIgniter."""
    input_code = """<?php
$config['base_url'] = 'http://example.com';
"""
    expected_code = """<?php
\CodeIgniter\Config\Services::set('base_url', 'http://example.com');
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored config", "")
    
    refactored_code, logs = codeigniter_refactor(temp_file, version="4")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored config" in logs