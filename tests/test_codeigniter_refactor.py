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