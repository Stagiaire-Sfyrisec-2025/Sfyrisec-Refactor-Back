import pytest
import os
from app.services.laravel.refactor import laravel_refactor

@pytest.mark.asyncio
async def test_laravel_helper_refactor(temp_file, mock_run_tool):
    """Teste la migration des helpers Laravel."""
    input_code = """<?php
use Session;
class ExampleController extends Controller {
    public function index() {
        $name = config('app.name');
    }
}
"""
    expected_code = """<?php
use Illuminate\Support\Facades\Config;
use Session;
class ExampleController extends Controller {
    public function index() {
        $name = Config::get('app.name');
    }
}
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored helper", "")
    
    refactored_code, logs = laravel_refactor(temp_file, version="8")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored helper" in logs

@pytest.mark.asyncio
async def test_laravel_session_refactor(temp_file, mock_run_tool):
    """Teste la migration des sessions Laravel."""
    input_code = """<?php
use Session;
class ExampleController extends Controller {
    public function index() {
        Session::put('user_id', 123);
    }
}
"""
    expected_code = """<?php
use Illuminate\Support\Facades\Session;
class ExampleController extends Controller {
    public function index() {
        Session::put('user_id', 123);
    }
}
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored session", "")
    
    refactored_code, logs = laravel_refactor(temp_file, version="8")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored session" in logs