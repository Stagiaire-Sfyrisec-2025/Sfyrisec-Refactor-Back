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

@pytest.mark.asyncio
async def test_laravel_route_refactor(temp_file, mock_run_tool):
    """Teste la migration des routes Laravel."""
    input_code = """<?php
use Illuminate\Support\Facades\Route;
Route::get('/home', 'HomeController@index');
"""
    expected_code = """<?php
use Illuminate\Support\Facades\Route;
Route::middleware(['web'])->get('/home', 'HomeController@index');
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored route", "")
    
    refactored_code, logs = laravel_refactor(temp_file, version="8")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored route" in logs

@pytest.mark.asyncio
async def test_laravel_model_refactor(temp_file, mock_run_tool):
    """Teste la migration des modèles Laravel."""
    input_code = """<?php
use Illuminate\Database\Eloquent\Model;
class User extends Model {
}
"""
    expected_code = """<?php
use Illuminate\Database\Eloquent\Model;
class User extends Model {
    public $timestamps = true;
}
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored model", "")
    
    refactored_code, logs = laravel_refactor(temp_file, version="8")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored model" in logs

@pytest.mark.asyncio
async def test_laravel_config_refactor(temp_file, mock_run_tool):
    """Teste la migration des configurations Laravel."""
    input_code = """<?php
return [
    'timezone' => 'UTC',
];
"""
    expected_code = """<?php
return [
    'timezone' => env('APP_TIMEZONE', 'UTC'),
];
"""
    with open(temp_file, "w") as f:
        f.write(input_code)
    
    mock_run_tool.return_value = ("Refactored config", "")
    
    refactored_code, logs = laravel_refactor(temp_file, version="8")
    
    assert refactored_code.strip() == expected_code.strip()
    assert "Refactored config" in logs